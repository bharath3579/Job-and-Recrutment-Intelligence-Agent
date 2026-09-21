# 🤖 AI Job & Recruitment Intelligence Agent

An end-to-end, **100% cost-free**, personal AI-powered Job and Recruitment Intelligence Agent tailored specifically for **Bharath Kumar** (B.Tech LNMIIT 2025, Data Engineer with Azure, Databricks, PySpark, SQL, ADLS Gen2, Delta Lake, Unity Catalog, Python).

---

## 🌟 Key Capabilities

1. **Two Distinct Operational Workflows**:
   - **Mode 1: 🔍 "Run Full Recruitment Scan"**: Scans publicly indexed LinkedIn posts and feeds using dynamic combinations of *(Roles × Skills × Signals × Locations)*. Only when a high-match opportunity is found ($\ge 70\%$) does it discover the recruiter for that specific role and draft personalized outreach into your Approval Queue.
   - **Mode 2: 🏢 "Direct Company Connect" (Campus / Off-Campus Parallel Shortcut)**: Heard about a campus drive or want to target a specific company? Enter the company name directly (e.g. *Cognizant*, *LTIMindtree*, *Tiger Analytics*). The agent skips general post searching and directly discovers Talent Acquisition, Campus Recruiters, and Data Engineering leads in India, drafting tailored 2025 off-campus inquiry messages.
2. **Strict Human-in-the-Loop Approval Queue**:
   - Every connection note (<300 characters, anti-spam, honest representation of LNMIIT 2025 background) and structured referral message is generated as a **Draft**.
   - No message is ever sent without your explicit review and approval via the Web/Mobile UI or CLI.
3. **Mandatory Evidence Rule**:
   - Every recruitment signal (walk-in drive, off-campus drive, "we're hiring" post, referral call) captures the exact author, date, source URL, urgency, and raw quote/snippet.
4. **100% Cost-Free & Mobile/iOS Ready**:
   - Zero paid APIs or subscriptions required.
   - SQLite relational database (`data/recruitment_tracker.db`) serves as the local source of truth.
   - Automatically synchronizes with Microsoft Excel workbook (`recruitment_tracker.xlsx`) across all 6 required sheets (*Jobs, People, Companies, Outreach, Recruitment Signals, Dashboard*).
   - Serves a mobile-first responsive dashboard and clean JSON REST API (`/api/v1/...`) ready for an iOS personal client (SwiftUI / Shortcuts / PWA) accessible directly over local Wi-Fi.
5. **Tracker Updates via Email & Manual Control**:
   - Quick-paste or ingest email notifications, recruiter replies, or interview invitations to automatically update application statuses and log audit records.
   - Full manual edit permissions to adjust statuses, notes, and dates anytime.

---

## 🚀 Quick Start Guide

### 1. Launch the Web & Mobile Dashboard
Run the following command in your terminal:
```powershell
python agent.py server
```
- **Desktop access**: Open your browser at [http://localhost:8000](http://localhost:8000)
- **iPhone / Mobile access**: Ensure your phone is connected to the same Wi-Fi network as your laptop. In Safari on your iPhone, open:
  ```text
  http://<your-laptop-ip-address>:8000
  ```
  *(Tip: In Safari, tap "Share" -> "Add to Home Screen" to install it like a native iOS app!)*

---

## 💻 Command-Line Interface (CLI)

You can perform all actions directly from your terminal:

| Command | Description |
| :--- | :--- |
| `python agent.py scan` | Run Mode 1: Full Recruitment Scan (Roles × Skills × Signals) |
| `python agent.py company-connect "Company Name"` | Run Mode 2: Targeted Company Scout & 2025 Off-Campus Outreach |
| `python agent.py email-ingest --text "email text"` | Ingest email alert / recruiter response & update application status |
| `python agent.py approve` | Interactive terminal approval queue for reviewing outreach drafts |
| `python agent.py sync` | Manually sync SQLite database to `recruitment_tracker.xlsx` |
| `python agent.py report --daily` | Print today's high-priority jobs, signals, and follow-ups |
| `python agent.py report --weekly` | Print weekly market intelligence and skill demand report |
| `python tests/run_tests.py` | Run the complete automated test suite |

---

## 📊 Excel Workbook Structure (`recruitment_tracker.xlsx`)

The central Excel workbook is continuously maintained with openpyxl across 6 sheets:
1. **Sheet 1 — Jobs**: Canonical deduplicated listings, match scores (0–100%), plain-text explainability (*"Why detected"*), freshness tiers, application statuses, and resume versions.
2. **Sheet 2 — People**: Discovered recruiters, talent acquisition leads, engineering hiring managers, and LNMIIT alumni with connection statuses.
3. **Sheet 3 — Companies**: Target companies, hiring frequency, relevant role counts, recruiters found, and priority ratings.
4. **Sheet 4 — Outreach**: Drafted connection requests, referral notes, dates, and approval statuses.
5. **Sheet 5 — Recruitment Signals**: Active hiring posts, walk-ins, off-campus drives, and referral opportunities with exact evidence quotes and URLs.
6. **Sheet 6 — Dashboard**: Summary KPI cards, pipeline conversion metrics, and follow-ups due.

---

## 📱 REST API Endpoints (For iOS Personal App)

| Endpoint | Method | Purpose |
| :--- | :--- | :--- |
| `/api/v1/stats` | `GET` | Overview KPI counts (high match jobs, signals, approvals) |
| `/api/v1/jobs` | `GET` | List all discovered jobs with match scores and details |
| `/api/v1/jobs/{id}/status` | `PATCH` | Manually update job application status |
| `/api/v1/signals` | `GET` | List active recruitment signals with evidence snippets |
| `/api/v1/people` | `GET` | List discovered recruiters and alumni |
| `/api/v1/approvals` | `GET` | List outreach drafts pending approval |
| `/api/v1/approvals/{id}/action`| `POST` | Approve, edit, or reject an outreach draft |
| `/api/v1/scan` | `POST` | Trigger Mode 1 Full Recruitment Scan |
| `/api/v1/company-connect` | `POST` | Trigger Mode 2 Direct Company Scout |
| `/api/v1/ingest/email` | `POST` | Ingest email alert / status update |
| `/api/v1/sync-excel` | `POST` | Force export to `recruitment_tracker.xlsx` |
| `/api/v1/download-excel` | `GET` | Download the latest Excel file |
| `/api/v1/reports/daily` | `GET` | Fetch daily markdown report |
| `/api/v1/reports/weekly` | `GET` | Fetch weekly markdown report |
| `/api/v1/pipeline/runs` | `GET` | Fetch pipeline telemetry and execution logs |

---

## 🔒 Candidate Profile & Security
- All sensitive candidate parameters are isolated in [`agent/config.py`](file:///c:/Users/Bharathkumar/Desktop/recrutment%20tracker/agent/config.py).
- No passwords, session tokens, or auth cookies are ever stored in Excel or plain text.
- Full forensic audit logs are recorded in the `audit_logs` table for complete transparency.
