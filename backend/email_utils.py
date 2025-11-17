import os
from email.message import EmailMessage
from typing import List, Tuple, Optional
import aiosmtplib

SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")
SMTP_FROM = os.getenv("SMTP_FROM", SMTP_USER or "noreply@example.com")
LEAD_TO = os.getenv("LEAD_TO", "bestdealmotors1626@gmail.com")


async def send_email(subject: str, html: str, attachments: Optional[List[Tuple[str, bytes, str]]] = None) -> bool:
    """
    Send an email.
    attachments: list of tuples (filename, bytes_content, mime_type)
    Returns True if sent or logged successfully.
    """
    msg = EmailMessage()
    msg["From"] = SMTP_FROM
    msg["To"] = LEAD_TO
    msg["Subject"] = subject
    msg.set_content("This is an HTML email. Please view in an HTML-capable client.")
    msg.add_alternative(html, subtype="html")

    for att in attachments or []:
        filename, content, mime_type = att
        maintype, subtype = (mime_type.split("/", 1) if "/" in mime_type else ("application", "octet-stream"))
        msg.add_attachment(content, maintype=maintype, subtype=subtype, filename=filename)

    # If SMTP not configured, just log and return True
    if not SMTP_HOST or not SMTP_USER or not SMTP_PASS:
        print("[EMAIL-LOG] Subject:", subject)
        print("[EMAIL-LOG] To:", LEAD_TO)
        print("[EMAIL-LOG] HTML:\n", html[:2000])
        if attachments:
            print(f"[EMAIL-LOG] {len(attachments)} attachment(s) logged")
        return True

    try:
        await aiosmtplib.send(
            msg,
            hostname=SMTP_HOST,
            port=SMTP_PORT,
            start_tls=True,
            username=SMTP_USER,
            password=SMTP_PASS,
        )
        return True
    except Exception as e:
        print("[EMAIL-ERROR]", e)
        return False
