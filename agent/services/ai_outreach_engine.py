"""AI-powered Personalized Outreach Engine supporting LLM generation (Gemini / OpenAI) with dynamic fallback."""

import logging
import os
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Tuple

from agent.config import (
    CANDIDATE_PROFILE,
    COUNTRY_TIMEZONES,
    GEMINI_API_KEY,
    OPENAI_API_KEY,
)

logger = logging.getLogger(__name__)


class AIOutreachEngine:
    """
    Generates tailored, high-converting, respectful outreach drafts:
    - Persona-Aware (Recruiter vs Hiring Manager vs Peer)
    - Objective-Driven (Job Inquiry, Referral Request, Project Pitch, Professional Connection)
    - Dual Formats: LinkedIn Note (<300 characters) & Full Business Email
    - Timezone-Aware Delivery Suggestion

    NOTE: Strict adherence to user preference — does NOT generate automated 3rd-person
    referral packets; keeps referral requests genuine, personal, and polite.
    """

    @classmethod
    def get_recommended_send_time(cls, country: str = "India") -> str:
        """Calculate the optimal outreach window in recipient's local business hours (Tue-Thu 8:45-9:30 AM)."""
        tz_info = COUNTRY_TIMEZONES.get(country, COUNTRY_TIMEZONES["India"])
        now = datetime.utcnow()
        # Find next Tuesday or Wednesday
        days_ahead = (1 - now.weekday()) % 7  # 1 = Tuesday
        if days_ahead <= 0:
            days_ahead += 7
        target_date = now + timedelta(days=days_ahead)
        date_str = target_date.strftime("%A, %b %d")
        return f"{date_str} at 09:00 AM {tz_info['label']}"

    @classmethod
    def generate_drafts(
        cls,
        recipient_name: str,
        company: str,
        job_title: str,
        person_type: str,
        country: str = "India",
        objective: str = "Ask about a job opportunity",
        skills: str = "Azure, Databricks, PySpark, SQL",
    ) -> Dict[str, Any]:
        """
        Generate both a concise LinkedIn note and a business email draft.
        Attempts LLM generation if API keys are set, otherwise uses intelligent reasoning templates.
        """
        # Try LLM generation first if keys exist
        llm_result = cls._try_llm_generation(
            recipient_name=recipient_name,
            company=company,
            job_title=job_title,
            person_type=person_type,
            country=country,
            objective=objective,
            skills=skills,
        )
        if llm_result:
            return llm_result

        # Fallback to high-context dynamic template engine
        return cls._dynamic_template_generation(
            recipient_name=recipient_name,
            company=company,
            job_title=job_title,
            person_type=person_type,
            country=country,
            objective=objective,
            skills=skills,
        )

    @classmethod
    def _try_llm_generation(
        cls,
        recipient_name: str,
        company: str,
        job_title: str,
        person_type: str,
        country: str,
        objective: str,
        skills: str,
    ) -> Optional[Dict[str, Any]]:
        """Attempt generation using Google Gemini or OpenAI."""
        g_key = os.getenv("GEMINI_API_KEY", GEMINI_API_KEY or "").strip()
        o_key = os.getenv("OPENAI_API_KEY", OPENAI_API_KEY or "").strip()

        candidate_name = CANDIDATE_PROFILE["name"]
        education = f"{CANDIDATE_PROFILE['education']['degree']} from {CANDIDATE_PROFILE['education']['institution']} ({CANDIDATE_PROFILE['education']['graduation_year']})"

        prompt = f"""You are an elite career outreach assistant for {candidate_name} ({education}), specializing in {skills}.
Generate two outreach messages to:
- Recipient: {recipient_name}
- Title/Persona: {person_type} at {company} ({country})
- Target Role: {job_title}
- Outreach Objective: {objective}

Requirements:
1. LINKEDIN NOTE: Exactly under 290 characters. Polite, humble, punchy, anti-spam, honest about 2025 graduation.
2. EMAIL: Concise subject line + 3-paragraph email (max 130 words). Mention specific skills ({skills}), relevant project experience, and an open, no-pressure call to action.

Output format exactly:
SUBJECT: <subject line>
EMAIL:
<email body>
LINKEDIN:
<linkedin note>"""

        if g_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=g_key)
                model = genai.GenerativeModel("gemini-1.5-flash")
                response = model.generate_content(prompt)
                text = response.text
                return cls._parse_llm_output(text, country, objective)
            except Exception as e:
                logger.debug(f"Gemini generation fallback: {e}")

        if o_key:
            try:
                import openai
                client = openai.OpenAI(api_key=o_key)
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7,
                )
                text = response.choices[0].message.content or ""
                return cls._parse_llm_output(text, country, objective)
            except Exception as e:
                logger.debug(f"OpenAI generation fallback: {e}")

        return None

    @classmethod
    def _parse_llm_output(cls, text: str, country: str, objective: str) -> Dict[str, Any]:
        subject = "Inquiry regarding Data Engineering opportunities"
        email_body = text
        linkedin_note = ""

        if "SUBJECT:" in text and "EMAIL:" in text:
            parts = text.split("EMAIL:")
            subject = parts[0].replace("SUBJECT:", "").strip()
            rest = parts[1]
            if "LINKEDIN:" in rest:
                email_parts = rest.split("LINKEDIN:")
                email_body = email_parts[0].strip()
                linkedin_note = email_parts[1].strip()
            else:
                email_body = rest.strip()

        if len(linkedin_note) > 295:
            linkedin_note = linkedin_note[:292] + "..."

        return {
            "subject": subject,
            "email_body": email_body,
            "linkedin_note": linkedin_note,
            "timezone_recommendation": cls.get_recommended_send_time(country),
            "generated_by": "AI LLM Model",
            "objective": objective,
        }

    @classmethod
    def _dynamic_template_generation(
        cls,
        recipient_name: str,
        company: str,
        job_title: str,
        person_type: str,
        country: str,
        objective: str,
        skills: str,
    ) -> Dict[str, Any]:
        """Dynamic reasoning templates tailoring outreach by Persona and Objective."""
        first_name = recipient_name.split()[0] if recipient_name else "there"
        p_type_lower = person_type.lower()
        obj_lower = objective.lower()

        is_recruiter = any(k in p_type_lower for k in ["recruiter", "talent", "hr", "sourcing"])
        is_manager = any(k in p_type_lower for k in ["manager", "lead", "director", "head", "architect"])
        is_peer = not is_recruiter and not is_manager

        # =========================================================================
        # 1. LINKEDIN NOTE GENERATION (<300 chars)
        # =========================================================================
        if "referral" in obj_lower:
            linkedin_note = (
                f"Hi {first_name}, I saw your data platform work at {company}. "
                f"I'm an Azure & Databricks Data Engineer (LNMIIT '25) seeking a {job_title} role. "
                f"Would love to connect and respectfully discuss if you'd be open to reviewing my background for a referral!"
            )
        elif "project" in obj_lower:
            linkedin_note = (
                f"Hi {first_name}, I admire {company}'s data engineering work. "
                f"I recently built an automated ELT pipeline on Databricks & Delta Lake (LNMIIT '25). "
                f"Would love to connect and share quick notes on the architecture if you're open to it!"
            )
        elif "connection" in obj_lower:
            linkedin_note = (
                f"Hi {first_name}, inspiring to follow your journey at {company}! "
                f"I'm a final-year B.Tech student at LNMIIT focusing on Azure, PySpark, and Databricks. "
                f"Would love to connect and learn from your engineering insights."
            )
        else:  # Job Opportunity (Default)
            if is_recruiter:
                linkedin_note = (
                    f"Hi {first_name}, I noticed your hiring activity for {job_title} at {company}. "
                    f"I'm a 2025 B.Tech graduate from LNMIIT with practical project experience in {skills}. "
                    f"Would love to connect regarding upcoming opportunities on your team."
                )
            elif is_manager:
                linkedin_note = (
                    f"Hi {first_name}, I've been following {company}'s data engineering initiatives. "
                    f"I build scalable Lakehouse pipelines with Databricks & PySpark (LNMIIT '25). "
                    f"Would love to connect to learn about your team's upcoming hiring priorities!"
                )
            else:
                linkedin_note = (
                    f"Hi {first_name}, great to connect with fellow data practitioners at {company}! "
                    f"I work with Azure, Databricks & Delta Lake (LNMIIT '25). "
                    f"Would love to connect and exchange thoughts on modern data engineering."
                )

        if len(linkedin_note) > 298:
            linkedin_note = linkedin_note[:295] + "..."

        # =========================================================================
        # 2. EMAIL DRAFT GENERATION
        # =========================================================================
        if "referral" in obj_lower:
            subject = f"Inquiry & Referral Request: {job_title} opening at {company}"
            email_body = f"""Hi {first_name},

I hope you are having a productive week.

I have been actively following {company}'s engineering work and recently noticed the {job_title} opening. Given my background in Azure Data Engineering, Databricks, PySpark, and Delta Lake, I believe my skills strongly align with your team's technical requirements.

I am a 2025 B.Tech graduate from The LNM Institute of Information Technology (LNMIIT). During my academic projects and internships, I designed automated metadata-driven ETL pipelines and implemented data reconciliation frameworks across distributed cloud clusters.

If you feel comfortable after a quick review of my profile, would you be open to referring me for this position? I have attached my resume for your convenience.

No pressure at all either way—I truly appreciate your time and consideration!

Best regards,
Bharath Kumar
B.Tech CCE, LNMIIT Jaipur (2025)
Azure Data Engineer | Databricks | PySpark
LinkedIn: linkedin.com/in/bharath-kumar-data"""

        elif "project" in obj_lower:
            subject = f"Project Discussion: Scalable Data Pipelines & {company} Data Platform"
            email_body = f"""Hi {first_name},

I hope this note finds you well.

I’ve been following {company}'s distributed data systems and recent work in data warehousing. As an aspiring Data Engineer (B.Tech LNMIIT 2025), I recently engineered an end-to-end data pipeline combining Azure Data Factory, Databricks Delta Lake, and PySpark to automate high-throughput SQL Server migrations with automated reconciliation.

I documented the architectural trade-offs, schema enforcement, and cost optimization techniques in a public technical project. Knowing your expertise heading engineering initiatives at {company}, I would be grateful for any brief feedback you might have on this design.

If you have 5-10 minutes in the coming weeks, I’d love the opportunity to briefly share the GitHub repository and discuss how similar patterns could benefit {company}'s platform.

Thank you for your time and guidance!

Warm regards,
Bharath Kumar
Azure & Databricks Data Engineer (LNMIIT '25)"""

        elif "connection" in obj_lower:
            subject = f"Connecting with {company} Data Engineering - Bharath Kumar (LNMIIT '25)"
            email_body = f"""Hi {first_name},

I hope you are having a wonderful week.

I came across your profile while researching data platform leaders at {company} and was impressed by your work scaling distributed data infrastructure.

I am a final-year B.Tech student at LNMIIT graduating in 2025, specializing in Azure Data Engineering, Databricks, PySpark, and Unity Catalog. I am passionate about cloud-native data architecture and would love to stay in touch and learn from your professional journey.

Looking forward to connecting with you!

Best regards,
Bharath Kumar
B.Tech CCE, LNMIIT Jaipur (2025)"""

        else:  # Job Opportunity
            subject = f"Application & Expression of Interest: {job_title} - Bharath Kumar"
            email_body = f"""Hi {first_name},

I hope you are doing well.

I am writing to express my strong enthusiasm for {job_title} opportunities at {company} in {country}. With hands-on experience designing robust cloud data pipelines using {skills}, I am eager to contribute to {company}'s data engineering initiatives.

I am graduating in 2025 with a B.Tech in Computer and Communication Engineering from LNMIIT Jaipur. My hands-on background includes:
- Developing PySpark & Delta Lake transformation pipelines with ACID compliance.
- Orchestrating scalable ingestion workflows in Azure Data Factory (ADF) & ADLS Gen2.
- Implementing Unity Catalog governance, data reconciliation, and query optimization.

I would welcome the opportunity to discuss how my technical skills and eagerness to solve complex data challenges can support your team. My resume is attached for your review.

Thank you very much for your time and consideration.

Sincerely,
Bharath Kumar
B.Tech CCE, LNMIIT Jaipur (2025)
Azure Data Engineer | Databricks | PySpark"""

        return {
            "subject": subject,
            "email_body": email_body.strip(),
            "linkedin_note": linkedin_note.strip(),
            "timezone_recommendation": cls.get_recommended_send_time(country),
            "generated_by": "Rule-Based Dynamic Intelligence Engine",
            "objective": objective,
        }
