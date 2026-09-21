#!/usr/bin/env python3
"""
Root entry point for the Job & Recruitment Intelligence Agent.
Usage:
  python agent.py scan
  python agent.py company-connect "Company Name"
  python agent.py email-ingest --text "email content"
  python agent.py sync
  python agent.py approve
  python agent.py report --daily
  python agent.py server
"""

import sys
from agent.cli import main

if __name__ == "__main__":
    main()
