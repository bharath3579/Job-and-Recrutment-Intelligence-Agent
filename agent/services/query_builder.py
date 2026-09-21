"""Dynamic multi-combination query builder for job search, LinkedIn signals, and company recruiter lookup."""

import random
from typing import Dict, List, Tuple
from agent.config import CANDIDATE_PROFILE, SEARCH_KEYWORDS


class QueryBuilder:
    """Generates search query strings combining roles, skills, signals, and locations."""

    @classmethod
    def build_linkedin_signal_queries(cls, max_queries: int = 8) -> List[Dict[str, str]]:
        """
        Generate dynamic combinations of:
        Roles x Skills x Signals x Locations targeting publicly indexed LinkedIn recruitment posts.
        """
        queries = []
        roles = SEARCH_KEYWORDS["roles"][:5]
        skills = SEARCH_KEYWORDS["skills"][:4]
        signals = ["Hiring", "We're hiring", "Referral", "Immediate joiners", "Off-campus", "Walk-in", "DM your resume"]
        locations = ["Hyderabad", "Remote", "Bengaluru", "Pune", "India"]

        # Core combinations
        for role in roles:
            for skill in skills[:2]:
                signal = random.choice(signals)
                loc = random.choice(locations)
                query_str = f'site:linkedin.com/posts "{role}" "{skill}" "{signal}" "{loc}"'
                queries.append({
                    "query": query_str,
                    "role": role,
                    "skill": skill,
                    "signal": signal,
                    "location": loc,
                    "target": "LinkedIn Posts",
                })

        # Add 2025 fresher / off-campus specific queries
        queries.append({
            "query": 'site:linkedin.com/posts "Data Engineer" ("2025 batch" OR "2025 graduates" OR "Off-campus" OR "Freshers") (Azure OR Databricks OR PySpark)',
            "role": "Data Engineer (2025 Batch)",
            "skill": "Azure / Databricks",
            "signal": "Off-campus / Freshers",
            "location": "India",
            "target": "LinkedIn Posts",
        })

        queries.append({
            "query": 'site:linkedin.com/posts "Azure Data Engineer" ("DM resume" OR "Send CV" OR "Referral") "Hyderabad"',
            "role": "Azure Data Engineer",
            "skill": "Azure / ADF / PySpark",
            "signal": "Referral / Direct DM",
            "location": "Hyderabad",
            "target": "LinkedIn Posts",
        })

        # Shuffle and return top requested
        random.seed(42)
        random.shuffle(queries)
        return queries[:max_queries]

    @classmethod
    def build_company_recruiter_query(cls, company_name: str) -> Dict[str, str]:
        """
        Build targeted recruiter & talent acquisition lookup query for a specific company (Mode 2).
        Focuses on HR leads, campus/university hiring, and Data Engineering engineering managers in India.
        """
        company_clean = company_name.strip()
        google_query = (
            f'site:linkedin.com/in "{company_clean}" '
            f'("Campus Recruiter" OR "University Hiring" OR "Talent Acquisition" OR "Technical Recruiter" OR "Data Engineering Manager") '
            f'India'
        )
        signals_query = (
            f'site:linkedin.com/posts "{company_clean}" ("hiring" OR "we are hiring" OR "off-campus" OR "referral" OR "drive") '
            f'("Data Engineer" OR "Data Engineering" OR "Azure" OR "Fresher")'
        )
        return {
            "company": company_clean,
            "people_search_query": google_query,
            "company_signal_query": signals_query,
        }
