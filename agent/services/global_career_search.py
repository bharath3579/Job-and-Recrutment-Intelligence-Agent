"""Global Career Outreach Orchestrator connecting job discovery, people intelligence, contact research, and personalized outreach."""

import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session

from agent.connectors.career_site_connector import CareerSiteConnector
from agent.connectors.hunter_connector import HunterConnector
from agent.connectors.public_search_connector import PublicSearchConnector
from agent.database import AuditLog, Company, Job, Outreach, Person, PipelineRun
from agent.services.ai_outreach_engine import AIOutreachEngine
from agent.services.deduplicator import Deduplicator
from agent.services.scorer import Scorer

logger = logging.getLogger(__name__)


class GlobalCareerSearch:
    """
    End-to-end execution of a targeted Global Career Search:
    1. Discovers open job opportunities from official careers portals and ATS feeds.
    2. Identifies matching recruiters, hiring managers, senior engineers, and alumni.
    3. Researches business contact information with Hunter.io and pattern analysis.
    4. Evaluates role relevance & contact confidence.
    5. Drafts persona-specific outreach into the Human Approval Queue.
    """

    @classmethod
    def execute_search(
        cls,
        db: Session,
        company: str,
        role: str = "Data Engineer",
        skills: str = "Azure, Databricks, PySpark, SQL",
        country: str = "India",
        people_to_find: str = "All relevant levels",
        outreach_objective: str = "Ask about a job opportunity",
    ) -> Dict[str, Any]:
        start_time = datetime.utcnow()
        run_id = f"RUN-SEARCH-{int(start_time.timestamp())}"
        company_clean = company.strip()
        role_clean = role.strip() or "Data Engineer"
        country_clean = country.strip() or "India"

        # -------------------------------------------------------------
        # 1. Ensure Company Record
        # -------------------------------------------------------------
        comp_rec = db.query(Company).filter(Company.company.ilike(company_clean)).first()
        domain = HunterConnector.infer_domain_from_company(company_clean)
        if not comp_rec:
            comp_rec = Company(
                company=company_clean,
                industry="Technology & Cloud Data Systems",
                careers_url=f"https://{domain}",
                location=country_clean,
                hiring_activity="Active",
                relevant_roles=1,
                priority="High",
                notes=f"Targeted global search initiated for {role_clean} in {country_clean}.",
            )
            db.add(comp_rec)
            db.commit()

        # -------------------------------------------------------------
        # 2. Discover Jobs & ATS Openings
        # -------------------------------------------------------------
        raw_jobs = CareerSiteConnector.search_company_careers(
            company=company_clean,
            role=role_clean,
            country=country_clean,
            limit=5,
        )

        saved_jobs = []
        for j_data in raw_jobs:
            score, explanation = Scorer.score_job({
                "job_title": j_data.get("title", role_clean),
                "skills": skills,
                "description": f"Role for {role_clean} at {company_clean}. Tech stack: {skills}.",
                "location": j_data.get("location", country_clean),
                "freshness_tier": "<24h",
                "experience_required": j_data.get("experience_required", "0-2 years"),
                "recruitment_signal": "Active Recruitment Signal",
            })

            # Check duplicate in DB
            existing_job = db.query(Job).filter(
                Job.company.ilike(company_clean),
                Job.job_title.ilike(j_data.get("title", role_clean)),
            ).first()

            if not existing_job:
                new_job = Job(
                    job_id=f"JOB-{abs(hash(company_clean + j_data.get('title', '') + str(datetime.utcnow()))) % 90000 + 10000}",
                    company=company_clean,
                    job_title=j_data.get("title", role_clean),
                    location=j_data.get("location", country_clean),
                    work_mode="Hybrid / Remote",
                    sources_json=f'["{j_data.get("source", "Career Site")}"]',
                    job_url=j_data.get("job_url"),
                    posted_date=j_data.get("posted_date", "Recent"),
                    freshness_tier="<24h",
                    deadline="Rolling",
                    experience_required=j_data.get("experience_required", "0-2 years"),
                    salary="Competitive / Market Standard",
                    skills=skills,
                    match_score=score,
                    match_explanation=explanation,
                    recruitment_signal="Active Recruitment Signal",
                    application_status="Discovered",
                    application_method="Direct Link / Referral",
                    notes=f"Target role identified via {j_data.get('source')}.",
                )
                db.add(new_job)
                saved_jobs.append(new_job)

        db.commit()

        # -------------------------------------------------------------
        # 3. Discover Decision Makers & Enforce Contact Research
        # -------------------------------------------------------------
        raw_people = PublicSearchConnector.discover_people(
            company=company_clean,
            role=role_clean,
            country=country_clean,
            persona_category=people_to_find,
        )

        saved_people = []
        drafts_created = []

        for p_data in raw_people:
            # Parse names
            full_name = p_data.get("name", "Talent Lead")
            name_parts = full_name.split()
            first_name = name_parts[0] if name_parts else "Contact"
            last_name = name_parts[1] if len(name_parts) > 1 else ""

            # Contact Research with Hunter.io
            contact_info = HunterConnector.find_email(
                first_name=first_name,
                last_name=last_name,
                company=company_clean,
                domain=domain,
            )

            # Calculate Person Relevance Score
            base_rel = p_data.get("relevance_base", 88.0)
            p_type = p_data.get("person_type", "Recruiter")
            if country_clean.lower() in p_data.get("country", "").lower():
                base_rel = min(99.0, base_rel + 3.0)

            score_explanation = f"{p_data.get('relevance_reason', '')} Contact verified via {contact_info.get('verification_status')} ({contact_info.get('score')}%)"

            # Check if person exists in DB
            person_rec = db.query(Person).filter(
                Person.company.ilike(company_clean),
                Person.job_title == p_data.get("job_title"),
            ).first()

            if not person_rec:
                person_id = f"PER-{uuid.uuid4().hex[:6].upper()}"
                person_rec = Person(
                    person_id=person_id,
                    name=full_name,
                    company=company_clean,
                    job_title=p_data.get("job_title"),
                    linkedin_url=p_data.get("linkedin_url"),
                    person_type=p_type,
                    connection_status="Not Connected",
                    relevant_job_id=saved_jobs[0].job_id if saved_jobs else None,
                    relevance_reason=p_data.get("relevance_reason"),
                    country=country_clean,
                    email=contact_info.get("email"),
                    email_type=contact_info.get("email_type", "Business"),
                    email_source=contact_info.get("source_name", "Hunter.io"),
                    verification_status=contact_info.get("verification_status", "Unverified"),
                    confidence_score=contact_info.get("score", 50.0),
                    skills_matched=skills,
                    relevance_score=base_rel,
                    score_breakdown=score_explanation,
                )
                db.add(person_rec)
                saved_people.append(person_rec)
            else:
                saved_people.append(person_rec)

            db.commit()

            # -------------------------------------------------------------
            # 4. Generate AI Outreach Drafts (Strict Human Approval)
            # -------------------------------------------------------------
            drafts = AIOutreachEngine.generate_drafts(
                recipient_name=full_name,
                company=company_clean,
                job_title=role_clean,
                person_type=p_type,
                country=country_clean,
                objective=outreach_objective,
                skills=skills,
            )

            # Check if outreach already drafted
            existing_outreach = db.query(Outreach).filter(
                Outreach.company.ilike(company_clean),
                Outreach.person == full_name,
                Outreach.objective == outreach_objective,
            ).first()

            if not existing_outreach:
                # Choose default channel based on email verification
                has_verified_email = "Verified" in contact_info.get("verification_status", "")
                primary_channel = "Email" if has_verified_email else "LinkedIn Note"
                primary_message = drafts["email_body"] if has_verified_email else drafts["linkedin_note"]

                outreach_id = f"OUT-{uuid.uuid4().hex[:6].upper()}"
                outreach_rec = Outreach(
                    outreach_id=outreach_id,
                    person_id=person_rec.person_id,
                    person=full_name,
                    company=company_clean,
                    job=role_clean,
                    message_type=f"{outreach_objective} ({p_type})",
                    channel=primary_channel,
                    subject=drafts.get("subject", f"Inquiry regarding {role_clean}"),
                    objective=outreach_objective,
                    timezone_recommended_send=drafts.get("timezone_recommendation", ""),
                    country=country_clean,
                    message=primary_message,
                    status="Pending Approval",
                    response="Draft awaiting candidate review",
                    notes=f"Generated via AI Outreach Engine for {p_type}. Recommended send: {drafts.get('timezone_recommendation')}.",
                )
                db.add(outreach_rec)
                drafts_created.append(outreach_rec)

        db.commit()

        # Update company stats
        comp_rec.recruiters_found = db.query(Person).filter(
            Person.company.ilike(company_clean),
            Person.person_type.in_(["Technical Recruiter", "HR Business Partner", "Campus Recruiter"]),
        ).count()
        comp_rec.hiring_managers_found = db.query(Person).filter(
            Person.company.ilike(company_clean),
            Person.person_type.in_(["Engineering Manager", "Lead / Senior Data Engineer"]),
        ).count()
        db.commit()

        # Record Pipeline Run
        duration = (datetime.utcnow() - start_time).total_seconds()
        run = PipelineRun(
            run_id=run_id,
            mode="global_career_search",
            status="SUCCESS",
            start_time=start_time,
            end_time=datetime.utcnow(),
            duration_seconds=duration,
            items_scanned=len(raw_jobs) + len(raw_people),
            qualified_jobs_count=len(saved_jobs),
            recruiters_found_count=len(saved_people),
            drafts_created_count=len(drafts_created),
            log_summary=(
                f"Global search for {role_clean} at {company_clean} ({country_clean}). "
                f"Found {len(saved_jobs)} jobs, {len(saved_people)} decision-makers, and drafted {len(drafts_created)} messages."
            ),
        )
        db.add(run)

        # Audit Log
        audit = AuditLog(
            entity_type="Search",
            entity_id=run_id,
            action="Global Career Search Executed",
            what_was_found=f"{len(saved_jobs)} jobs, {len(saved_people)} people at {company_clean}",
            where_found=f"Career Sites, ATS feeds, Hunter.io ({domain}), Public Profiles",
            why_relevant=f"Matched target role '{role_clean}', skills '{skills}', and country '{country_clean}'",
            recommended_action="Review and approve personalized drafts in the Approval Queue.",
            user_approval_status="Pending",
            outcome=f"{len(drafts_created)} drafts ready for approval.",
        )
        db.add(audit)
        db.commit()

        return {
            "success": True,
            "company": company_clean,
            "role": role_clean,
            "country": country_clean,
            "domain": domain,
            "jobs_found": [j.to_dict() for j in saved_jobs],
            "people_found": [p.to_dict() for p in saved_people],
            "drafts_created": [d.to_dict() for d in drafts_created],
            "recommended_send_time": AIOutreachEngine.get_recommended_send_time(country_clean),
        }
