"""
Weekly Pipeline
---------------
Chains the full workflow into one command, meant to be triggered by a
Windows Scheduled Task (or cron, on Mac/Linux) on a recurring cadence:

  1. Re-run the evidence evaluation (evaluate.py's logic)
  2. Regenerate the HTML report (report_builder's logic)
  3. Email it to a fixed list of stakeholders

Requires the same environment variables as the rest of the project
(ANTHROPIC_API_KEY, GMAIL_ADDRESS, GMAIL_APP_PASSWORD) to already be set
system-wide (not just in one terminal session) — see the note in README
about setting these as permanent user environment variables for scheduled
runs to work, since a Scheduled Task does not inherit a terminal's
temporary session variables.

Usage:
    python src/run_pipeline.py
"""

import os
import sys
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import evaluate
import generate_report
from email_sender import send_report_email
from report_builder import build_report_html

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_PATH = os.path.join(BASE_DIR, "output", "pipeline_log.txt")

# Edit this list with the stakeholders who should receive the weekly report.
STAKEHOLDER_EMAILS = [
    "superethan18@gmail.com",  
]


def log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {message}"
    print(line)
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def main():
    log("Pipeline run started.")

    try:
        evaluate.main()
        log("Evidence evaluation complete.")
    except Exception as e:
        log(f"ERROR during evaluation: {e}")
        return

    try:
        results = generate_report.load_results()
        html = build_report_html(results)
        os.makedirs(os.path.dirname(generate_report.REPORT_PATH), exist_ok=True)
        with open(generate_report.REPORT_PATH, "w", encoding="utf-8") as f:
            f.write(html)
        log("Report regenerated.")
    except Exception as e:
        log(f"ERROR during report generation: {e}")
        return

    for address in STAKEHOLDER_EMAILS:
        try:
            send_report_email(address, html)
            log(f"Report emailed to {address}.")
        except Exception as e:
            log(f"ERROR emailing {address}: {e}")

    log("Pipeline run finished.")


if __name__ == "__main__":
    main()
