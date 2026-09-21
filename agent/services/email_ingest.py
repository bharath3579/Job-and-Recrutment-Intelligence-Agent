"""Email ingestion service to parse incoming job alerts, interview invites, and recruiter replies."""

import re
from datetime import datetime
from typing import Any, Dict, Optional, Tuple
from sqlalchemy.orm import Session

from agent.database import AuditLog, Job, Outreach, Person


class EmailIngest:
    """
    Parses email text or alerts to automatically update application statuses,
    interview invitations, recruiter replies, and campus notifications.
    """

    @classmethod
    def process_email_text(cls, db: Session, email_body: str, sender: str = "") -> Dict[str, Any]:
        """
        Analyze incoming email content, identify company and role, update tracker status,
        and record an audit entry.
        """
        text = email_body.strip()
        t_lower = text.lower()
        now = datetime.utcnow()

        # 1. Detect Company
        matched_company = None
        all_jobs = db.query(Job).all()
        for j in all_jobs:
            if j.company.lower() in t_lower:
                matched_company = j.company
                break

        # If not in existing jobs, look for company indicators
        if not matched_company:
            comp_match = re.search(r"(?:from|team|at|careers\s*@|hr\s*@)\s*([A-Za-z0-9\s&]{3,30})", text, re.I)
            if comp_match:
                matched_company = comp_match.group(1).strip()
            else:
                matched_company = "General Recruiter Notification"

        # 2. Detect Intent and Status Change
        new_status = "Reviewed"
        action_note = "Email received"
        intent = "General Alert"

        if any(k in t_lower for k in ["interview", "discussion", "technical round", "schedule a call", "hiring manager discussion"]):
            new_status = "Interview"
            intent = "Interview Invitation"
            action_note = f"Interview invitation detected on {now.strftime('%Y-%m-%d')}."
        elif any(k in t_lower for k in ["offer", "pleased to offer", "letter of intent"]):
            new_status = "Offer"
            intent = "Job Offer"
            action_note = f"Offer notification detected on {now.strftime('%Y-%m-%d')}."
        elif any(k in t_lower for k in ["assessment", "hackerrank", "codility", "test link", "online test"]):
            new_status = "Assessment"
            intent = "Online Assessment"
            action_note = f"Online technical assessment received on {now.strftime('%Y-%m-%d')}."
        elif any(k in t_lower for k in ["thank you for applying", "application received", "successfully submitted"]):
            new_status = "Applied"
            intent = "Application Confirmation"
            action_note = f"Application confirmed received on {now.strftime('%Y-%m-%d')}."
        elif any(k in t_lower for k in ["not moving forward", "regret to inform", "other candidates"]):
            new_status = "Rejected"
            intent = "Application Decision"
            action_note = f"Rejection notice received on {now.strftime('%Y-%m-%d')}."
        elif any(k in t_lower for k in ["referral", "referred you", "referral submitted"]):
            intent = "Referral Submission"
            action_note = f"Referral confirmed submitted on {now.strftime('%Y-%m-%d')}."

        # 3. Update Existing Job(s) if found
        updated_job_id = None
        target_jobs = db.query(Job).filter(Job.company.ilike(f"%{matched_company}%")).all()
        for target_job in target_jobs:
            target_job.application_status = new_status
            target_job.notes = f"{target_job.notes}\n[Email Update {now.strftime('%Y-%m-%d')}]: {action_note}".strip()
            target_job.last_checked = now
            updated_job_id = target_job.job_id

        # 4. Check if a Person/Outreach replied
        target_outreach = db.query(Outreach).filter(Outreach.company.ilike(f"%{matched_company}%")).first()
        if target_outreach:
            target_outreach.response = f"Replied: {intent}"
            target_outreach.status = "Sent"

        # 5. Record Audit Log
        audit = AuditLog(
            entity_type="Email",
            entity_id=updated_job_id or matched_company,
            action="EMAIL_STATUS_INGESTED",
            what_was_found=f"Received email from '{sender or 'Recruitment'}' regarding {matched_company}. Intent: {intent}.",
            where_found="Email Ingestion Pipeline",
            why_relevant=f"Triggered tracker status update to '{new_status}'.",
            recommended_action=action_note,
            user_approval_status="Approved",
            outcome=f"Application status updated to '{new_status}'.",
        )
        db.add(audit)
        db.commit()

        return {
            "success": True,
            "company": matched_company,
            "intent": intent,
            "new_status": new_status,
            "updated_job_id": updated_job_id,
            "note": action_note,
        }
