"""Recruitment signal classification engine with mandatory source evidence retention."""

import re
from typing import Any, Dict, Optional, Tuple


class SignalDetector:
    """
    Classifies raw text into Recruitment Signal Types (A through F)
    and extracts full evidence snippets, author, and application method.
    """

    SIGNAL_TYPES = {
        "ACTIVE_RECRUITMENT": "Active Recruitment Signal",
        "RECRUITMENT_EVENT": "Recruitment Event",
        "CAMPUS_OFFCAMPUS": "Campus/Off-Campus Hiring",
        "REFERRAL_OPPORTUNITY": "Referral Opportunity",
        "PIPELINE_SIGNAL": "Hiring Pipeline Signal",
        "NORMAL_POSTING": "Normal Job Posting",
    }

    @classmethod
    def classify_text(cls, text: str, author_role: str = "") -> Tuple[str, str, str, str]:
        """
        Classify text snippet into Signal Type, urgency, evidence snippet, and application method.
        Returns: (signal_type, urgency, evidence_snippet, application_method)
        """
        t = text.lower()

        # 1. Check for Referral Opportunity
        if any(k in t for k in ["dm for referral", "referral", "willing to refer", "refer candidates", "can refer"]):
            evidence = cls._extract_evidence(text, ["referral", "refer", "dm"])
            return (
                cls.SIGNAL_TYPES["REFERRAL_OPPORTUNITY"],
                "High",
                evidence,
                "LinkedIn DM / Message",
            )

        # 2. Check for Recruitment Event (Walk-in, Drive)
        if any(k in t for k in ["walk-in", "walkin", "recruitment drive", "hiring drive", "interview drive", "in-person interview"]):
            evidence = cls._extract_evidence(text, ["walk-in", "drive", "interview"])
            return (
                cls.SIGNAL_TYPES["RECRUITMENT_EVENT"],
                "Urgent",
                evidence,
                "In-person / Walk-in Registration",
            )

        # 3. Check for Campus / Off-Campus Hiring
        if any(k in t for k in ["off-campus", "offcampus", "campus hiring", "2025 batch", "2025 passout", "2025 graduates", "freshers drive"]):
            evidence = cls._extract_evidence(text, ["off-campus", "campus", "2025", "fresher"])
            return (
                cls.SIGNAL_TYPES["CAMPUS_OFFCAMPUS"],
                "High",
                evidence,
                "Campus / Off-Campus Application Link",
            )

        # 4. Check for Active Recruitment Signal ("We are hiring", "DM resume", "Send CV")
        if any(k in t for k in ["we are hiring", "we're hiring", "actively hiring", "multiple openings", "dm your resume", "send your resume", "share cv", "immediate joiners"]):
            evidence = cls._extract_evidence(text, ["hiring", "resume", "cv", "openings", "joiners"])
            app_method = "Email / DM"
            if "dm" in t:
                app_method = "LinkedIn DM"
            elif "@" in t:
                app_method = "Direct Email"
            return (
                cls.SIGNAL_TYPES["ACTIVE_RECRUITMENT"],
                "Urgent" if "immediate" in t or "urgent" in t else "High",
                evidence,
                app_method,
            )

        # 5. Check for Hiring Pipeline Signal (Recruiter recurring posting or multiple roles)
        if any(k in author_role.lower() for k in ["recruiter", "talent acquisition", "ta lead", "sourcer"]) and any(k in t for k in ["open positions", "hiring for", "looking for"]):
            evidence = cls._extract_evidence(text, ["looking for", "open positions", "hiring"])
            return (
                cls.SIGNAL_TYPES["PIPELINE_SIGNAL"],
                "Medium",
                evidence,
                "Recruiter Profile / Portal",
            )

        # 6. Default: Normal Job Posting
        evidence = cls._extract_evidence(text, ["data engineer", "opening", "job"])
        return (
            cls.SIGNAL_TYPES["NORMAL_POSTING"],
            "Medium",
            evidence,
            "Job Application Link",
        )

    @staticmethod
    def _extract_evidence(full_text: str, keywords: list) -> str:
        """Extract a 2-3 sentence snippet around the matching keywords to preserve genuine evidence."""
        sentences = re.split(r"(?<=[.!?\n])\s+", full_text.strip())
        matched = []
        for s in sentences:
            if any(k in s.lower() for k in keywords):
                clean_s = s.strip().replace("\n", " ")
                if len(clean_s) > 10:
                    matched.append(clean_s)
            if len(matched) >= 2:
                break

        if matched:
            return " | ".join(matched)[:300]
        return full_text.strip()[:250]
