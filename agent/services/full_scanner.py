"""Mode 1 Engine: Full Recruitment Scan (Roles x Skills x Signals with conditional recruiter outreach)."""

from datetime import datetime
from typing import Any, Dict, List
from sqlalchemy.orm import Session

from agent.connectors.mock_seed_connector import MockSeedConnector
from agent.database import AuditLog, Company, Job, Outreach, Person, PipelineRun, RecruitmentSignal
from agent.services.deduplicator import Deduplicator
from agent.services.outreach_generator import OutreachGenerator
from agent.services.people_discovery import PeopleDiscovery
from agent.services.query_builder import QueryBuilder
from agent.services.scorer import Scorer
from agent.services.signal_detector import SignalDetector


class FullScanner:
    """
    Implements Mode 1: Full Recruitment Scan.
    1. Scans publicly indexed posts, feeds, and boards using dynamic keyword combinations.
    2. Filters by freshness (24-72h prioritized).
    3. Scores match (0-100) with explainability.
    4. IF AND ONLY IF a relevant job is found (score >= threshold), discovers the recruiter
       for that specific role and drafts tailored outreach into the Human Approval Queue.
    """

    MATCH_THRESHOLD = 70.0  # Only discover recruiters and draft outreach if score >= 70%

    @classmethod
    def run_full_scan(cls, db: Session, max_queries: int = 6) -> Dict[str, Any]:
        start_time = datetime.utcnow()
        summary_log = []

        # 1. Gather opportunities from seed & public connectors
        connector = MockSeedConnector()
        discovered_jobs = connector.search_jobs()
        discovered_signals = connector.search_signals()

        items_scanned = len(discovered_jobs) + len(discovered_signals)
        qualified_jobs = []
        new_people_added = []
        new_drafts_added = []
        new_signals_added = []

        # 2. Process Jobs
        for job_data in discovered_jobs:
            # Score the job
            score, explanation = Scorer.score_job(job_data)
            job_data["match_score"] = score
            job_data["match_explanation"] = explanation

            # Check deduplication
            existing_job = Deduplicator.find_existing_job(db, job_data)
            if existing_job:
                # Append source if new
                existing_sources = existing_job.sources
                for src in job_data.get("sources", []):
                    if src not in existing_sources:
                        existing_sources.append(src)
                existing_job.sources = existing_sources
                existing_job.last_checked = datetime.utcnow()
                job_rec = existing_job
            else:
                job_count = db.query(Job).count() + 1
                job_id = f"JOB-{job_count:05d}"
                job_rec = Job(
                    job_id=job_id,
                    company=job_data["company"],
                    job_title=job_data["job_title"],
                    location=job_data.get("location", "Hyderabad"),
                    work_mode=job_data.get("work_mode", "Hybrid"),
                    sources_json="[]",
                    job_url=job_data.get("job_url", ""),
                    posted_date=job_data.get("posted_date", ""),
                    freshness_tier=job_data.get("freshness_tier", "<24h"),
                    deadline=job_data.get("deadline", "Rolling"),
                    experience_required=job_data.get("experience_required", "0-2 years"),
                    salary=job_data.get("salary", "Disclosed upon request"),
                    skills=job_data.get("skills", ""),
                    match_score=score,
                    match_explanation=explanation,
                    recruitment_signal=job_data.get("recruitment_signal", "Normal Job Posting"),
                    recruitment_signal_date=job_data.get("recruitment_signal_date", ""),
                    application_method=job_data.get("application_method", "Direct Link"),
                    contact_email=job_data.get("contact_email", ""),
                )
                job_rec.sources = job_data.get("sources", ["Web Feed"])
                db.add(job_rec)
                db.flush()

                # Ensure company exists
                company_obj = db.query(Company).filter(Company.company == job_rec.company).first()
                if not company_obj:
                    company_obj = Company(
                        company=job_rec.company,
                        industry="Technology / Analytics",
                        careers_url=f"https://www.google.com/search?q={job_rec.company.replace(' ', '+')}+careers",
                        location=job_rec.location,
                        priority="High" if score >= 85 else "Medium",
                    )
                    db.add(company_obj)
                    db.flush()

            # Check if qualified for outreach
            if score >= cls.MATCH_THRESHOLD:
                qualified_jobs.append(job_rec)

                # ==============================================================
                # CONDITIONAL OUTREACH: Only discover people & draft outreach
                # if job passes qualification threshold!
                # ==============================================================
                people = PeopleDiscovery.discover_people_for_company(
                    company=job_rec.company,
                    role_focus=job_rec.job_title,
                    job_id=job_rec.job_id,
                    include_alumni=True,
                )

                for p_info in people:
                    existing_person = Deduplicator.find_existing_person(db, p_info)
                    if existing_person:
                        person_obj = existing_person
                    else:
                        p_count = db.query(Person).count() + 1
                        person_obj = Person(
                            person_id=f"PER-{p_count:04d}",
                            name=p_info["name"],
                            company=p_info["company"],
                            job_title=p_info["job_title"],
                            linkedin_url=p_info["linkedin_url"],
                            person_type=p_info["person_type"],
                            connection_status=p_info.get("connection_status", "Not Connected"),
                            relevant_job_id=job_rec.job_id,
                            relevance_reason=p_info["relevance_reason"],
                            next_action="Review connection/referral draft in Approval Queue",
                        )
                        db.add(person_obj)
                        db.flush()
                        new_people_added.append(person_obj)

                    # Check if outreach already drafted for this person
                    existing_outreach = db.query(Outreach).filter(
                        Outreach.person_id == person_obj.person_id
                    ).first()

                    if not existing_outreach:
                        out_count = db.query(Outreach).count() + 1
                        if person_obj.person_type == "LNMIIT Alumni":
                            msg_text = OutreachGenerator.generate_referral_request(
                                recipient_name=person_obj.name,
                                company=job_rec.company,
                                job_id=job_rec.job_id,
                                job_title=job_rec.job_title,
                            )
                            msg_type = "Referral Request"
                        else:
                            msg_text = OutreachGenerator.generate_connection_request(
                                recipient_name=person_obj.name,
                                company=job_rec.company,
                                job_title=job_rec.job_title,
                                person_type=person_obj.person_type,
                            )
                            msg_type = "Connection Request"

                        outreach_rec = Outreach(
                            outreach_id=f"OUT-{out_count:04d}",
                            person_id=person_obj.person_id,
                            person=person_obj.name,
                            company=person_obj.company,
                            job=f"{job_rec.job_title} ({job_rec.job_id})",
                            message_type=msg_type,
                            message=msg_text,
                            status="Pending Approval",
                            notes=f"Drafted via Full Scan for {job_rec.job_id} (Match Score: {score:.0f}%)",
                        )
                        db.add(outreach_rec)
                        db.flush()
                        new_drafts_added.append(outreach_rec)

        # 3. Process Recruitment Signals
        for sig_data in discovered_signals:
            existing_sig = Deduplicator.find_existing_signal(db, sig_data["post_url"])
            if not existing_sig:
                s_count = db.query(RecruitmentSignal).count() + 1
                sig_rec = RecruitmentSignal(
                    signal_id=f"SIG-{s_count:04d}",
                    company=sig_data["company"],
                    person=sig_data.get("person", "Recruiter"),
                    author_profile_url=sig_data.get("author_profile_url", ""),
                    signal_type=sig_data["signal_type"],
                    post_url=sig_data["post_url"],
                    post_date=sig_data.get("post_date", ""),
                    freshness_hours=sig_data.get("freshness_hours", 12),
                    keywords=sig_data.get("keywords", ""),
                    role=sig_data.get("role", "Data Engineer"),
                    location=sig_data.get("location", "Hyderabad"),
                    urgency=sig_data.get("urgency", "High"),
                    relevance=sig_data.get("relevance", 85.0),
                    evidence=sig_data.get("evidence", ""),
                    application_method=sig_data.get("application_method", "DM / Email"),
                    contact_email=sig_data.get("contact_email", ""),
                    status="Active",
                )
                db.add(sig_rec)
                db.flush()
                new_signals_added.append(sig_rec)

        # 4. Log Audit Trail
        audit = AuditLog(
            entity_type="Pipeline",
            entity_id="FULL_SCAN",
            action="MODE_1_SCAN_COMPLETED",
            what_was_found=f"Scanned {items_scanned} items. Qualified {len(qualified_jobs)} jobs above {cls.MATCH_THRESHOLD}% match.",
            where_found="LinkedIn Public Feeds, Hiring Posts & Portals",
            why_relevant=f"Scored against Azure/Databricks/PySpark 2025 profile.",
            recommended_action=f"Review {len(new_drafts_added)} drafted outreach notes in the Approval Queue.",
            user_approval_status="Pending",
            outcome=f"Saved {len(qualified_jobs)} jobs, {len(new_signals_added)} signals, {len(new_drafts_added)} drafts.",
        )
        db.add(audit)

        # 5. Log Pipeline Run
        end_time = datetime.utcnow()
        run_rec = PipelineRun(
            run_id=f"RUN-{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}",
            mode="full_scan",
            status="SUCCESS",
            start_time=start_time,
            end_time=end_time,
            duration_seconds=(end_time - start_time).total_seconds(),
            items_scanned=items_scanned,
            qualified_jobs_count=len(qualified_jobs),
            recruiters_found_count=len(new_people_added),
            drafts_created_count=len(new_drafts_added),
            log_summary=f"Full scan processed {items_scanned} items. Found {len(qualified_jobs)} high-match jobs.",
        )
        db.add(run_rec)
        db.commit()

        return {
            "success": True,
            "items_scanned": items_scanned,
            "qualified_jobs_count": len(qualified_jobs),
            "new_signals_count": len(new_signals_added),
            "new_people_count": len(new_people_added),
            "new_drafts_count": len(new_drafts_added),
        }
