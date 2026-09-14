"""
Report Generator
-----------------
Reads output/results.json and produces output/report.html — a styled,
self-contained audit-style report suitable for a live demo.

Usage:
    python src/generate_report.py
"""

import json
import os
import sys

sys.path.append(os.path.dirname(__file__))
from report_builder import build_report_html

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS_PATH = os.path.join(BASE_DIR, "output", "results.json")
REPORT_PATH = os.path.join(BASE_DIR, "output", "report.html")


def load_results():
    with open(RESULTS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    results = load_results()
    html = build_report_html(results)

    os.makedirs(os.path.dirname(REPORT_PATH), exist_ok=True)
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Report written to {REPORT_PATH}")


if __name__ == "__main__":
    main()
