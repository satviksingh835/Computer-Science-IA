import os
import smtplib
from email.mime.text import MIMEText

# Simple SMTP mailer using environment variables
SMTP_HOST = os.environ.get('SMTP_HOST', 'smtp.gmail.com')
SMTP_PORT = int(os.environ.get('SMTP_PORT', '587'))
SENDER = os.environ.get('EMAIL_SENDER')
PASSWORD = os.environ.get('EMAIL_PASSWORD')


def send_email_smtp(to_email, subject, body):
    """Send an email via SMTP. Returns True on success, False otherwise."""
    if not SENDER or not PASSWORD:
        raise RuntimeError('EMAIL_SENDER and EMAIL_PASSWORD must be set in environment')

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = SENDER
    msg['To'] = to_email

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=20) as server:
            server.starttls()
            server.login(SENDER, PASSWORD)
            server.sendmail(SENDER, [to_email], msg.as_string())
        return True
    except Exception as e:
        # caller should log the error
        return False

# Backwards-compat wrapper used by app.py
def send_absence_email_simple(student_email, class_name, date):
    subject = f"Absence Notification - {class_name}"
    body = f"""
    Dear Student,

    This is to inform you that you were marked absent for the class {class_name} on {date}.

    If you believe this is an error, please contact your teacher.

    Best regards,
    Attendance System
    """
    return send_email_smtp(student_email, subject, body)
