# Compliance Evidence Evaluator

A proof-of-concept agent that evaluates whether an organization's evidence
satisfies compliance controls across **SOC 2**, **ISO 27001**, and
**AIUC-1** (the emerging AI agent security/safety/reliability standard) —
producing a status, confidence level, and cited rationale for each control.

## Why this exists

Compliance evidence review is typically a manual, spreadsheet-driven process:
someone reads each control, digs through policy docs and system exports, and
decides whether the evidence supports it. This is slow, inconsistent, and
doesn't scale — especially as AI-specific frameworks like AIUC-1 add new,
fast-evolving requirements (AIUC-1 alone updates quarterly) on top of
existing SOC 2 / ISO 27001 programs.

This matters most for vertical AI agents operating inside regulated
workflows — where an agent's output doesn't just inform a user, it feeds a
record that a customer, auditor, or downstream institution relies on as
accurate. In that context, accountability and tamper-evidence aren't nice
extras; they're the trust layer that makes the product usable at all, which
is why this project treats AIUC-1's Accountability domain (tamper-evident
audit logging, named ownership of agent decisions) as a first-class concern
alongside the more commonly discussed Data & Privacy controls.

This tool automates the first pass: it reads real control language and a
folder of evidence documents, and returns a structured determination with
rationale — flagging clear gaps rather than rubber-stamping everything as met.

## Project structure

```
compliance-agent/
├── data/
│   ├── controls.json           # SOC 2, ISO 27001, and AIUC-1 controls
│   └── evidence/                # mock evidence documents
├── src/
│   ├── config.py                 # API key + model configuration
│   ├── evaluate.py               # core evaluation script
│   ├── report_builder.py         # shared HTML rendering (used by both below)
│   ├── generate_report.py        # writes a static report.html file
│   ├── app.py                    # live server: report + working "Send Report" button
│   └── email_sender.py           # Gmail SMTP sending logic
├── output/
│   └── results.json              # generated after running evaluate.py
└── README.md
```

## Setup

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Set your Anthropic API key as an environment variable:
   ```
   export ANTHROPIC_API_KEY="sk-ant-..."
   ```
   (Get a key at console.anthropic.com — this is separate from a claude.ai login.)

3. Run the evaluator:
   ```
   python src/evaluate.py
   ```

4. Results are written to `output/results.json`.

5. Generate the static visual report:
   ```
   python src/generate_report.py
   ```
   This produces `output/report.html` — open it in any browser.

## Live server with email delivery

Instead of (or in addition to) the static report, you can run a live local
server that adds a working "Send Report" button — type an email address,
click send, and the report is emailed as an HTML attachment.

**One-time setup (Gmail app password):**
1. Enable 2-Step Verification on the Gmail account you want to send from, if
   not already on: myaccount.google.com/security
2. Generate an app password at myaccount.google.com/apppasswords (choose
   "Mail" as the app). This gives you a 16-character password — this is
   NOT your normal Gmail password, and it's the only thing that gets stored
   as an environment variable, so your real password is never exposed.
3. Set two more environment variables:
   ```
   export GMAIL_ADDRESS="youraddress@gmail.com"
   export GMAIL_APP_PASSWORD="xxxxxxxxxxxxxxxx"
   ```

**Run the server:**
```
python src/app.py
```
Then open **http://127.0.0.1:5000** in a browser. Type a recipient email
into the bar at the top and click **Send Report**.

**Security note:** this is a local demo server, not a production
deployment — there's no login/authentication on the `/send` route, so
anyone who can reach this URL on your machine could trigger a send. That's
fine for a local demo on your own laptop; don't deploy this as-is to a
public server.

## Notes / limitations

This is a proof-of-concept demonstrating the pattern, not a production audit
tool. Real-world use would require:
- Human review of every determination before it's treated as authoritative
- Ingesting evidence directly from source systems rather than static files
- Validation against an accredited auditor's judgment
- A versioned control set that tracks AIUC-1's quarterly updates
- Real authentication on the email-send route, and a transactional email
  provider (rather than personal Gmail) for anything beyond a demo

## Frameworks referenced

- SOC 2 Trust Services Criteria (AICPA)
- ISO/IEC 27001:2022 Annex A
- AIUC-1 (Artificial Intelligence Underwriting Company) — see aiuc-1.com
