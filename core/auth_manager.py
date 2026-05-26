import os
import smtplib
import random
import string
import time
from email.mime.text import MIMEText

from core.paths import load_authorized_users_map, load_smtp_config

_AUTHORIZED_USERS_CACHE = None


def _load_authorized_users():
    """Load OTP user map (real emails first, not template you@example.com)."""
    try:
        return load_authorized_users_map()
    except Exception as e:
        print(f"⚠️ Could not load authorized_users yaml: {e}")
        return {}


def get_authorized_users():
    global _AUTHORIZED_USERS_CACHE
    if _AUTHORIZED_USERS_CACHE is None:
        _AUTHORIZED_USERS_CACHE = _load_authorized_users()
    return _AUTHORIZED_USERS_CACHE


# OTP Storage (In-memory for session)
# Format: { "email": { "code": "123456", "timestamp": 123456789 } }
otp_storage = {}


class AuthManager:
    def __init__(self):
        cfg = load_smtp_config()
        self.sender_email = cfg["email"]
        self.sender_password = cfg["app_password"]
        self.smtp_host = cfg["host"]
        self.smtp_port = cfg["port"]

    def smtp_configured(self):
        return bool(self.sender_email and self.sender_password)

    def get_email_for_user(self, name):
        return get_authorized_users().get(name)

    def generate_otp(self, user_name):
        """Generates a 6-digit OTP and stores it."""
        email = self.get_email_for_user(user_name)
        if not email:
            return False, "User not found."

        code = "".join(random.choices(string.digits, k=6))
        otp_storage[email] = {"code": code, "timestamp": time.time()}
        return code, email

    def send_otp_email(self, user_name, smtp_password=None):
        """Generates OTP and emails it via Gmail SMTP."""
        password_to_use = (smtp_password if smtp_password else self.sender_password) or ""

        code, email = self.generate_otp(user_name)
        if not code:
            return False, "Invalid User"

        message_body = (
            f"Hello {user_name},\n\nYour Login OTP for Jobs Pro is: {code}\n\n"
            "This code expires in 5 minutes."
        )

        if not password_to_use or not self.sender_email:
            return False, (
                "OTP email is not configured. Add data/smtp_config.yaml "
                "(see smtp_config.template.yaml) or set JOBSPRO_SMTP_EMAIL and "
                "JOBSPRO_SMTP_APP_PASSWORD, then rebuild the app."
            )

        try:
            msg = MIMEText(message_body)
            msg["Subject"] = "Jobs Pro Login Verification"
            msg["From"] = self.sender_email
            msg["To"] = email

            with smtplib.SMTP_SSL(self.smtp_host, self.smtp_port) as server:
                server.login(self.sender_email, password_to_use)
                server.sendmail(self.sender_email, email, msg.as_string())

            return True, f"OTP sent successfully to {email}"

        except Exception as e:
            print(f"SMTP Error: {e}")
            return False, f"Failed to send email: {e}"

    def verify_otp(self, user_name, input_code):
        """Verifies the OTP for the given user."""
        email = self.get_email_for_user(user_name)
        if not email:
            return False

        record = otp_storage.get(email)
        if not record:
            return False

        if time.time() - record["timestamp"] > 300:
            return False

        if record["code"] == input_code:
            del otp_storage[email]
            return True

        return False
