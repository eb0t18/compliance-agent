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
from datetime import date

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS_PATH = os.path.join(BASE_DIR, "output", "results.json")
REPORT_PATH = os.path.join(BASE_DIR, "output", "report.html")

FRAMEWORK_ORDER = ["SOC 2", "ISO 27001", "AIUC-1"]
FRAMEWORK_ACCENT = {
    "SOC 2": "#435672",
    "ISO 27001": "#6B7550",
    "AIUC-1": "#6E4A6E",
}
STATUS_COLOR = {
    "Met": "#2E6F4E",
    "Partial": "#A6790A",
    "Gap": "#9C3B2E",
    "Error": "#9C3B2E",
}
STATUS_WEIGHT = {"Met": 1.0, "Partial": 0.5, "Gap": 0.0, "Error": 0.0}


def load_results():
    with open(RESULTS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def group_by_framework(results):
    grouped = {fw: [] for fw in FRAMEWORK_ORDER}
    for r in results:
        grouped.setdefault(r["framework"], []).append(r)
    return grouped


def compute_readiness(results):
    if not results:
        return 0
    total = sum(STATUS_WEIGHT.get(r.get("status", "Gap"), 0) for r in results)
    return round((total / len(results)) * 100)


def render_control_row(r):
    status = r.get("status", "Error")
    color = STATUS_COLOR.get(status, "#9C3B2E")
    evidence = r.get("evidence_files_used", [])
    evidence_html = (
        "".join(f'<span class="ev-tag">{e}</span>' for e in evidence)
        if evidence
        else '<span class="ev-tag ev-none">no evidence found</span>'
    )
    return f"""
    <details class="control-row">
      <summary>
        <span class="control-id">{r['id']}</span>
        <span class="control-name">{r['name']}</span>
        <span class="status-pill" style="--pill-color:{color}">{status}</span>
      </summary>
      <div class="control-detail">
        <p class="requirement"><strong>Requirement:</strong> {r['requirement_text']}</p>
        <p class="rationale">{r.get('rationale', '')}</p>
        <div class="evidence-list">{evidence_html}</div>
      </div>
    </details>
    """


def render_framework_section(framework, controls):
    accent = FRAMEWORK_ACCENT.get(framework, "#435672")
    met = sum(1 for c in controls if c.get("status") == "Met")
    total = len(controls)
    rows = "".join(render_control_row(c) for c in controls)
    return f"""
    <section class="framework-section" style="--fw-accent:{accent}">
      <div class="framework-header">
        <h2>{framework}</h2>
        <span class="framework-count">{met} / {total} met</span>
      </div>
      {rows}
    </section>
    """


def render_summary_bar(results):
    total = len(results)
    counts = {"Met": 0, "Partial": 0, "Gap": 0}
    for r in results:
        s = r.get("status", "Gap")
        if s in counts:
            counts[s] += 1
        else:
            counts["Gap"] += 1
    segments = ""
    for status, count in counts.items():
        if count == 0:
            continue
        pct = (count / total) * 100
        segments += f'<div class="seg" style="width:{pct}%; background:{STATUS_COLOR[status]}" title="{status}: {count}"></div>'
    legend = "".join(
        f'<span class="legend-item"><i style="background:{STATUS_COLOR[s]}"></i>{s} ({c})</span>'
        for s, c in counts.items()
    )
    return f"""
    <div class="summary-bar">{segments}</div>
    <div class="summary-legend">{legend}</div>
    """


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Compliance Readiness Report — FormFlow Inc.</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Source+Serif+4:opsz,wght@8..60,400;8..60,600;8..60,700&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
  :root {{
    --paper: #F7F6F2;
    --ink: #20242B;
    --ink-soft: #55606B;
    --hairline: #D9D5CC;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0;
    background: var(--paper);
    color: var(--ink);
    font-family: 'Inter', system-ui, sans-serif;
    line-height: 1.5;
  }}
  .page {{
    max-width: 760px;
    margin: 0 auto;
    padding: 64px 32px 96px;
  }}
  .masthead {{
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    border-bottom: 2px solid var(--ink);
    padding-bottom: 24px;
    margin-bottom: 40px;
  }}
  .masthead h1 {{
    font-family: 'Source Serif 4', Georgia, serif;
    font-weight: 600;
    font-size: 30px;
    margin: 0 0 6px;
    letter-spacing: -0.01em;
  }}
  .masthead .subtitle {{
    color: var(--ink-soft);
    font-size: 14px;
  }}
  .stamp {{
    width: 92px;
    height: 92px;
    border-radius: 50%;
    border: 2.5px solid var(--ink);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    margin-left: 20px;
  }}
  .stamp .pct {{
    font-family: 'Source Serif 4', Georgia, serif;
    font-size: 26px;
    font-weight: 700;
    line-height: 1;
  }}
  .stamp .label {{
    font-size: 9px;
    letter-spacing: 0.04em;
    color: var(--ink-soft);
    margin-top: 2px;
  }}
  .summary-bar {{
    display: flex;
    width: 100%;
    height: 10px;
    border-radius: 3px;
    overflow: hidden;
    margin-top: 8px;
  }}
  .summary-legend {{
    display: flex;
    gap: 18px;
    margin: 10px 0 40px;
    font-size: 13px;
    color: var(--ink-soft);
  }}
  .summary-legend i {{
    display: inline-block;
    width: 9px;
    height: 9px;
    border-radius: 2px;
    margin-right: 6px;
    vertical-align: middle;
  }}
  .framework-section {{
    margin-bottom: 36px;
  }}
  .framework-header {{
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    border-bottom: 1.5px solid var(--fw-accent);
    padding-bottom: 6px;
    margin-bottom: 4px;
  }}
  .framework-header h2 {{
    font-family: 'Source Serif 4', Georgia, serif;
    font-weight: 600;
    font-size: 20px;
    color: var(--fw-accent);
    margin: 0;
  }}
  .framework-count {{
    font-size: 13px;
    color: var(--ink-soft);
  }}
  .control-row {{
    border-bottom: 1px solid var(--hairline);
  }}
  .control-row summary {{
    list-style: none;
    display: flex;
    align-items: center;
    gap: 14px;
    padding: 13px 2px;
    cursor: pointer;
  }}
  .control-row summary::-webkit-details-marker {{ display: none; }}
  .control-row summary::before {{
    content: '›';
    display: inline-block;
    font-size: 16px;
    color: var(--ink-soft);
    transition: transform 0.15s ease;
    width: 10px;
  }}
  .control-row[open] summary::before {{
    transform: rotate(90deg);
  }}
  .control-id {{
    font-size: 12.5px;
    color: var(--ink-soft);
    width: 130px;
    flex-shrink: 0;
  }}
  .control-name {{
    flex: 1;
    font-size: 14.5px;
    font-weight: 500;
  }}
  .status-pill {{
    font-size: 11.5px;
    font-weight: 600;
    color: var(--pill-color);
    border: 1.3px solid var(--pill-color);
    border-radius: 20px;
    padding: 2px 10px;
    flex-shrink: 0;
  }}
  .control-detail {{
    padding: 0 2px 18px 24px;
  }}
  .control-detail .requirement {{
    font-size: 13px;
    color: var(--ink-soft);
    margin: 0 0 10px;
  }}
  .control-detail .rationale {{
    font-size: 14px;
    margin: 0 0 12px;
  }}
  .evidence-list {{
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
  }}
  .ev-tag {{
    font-size: 11.5px;
    background: #EEECE5;
    border-radius: 4px;
    padding: 3px 8px;
    color: var(--ink-soft);
  }}
  .ev-none {{
    background: transparent;
    border: 1px dashed var(--hairline);
    font-style: italic;
  }}
  .footnote {{
    margin-top: 48px;
    padding-top: 20px;
    border-top: 1px solid var(--hairline);
    font-size: 12.5px;
    color: var(--ink-soft);
  }}
</style>
</head>
<body>
<div class="page">
  <div class="masthead">
    <div>
      <h1>Compliance Readiness Report</h1>
      <div class="subtitle">FormFlow Inc. — generated {gen_date}</div>
    </div>
    <div class="stamp">
      <div class="pct">{readiness}%</div>
      <div class="label">READY</div>
    </div>
  </div>

  {summary_bar}

  {sections}

  <div class="footnote">
    Generated by an evidence-mapping proof-of-concept. Findings are model-generated
    from a limited evidence set and are not a substitute for review by an
    accredited auditor. Frameworks referenced: SOC 2 (AICPA), ISO/IEC 27001:2022,
    and AIUC-1.
  </div>
</div>
</body>
</html>
"""


def main():
    results = load_results()
    grouped = group_by_framework(results)
    readiness = compute_readiness(results)
    summary_bar = render_summary_bar(results)
    sections = "".join(
        render_framework_section(fw, grouped[fw]) for fw in FRAMEWORK_ORDER if grouped[fw]
    )

    html = HTML_TEMPLATE.format(
        gen_date=date.today().strftime("%B %-d, %Y") if os.name != "nt" else date.today().strftime("%B %d, %Y"),
        readiness=readiness,
        summary_bar=summary_bar,
        sections=sections,
    )

    os.makedirs(os.path.dirname(REPORT_PATH), exist_ok=True)
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Report written to {REPORT_PATH}")


if __name__ == "__main__":
    main()
