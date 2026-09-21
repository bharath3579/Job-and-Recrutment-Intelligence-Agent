"""Command-Line Interface (CLI) for the Recruitment Intelligence Agent."""

import argparse
import sys
from pathlib import Path
import uvicorn

from agent.config import SERVER_HOST, SERVER_PORT
from agent.database import SessionLocal, init_db, Outreach
from agent.services.company_scout import CompanyScout
from agent.services.email_ingest import EmailIngest
from agent.services.excel_sync import ExcelSync
from agent.services.full_scanner import FullScanner
from agent.services.reporter import Reporter


def main():
    parser = argparse.ArgumentParser(
        description="Antigravity Job & Recruitment Intelligence Agent CLI",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", help="Agent commands")

    # Command: scan (Mode 1)
    subparsers.add_parser("scan", help="Run Mode 1: Full Recruitment Scan (Roles x Skills x Signals)")

    # Command: company-connect (Mode 2)
    scout_parser = subparsers.add_parser("company-connect", help="Run Mode 2: Targeted Company Direct Connect")
    scout_parser.add_argument("company", help="Target company name (e.g. Cognizant, LTIMindtree)")
    scout_parser.add_argument("--reason", default="Campus hiring announced / Parallel off-campus inquiry", help="Reason or context")

    # Command: email-ingest
    email_parser = subparsers.add_parser("email-ingest", help="Ingest email alert / recruiter reply")
    email_parser.add_argument("--text", help="Raw email text")
    email_parser.add_argument("--file", help="Path to text file containing email body")

    # Command: sync
    subparsers.add_parser("sync", help="Synchronize SQLite database to recruitment_tracker.xlsx")

    # Command: approve
    subparsers.add_parser("approve", help="Interactive terminal approval queue for outreach drafts")

    # Command: report
    report_parser = subparsers.add_parser("report", help="Generate intelligence markdown reports")
    report_parser.add_argument("--daily", action="store_true", help="Print daily report")
    report_parser.add_argument("--weekly", action="store_true", help="Print weekly report")

    # Command: parse-resume
    resume_cmd = subparsers.add_parser("parse-resume", help="Parse .docx ATS resume and display extracted skills & profile")
    resume_cmd.add_argument("--file", help="Path to .docx resume (optional)")

    # Command: server
    server_parser = subparsers.add_parser("server", help="Launch local FastAPI dashboard & REST API server")
    server_parser.add_argument("--host", default=SERVER_HOST, help="Host address (default 0.0.0.0 for LAN/phone access)")
    server_parser.add_argument("--port", type=int, default=SERVER_PORT, help="Port (default 8000)")

    args = parser.parse_args()

    # Ensure DB is initialized
    init_db()
    db = SessionLocal()

    try:
        if args.command == "scan":
            print("\n[+] Running Mode 1: Full Recruitment Scan (Roles x Skills x Signals)...")
            res = FullScanner.run_full_scan(db)
            ExcelSync.sync_database_to_excel(db)
            print(f"[OK] Scan Completed!")
            print(f"    - Items Scanned: {res['items_scanned']}")
            print(f"    - Qualified Jobs: {res['qualified_jobs_count']}")
            print(f"    - Signals Tracked: {res['new_signals_count']}")
            print(f"    - People Discovered: {res['new_people_count']}")
            print(f"    - Outreach Drafted: {res['new_drafts_count']}")
            print(f"    - Excel Tracker: Updated recruitment_tracker.xlsx")

        elif args.command == "company-connect":
            print(f"\n[+] Running Mode 2: Targeted Company Direct Connect for '{args.company}'...")
            res = CompanyScout.scout_company(db, company_name=args.company, reason=args.reason)
            ExcelSync.sync_database_to_excel(db)
            print(f"[OK] Company Connect Completed for {res['company']}!")
            print(f"    - Key Recruiters/Leads Found: {res['people_count']}")
            print(f"    - Tailored 2025 Outreach Drafts Created: {res['outreach_count']}")
            print(f"    - Excel Tracker: Updated recruitment_tracker.xlsx")

        elif args.command == "email-ingest":
            email_body = args.text
            if args.file and Path(args.file).exists():
                email_body = Path(args.file).read_text(encoding="utf-8")
            if not email_body:
                print("[-] Please provide email body via --text or --file")
                sys.exit(1)
            res = EmailIngest.process_email_text(db, email_body)
            ExcelSync.sync_database_to_excel(db)
            print(f"[OK] Email Processed!")
            print(f"    - Company: {res['company']}")
            print(f"    - Detected Intent: {res['intent']}")
            print(f"    - New Application Status: {res['new_status']}")
            print(f"    - Note: {res['note']}")

        elif args.command == "sync":
            print("\n[+] Synchronizing SQLite database with recruitment_tracker.xlsx...")
            path = ExcelSync.sync_database_to_excel(db)
            print(f"[OK] Successfully synced all 6 sheets to: {path}")

        elif args.command == "approve":
            pending = db.query(Outreach).filter(Outreach.status == "Pending Approval").all()
            if not pending:
                print("\n[OK] Approval queue is clear! No pending outreach drafts.")
                return

            print(f"\n--- Human Approval Queue ({len(pending)} pending items) ---")
            for item in pending:
                print("\n" + "=" * 60)
                print(f"Outreach ID : {item.outreach_id}")
                print(f"Recipient   : {item.person} ({item.company})")
                print(f"Type        : {item.message_type}")
                print(f"Target Role : {item.job}")
                print("-" * 60)
                print(item.message)
                print("=" * 60)

                choice = input("\n[A]pprove & Mark Sent | [R]eject | [S]kip | [Q]uit: ").strip().lower()
                if choice == "a":
                    item.status = "Approved"
                    print("-> Approved and marked Sent!")
                elif choice == "r":
                    item.status = "Rejected"
                    print("-> Rejected!")
                elif choice == "q":
                    break

            db.commit()
            ExcelSync.sync_database_to_excel(db)
            print("\n[OK] Queue updated and synced to Excel.")

        elif args.command == "report":
            report_text = Reporter.generate_weekly_report(db) if args.weekly else Reporter.generate_daily_report(db)
            try:
                print(report_text)
            except UnicodeEncodeError:
                print(report_text.encode("ascii", errors="ignore").decode("ascii"))

        elif args.command == "parse-resume":
            from agent.services.resume_parser import ResumeParser
            if args.file:
                target_file = Path(args.file)
            else:
                available = ResumeParser.get_available_resumes()
                if not available:
                    target_file = ResumeParser.create_sample_ats_resume()
                else:
                    target_file = available[0]

            print(f"\n[+] Parsing ATS .docx Resume: {target_file.name}")
            data = ResumeParser.parse_docx(target_file)
            print(f"    - Contact Email: {data.get('email') or 'Not found'}")
            print(f"    - Contact Phone: {data.get('phone') or 'Not found'}")
            print(f"    - LinkedIn: {data.get('linkedin') or 'Not found'}")
            print(f"    - Skills Extracted ({len(data.get('skills', []))}):")
            for s in data.get("skills", []):
                print(f"      * {s}")
            print(f"\n[OK] ATS Resume loaded successfully.")

        elif args.command == "server":
            print(f"\n[+] Starting Recruitment Intelligence Dashboard Server on http://{args.host}:{args.port}")
            print(f"    - Local Access: http://localhost:{args.port}")
            print(f"    - Mobile/Phone Access: Connect phone to same Wi-Fi and open http://<your-laptop-ip>:{args.port}")
            uvicorn.run("agent.api:app", host=args.host, port=args.port, reload=False)

        else:
            parser.print_help()

    finally:
        db.close()


if __name__ == "__main__":
    main()
