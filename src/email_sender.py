"""
Email Sender
------------
Sends the compliance report via Gmail SMTP. Requires two environment
variables to be set (same pattern as ANTHROPIC_API_KEY):

  GMAIL_ADDRESS       - the Gmail account sending the report
  GMAIL_APP_PASSWORD  - a 16-character app password (NOT your regular
                        Gmail password) generated at
                        https://myaccount.google.com/apppasswords
                        (requires 2-Step Verification to be enabled first)
"""

import os
import smtplib
from email.message import EmailMessage

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587


def send_report_email(to_address, html_content, subject="Compliance Readiness Report"):
    gmail_address = os.environ.get("GMAIL_ADDRESS")
    gmail_app_password = os.environ.get("GMAIL_APP_PASSWORD")

    if not gmail_address or not gmail_app_password:
        raise EnvironmentError(
            "GMAIL_ADDRESS and GMAIL_APP_PASSWORD must be set as environment "
            "variables before sending email."
        )

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = gmail_address
    msg["To"] = to_address
    msg.set_content
    (
        "Hello, \n\n"
        "Attached is a compliance readiness report evaluating current evidence "
        "against controls from SOC 2, ISO 27001, and AIUC-1 (the AI agent "
        "security, safety, and accountability standard).\n\n"
        "Open the attached HTML file in a web browser to view the full "
        "interactive report. It includes:\n\n"
        "- An overall readiness score, plus a breakdown by framework\n"
        "- Every control organized by domain, with a Met / Partial / Gap "
        "status for each\n"
        "- Click any control to expand it and see the specific evidence "
        "reviewed and the rationale behind its status\n"
        "- Particular attention to AIUC-1's Accountability domain (audit "
        "logging, named ownership of AI system changes), given how directly "
        "it relates to tamper-evident, auditable AI output\n\n"
        "This report reflects a proof-of-concept evidence-mapping process, "
        "not a substitute for a formal audit — findings are meant to "
        "highlight where a deeper review would be most valuable."
    )
    msg.add_attachment(
        html_content.encode("utf-8"),
        maintype="text",
        subtype="html",
        filename="compliance_report.html",
    )

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        server.login(gmail_address, gmail_app_password)
        server.send_message(msg)
