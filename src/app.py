"""
Live Report Server
------------------
Serves the compliance report at http://127.0.0.1:5000 with a working
"Send Report" form at the top — type an email address, click send, and
the report is emailed as an HTML attachment via Gmail SMTP.

This is a local demo server, not a production deployment: there is no
authentication on the /send route, so anyone who can reach this URL on
your machine could trigger an email send. Fine for a local demo on your
own laptop; do not expose this to the internet as-is.

Usage:
    python src/app.py
    then open http://127.0.0.1:5000 in a browser
"""

import json
import os
import sys

from flask import Flask, redirect, request, url_for

sys.path.append(os.path.dirname(__file__))
from email_sender import send_report_email
from report_builder import build_report_html

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS_PATH = os.path.join(BASE_DIR, "output", "results.json")

app = Flask(__name__)

SEND_FORM_STYLE = """
  .send-bar {
    background: #EEECE5;
    border-radius: 8px;
    padding: 14px 18px;
    margin-bottom: 28px;
    display: flex;
    align-items: center;
    gap: 10px;
    flex-wrap: wrap;
  }
  .send-bar input[type=email] {
    flex: 1;
    min-width: 200px;
    padding: 8px 12px;
    border: 1px solid var(--hairline);
    border-radius: 6px;
    font-family: 'Inter', sans-serif;
    font-size: 14px;
  }
  .send-bar button {
    background: var(--ink);
    color: var(--paper);
    border: none;
    border-radius: 6px;
    padding: 9px 16px;
    font-size: 14px;
    font-weight: 600;
    cursor: pointer;
  }
  .send-bar button:hover {
    opacity: 0.9;
  }
  .send-banner {
    background: #E4EDE7;
    border: 1px solid #2E6F4E;
    color: #2E6F4E;
    border-radius: 6px;
    padding: 10px 14px;
    margin-bottom: 20px;
    font-size: 13.5px;
  }
  .send-banner.error {
    background: #F5E6E3;
    border-color: #9C3B2E;
    color: #9C3B2E;
  }
"""


def load_results():
    with open(RESULTS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def render_send_bar(message=None, error=False):
    banner = ""
    if message:
        css_class = "send-banner error" if error else "send-banner"
        banner = f'<div class="{css_class}">{message}</div>'
    return f"""
    {banner}
    <form class="send-bar" method="POST" action="/send">
      <input type="email" name="to_address" placeholder="stakeholder@company.com" required>
      <button type="submit">Send Report</button>
    </form>
    """


@app.route("/")
def index():
    results = load_results()
    sent = request.args.get("sent")
    error = request.args.get("error")

    if sent:
        top = render_send_bar(f"Report sent to {sent}.")
    elif error:
        top = render_send_bar(f"Couldn't send report: {error}", error=True)
    else:
        top = render_send_bar()

    html = build_report_html(results, extra_style=SEND_FORM_STYLE, extra_body_top=top)
    return html


@app.route("/send", methods=["POST"])
def send():
    to_address = request.form.get("to_address", "").strip()
    if not to_address:
        return redirect(url_for("index", error="No email address provided"))

    results = load_results()
    # Render a clean copy (no send-bar/banner) for the actual emailed report.
    html = build_report_html(results)

    try:
        send_report_email(to_address, html)
    except Exception as e:
        return redirect(url_for("index", error=str(e)))

    return redirect(url_for("index", sent=to_address))


if __name__ == "__main__":
    app.run(debug=True, port=5000)
