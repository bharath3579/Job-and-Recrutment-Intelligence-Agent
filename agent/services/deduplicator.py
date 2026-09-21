"""Canonical deduplication engine for job postings, recruitment signals, and contacts."""

import re
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session

from agent.database import Job, Person, RecruitmentSignal


class Deduplicator:
    """Detects and resolves duplicate job postings and contacts across multiple sources."""

    @staticmethod
    def normalize_string(text: Optional[str]) -> str:
        """Normalize string by lowercasing, removing punctuation and extra spaces."""
        if not text:
            return ""
        text = text.lower()
        text = re.sub(r"[^\w\s]", " ", text)
        return " ".join(text.split())

    @staticmethod
    def normalize_company(company: Optional[str]) -> str:
        """Normalize company name, removing corporate suffixes."""
        if not company:
            return ""
        c = company.lower()
        suffixes = [
            "private limited", "pvt ltd", "ltd", "inc", "technologies", 
            "technology", "solutions", "services", "corporation", "corp", "india"
        ]
        for s in suffixes:
            c = re.sub(rf"\b{s}\b", "", c)
        return " ".join(c.split())

    @classmethod
    def are_jobs_duplicate(cls, job1: Dict[str, Any], job2: Dict[str, Any]) -> bool:
        """Check if two job postings represent the same opportunity."""
        # 1. Exact URL match
        url1 = (job1.get("job_url") or "").strip().lower()
        url2 = (job2.get("job_url") or "").strip().lower()
        if url1 and url2 and url1 == url2:
            return True

        # 2. Normalized Company + Normalized Title + Location match
        comp1 = cls.normalize_company(job1.get("company", ""))
        comp2 = cls.normalize_company(job2.get("company", ""))
        if not comp1 or not comp2 or comp1 != comp2:
            return False

        title1 = cls.normalize_string(job1.get("job_title", ""))
        title2 = cls.normalize_string(job2.get("job_title", ""))

        # Token overlap for title
        tokens1 = set(title1.split())
        tokens2 = set(title2.split())
        if not tokens1 or not tokens2:
            return False

        intersection = tokens1.intersection(tokens2)
        overlap_ratio = len(intersection) / min(len(tokens1), len(tokens2))

        # Check location compatibility
        loc1 = cls.normalize_string(job1.get("location", ""))
        loc2 = cls.normalize_string(job2.get("location", ""))
        location_matches = (
            not loc1 or not loc2 or 
            "remote" in loc1 or "remote" in loc2 or 
            loc1 in loc2 or loc2 in loc1
        )

        return overlap_ratio >= 0.70 and location_matches

    @classmethod
    def find_existing_job(cls, db: Session, job_dict: Dict[str, Any]) -> Optional[Job]:
        """Search database for an existing canonical job that matches the candidate job."""
        job_url = (job_dict.get("job_url") or "").strip()
        if job_url:
            existing = db.query(Job).filter(Job.job_url == job_url).first()
            if existing:
                return existing

        comp_norm = cls.normalize_company(job_dict.get("company", ""))
        all_jobs = db.query(Job).all()
        for j in all_jobs:
            if cls.are_jobs_duplicate(j.to_dict(), job_dict):
                return j
        return None

    @classmethod
    def find_existing_person(cls, db: Session, person_dict: Dict[str, Any]) -> Optional[Person]:
        """Search database for an existing person by LinkedIn URL or Name + Company."""
        linkedin_url = (person_dict.get("linkedin_url") or "").strip().lower()
        if linkedin_url:
            existing = db.query(Person).filter(Person.linkedin_url.ilike(linkedin_url)).first()
            if existing:
                return existing

        name_norm = cls.normalize_string(person_dict.get("name", ""))
        comp_norm = cls.normalize_company(person_dict.get("company", ""))

        all_people = db.query(Person).all()
        for p in all_people:
            if (
                cls.normalize_string(p.name) == name_norm and
                cls.normalize_company(p.company) == comp_norm
            ):
                return p
        return None

    @classmethod
    def find_existing_signal(cls, db: Session, post_url: str) -> Optional[RecruitmentSignal]:
        """Check if recruitment post signal is already recorded."""
        if not post_url:
            return None
        return db.query(RecruitmentSignal).filter(RecruitmentSignal.post_url == post_url).first()
