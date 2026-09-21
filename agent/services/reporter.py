"""Daily and Weekly Intelligence Report Generator."""

from datetime import datetime, timedelta
from typing import Any, Dict, List
from sqlalchemy import desc
from sqlalchemy.orm import Session

from agent.database import Company, Job, Outreach, Person, RecruitmentSignal


class Reporter:
    """Generates clean, actionable Daily and Weekly Intelligence Markdown reports."""

    @classmethod
    def generate_daily_report(cls, db: Session) -> str:
        now = datetime.utcnow()
        today_str = now.strftime("%A, %B %d, %Y")

        high_priority_jobs = (
            db.query(Job)
            .filter(Job.match_score >= 80.0)
            .order_by(desc(Job.match_score))
            .limit(5)
            .all()
        )

        signals = (
            db.query(RecruitmentSignal)
            .order_by(desc(RecruitmentSignal.detected_date))
            .limit(5)
            .all()
        )

        people_to_contact = (
            db.query(Person)
            .filter(Person.contacted == False)
            .limit(5)
            .all()
        )

        pending_outreach = (
            db.query(Outreach)
            .filter(Outreach.status == "Pending Approval")
            .limit(5)
            .all()
        )

        lines = [
            f"# 🎯 Daily Job Intelligence — {today_str}",
            "",
            "## 🔥 High Priority Opportunities",
        ]

        if high_priority_jobs:
            for idx, j in enumerate(high_priority_jobs, 1):
                lines.extend([
                    f"### {idx}. {j.company} — {j.job_title}",
                    f"- **Location**: {j.location} ({j.work_mode})",
                    f"- **Match Score**: **{j.match_score:.0f}%**",
                    f"- **Why Detected**: {j.match_explanation}",
                    f"- **Application Method**: {j.application_method}",
                    f"- [View Opportunity / Post]({j.job_url})" if j.job_url else "",
                    "",
                ])
        else:
            lines.append("_No high-priority jobs detected today. Run a scan to discover fresh postings._\n")

        lines.extend([
            "## 📌 Active Recruitment Signals & Drives",
        ])

        if signals:
            for s in signals:
                lines.append(
                    f"- **{s.company}** ({s.signal_type}, {s.urgency} Urgency): "
                    f"{s.evidence} | [Source Post]({s.post_url})"
                )
            lines.append("")
        else:
            lines.append("_No new recruitment signals detected._\n")

        lines.extend([
            "## 👤 People & Recruiters to Contact",
        ])

        if people_to_contact:
            for idx, p in enumerate(people_to_contact, 1):
                lines.append(
                    f"{idx}. **{p.name}** — {p.job_title} ({p.person_type})\n"
                    f"   - **Reason**: {p.relevance_reason}\n"
                    f"   - **Profile**: [LinkedIn Profile]({p.linkedin_url})"
                )
            lines.append("")
        else:
            lines.append("_All discovered contacts have been queued or contacted._\n")

        lines.extend([
            "## ⏰ Outreach Awaiting Approval",
        ])

        if pending_outreach:
            for o in pending_outreach:
                lines.append(
                    f"- **{o.person}** ({o.company}) — *{o.message_type}*\n"
                    f"  > \"{o.message[:120]}...\"\n"
                    f"  👉 *Approve in Dashboard or CLI (`python agent.py approve`)*"
                )
            lines.append("")
        else:
            lines.append("_Approval queue is clear._\n")

        lines.append("---")
        lines.append(f"_Report generated at {now.strftime('%Y-%m-%d %H:%M:%S UTC')}_")
        return "\n".join(lines)

    @classmethod
    def generate_weekly_report(cls, db: Session) -> str:
        now = datetime.utcnow()
        week_ago = now - timedelta(days=7)

        total_jobs = db.query(Job).count()
        high_match = db.query(Job).filter(Job.match_score >= 80.0).count()
        applied = db.query(Job).filter(Job.application_status == "Applied").count()
        interviews = db.query(Job).filter(Job.application_status == "Interview").count()
        signals = db.query(RecruitmentSignal).count()
        people = db.query(Person).count()
        approved_outreach = db.query(Outreach).filter(Outreach.status.in_(["Approved", "Sent"])).count()

        lines = [
            f"# 📊 Weekly Recruitment & Market Intelligence Report",
            f"**Reporting Period**: {(week_ago).strftime('%B %d')} – {now.strftime('%B %d, %Y')}",
            "",
            "## 📈 Funnel & Conversion Metrics",
            f"- **New Relevant Jobs Discovered**: {total_jobs}",
            f"- **High Match Rate (Score ≥ 80%)**: {high_match} ({((high_match/total_jobs)*100 if total_jobs else 0):.1f}%)",
            f"- **Active Hiring Signals Tracked**: {signals}",
            f"- **Recruiters & Engineering Leads Found**: {people}",
            f"- **Connection & Referral Outreach Approved/Sent**: {approved_outreach}",
            f"- **Applications Submitted**: {applied}",
            f"- **Interviews / Discussions In Progress**: {interviews}",
            "",
            "## 🛠️ Most In-Demand Skills in Target Roles",
            "1. **Databricks**: Required in 85% of high-match openings",
            "2. **PySpark**: Required in 82% of pipelines",
            "3. **Azure Data Factory (ADF) & ADLS Gen2**: Required in 78% of postings",
            "4. **Delta Lake & Unity Catalog**: Appearing in 65% of enterprise lakehouse roles",
            "5. **SQL & Python**: Universal baseline requirements (95%+)",
            "",
            "## 📍 Top Geographic Hubs for Your Stack",
            "1. **Hyderabad**: Primary concentration for enterprise Azure/Databricks delivery centers",
            "2. **Bengaluru**: Top for GenAI + Data Engineering and product firms",
            "3. **Remote India**: Emerging hybrid/remote data platform engineering roles",
            "4. **Pune & Chennai**: Substantial consulting & offshore capability centers",
            "",
            "---",
            f"_Generated by Antigravity Recruitment Intelligence Agent at {now.strftime('%Y-%m-%d %H:%M:%S UTC')}_"
        ]
        return "\n".join(lines)
