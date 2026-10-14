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

# External API & AI Integrations
HUNTER_API_KEY = os.getenv("HUNTER_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Global Target Countries Supported
SUPPORTED_COUNTRIES = [
    "India",
    "United States",
    "United Kingdom",
    "Germany",
    "ireland",
    "Singapore",
    "Australia",
    "new zealand",
    "Remote",
]

# Timezone mapping for country-aware outreach delivery
COUNTRY_TIMEZONES = {
    "India": {"tz": "Asia/Kolkata", "label": "IST (UTC+5:30)", "offset_hours": 5.5},
    "United States": {"tz": "America/New_York", "label": "EST (UTC-5)", "offset_hours": -5.0},
    "United Kingdom": {"tz": "Europe/London", "label": "GMT/BST (UTC+0)", "offset_hours": 0.0},
    "Germany": {"tz": "Europe/Berlin", "label": "CET (UTC+1)", "offset_hours": 1.0},
    "Canada": {"tz": "America/Toronto", "label": "EST (UTC-5)", "offset_hours": -5.0},
    "Singapore": {"tz": "Asia/Singapore", "label": "SGT (UTC+8)", "offset_hours": 8.0},
    "Australia": {"tz": "Australia/Sydney", "label": "AEST (UTC+10)", "offset_hours": 10.0},
    "Netherlands": {"tz": "Europe/Amsterdam", "label": "CET (UTC+1)", "offset_hours": 1.0},
    "Remote": {"tz": "UTC", "label": "UTC", "offset_hours": 0.0},
}

# ==============================================================================
# CANDIDATE PROFILE SPECIFICATION
# ==============================================================================
CANDIDATE_PROFILE = {
    "name": "Bharath Kumar Makkena",
    "email": "bharathalu35@gmail.com",
    "phone": "+91 93926 62638",
    "linkedin": "https://www.linkedin.com/in/bharath-kumar-makkena",
    "github": "https://github.com/bharath3579",
    "education": {
        "degree": "B.Tech in Computer and Communication Engineering",
        "institution": "The LNM Institute of Information Technology (LNMIIT), Jaipur",
        "graduation_year": 2025,
    },
    "current_career": "Data Engineer @ Celebal Technologies",
    "current_experience": {
        "company": "Celebal Technologies",
        "role": "Data Engineer",
        "tenure": "Apr 2025 - Present",
        "highlights": [
            "Migrated production pipelines & tables from Azure Synapse and legacy systems (Teradata, Oracle, SQL Server) to Databricks Unity Catalog.",
            "Standardized metadata-driven architecture with ADF, reducing pipeline duplication by ~70%.",
            "Halved total pipeline runtime from 60h to 30h via Spark tuning (broadcast joins, partition pruning, Adaptive Query Execution).",
            "Engineered hash-based data reconciliation framework verifying row/column-level integrity post-migration.",
            "Built multi-agent LLM migration system with RAG integration, automating ~70% of legacy-to-Spark code conversion.",
            "Mentored junior engineers on PySpark, SQL, and distributed pipeline practices.",
        ],
    },
    "previous_experience": [
        {
            "company": "Bluestock Fintech",
            "role": "Software Developer Intern",
            "tenure": "Mar 2023 - Jul 2023",
            "highlights": "Fintech stock analytics backend services, data-driven technical analysis features, full product lifecycle.",
        }
    ],
    "certifications": [
        "Databricks Certified Professional Data Engineer",
        "Databricks Certified Associate Data Engineer",
        "Microsoft DP-700 - Azure Data Analyst Associate",
        "Anthropic - Claude Certified Architect",
    ],
    "achievements": [
        "TVS Grid 6.0 - Top 14 out of 2,00,000+ participants (Fraud Detection & Risk Analytics)",
        "TATA Imagination - Top 500 out of 5,00,000+ participants",
        "LeetCode - Rating 1989 (Top 3%, 700+ problems solved)",
    ],
    "primary_skills": [
        "Azure Data Engineering",
        "Databricks",
        "Unity Catalog",
        "PySpark",
        "Spark SQL",
        "SQL",
        "T-SQL",
        "Azure Data Factory (ADF)",
        "ADLS Gen2",
        "Delta Lake",
        "Azure Synapse",
        "Spark Tuning",
        "Adaptive Query Execution (AQE)",
        "Auto Loader",
        "Schema Evolution",
        "Data Reconciliation",
        "ETL/ELT",
        "Lakehouse",
        "Agentic AI",
        "LangGraph",
        "LangChain",
        "RAG",
        "LLMs",
        "Python",
    ],
    "secondary_skills": [
        "Teradata",
        "Oracle",
        "SQL Server",
        "Power BI",
        "Fraud Analytics",
        "Clustering",
        "Feature Engineering",
        "Git",
        "JavaScript",
        "React",
        "Node.js",
        "MongoDB",
        "MySQL",
        "C++",
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
