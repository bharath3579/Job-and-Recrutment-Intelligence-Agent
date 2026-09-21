"""Configuration settings and candidate profile for the Job & Recruitment Intelligence Agent."""

import os
from pathlib import Path
from typing import Dict, List

# Base Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RESUMES_DIR = BASE_DIR / "resumes"
DATA_DIR.mkdir(parents=True, exist_ok=True)
RESUMES_DIR.mkdir(parents=True, exist_ok=True)

# Database & Storage Files
DB_FILE = DATA_DIR / "recruitment_tracker.db"
DATABASE_URL = f"sqlite:///{DB_FILE}"
EXCEL_FILE = BASE_DIR / "recruitment_tracker.xlsx"

# Web Server Configuration
SERVER_HOST = "0.0.0.0"
SERVER_PORT = 8000

# ==============================================================================
# CANDIDATE PROFILE SPECIFICATION
# ==============================================================================
CANDIDATE_PROFILE = {
    "name": "Bharath Kumar",
    "education": {
        "degree": "B.Tech in Computer and Communication Engineering",
        "institution": "The LNM Institute of Information Technology (LNMIIT), Jaipur",
        "graduation_year": 2025,
    },
    "current_career": "Data Engineering / Azure Data Engineer",
    "primary_skills": [
        "Azure Data Engineering",
        "Databricks",
        "PySpark",
        "SQL",
        "Azure Data Factory (ADF)",
        "ADLS Gen2",
        "Delta Lake",
        "Unity Catalog",
        "Data Migration",
        "SQL Server to Databricks Migration",
        "ETL/ELT",
        "Data Reconciliation",
        "Metadata-driven Pipelines",
        "Python",
    ],
    "secondary_skills": [
        "JavaScript",
        "React",
        "Node.js",
        "MongoDB",
        "MySQL",
        "C++",
        "Machine Learning",
        "Deep Learning",
        "DSA",
    ],
    "target_roles": [
        "Data Engineer",
        "Azure Data Engineer",
        "Databricks Data Engineer",
        "Cloud Data Engineer",
        "Data Engineering",
        "Analytics Engineer",
        "ETL Developer",
        "Big Data Engineer",
        "PySpark Developer",
        "AI/Data Engineering",
        "GenAI Data Engineer",
        "Agentic AI Data Engineer",
    ],
    "preferred_locations": {
        "Hyderabad": 1.0,      # Highest priority
        "Remote": 1.0,         # Remote India
        "Remote India": 1.0,
        "Bengaluru": 0.95,
        "Bangalore": 0.95,
        "Pune": 0.90,
        "Chennai": 0.85,
        "Delhi NCR": 0.85,
        "Gurgaon": 0.85,
        "Noida": 0.85,
        "Mumbai": 0.85,
        "India": 0.70,
        "Other India": 0.70,
    },
}

# ==============================================================================
# RECRUITMENT SIGNAL KEYWORDS & SEARCH PHRASES
# ==============================================================================
SEARCH_KEYWORDS = {
    "roles": [
        "Data Engineer",
        "Azure Data Engineer",
        "Databricks Engineer",
        "Databricks Data Engineer",
        "PySpark Developer",
        "Cloud Data Engineer",
        "Analytics Engineer",
        "ETL Developer",
        "Big Data Engineer",
        "Data Platform Engineer",
    ],
    "skills": [
        "Databricks",
        "PySpark",
        "Azure Data Factory",
        "Delta Lake",
        "ADLS Gen2",
        "Unity Catalog",
        "Data Migration",
        "Python",
        "SQL",
    ],
    "signals": [
        "Hiring",
        "We're hiring",
        "Actively hiring",
        "Looking for",
        "Openings",
        "Referral",
        "Refer",
        "Walk-in",
        "Recruitment drive",
        "Hiring drive",
        "Off-campus",
        "Campus hiring",
        "Freshers",
        "2025 batch",
        "2025 graduates",
        "Immediate joiners",
        "Urgent requirement",
        "Multiple openings",
        "DM your resume",
        "Share your resume",
        "Send your CV",
    ],
    "target_locations": [
        "Hyderabad",
        "Remote",
        "Bengaluru",
        "Pune",
        "Chennai",
        "Delhi NCR",
        "Mumbai",
    ],
}

# Standard Target Companies in India hiring Data Engineers / GCCs / Tech Services
POPULAR_TECH_COMPANIES = [
    "Cognizant",
    "TCS",
    "Infosys",
    "Wipro",
    "LTIMindtree",
    "Accenture",
    "Tiger Analytics",
    "Fractal Analytics",
    "Celebal Technologies",
    "LatentView Analytics",
    "Mu Sigma",
    "ZS Associates",
    "Capgemini",
    "Deloitte",
    "PwC India",
    "EY India",
    "KPMG India",
    "Persistent Systems",
    "Hexaware",
    "Brillio",
    "Mphasis",
    "Coforge",
    "Tech Mahindra",
    "HCLTech",
    "Thoughtworks",
    "EPAM Systems",
    "Publicis Sapient",
]

# Scoring Weights
SCORE_WEIGHTS = {
    "skills": 35,
    "experience_role": 25,
    "location": 20,
    "freshness_urgency": 10,
    "recruitment_signal_referral": 10,
}

# Freshness Cutoffs (in hours)
FRESHNESS_TIERS = {
    "TIER_1": 24,       # < 24 hours (super fresh)
    "TIER_1B": 72,      # 24 - 72 hours (recent)
    "TIER_2": 168,      # up to 7 days (active)
    "STALE": 336,       # > 14 days (stale)
}
