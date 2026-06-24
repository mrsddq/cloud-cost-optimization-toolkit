from __future__ import annotations

import json
import smtplib
import urllib.request
from email.message import EmailMessage


def send_slack_webhook(webhook_url: str, text: str) -> None:
    payload = json.dumps({"text": text}).encode("utf-8")
    request = urllib.request.Request(
        webhook_url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=10) as response:
        if response.status >= 300:
            raise RuntimeError(f"Slack webhook failed with status {response.status}")


def send_email_report(smtp_host: str, sender: str, recipient: str, subject: str, body: str) -> None:
    message = EmailMessage()
    message["From"] = sender
    message["To"] = recipient
    message["Subject"] = subject
    message.set_content(body)
    with smtplib.SMTP(smtp_host) as smtp:
        smtp.send_message(message)
