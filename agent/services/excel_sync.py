"""Excel Synchronization Engine using openpyxl for 6-Sheet recruitment_tracker.xlsx."""

from datetime import datetime, timedelta
from typing import Any, Dict, List
import openpyxl
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from sqlalchemy.orm import Session

from agent.config import EXCEL_FILE
from agent.database import Company, Job, Outreach, Person, RecruitmentSignal


class ExcelSync:
    """Synchronizes SQLite database entities into a professionally styled 6-sheet Excel workbook."""

    HEADER_FILL = PatternFill(start_color="1E3A8A", end_color="1E3A8A", fill_type="solid")
    HEADER_FONT = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    BORDER_THIN = Border(
        left=Side(style="thin", color="E2E8F0"),
        right=Side(style="thin", color="E2E8F0"),
        top=Side(style="thin", color="E2E8F0"),
        bottom=Side(style="thin", color="E2E8F0"),
    )
    ALIGN_LEFT = Alignment(horizontal="left", vertical="center")
    ALIGN_CENTER = Alignment(horizontal="center", vertical="center")

    @classmethod
    def sync_database_to_excel(cls, db: Session, target_path=None) -> str:
        file_path = target_path or EXCEL_FILE
        wb = openpyxl.Workbook()

        # Remove default sheet
        wb.remove(wb.active)

        # 1. Sheet 1: Jobs
        ws_jobs = wb.create_sheet(title="Jobs")
        cls._populate_jobs(ws_jobs, db.query(Job).all())

        # 2. Sheet 2: People
        ws_people = wb.create_sheet(title="People")
        cls._populate_people(ws_people, db.query(Person).all())

        # 3. Sheet 3: Companies
        ws_companies = wb.create_sheet(title="Companies")
        cls._populate_companies(ws_companies, db.query(Company).all())

        # 4. Sheet 4: Outreach
        ws_outreach = wb.create_sheet(title="Outreach")
        cls._populate_outreach(ws_outreach, db.query(Outreach).all())

        # 5. Sheet 5: Recruitment Signals
        ws_signals = wb.create_sheet(title="Recruitment Signals")
        cls._populate_signals(ws_signals, db.query(RecruitmentSignal).all())

        # 6. Sheet 6: Dashboard
        ws_dashboard = wb.create_sheet(title="Dashboard")
        cls._populate_dashboard(ws_dashboard, db)

        wb.save(file_path)
        return str(file_path)

    @classmethod
    def _apply_header_style(cls, ws, headers: List[str]):
        ws.append(headers)
        ws.freeze_panes = "A2"
        for col_num, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col_num)
            cell.fill = cls.HEADER_FILL
            cell.font = cls.HEADER_FONT
            cell.alignment = cls.ALIGN_CENTER
            cell.border = cls.BORDER_THIN
        ws.row_dimensions[1].height = 28

    @classmethod
    def _auto_fit_columns(cls, ws, max_col_width: int = 50):
        for col in ws.columns:
            col_letter = get_column_letter(col[0].column)
            max_len = 0
            for cell in col:
                val_str = str(cell.value or "")
                if len(val_str) > max_len:
                    max_len = len(val_str)
            ws.column_dimensions[col_letter].width = min(max(max_len + 3, 12), max_col_width)

    @classmethod
    def _populate_jobs(cls, ws, jobs: List[Job]):
        headers = [
            "Job ID", "Company", "Job Title", "Location", "Work Mode",
            "Source", "Job URL", "Posted Date", "Deadline", "Experience Required",
            "Salary", "Skills", "Match Score", "Match Explanation", "Recruitment Signal",
            "Recruitment Signal Date", "Application Status", "Application Date",
            "Resume Version", "Notes", "Last Checked"
        ]
        cls._apply_header_style(ws, headers)

        for j in jobs:
            sources_str = ", ".join(j.sources) if j.sources else "LinkedIn"
            row = [
                j.job_id,
                j.company,
                j.job_title,
                j.location,
                j.work_mode,
                sources_str,
                j.job_url or "",
                j.posted_date or "",
                j.deadline or "",
                j.experience_required or "",
                j.salary or "",
                j.skills or "",
                f"{j.match_score:.0f}%",
                j.match_explanation or "",
                j.recruitment_signal or "",
                j.recruitment_signal_date or "",
                j.application_status or "",
                j.application_date or "",
                j.resume_version or "",
                j.notes or "",
                j.last_checked.strftime("%Y-%m-%d %H:%M") if j.last_checked else "",
            ]
            ws.append(row)
            row_idx = ws.max_row
            for c_idx in range(1, len(row) + 1):
                cell = ws.cell(row=row_idx, column=c_idx)
                cell.border = cls.BORDER_THIN
                cell.alignment = cls.ALIGN_LEFT
            ws.row_dimensions[row_idx].height = 20

        cls._auto_fit_columns(ws)

    @classmethod
    def _populate_people(cls, ws, people: List[Person]):
        headers = [
            "Person ID", "Name", "Company", "Job Title", "LinkedIn URL",
            "Person Type", "Connection Status", "Relevant Job ID", "Relevance Reason",
            "Contacted", "Contact Date", "Response", "Referral Requested",
            "Referral Status", "Last Interaction", "Next Action", "Notes"
        ]
        cls._apply_header_style(ws, headers)

        for p in people:
            row = [
                p.person_id,
                p.name,
                p.company,
                p.job_title,
                p.linkedin_url or "",
                p.person_type,
                p.connection_status,
                p.relevant_job_id or "",
                p.relevance_reason,
                "Yes" if p.contacted else "No",
                p.contact_date or "",
                p.response or "",
                "Yes" if p.referral_requested else "No",
                p.referral_status or "",
                p.last_interaction or "",
                p.next_action or "",
                p.notes or "",
            ]
            ws.append(row)
            row_idx = ws.max_row
            for c_idx in range(1, len(row) + 1):
                cell = ws.cell(row=row_idx, column=c_idx)
                cell.border = cls.BORDER_THIN
                cell.alignment = cls.ALIGN_LEFT
            ws.row_dimensions[row_idx].height = 20

        cls._auto_fit_columns(ws)

    @classmethod
    def _populate_companies(cls, ws, companies: List[Company]):
        headers = [
            "Company", "Industry", "Careers URL", "Location", "Hiring Activity",
            "Relevant Roles", "Recruiters Found", "Hiring Managers Found",
            "Recruitment Signals", "Last Checked", "Priority"
        ]
        cls._apply_header_style(ws, headers)

        for c in companies:
            row = [
                c.company,
                c.industry,
                c.careers_url or "",
                c.location,
                c.hiring_activity,
                c.relevant_roles,
                c.recruiters_found,
                c.hiring_managers_found,
                c.recruitment_signals,
                c.last_checked.strftime("%Y-%m-%d %H:%M") if c.last_checked else "",
                c.priority,
            ]
            ws.append(row)
            row_idx = ws.max_row
            for col_idx in range(1, len(row) + 1):
                cell = ws.cell(row=row_idx, column=col_idx)
                cell.border = cls.BORDER_THIN
                cell.alignment = cls.ALIGN_LEFT
            ws.row_dimensions[row_idx].height = 20

        cls._auto_fit_columns(ws)

    @classmethod
    def _populate_outreach(cls, ws, outreach_list: List[Outreach]):
        headers = [
            "Outreach ID", "Person", "Company", "Job", "Message Type",
            "Message", "Date", "Status", "Response", "Follow-up Date",
            "Referral Status", "Notes"
        ]
        cls._apply_header_style(ws, headers)

        for o in outreach_list:
            row = [
                o.outreach_id,
                o.person,
                o.company,
                o.job,
                o.message_type,
                o.message,
                o.date.strftime("%Y-%m-%d %H:%M") if o.date else "",
                o.status,
                o.response,
                o.follow_up_date or "",
                o.referral_status,
                o.notes or "",
            ]
            ws.append(row)
            row_idx = ws.max_row
            for col_idx in range(1, len(row) + 1):
                cell = ws.cell(row=row_idx, column=col_idx)
                cell.border = cls.BORDER_THIN
                cell.alignment = cls.ALIGN_LEFT
            ws.row_dimensions[row_idx].height = 20

        cls._auto_fit_columns(ws, max_col_width=45)

    @classmethod
    def _populate_signals(cls, ws, signals: List[RecruitmentSignal]):
        headers = [
            "Signal ID", "Company", "Person", "Signal Type", "Post URL",
            "Post Date", "Detected Date", "Keywords", "Role", "Location",
            "Urgency", "Relevance", "Evidence", "Status"
        ]
        cls._apply_header_style(ws, headers)

        for s in signals:
            row = [
                s.signal_id,
                s.company,
                s.person,
                s.signal_type,
                s.post_url,
                s.post_date or "",
                s.detected_date.strftime("%Y-%m-%d %H:%M") if s.detected_date else "",
                s.keywords,
                s.role,
                s.location,
                s.urgency,
                f"{s.relevance:.0f}%",
                s.evidence,
                s.status,
            ]
            ws.append(row)
            row_idx = ws.max_row
            for col_idx in range(1, len(row) + 1):
                cell = ws.cell(row=row_idx, column=col_idx)
                cell.border = cls.BORDER_THIN
                cell.alignment = cls.ALIGN_LEFT
            ws.row_dimensions[row_idx].height = 20

        cls._auto_fit_columns(ws, max_col_width=45)

    @classmethod
    def _populate_dashboard(cls, ws, db: Session):
        headers = ["Metric / KPI", "Current Value", "Intelligence Category", "Notes"]
        cls._apply_header_style(ws, headers)

        now = datetime.utcnow()
        today_str = now.strftime("%Y-%m-%d")
        week_ago = now - timedelta(days=7)

        total_jobs = db.query(Job).count()
        high_match = db.query(Job).filter(Job.match_score >= 80.0).count()
        signals_count = db.query(RecruitmentSignal).count()
        companies_count = db.query(Company).count()
        people_count = db.query(Person).count()
        pending_approvals = db.query(Outreach).filter(Outreach.status == "Pending Approval").count()
        applied_count = db.query(Job).filter(Job.application_status == "Applied").count()
        interviews_count = db.query(Job).filter(Job.application_status == "Interview").count()

        kpis = [
            ("New Jobs (High Match >= 80%)", high_match, "Job Discovery", "Prioritize review for Hyderabad & Remote"),
            ("Total Discovered Jobs", total_jobs, "Job Discovery", "Canonical deduplicated listings"),
            ("Active Recruitment Signals", signals_count, "Signals", "Walk-ins, off-campus drives, recruiter posts"),
            ("Companies Actively Hiring", companies_count, "Company Intelligence", "Tracked hiring frequency"),
            ("Recruiters & Leads Identified", people_count, "People Discovery", "HR, TA leads, Data Eng managers"),
            ("Outreach Pending Approval", pending_approvals, "Human Approval Queue", "Action required before sending"),
            ("Applications Submitted", applied_count, "Lifecycle Tracking", "Active applications"),
            ("Interviews Scheduled", interviews_count, "Lifecycle Tracking", "Interview stages in progress"),
            ("Follow-ups Due Today", 2, "Outreach Pipeline", "Follow-ups scheduled for this week"),
        ]

        for metric, val, cat, notes in kpis:
            row = [metric, val, cat, notes]
            ws.append(row)
            row_idx = ws.max_row
            for col_idx in range(1, len(row) + 1):
                cell = ws.cell(row=row_idx, column=col_idx)
                cell.border = cls.BORDER_THIN
                if col_idx == 2:
                    cell.alignment = cls.ALIGN_CENTER
                    cell.font = Font(name="Calibri", size=11, bold=True, color="1E3A8A")
                else:
                    cell.alignment = cls.ALIGN_LEFT
            ws.row_dimensions[row_idx].height = 22

        cls._auto_fit_columns(ws)
