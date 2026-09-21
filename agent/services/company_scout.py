"""Mode 2 Engine: Targeted Company Direct Connect and Campus/Off-Campus Parallel Pipeline."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session

from agent.database import AuditLog, Company, Job, Outreach, Person, PipelineRun
from agent.services.deduplicator import Deduplicator
from agent.services.outreach_generator import OutreachGenerator
from agent.services.people_discovery import PeopleDiscovery


class CompanyScout:
    """
    Implements Mode 2: Direct Company Connect.
    Allows user to input a company name (e.g., when they hear about campus hiring or want to target a firm),
    discovers HR / Campus recruiters, and drafts personalized 2025 off-campus outreach messages directly
    into the tracker and approval queue.
    """

    @classmethod
    def scout_company(
        cls,
        db: Session,
        company_name: str,
        reason: str = "Campus hiring announced / Parallel off-campus inquiry",
    ) -> Dict[str, Any]:
        """
        Execute Mode 2 for a specific company:
        1. Find or create company entry.
        2. Discover Talent Acquisition & Engineering leads.
        3. Draft tailored 2025 off-campus connection requests.
        4. Place in Approval Queue.
        5. Log complete audit trail.
        """
        start_time = datetime.utcnow()
        clean_company = company_name.strip()
        if not clean_company:
            return {"success": False, "error": "Company name is required."}

        # 1. Update or create Company in DB
        company_obj = db.query(Company).filter(Company.company.ilike(clean_company)).first()
        if not company_obj:
            company_obj = Company(
                company=clean_company,
                industry="Information Technology & Analytics",
                careers_url=f"https://www.google.com/search?q={clean_company.replace(' ', '+')}+careers",
                location="Hyderabad / Bengaluru / India",
                hiring_activity="Active Campus / Off-Campus",
                priority="High",
                notes=f"Targeted via Direct Company Connect. Reason: {reason}",
            )
            db.add(company_obj)
            db.flush()

        # 2. Discover People (Campus Recruiter, Hiring Lead, Alumni)
        discovered_people = PeopleDiscovery.discover_people_for_company(
            company=clean_company,
            role_focus="Data Engineering (Azure / Databricks)",
            include_alumni=True,
        )

        created_people_records = []
        created_outreach_records = []

        for p_data in discovered_people:
            # Check deduplication
            existing_person = Deduplicator.find_existing_person(db, p_data)
            if existing_person:
                person_rec = existing_person
            else:
                person_count = db.query(Person).count() + 1
                person_rec = Person(
                    person_id=f"PER-{person_count:04d}",
                    name=p_data["name"],
                    company=p_data["company"],
                    job_title=p_data["job_title"],
                    linkedin_url=p_data["linkedin_url"],
                    person_type=p_data["person_type"],
                    connection_status=p_data.get("connection_status", "Not Connected"),
                    relevant_job_id=p_data.get("relevant_job_id"),
                    relevance_reason=p_data["relevance_reason"],
                    next_action="Review & approve 2025 off-campus connection message",
                )
                db.add(person_rec)
                db.flush()

            created_people_records.append(person_rec)

            # 3. Draft tailored 2025 Campus/Off-Campus outreach message
            outreach_count = db.query(Outreach).count() + 1
            if person_rec.person_type == "LNMIIT Alumni":
                draft_msg = OutreachGenerator.generate_connection_request(
                    recipient_name=person_rec.name,
                    company=clean_company,
                    job_title="Data Engineer",
                    person_type="LNMIIT Alumni",
                )
            else:
                draft_msg = OutreachGenerator.generate_campus_parallel_inquiry(
                    recipient_name=person_rec.name,
                    company=clean_company,
                    role="Data Engineer",
                )

            outreach_rec = Outreach(
                outreach_id=f"OUT-{outreach_count:04d}",
                person_id=person_rec.person_id,
                person=person_rec.name,
                company=clean_company,
                job="Data Engineer (2025 Off-Campus)",
                message_type="2025 Off-Campus Inquiry",
                message=draft_msg,
                status="Pending Approval",
                notes=f"Targeted outreach initiated for {reason}",
            )
            db.add(outreach_rec)
            db.flush()
            created_outreach_records.append(outreach_rec)

        # Update company stats
        company_obj.recruiters_found = len(created_people_records)
        company_obj.last_checked = datetime.utcnow()

        # 4. Log Audit Trail
        audit = AuditLog(
            entity_type="Company",
            entity_id=clean_company,
            action="DIRECT_COMPANY_CONNECT",
            what_was_found=f"Targeted company scout for {clean_company}. Discovered {len(created_people_records)} key contacts.",
            where_found="Direct Company Scout (Mode 2)",
            why_relevant=f"Candidate identified active campus hiring; scouted for parallel 2025 off-campus pipeline.",
            recommended_action=f"Approve connection requests for {len(created_outreach_records)} recruiters/leads in Approval Queue.",
            user_approval_status="Pending",
            outcome="Contacts and personalized outreach drafts saved to SQLite and Excel tracker.",
        )
        db.add(audit)

        # 5. Log Pipeline Run
        end_time = datetime.utcnow()
        run_count = db.query(PipelineRun).count() + 1
        pipeline_run = PipelineRun(
            run_id=f"RUN-{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}",
            mode="company_connect",
            status="SUCCESS",
            start_time=start_time,
            end_time=end_time,
            duration_seconds=(end_time - start_time).total_seconds(),
            items_scanned=1,
            qualified_jobs_count=0,
            recruiters_found_count=len(created_people_records),
            drafts_created_count=len(created_outreach_records),
            log_summary=f"Scouted {clean_company}: added {len(created_people_records)} people, {len(created_outreach_records)} outreach drafts.",
        )
        db.add(pipeline_run)
        db.commit()

        return {
            "success": True,
            "company": clean_company,
            "people_count": len(created_people_records),
            "outreach_count": len(created_outreach_records),
            "people": [p.to_dict() for p in created_people_records],
            "outreach": [o.to_dict() for o in created_outreach_records],
        }
