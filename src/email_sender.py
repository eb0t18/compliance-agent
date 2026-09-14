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
    msg.set_content(
        "Your compliance readiness report is attached as an HTML file.\n\n"
        "Open the attachment in a web browser to view the full interactive "
        "report, including expandable rationale for each control."
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
