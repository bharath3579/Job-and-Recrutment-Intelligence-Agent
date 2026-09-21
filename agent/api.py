"""FastAPI application providing REST endpoints and serving the mobile-first recruitment dashboard."""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from sqlalchemy import desc
from sqlalchemy.orm import Session

from agent.config import CANDIDATE_PROFILE, EXCEL_FILE
from agent.database import (
    Company,
    Job,
    Outreach,
    Person,
    PipelineRun,
    RecruitmentSignal,
    get_db,
    init_db,
)
from agent.services.company_scout import CompanyScout
from agent.services.email_ingest import EmailIngest
from agent.services.excel_sync import ExcelSync
from agent.services.full_scanner import FullScanner
from agent.services.reporter import Reporter
from agent.services.resume_parser import ResumeParser

app = FastAPI(
    title="Recruitment Intelligence Agent API",
    description="Cost-free, personal AI-powered Job and Recruitment Intelligence Agent",
    version="1.0.0",
)

# CORS configuration for personal mobile/iOS access over LAN
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Templates directory
TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


# Pydantic Request Models
class CompanyConnectRequest(BaseModel):
    company: str
    reason: Optional[str] = "Campus hiring announced / Parallel off-campus inquiry"


class EmailIngestRequest(BaseModel):
    email_text: str
    sender: Optional[str] = ""


class ApprovalActionRequest(BaseModel):
    action: str  # approve, reject, edit_and_approve
    message: Optional[str] = None


class JobStatusUpdateRequest(BaseModel):
    status: str


# ==============================================================================
# UI ROUTES
# ==============================================================================
@app.get("/", response_class=HTMLResponse)
@app.get("/dashboard", response_class=HTMLResponse)
def get_dashboard(request: Request):
    html_file = TEMPLATES_DIR / "dashboard.html"
    return HTMLResponse(content=html_file.read_text(encoding="utf-8"))


# ==============================================================================
# API V1: CORE INTELLIGENCE PIPELINE ENDPOINTS
# ==============================================================================
@app.get("/api/v1/stats")
def get_stats(db: Session = Depends(get_db)):
    total_jobs = db.query(Job).count()
    high_match = db.query(Job).filter(Job.match_score >= 80.0).count()
    active_signals = db.query(RecruitmentSignal).filter(RecruitmentSignal.status == "Active").count()
    pending_approvals = db.query(Outreach).filter(Outreach.status == "Pending Approval").count()
    applied_count = db.query(Job).filter(Job.application_status == "Applied").count()
    interviews_count = db.query(Job).filter(Job.application_status == "Interview").count()

    return {
        "total_jobs": total_jobs,
        "high_match_jobs": high_match,
        "active_signals": active_signals,
        "pending_approvals": pending_approvals,
        "applied_count": applied_count,
        "interviews_count": interviews_count,
    }


@app.post("/api/v1/scan")
def trigger_full_scan(db: Session = Depends(get_db)):
    """Mode 1: Execute Full Recruitment Scan."""
    result = FullScanner.run_full_scan(db)
    # Auto sync to Excel
    ExcelSync.sync_database_to_excel(db)
    return result


@app.post("/api/v1/company-connect")
def trigger_company_connect(req: CompanyConnectRequest, db: Session = Depends(get_db)):
    """Mode 2: Targeted Company Direct Connect (e.g. for campus/parallel off-campus pipeline)."""
    result = CompanyScout.scout_company(db, company_name=req.company, reason=req.reason or "")
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    # Auto sync to Excel
    ExcelSync.sync_database_to_excel(db)
    return result


@app.post("/api/v1/ingest/email")
def ingest_email(req: EmailIngestRequest, db: Session = Depends(get_db)):
    """Parse email and update application/interview status."""
    result = EmailIngest.process_email_text(db, email_body=req.email_text, sender=req.sender or "")
    # Auto sync to Excel
    ExcelSync.sync_database_to_excel(db)
    return result


# ==============================================================================
# API V1: DATA & APPROVAL MANAGEMENT
# ==============================================================================
@app.get("/api/v1/jobs")
def list_jobs(db: Session = Depends(get_db)):
    jobs = db.query(Job).order_by(desc(Job.match_score)).all()
    return [j.to_dict() for j in jobs]


@app.patch("/api/v1/jobs/{job_id}/status")
def update_job_status(job_id: int, req: JobStatusUpdateRequest, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    job.application_status = req.status
    db.commit()
    return {"success": True, "job_id": job.job_id, "status": job.application_status}


@app.get("/api/v1/signals")
def list_signals(db: Session = Depends(get_db)):
    signals = db.query(RecruitmentSignal).order_by(desc(RecruitmentSignal.detected_date)).all()
    return [s.to_dict() for s in signals]


@app.get("/api/v1/people")
def list_people(db: Session = Depends(get_db)):
    people = db.query(Person).order_by(desc(Person.created_at)).all()
    return [p.to_dict() for p in people]


@app.get("/api/v1/approvals")
def list_approvals(db: Session = Depends(get_db)):
    approvals = db.query(Outreach).filter(Outreach.status == "Pending Approval").order_by(desc(Outreach.date)).all()
    return [a.to_dict() for a in approvals]


@app.post("/api/v1/approvals/{outreach_id}/action")
def handle_approval_action(outreach_id: int, req: ApprovalActionRequest, db: Session = Depends(get_db)):
    outreach = db.query(Outreach).filter(Outreach.id == outreach_id).first()
    if not outreach:
        raise HTTPException(status_code=404, detail="Outreach draft not found")

    if req.action == "approve":
        outreach.status = "Approved"
        outreach.notes = f"{outreach.notes}\nApproved by user for sending."
    elif req.action == "reject":
        outreach.status = "Rejected"
        outreach.notes = f"{outreach.notes}\nRejected by user."
    elif req.action == "edit_and_approve":
        if req.message:
            outreach.message = req.message
        outreach.status = "Approved"
        outreach.notes = f"{outreach.notes}\nEdited and approved by user."

    db.commit()
    ExcelSync.sync_database_to_excel(db)
    return {"success": True, "outreach_id": outreach.outreach_id, "status": outreach.status}


@app.get("/api/v1/profile")
def get_profile():
    return CANDIDATE_PROFILE


@app.get("/api/v1/resume/parsed")
def get_parsed_resume():
    resumes = ResumeParser.get_available_resumes()
    if not resumes:
        sample_path = ResumeParser.create_sample_ats_resume()
        resumes = [sample_path]
    latest_resume = resumes[0]
    return ResumeParser.parse_docx(latest_resume)


@app.get("/api/v1/pipeline/runs")
def list_pipeline_runs(db: Session = Depends(get_db)):
    runs = db.query(PipelineRun).order_by(desc(PipelineRun.start_time)).limit(15).all()
    return [r.to_dict() for r in runs]


# ==============================================================================
# API V1: EXCEL SYNC & DOWNLOAD
# ==============================================================================
@app.post("/api/v1/sync-excel")
def sync_excel(db: Session = Depends(get_db)):
    path = ExcelSync.sync_database_to_excel(db)
    return {"success": True, "file_path": path}


@app.get("/api/v1/download-excel")
def download_excel(db: Session = Depends(get_db)):
    ExcelSync.sync_database_to_excel(db)
    if not EXCEL_FILE.exists():
        raise HTTPException(status_code=404, detail="Excel tracker not found")
    return FileResponse(
        path=str(EXCEL_FILE),
        filename="recruitment_tracker.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


# ==============================================================================
# API V1: INTELLIGENCE REPORTS
# ==============================================================================
@app.get("/api/v1/reports/daily")
def get_daily_report(db: Session = Depends(get_db)):
    report_md = Reporter.generate_daily_report(db)
    return {"report": report_md}


@app.get("/api/v1/reports/weekly")
def get_weekly_report(db: Session = Depends(get_db)):
    report_md = Reporter.generate_weekly_report(db)
    return {"report": report_md}


@app.on_event("startup")
def on_startup():
    init_db()
