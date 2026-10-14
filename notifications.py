"""Booking notifications: always stored in-app, and also e-mailed when SMTP is configured.

Set these environment variables to enable real e-mail (otherwise e-mails are only logged
to the console, which is enough for a demo):
    MAIL_SERVER, MAIL_PORT (default 587), MAIL_USERNAME, MAIL_PASSWORD, MAIL_FROM
"""
import os
import smtplib
import logging
from email.message import EmailMessage
from extensions import db
from models import Notification

log = logging.getLogger('fixlocal.notify')


def _send_email(to_addr, subject, body):
    server = os.environ.get('MAIL_SERVER')
    if not server:
        log.warning('[email not configured] To: %s | %s | %s', to_addr, subject, body)
        return
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = os.environ.get('MAIL_FROM', os.environ.get('MAIL_USERNAME', 'noreply@fixlocal.local'))
    msg['To'] = to_addr
    msg.set_content(body)
    try:
        with smtplib.SMTP(server, int(os.environ.get('MAIL_PORT', 587)), timeout=10) as smtp:
            smtp.starttls()
            if os.environ.get('MAIL_USERNAME'):
                smtp.login(os.environ['MAIL_USERNAME'], os.environ.get('MAIL_PASSWORD', ''))
            smtp.send_message(msg)
    except Exception:  # never let a mail failure break a booking action
        log.exception('Failed to send email to %s', to_addr)


def notify(user, message, link=None):
    """Create an in-app notification (added to the session, caller commits) and email the user."""
    db.session.add(Notification(user_id=user.id, message=message, link=link))
    _send_email(user.email, 'FixLocal: ' + message[:60], message)
