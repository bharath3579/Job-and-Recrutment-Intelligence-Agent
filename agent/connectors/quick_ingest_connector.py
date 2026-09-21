"""Quick Ingest Connector for parsing pasted job descriptions, LinkedIn URLs, or email notices."""

import re
from datetime import datetime
from typing import Any, Dict, Optional

from agent.connectors.base import BaseConnector
from agent.services.scorer import Scorer
from agent.services.signal_detector import SignalDetector


class QuickIngestConnector(BaseConnector):
    """Parses raw text or URLs pasted from browser or mobile share sheet."""

    @property
    def source_name(self) -> str:
        return "Quick Ingest / Manual Ingestion"

    def search_jobs(self, query: str = "", location: str = "Hyderabad", limit: int = 10):
        return []

    def search_signals(self, query: str = "", limit: int = 10):
        return []

    @classmethod
    def parse_raw_input(
        cls,
        raw_text: str,
        source_url: Optional[str] = None,
        company_override: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Extract structured fields from freeform job posting text or pasted URL content.
        """
        text = raw_text.strip()
        now = datetime.utcnow()

        # 1. Company Detection
        company = company_override or "Unknown Company"
        if not company_override:
            # Look for common patterns like "Company: X", "at X", or recognized brands
            comp_match = re.search(r"(?:company|organization|at|joining)\s*[:\-]?\s*([A-Za-z0-9\s&]{3,30})", text, re.I)
            if comp_match:
                company = comp_match.group(1).strip()
            else:
                lines = [line.strip() for line in text.split("\n") if line.strip()]
                if lines:
                    company = lines[0][:40]

        # 2. Title Detection
        job_title = "Data Engineer"
        title_match = re.search(r"(?:role|title|position|hiring for)\s*[:\-]?\s*([A-Za-z0-9\s\-/]{4,50})", text, re.I)
        if title_match:
            job_title = title_match.group(1).strip()
        else:
            for potential in ["Azure Data Engineer", "Databricks Data Engineer", "PySpark Developer", "Data Engineer", "Cloud Data Engineer"]:
                if potential.lower() in text.lower():
                    job_title = potential
                    break

        # 3. Location Detection
        location = "Hyderabad"
        for loc in ["Hyderabad", "Bengaluru", "Bangalore", "Pune", "Chennai", "Delhi NCR", "Gurgaon", "Noida", "Mumbai", "Remote"]:
            if loc.lower() in text.lower():
                location = "Remote India" if loc.lower() == "remote" else loc
                break

        # 4. Experience & Work mode
        exp = "0-2 years"
        exp_match = re.search(r"(\d+(?:\s*-\s*\d+)?\s*(?:\+|years?|yrs?|passout|batch))", text, re.I)
        if exp_match:
            exp = exp_match.group(1).strip()

        work_mode = "Hybrid"
        if "remote" in text.lower():
            work_mode = "Remote"
        elif "on-site" in text.lower() or "in-office" in text.lower() or "walk-in" in text.lower():
            work_mode = "On-site"

        # 5. Extract Email and Application Method
        email_match = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", text)
        contact_email = email_match.group(0) if email_match else ""

        # 6. Signal Classification
        signal_type, urgency, evidence, app_method = SignalDetector.classify_text(text)
        if contact_email:
            app_method = f"Direct Email ({contact_email})"

        # 7. Extract Skills
        skills_found = []
        for s in ["Databricks", "PySpark", "Azure", "Azure Data Factory", "ADF", "Delta Lake", "Unity Catalog", "SQL", "Python", "ADLS", "ETL"]:
            if re.search(rf"\b{re.escape(s)}\b", text, re.I):
                skills_found.append(s)
        skills_str = ", ".join(skills_found) if skills_found else "Data Engineering, SQL, Python"

        url = source_url or "https://www.linkedin.com"

        return {
            "company": company,
            "job_title": job_title,
            "location": location,
            "work_mode": work_mode,
            "sources": ["Quick Ingest"],
            "job_url": url,
            "posted_date": now.strftime("%Y-%m-%d %H:%M"),
            "freshness_tier": "<24h",
            "deadline": "Rolling",
            "experience_required": exp,
            "salary": "Disclosed upon inquiry",
            "skills": skills_str,
            "description": text[:800],
            "recruitment_signal": signal_type,
            "recruitment_signal_date": now.strftime("%Y-%m-%d"),
            "application_method": app_method,
            "contact_email": contact_email,
            "evidence": evidence,
            "urgency": urgency,
        }
