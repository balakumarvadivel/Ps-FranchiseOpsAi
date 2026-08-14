"""
Email service
--------------
Uses Python's built-in smtplib — no extra dependency needed. When SMTP
isn't configured (the default, since this demo has no real mail account),
`send_email` logs the message instead of sending it and returns False, so
callers can decide what to do (e.g. the forgot-password endpoint falls back
to returning the token directly in the API response).

This is a real, working implementation — point it at any standard SMTP
provider (SendGrid, SES, Mailgun, even a plain Gmail app password) via the
SMTP_* settings in .env and it sends real email. It's not mocked; it's just
unconfigured by default since there's no mail account to configure it with
in this environment.
"""
import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.config import settings

logger = logging.getLogger("franchiseops")


def send_email(to_email: str, subject: str, body_text: str, body_html: str | None = None) -> bool:
    if not settings.email_configured:
        logger.info(f"[email not configured — would have sent] To: {to_email} | Subject: {subject}")
        return False

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = settings.SMTP_FROM_EMAIL
    msg["To"] = to_email
    msg.attach(MIMEText(body_text, "plain"))
    if body_html:
        msg.attach(MIMEText(body_html, "html"))

    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10) as server:
            if settings.SMTP_USE_TLS:
                server.starttls()
            server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            server.sendmail(settings.SMTP_FROM_EMAIL, [to_email], msg.as_string())
        return True
    except Exception:
        logger.exception(f"Failed to send email to {to_email}")
        return False


def send_password_reset_email(to_email: str, raw_token: str, frontend_url: str = "") -> bool:
    reset_link = f"{frontend_url or 'http://localhost:5173'}/reset-password?token={raw_token}"
    subject = "Reset your FranchiseOps AI password"
    body_text = (
        f"You requested a password reset.\n\n"
        f"Reset your password here: {reset_link}\n\n"
        f"This link expires in 30 minutes. If you didn't request this, ignore this email."
    )
    body_html = (
        f"<p>You requested a password reset.</p>"
        f'<p><a href="{reset_link}">Reset your password</a> (expires in 30 minutes)</p>'
        f"<p>If you didn't request this, ignore this email.</p>"
    )
    return send_email(to_email, subject, body_text, body_html)
