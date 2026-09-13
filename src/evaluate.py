"""
Compliance Evidence Evaluator
------------------------------
Reads a set of controls (SOC 2 / ISO 27001 / AIUC-1) and a folder of
evidence documents, then asks Claude to assess whether the evidence
satisfies each control — returning a status, confidence, and rationale.

Usage:
    python evaluate.py
"""

import json
import os
import sys
import requests

sys.path.append(os.path.dirname(__file__))
from config import API_KEY, EVAL_MODEL, API_URL, ANTHROPIC_VERSION

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONTROLS_PATH = os.path.join(BASE_DIR, "data", "controls.json")
EVIDENCE_DIR = os.path.join(BASE_DIR, "data", "evidence")
OUTPUT_PATH = os.path.join(BASE_DIR, "output", "results.json")


def load_controls():
    with open(CONTROLS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def load_all_evidence():
    """Load every evidence file into one combined text blob with filenames
    labeled, so the model can see everything and decide what's relevant."""
    combined = []
    for fname in sorted(os.listdir(EVIDENCE_DIR)):
        fpath = os.path.join(EVIDENCE_DIR, fname)
        if os.path.isfile(fpath):
            with open(fpath, "r", encoding="utf-8") as f:
                content = f.read()
            combined.append(f"--- FILE: {fname} ---\n{content}")
    return "\n\n".join(combined)


def build_prompt(control, evidence_text):
    return f"""You are a compliance auditor assistant. Evaluate whether the
provided evidence satisfies the given control requirement.

CONTROL
ID: {control['id']}
Framework: {control['framework']}
Name: {control['name']}
Requirement: {control['requirement_text']}

EVIDENCE (multiple files, only some may be relevant)
{evidence_text}

Respond with ONLY a JSON object (no markdown fences, no preamble) in this
exact shape:
{{
  "status": "Met" | "Partial" | "Gap",
  "confidence": "High" | "Medium" | "Low",
  "rationale": "one to two sentence explanation citing which evidence file(s) informed this decision",
  "evidence_files_used": ["filename1", "filename2"]
}}

Be honest and specific. If evidence explicitly documents a known gap or
limitation, reflect that as "Gap" or "Partial" rather than "Met" — do not
be lenient. If no evidence is relevant to this control, mark it "Gap" with
confidence "High" and say so.

IMPORTANT — relevance discipline: only cite and factor in evidence files
that are directly relevant to THIS control's specific subject matter. Do
not pull in unrelated systems or issues just because they represent some
general risk elsewhere in the organization. For example, an unrelated AI
agent's data-handling gaps should NOT be cited as evidence against a
control about physical backup infrastructure or asset inventory, unless
the control's requirement text specifically concerns that system. Only
cross-reference another system's gap when the control's own requirement
text would reasonably cover that system (e.g., a general "system
monitoring" control MAY reasonably include the AI agent subsystem since
monitoring is meant to be organization-wide; a "backup and recovery"
control should not, unless backups are explicitly discussed in evidence).
"""


def call_claude(prompt, model):
    headers = {
        "x-api-key": API_KEY,
        "anthropic-version": ANTHROPIC_VERSION,
        "content-type": "application/json",
    }
    body = {
        "model": model,
        "max_tokens": 400,
        "messages": [{"role": "user", "content": prompt}],
    }
    resp = requests.post(API_URL, headers=headers, json=body, timeout=60)
    resp.raise_for_status()
    data = resp.json()
    text = "".join(
        block.get("text", "") for block in data.get("content", []) if block.get("type") == "text"
    )
    return text.strip()


def parse_json_response(raw_text, control_id):
    cleaned = raw_text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        if cleaned.startswith("json"):
            cleaned = cleaned[4:]
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        return {
            "status": "Error",
            "confidence": "Low",
            "rationale": f"Could not parse model response for {control_id}: {raw_text[:200]}",
            "evidence_files_used": [],
        }


def main():
    controls = load_controls()
    evidence_text = load_all_evidence()

    results = []
    print(f"Evaluating {len(controls)} controls against combined evidence...\n")

    for control in controls:
        prompt = build_prompt(control, evidence_text)
        raw = call_claude(prompt, EVAL_MODEL)
        parsed = parse_json_response(raw, control["id"])

        result = {
            "id": control["id"],
            "framework": control["framework"],
            "name": control["name"],
            "requirement_text": control["requirement_text"],
            **parsed,
        }
        results.append(result)

        status = result.get("status", "Unknown")
        print(f"[{status:8}] {control['id']:20} {control['name']}")

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print(f"\nDone. Results written to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
