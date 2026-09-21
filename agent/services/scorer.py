"""Relevance Scoring Engine (0-100) with explainable reasoning."""

import re
from typing import Any, Dict, List, Tuple
from agent.config import CANDIDATE_PROFILE, SCORE_WEIGHTS, FRESHNESS_TIERS


class Scorer:
    """Calculates deterministic, transparent 0-100 match scores and generates human-readable explanations."""

    PRIMARY_SKILLS_WEIGHTED = {
        "databricks": 6.0,
        "pyspark": 6.0,
        "azure data engineering": 5.0,
        "azure": 4.0,
        "azure data factory": 4.0,
        "adf": 4.0,
        "delta lake": 4.0,
        "unity catalog": 4.0,
        "sql": 4.0,
        "python": 4.0,
        "adls": 3.0,
        "data migration": 3.0,
        "etl": 3.0,
        "elt": 3.0,
        "data pipeline": 3.0,
    }

    TARGET_ROLE_KEYWORDS = [
        "data engineer",
        "azure data engineer",
        "databricks",
        "pyspark",
        "cloud data engineer",
        "analytics engineer",
        "etl developer",
        "big data engineer",
        "data platform engineer",
        "ai data engineer",
    ]

    @classmethod
    def score_job(cls, job_dict: Dict[str, Any]) -> Tuple[float, str]:
        """
        Evaluate job opportunity against candidate profile.
        Returns: (score, explainable_reason)
        """
        title = (job_dict.get("job_title") or "").lower()
        skills_text = (job_dict.get("skills") or "").lower()
        desc = (job_dict.get("description") or "").lower()
        full_text = f"{title} {skills_text} {desc}"

        location = (job_dict.get("location") or "").lower()
        freshness_tier = job_dict.get("freshness_tier") or "<24h"
        recruitment_signal = (job_dict.get("recruitment_signal") or "").lower()
        exp_req = (job_dict.get("experience_required") or "").lower()

        reasons = []

        # -------------------------------------------------------------
        # 1. Skill Match (Max 35 points)
        # -------------------------------------------------------------
        skill_points = 0.0
        matched_skills = []
        for skill_kw, weight in cls.PRIMARY_SKILLS_WEIGHTED.items():
            pattern = rf"\b{re.escape(skill_kw)}\b"
            if re.search(pattern, full_text):
                skill_points += weight
                matched_skills.append(skill_kw.title())

        # Cap at 35
        skill_score = min(35.0, skill_points)
        if matched_skills:
            top_skills = matched_skills[:4]
            reasons.append(f"Strong skill match on {', '.join(top_skills)} ({skill_score:.0f}/35)")
        else:
            reasons.append(f"Base data engineering skills ({skill_score:.0f}/35)")

        # -------------------------------------------------------------
        # 2. Experience & Role Match (Max 25 points)
        # -------------------------------------------------------------
        role_score = 15.0  # base
        matched_role = False
        for r_kw in cls.TARGET_ROLE_KEYWORDS:
            if r_kw in title:
                role_score = 20.0
                matched_role = True
                break

        # Check experience suitability (candidate is 2025 grad, 0-2 yrs)
        if any(x in exp_req or x in full_text for x in ["fresher", "2025", "0-1", "0-2", "0-3", "entry", "graduate", "junior", "associate"]):
            role_score = min(25.0, role_score + 5.0)
            reasons.append("Optimal experience level (0-2 yrs / 2025 grad)")
        elif any(x in exp_req for x in ["5+", "7+", "8+", "10+", "lead", "principal", "architect"]):
            role_score = max(5.0, role_score - 10.0)
            reasons.append("Senior experience requested")
        else:
            role_score = min(25.0, role_score + 3.0)

        # -------------------------------------------------------------
        # 3. Location Match (Max 20 points)
        # -------------------------------------------------------------
        location_score = 12.0
        matched_loc_name = "India"
        for loc_name, weight in CANDIDATE_PROFILE["preferred_locations"].items():
            if loc_name.lower() in location:
                location_score = 20.0 * weight
                matched_loc_name = loc_name
                break

        if "hyderabad" in location:
            reasons.append("Primary preferred location: Hyderabad (+20)")
        elif "remote" in location:
            reasons.append("Remote India opportunity (+20)")
        else:
            reasons.append(f"{matched_loc_name} location (+{location_score:.0f})")

        # -------------------------------------------------------------
        # 4. Freshness & Urgency (Max 10 points)
        # -------------------------------------------------------------
        freshness_score = 5.0
        if freshness_tier == "<24h":
            freshness_score = 10.0
            reasons.append("Posted < 24 hours ago (+10)")
        elif freshness_tier == "24-72h":
            freshness_score = 8.0
            reasons.append("Posted within 24-72 hours (+8)")
        elif freshness_tier == "<7d":
            freshness_score = 6.0
            reasons.append("Posted this week (+6)")
        else:
            freshness_score = 2.0
            reasons.append("Older posting (+2)")

        # Urgency bonus
        if any(u in full_text for u in ["immediate", "urgent", "hiring urgently", "quick joiner"]):
            freshness_score = min(10.0, freshness_score + 2.0)

        # -------------------------------------------------------------
        # 5. Recruitment Signal & Referral Bonus (Max 10 points)
        # -------------------------------------------------------------
        signal_score = 4.0
        if "active recruitment signal" in recruitment_signal or "dm" in full_text or "share your resume" in full_text:
            signal_score = 10.0
            reasons.append("Recruiter explicitly requesting resumes / active signal (+10)")
        elif "campus" in recruitment_signal or "off-campus" in recruitment_signal or "walk-in" in recruitment_signal:
            signal_score = 10.0
            reasons.append("Recruitment drive / off-campus opportunity (+10)")
        elif "referral" in recruitment_signal or "refer" in full_text:
            signal_score = 9.0
            reasons.append("Referral channel available (+9)")
        elif "pipeline" in recruitment_signal:
            signal_score = 7.0
            reasons.append("Active company recruitment pipeline (+7)")

        # -------------------------------------------------------------
        # Total Calculation
        # -------------------------------------------------------------
        total_score = skill_score + role_score + location_score + freshness_score + signal_score
        total_score = min(100.0, max(0.0, round(total_score, 1)))

        explanation = ", ".join(reasons) + f". Total Score: {total_score:.0f}/100."
        return total_score, explanation
