import os
import smtplib
import random
import string
import time
from email.mime.text import MIMEText


def _load_authorized_users():
    """Load OTP user map from data/authorized_users.yaml if present, else template."""
    try:
        import yaml

        base = os.path.join(os.path.dirname(__file__), "..", "data")
        for name in ("authorized_users.yaml", "authorized_users.template.yaml"):
            path = os.path.join(base, name)
            if os.path.isfile(path):
                with open(path, encoding="utf-8") as f:
                    data = yaml.safe_load(f) or {}
                users = data.get("users")
                if isinstance(users, dict) and users:
                    return users
    except Exception as e:
        print(f"⚠️ Could not load authorized_users yaml: {e}")
    return {}


AUTHORIZED_USERS = _load_authorized_users()

# OTP Storage (In-memory for session)
# Format: { "email": { "code": "123456", "timestamp": 123456789 } }
otp_storage = {}


class AuthManager:
    def __init__(self):
        # Use environment variables — never commit app passwords to git
        self.sender_email = os.environ.get("JOBSPRO_SMTP_EMAIL", "").strip()
        self.sender_password = os.environ.get("JOBSPRO_SMTP_APP_PASSWORD", "").strip()

    def get_email_for_user(self, name):
        return AUTHORIZED_USERS.get(name)

    def generate_otp(self, user_name):
        """Generates a 6-digit OTP and stores it."""
        email = self.get_email_for_user(user_name)
        if not email:
            return False, "User not found."

        # Generate 6-digit code
        code = "".join(random.choices(string.digits, k=6))

        # Store
        otp_storage[email] = {"code": code, "timestamp": time.time()}

        return code, email

    def send_otp_email(self, user_name, smtp_password=None):
        """
        Generates OTP and attempts to email it.
        """
        password_to_use = (smtp_password if smtp_password else self.sender_password) or ""

        code, email = self.generate_otp(user_name)
        if not code:
            return False, "Invalid User"

        message_body = (
            f"Hello {user_name},\n\nYour Login OTP for Jobs Pro is: {code}\n\n"
            "This code expires in 5 minutes."
        )

        if not password_to_use or not self.sender_email:
            print("========================================")
            print(f" [SIMULATION] Sending Email to: {email}")
            print(f" [CONTENT] {message_body}")
            print("========================================")
            print(
                "ℹ️ Set JOBSPRO_SMTP_EMAIL and JOBSPRO_SMTP_APP_PASSWORD for real SMTP "
                "(Gmail app password)."
            )
            return True, f"[SIMULATION] OTP Sent to {email}.\n\nYour CODE is: {code}"

        try:
            msg = MIMEText(message_body)
            msg["Subject"] = "Jobs Pro Login Verification"
            msg["From"] = self.sender_email
            msg["To"] = email

            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(self.sender_email, password_to_use)
                server.sendmail(self.sender_email, email, msg.as_string())

            return True, f"OTP sent successfully to {email}"

        except Exception as e:
            print(f"SMTP Error: {e}")
            return False, f"Failed to email: {e}"

    def verify_otp(self, user_name, input_code):
        """Verifies the OTP for the given user."""
        email = self.get_email_for_user(user_name)
        if not email:
            return False

        record = otp_storage.get(email)
        if not record:
            return False  # No OTP generated

        if time.time() - record["timestamp"] > 300:
            return False

        if record["code"] == input_code:
            del otp_storage[email]
            return True

        return False
