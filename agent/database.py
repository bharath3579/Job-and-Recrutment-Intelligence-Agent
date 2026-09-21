"""Database schema, models, and session management using SQLAlchemy and SQLite."""

import json
from datetime import datetime
from typing import Any, Dict, List, Optional
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    create_engine,
    desc,
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

from agent.config import DATABASE_URL

Base = declarative_base()


class Job(Base):
    """Canonical Job posting entity with multi-source tracking and deduplication."""
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(String(50), unique=True, index=True, nullable=False)  # e.g., JOB-00101
    company = Column(String(200), index=True, nullable=False)
    job_title = Column(String(250), index=True, nullable=False)
    location = Column(String(150), default="Hyderabad")
    work_mode = Column(String(50), default="Hybrid")  # Remote, Hybrid, On-site, Unspecified
    sources_json = Column(Text, default="[]")  # JSON list of sources e.g. ["LinkedIn", "Company Careers"]
    job_url = Column(String(500), nullable=True)
    posted_date = Column(String(50), nullable=True)
    freshness_tier = Column(String(50), default="<24h")  # <24h, 24-72h, <7d, Stale
    deadline = Column(String(50), default="Not specified")
    experience_required = Column(String(100), default="0-2 years")
    salary = Column(String(100), default="Not disclosed")
    skills = Column(Text, default="")
    match_score = Column(Float, default=0.0)  # 0 to 100
    match_explanation = Column(Text, default="")
    recruitment_signal = Column(String(100), default="Normal Job Posting")
    recruitment_signal_date = Column(String(50), nullable=True)
    application_status = Column(
        String(50), default="Discovered"
    )  # Discovered, Reviewed, Shortlisted, Applied, Interview, Rejected, Offer
    application_date = Column(String(50), nullable=True)
    resume_version = Column(String(100), default="Resume_Data_Engineering.pdf")
    application_method = Column(String(100), default="Direct Link")  # DM, Email, Form, Direct Link
    contact_email = Column(String(150), nullable=True)
    notes = Column(Text, default="")
    last_checked = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

    @property
    def sources(self) -> List[str]:
        try:
            return json.loads(self.sources_json or "[]")
        except Exception:
            return [self.sources_json] if self.sources_json else []

    @sources.setter
    def sources(self, val: List[str]):
        self.sources_json = json.dumps(val or [])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "job_id": self.job_id,
            "company": self.company,
            "job_title": self.job_title,
            "location": self.location,
            "work_mode": self.work_mode,
            "sources": self.sources,
            "job_url": self.job_url,
            "posted_date": self.posted_date,
            "freshness_tier": self.freshness_tier,
            "deadline": self.deadline,
            "experience_required": self.experience_required,
            "salary": self.salary,
            "skills": self.skills,
            "match_score": self.match_score,
            "match_explanation": self.match_explanation,
            "recruitment_signal": self.recruitment_signal,
            "application_status": self.application_status,
            "application_date": self.application_date,
            "resume_version": self.resume_version,
            "application_method": self.application_method,
            "contact_email": self.contact_email,
            "notes": self.notes,
            "last_checked": self.last_checked.strftime("%Y-%m-%d %H:%M") if self.last_checked else "",
        }


class Company(Base):
    """Company hiring profile and intelligence."""
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, autoincrement=True)
    company = Column(String(200), unique=True, index=True, nullable=False)
    industry = Column(String(100), default="Technology / Analytics")
    careers_url = Column(String(500), nullable=True)
    location = Column(String(200), default="India")
    hiring_activity = Column(String(100), default="Active")  # High, Moderate, Active, Occasional
    relevant_roles = Column(Integer, default=1)
    recruiters_found = Column(Integer, default=0)
    hiring_managers_found = Column(Integer, default=0)
    recruitment_signals = Column(Integer, default=0)
    last_checked = Column(DateTime, default=datetime.utcnow)
    priority = Column(String(50), default="High")  # High, Medium, Low
    notes = Column(Text, default="")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "company": self.company,
            "industry": self.industry,
            "careers_url": self.careers_url,
            "location": self.location,
            "hiring_activity": self.hiring_activity,
            "relevant_roles": self.relevant_roles,
            "recruiters_found": self.recruiters_found,
            "hiring_managers_found": self.hiring_managers_found,
            "recruitment_signals": self.recruitment_signals,
            "last_checked": self.last_checked.strftime("%Y-%m-%d %H:%M") if self.last_checked else "",
            "priority": self.priority,
            "notes": self.notes,
        }


class Person(Base):
    """Recruiters, Hiring Managers, Alumni, and Senior Engineers."""
    __tablename__ = "people"

    id = Column(Integer, primary_key=True, autoincrement=True)
    person_id = Column(String(50), unique=True, index=True, nullable=False)  # e.g., PER-001
    name = Column(String(150), nullable=False)
    company = Column(String(200), index=True, nullable=False)
    job_title = Column(String(200), default="Recruiter / Talent Acquisition")
    linkedin_url = Column(String(500), unique=True, index=True, nullable=True)
    person_type = Column(
        String(100), default="Recruiter"
    )  # Recruiter, Talent Acquisition, Hiring Manager, Data Engineering Lead, LNMIIT Alumni, Senior DE
    connection_status = Column(
        String(50), default="Not Connected"
    )  # Existing, Not Connected, Pending, Connected
    relevant_job_id = Column(String(50), nullable=True)
    relevance_reason = Column(Text, default="")
    contacted = Column(Boolean, default=False)
    contact_date = Column(String(50), nullable=True)
    response = Column(String(100), default="No response yet")
    referral_requested = Column(Boolean, default=False)
    referral_status = Column(String(100), default="Not Requested")  # Not Requested, Requested, Received, Declined
    last_interaction = Column(String(100), default="Identified")
    next_action = Column(String(200), default="Review & approve connection request")
    notes = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "person_id": self.person_id,
            "name": self.name,
            "company": self.company,
            "job_title": self.job_title,
            "linkedin_url": self.linkedin_url,
            "person_type": self.person_type,
            "connection_status": self.connection_status,
            "relevant_job_id": self.relevant_job_id,
            "relevance_reason": self.relevance_reason,
            "contacted": "Yes" if self.contacted else "No",
            "contact_date": self.contact_date or "",
            "response": self.response,
            "referral_requested": "Yes" if self.referral_requested else "No",
            "referral_status": self.referral_status,
            "last_interaction": self.last_interaction,
            "next_action": self.next_action,
            "notes": self.notes,
        }


class RecruitmentSignal(Base):
    """Active hiring signals, walk-ins, off-campus drives, and referral calls."""
    __tablename__ = "recruitment_signals"

    id = Column(Integer, primary_key=True, autoincrement=True)
    signal_id = Column(String(50), unique=True, index=True, nullable=False)  # e.g., SIG-001
    company = Column(String(200), index=True, nullable=False)
    person = Column(String(150), default="Recruiter / Talent Acquisition")
    author_profile_url = Column(String(500), nullable=True)
    signal_type = Column(
        String(100), nullable=False
    )  # Active Recruitment Signal, Recruitment Event, Campus/Off-Campus Hiring, Referral Opportunity, Pipeline Signal, Normal Job Posting
    post_url = Column(String(500), nullable=False)
    post_date = Column(String(50), nullable=True)
    detected_date = Column(DateTime, default=datetime.utcnow)
    freshness_hours = Column(Integer, default=12)
    keywords = Column(String(300), default="")
    role = Column(String(200), default="Data Engineer")
    location = Column(String(150), default="Hyderabad / Remote")
    urgency = Column(String(50), default="High")  # Urgent, High, Medium, Low
    relevance = Column(Float, default=85.0)  # 0 to 100
    evidence = Column(Text, nullable=False)  # Snippet / quote showing evidence
    application_method = Column(String(100), default="DM / Email")
    contact_email = Column(String(150), nullable=True)
    status = Column(String(50), default="Active")  # Active, Actioned, Closed, Stale

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "signal_id": self.signal_id,
            "company": self.company,
            "person": self.person,
            "author_profile_url": self.author_profile_url,
            "signal_type": self.signal_type,
            "post_url": self.post_url,
            "post_date": self.post_date or "",
            "detected_date": self.detected_date.strftime("%Y-%m-%d %H:%M") if self.detected_date else "",
            "freshness_hours": self.freshness_hours,
            "keywords": self.keywords,
            "role": self.role,
            "location": self.location,
            "urgency": self.urgency,
            "relevance": self.relevance,
            "evidence": self.evidence,
            "application_method": self.application_method,
            "contact_email": self.contact_email or "",
            "status": self.status,
        }


class Outreach(Base):
    """Personalized outreach messages with strict Human Approval workflow."""
    __tablename__ = "outreach"

    id = Column(Integer, primary_key=True, autoincrement=True)
    outreach_id = Column(String(50), unique=True, index=True, nullable=False)  # e.g., OUT-001
    person_id = Column(String(50), nullable=True)
    person = Column(String(150), nullable=False)
    company = Column(String(200), nullable=False)
    job = Column(String(200), default="Data Engineer")
    message_type = Column(
        String(100), default="Connection Request"
    )  # Connection Request, Referral Request, 2025 Off-Campus Inquiry, Follow-up
    message = Column(Text, nullable=False)
    date = Column(DateTime, default=datetime.utcnow)
    status = Column(
        String(50), default="Pending Approval"
    )  # Draft, Pending Approval, Approved, Rejected, Sent
    response = Column(String(100), default="Pending response")
    follow_up_date = Column(String(50), nullable=True)
    referral_status = Column(String(100), default="Not Started")
    notes = Column(Text, default="")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "outreach_id": self.outreach_id,
            "person_id": self.person_id,
            "person": self.person,
            "company": self.company,
            "job": self.job,
            "message_type": self.message_type,
            "message": self.message,
            "date": self.date.strftime("%Y-%m-%d %H:%M") if self.date else "",
            "status": self.status,
            "response": self.response,
            "follow_up_date": self.follow_up_date or "",
            "referral_status": self.referral_status,
            "notes": self.notes,
        }


class ResumeVersion(Base):
    """Tracks tailored resume versions and usage."""
    __tablename__ = "resume_versions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)
    filename = Column(String(200), nullable=False)
    focus_area = Column(String(250), default="Data Engineering")
    times_used = Column(Integer, default=0)
    last_used_date = Column(DateTime, nullable=True)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "filename": self.filename,
            "focus_area": self.focus_area,
            "times_used": self.times_used,
            "last_used_date": self.last_used_date.strftime("%Y-%m-%d") if self.last_used_date else "Never",
        }


class PipelineRun(Base):
    """Logs details and telemetry for every pipeline execution."""
    __tablename__ = "pipeline_runs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    run_id = Column(String(50), unique=True, index=True, nullable=False)  # e.g., RUN-20260921-1400
    mode = Column(String(50), nullable=False)  # full_scan, company_connect, email_ingest, excel_sync
    status = Column(String(50), default="SUCCESS")  # SUCCESS, PARTIAL, FAILED
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    duration_seconds = Column(Float, default=0.0)
    items_scanned = Column(Integer, default=0)
    qualified_jobs_count = Column(Integer, default=0)
    recruiters_found_count = Column(Integer, default=0)
    drafts_created_count = Column(Integer, default=0)
    log_summary = Column(Text, default="")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "run_id": self.run_id,
            "mode": self.mode,
            "status": self.status,
            "start_time": self.start_time.strftime("%Y-%m-%d %H:%M:%S") if self.start_time else "",
            "end_time": self.end_time.strftime("%Y-%m-%d %H:%M:%S") if self.end_time else "",
            "duration_seconds": round(self.duration_seconds, 2),
            "items_scanned": self.items_scanned,
            "qualified_jobs_count": self.qualified_jobs_count,
            "recruiters_found_count": self.recruiters_found_count,
            "drafts_created_count": self.drafts_created_count,
            "log_summary": self.log_summary,
        }


class AuditLog(Base):
    """Full forensic audit trail of all agent actions and discoveries."""
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    entity_type = Column(String(50), nullable=False)  # Job, Signal, Person, Outreach, Pipeline
    entity_id = Column(String(50), nullable=False)
    action = Column(String(100), nullable=False)
    what_was_found = Column(Text, default="")
    where_found = Column(String(500), default="")
    why_relevant = Column(Text, default="")
    recommended_action = Column(Text, default="")
    user_approval_status = Column(String(50), default="N/A")  # N/A, Pending, Approved, Rejected
    outcome = Column(Text, default="")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "timestamp": self.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "entity_type": self.entity_type,
            "entity_id": self.entity_id,
            "action": self.action,
            "what_was_found": self.what_was_found,
            "where_found": self.where_found,
            "why_relevant": self.why_relevant,
            "recommended_action": self.recommended_action,
            "user_approval_status": self.user_approval_status,
            "outcome": self.outcome,
        }


# Database Engine and Session Factory
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # For multi-threaded FastAPI access
    echo=False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Create all tables and seed standard resume versions if not present."""
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    try:
        # Seed standard resume profiles
        existing_resumes = session.query(ResumeVersion).count()
        if existing_resumes == 0:
            default_resumes = [
                ResumeVersion(
                    name="Data Engineering (General)",
                    filename="Resume_Data_Engineering.pdf",
                    focus_area="Core Data Engineering (Azure, PySpark, SQL, ETL)",
                ),
                ResumeVersion(
                    name="Databricks & Azure Specialist",
                    filename="Resume_Databricks_Azure.pdf",
                    focus_area="Databricks, Delta Lake, Unity Catalog, ADF",
                ),
                ResumeVersion(
                    name="AI & GenAI Data Engineering",
                    filename="Resume_AI_Data_Engineering.pdf",
                    focus_area="AI Data Pipelines, Vector DBs, LLM data prep",
                ),
                ResumeVersion(
                    name="Software & Data Systems",
                    filename="Resume_Software_Engineering.pdf",
                    focus_area="Fullstack + Data (React, Node, Python, C++, SQL)",
                ),
            ]
            session.add_all(default_resumes)
            session.commit()
    finally:
        session.close()


def get_db():
    """FastAPI dependency for obtaining a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
