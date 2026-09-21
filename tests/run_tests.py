"""Standard library test runner for tests/test_agent.py."""

import os
import sys
import tempfile
from pathlib import Path

# Add project root
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

import tests.test_agent as t
from agent.database import Base, create_engine, sessionmaker

def run_all():
    print("=" * 60)
    print("Running Recruitment Intelligence Agent Automated Tests")
    print("=" * 60)

    # 1. Query Builder
    print("[1/9] Testing Query Builder...")
    t.test_query_builder()
    print("      [OK] Query Builder passed.")

    # 2. Signal Detector
    print("[2/9] Testing Signal Detector (Types A-F & Evidence)...")
    t.test_signal_detector()
    print("      [OK] Signal Detector passed.")

    # 3. Scorer
    print("[3/9] Testing 0-100 Relevance Scorer & Explainability...")
    t.test_scorer()
    print("      [OK] Scorer passed.")

    # 4. Deduplicator
    print("[4/9] Testing Deduplication Engine...")
    t.test_deduplicator()
    print("      [OK] Deduplicator passed.")

    # 5. Outreach Generator
    print("[5/9] Testing Outreach Generator (Anti-Spam, <300 char, Referrals)...")
    t.test_outreach_generator()
    print("      [OK] Outreach Generator passed.")

    # In-memory DB setup for database tests
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSession()

    # 6. Mode 1 Full Scan
    print("[6/9] Testing Mode 1: Full Recruitment Scan...")
    t.test_mode_1_full_scan(db)
    print("      [OK] Mode 1 Full Scan passed.")

    # 7. Mode 2 Company Scout
    print("[7/9] Testing Mode 2: Targeted Company Direct Connect...")
    t.test_mode_2_company_scout(db)
    print("      [OK] Mode 2 Company Scout passed.")

    # 8. Email Ingestion
    print("[8/9] Testing Email Ingestion & Status Auto-Update...")
    t.test_email_ingest(db)
    print("      [OK] Email Ingest passed.")

    # 9. Excel Sync (6 sheets) & Reports
    print("[9/9] Testing 6-Sheet Excel Sync & Reports...")
    with tempfile.TemporaryDirectory() as tmpdir:
        t.test_excel_sync(db, Path(tmpdir))
    t.test_reports(db)
    print("      [OK] Excel Sync (Jobs, People, Companies, Outreach, Signals, Dashboard) & Reports passed.")

    print("\n" + "=" * 60)
    print("ALL 9 TESTS PASSED SUCCESSFULLY! (100% Pass Rate)")
    print("=" * 60)

if __name__ == "__main__":
    run_all()
