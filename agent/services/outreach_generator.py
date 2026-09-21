"""Outreach generator for personalized, high-converting, anti-spam connection requests and referral messages."""

from typing import Any, Dict, Optional
from agent.config import CANDIDATE_PROFILE


class OutreachGenerator:
    """
    Generates structured, professional messages tailored to the recipient's role,
    the target job, and genuine candidate background.
    """

    @classmethod
    def generate_connection_request(
        cls,
        recipient_name: str,
        company: str,
        job_title: str = "Data Engineer",
        person_type: str = "Recruiter",
    ) -> str:
        """
        Generate a concise (<300 chars), personalized LinkedIn connection request.
        Adheres to LinkedIn character limit and anti-spam authenticity rules.
        """
        first_name = recipient_name.split()[0] if recipient_name else "there"

        if "alumni" in person_type.lower():
            msg = (
                f"Hi {first_name}, I'm a final-year student at LNMIIT (2025 batch) specializing in "
                f"Azure Data Engineering & Databricks. Great to see fellow alumni at {company}! "
                f"Would love to connect and follow your journey."
            )
        elif any(k in person_type.lower() for k in ["recruiter", "talent", "hr"]):
            msg = (
                f"Hi {first_name}, I noticed your hiring activity for Data Engineering at {company}. "
                f"I'm a 2025 B.Tech graduate from LNMIIT with hands-on experience in Azure, Databricks & PySpark. "
                f"Would love to connect regarding upcoming opportunities."
            )
        else:  # Engineering Manager / Senior Data Engineer
            msg = (
                f"Hi {first_name}, I admire the data platform work at {company}. "
                f"I work extensively with Databricks, PySpark, and Azure data pipelines (LNMIIT '25). "
                f"Would love to connect and learn from your team's engineering insights."
            )

        # Ensure strict adherence to LinkedIn's 300-char connection note limit
        if len(msg) > 298:
            msg = msg[:295] + "..."
        return msg

    @classmethod
    def generate_referral_request(
        cls,
        recipient_name: str,
        company: str,
        job_id: str,
        job_title: str,
        key_stack: str = "Azure, Databricks & PySpark",
    ) -> str:
        """
        Generate a structured 5-part referral request:
        1. Short polite introduction
        2. Relevant role and Job ID
        3. Clear candidate match (B.Tech LNMIIT 2025, Databricks, PySpark, Delta Lake)
        4. Polite no-pressure referral ask
        5. Resume availability
        """
        first_name = recipient_name.split()[0] if recipient_name else "there"

        msg = f"""Hi {first_name},

I hope you are having a productive week.

I came across the {job_title} opening at {company} (Job ID: {job_id}) and felt my background aligns well with the team's requirements.

I am a 2025 B.Tech graduate from LNMIIT with practical project and internship experience in {key_stack}, Delta Lake, and building scalable ETL/ELT pipelines.

If you feel comfortable, would you be open to referring my profile for this role? I have attached my resume tailored to this opening for your quick review.

No pressure at all either way—I truly appreciate your time and consideration!

Best regards,
Bharath Kumar
B.Tech CCE, LNMIIT Jaipur (2025)
Azure Data Engineer | Databricks | PySpark"""
        return msg.strip()

    @classmethod
    def generate_campus_parallel_inquiry(
        cls,
        recipient_name: str,
        company: str,
        role: str = "Data Engineer / Graduate Engineer",
    ) -> str:
        """
        Generate a targeted inquiry for parallel off-campus opportunities when campus hiring is underway.
        """
        first_name = recipient_name.split()[0] if recipient_name else "there"

        msg = (
            f"Hi {first_name}, I noticed {company} is actively recruiting 2025 engineering graduates. "
            f"I am a 2025 B.Tech graduate from LNMIIT with hands-on expertise in Azure Data Engineering, "
            f"Databricks, and PySpark. Would love to connect and explore whether any parallel off-campus "
            f"opportunities are available for early-career data engineers."
        )
        if len(msg) > 298:
            msg = msg[:295] + "..."
        return msg

    @classmethod
    def generate_follow_up(cls, recipient_name: str, company: str, job_title: str) -> str:
        """Generate a polite follow-up message after 5-7 days."""
        first_name = recipient_name.split()[0] if recipient_name else "there"

        msg = (
            f"Hi {first_name}, following up gently on my earlier note regarding the {job_title} role at {company}. "
            f"I understand you have a busy schedule, so no rush at all! Please let me know if you would like me "
            f"to share my updated resume or GitHub project demos. Thank you again for your time!"
        )
        return msg
