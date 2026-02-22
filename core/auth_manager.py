import smtplib
import random
import string
import time
from email.mime.text import MIMEText

# User Configuration
AUTHORIZED_USERS = {
    "Praneeth": "pc@innovcentric.com",
    "Jonathan": "jt@innovcentric.com",
    "Naveen": "hiring@innovcentric.com",
    "Sathvik": "sankasathvik201@gmail.com",
}

# OTP Storage (In-memory for session)
# Format: { "email": { "code": "123456", "timestamp": 123456789 } }
otp_storage = {}

class AuthManager:
    def __init__(self):
        self.sender_email = "jt@innovcentric.com"
        # REAL APP PASSWORD PROVIDED BY USER
        self.sender_password = "qdxs mmnf ouwu blpj" 

    def get_email_for_user(self, name):
        return AUTHORIZED_USERS.get(name)

    def generate_otp(self, user_name):
        """Generates a 6-digit OTP and stores it."""
        email = self.get_email_for_user(user_name)
        if not email:
            return False, "User not found."

        # Generate 6-digit code
        code = ''.join(random.choices(string.digits, k=6))
        
        # Store
        otp_storage[email] = {
            "code": code,
            "timestamp": time.time()
        }
        
        return code, email

    def send_otp_email(self, user_name, smtp_password=None):
        """
        Generates OTP and attempts to email it.
        """
        # Use stored password if not explicitly passed
        password_to_use = smtp_password if smtp_password else self.sender_password

        code, email = self.generate_otp(user_name)
        if not code:
            return False, "Invalid User"

        message_body = f"Hello {user_name},\n\nYour Login OTP for Jobs Pro is: {code}\n\nThis code expires in 5 minutes."

        # --- SIMULATION MODE (Only if NO password available) ---
        if not password_to_use:
            print(f"========================================")
            print(f" [SIMULATION] Sending Email to: {email}")
            print(f" [CONTENT] {message_body}")
            print(f"========================================")
            # Return code in message for GUI simulation
            return True, f"[SIMULATION] OTP Sent to {email}.\n\nYour CODE is: {code}"

        # --- REAL SENDING MODE ---
        try:
            msg = MIMEText(message_body)
            msg['Subject'] = "Jobs Pro Login Verification"
            msg['From'] = self.sender_email
            msg['To'] = email

            # Connect to G-Suite / Gmail SMTP
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
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
            return False # No OTP generated
            
        # Check Expiry (5 mins)
        if time.time() - record['timestamp'] > 300:
            return False
            
        # Check Code
        if record['code'] == input_code:
            # Clear used OTP
            del otp_storage[email]
            return True
            
        return False
