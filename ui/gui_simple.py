"""
Simplified Jobs Pro GUI - Clean and minimal
Uses YAML for configuration
"""
import customtkinter as ctk
import tkinter as tk
from threading import Thread
import sys
import os
import yaml

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import Core
from core import auth_manager
from core import apply_bot
from core import login
from core import url_builder

# Configuration
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# Load user config from YAML
def load_user_config():
    """Load user configuration from YAML file"""
    config_paths = [
        os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'user_config.yaml'),
        os.path.join(os.path.dirname(__file__), '..', 'data', 'user_config.yaml'),
    ]
    for path in config_paths:
        if os.path.exists(path):
            with open(path, 'r') as f:
                return yaml.safe_load(f) or {}
    return {}

def load_user_profile():
    """Load user profile from YAML file"""
    config_paths = [
        os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'user_profile.yaml'),
        os.path.join(os.path.dirname(__file__), '..', 'data', 'user_profile.yaml'),
    ]
    for path in config_paths:
        if os.path.exists(path):
            with open(path, 'r') as f:
                return yaml.safe_load(f) or {}
    return {}

class JobsProSimple(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Window Setup
        self.title("Jobs Pro - Simple")
        self.geometry("900x700")
        
        # Load Configs
        self.user_config = load_user_config()
        self.user_profile = load_user_profile()
        
        # Managers
        self.auth = auth_manager.AuthManager()
        
        # State
        self.authenticated_user = None
        self.is_running = False
        
        # Show Login
        self.show_login_screen()
    
    def show_login_screen(self):
        """Simple login screen with job board selection"""
        self.frame_auth = ctk.CTkFrame(self, corner_radius=15)
        self.frame_auth.place(relx=0.5, rely=0.5, anchor="center")
        
        ctk.CTkLabel(self.frame_auth, text="Jobs Pro", font=("Roboto", 28, "bold")).pack(pady=20, padx=40)
        
        # User Selection
        ctk.CTkLabel(self.frame_auth, text="Select User").pack(anchor="w", padx=20)
        _names = list(auth_manager.AUTHORIZED_USERS.keys())
        if not _names:
            _names = ["UserOne"]
        self.user_var = ctk.StringVar(value=_names[0])
        self.combo_user = ctk.CTkComboBox(
            self.frame_auth, 
            values=_names,
            variable=self.user_var
        )
        self.combo_user.pack(fill="x", padx=20, pady=(0, 15))
        
        # Name Entry
        ctk.CTkLabel(self.frame_auth, text="Your Name").pack(anchor="w", padx=20)
        self.entry_name = ctk.CTkEntry(self.frame_auth, placeholder_text="Enter your full name")
        # Pre-fill from YAML if available
        if self.user_profile.get('full_name'):
            self.entry_name.insert(0, self.user_profile['full_name'])
        self.entry_name.pack(fill="x", padx=20, pady=(0, 15))
        
        # Job Board Selection - NEW!
        ctk.CTkLabel(self.frame_auth, text="Select Job Board", font=("Roboto", 12, "bold"), text_color="#3B82F6").pack(anchor="w", padx=20)
        self.job_board_var = ctk.StringVar(value="Dice")
        self.frame_job_board = ctk.CTkFrame(self.frame_auth, fg_color="transparent")
        self.frame_job_board.pack(fill="x", padx=20, pady=(0, 15))
        
        # Dice Radio Button
        self.radio_dice = ctk.CTkRadioButton(
            self.frame_job_board, 
            text="🎲 Dice", 
            variable=self.job_board_var, 
            value="Dice",
            command=self.on_job_board_change
        )
        self.radio_dice.pack(side="left", padx=(0, 20))
        
        # Monster Radio Button
        self.radio_monster = ctk.CTkRadioButton(
            self.frame_job_board, 
            text="👾 Monster", 
            variable=self.job_board_var, 
            value="Monster",
            command=self.on_job_board_change
        )
        self.radio_monster.pack(side="left")
        
        # Send OTP Button
        self.btn_send_otp = ctk.CTkButton(
            self.frame_auth, 
            text="Send OTP 📩", 
            fg_color="#EAB308", 
            hover_color="#CA8A04", 
            command=self.on_send_otp
        )
        self.btn_send_otp.pack(fill="x", padx=20, pady=10)
        
        # OTP Entry (Hidden initially)
        self.frame_otp = ctk.CTkFrame(self.frame_auth, fg_color="transparent")
        self.entry_otp = ctk.CTkEntry(
            self.frame_otp, 
            placeholder_text="Enter 6-digit Code", 
            justify="center", 
            font=("Mono", 16)
        )
        self.btn_verify = ctk.CTkButton(
            self.frame_otp, 
            text="Verify & Login 🔓", 
            command=self.on_verify
        )
        self.btn_verify.pack(fill="x", pady=10, side="bottom")
        self.entry_otp.pack(fill="x", pady=5, side="top")
    
    def on_job_board_change(self):
        """Handle job board selection change"""
        selected = self.job_board_var.get()
        print(f"Selected job board: {selected}")
    
    def on_send_otp(self):
        """Send OTP to user"""
        user = self.user_var.get()
        name = self.entry_name.get()
        
        if not name:
            self.show_error("Please enter your name first.")
            return
        
        self.btn_send_otp.configure(state="disabled", text="Sending...")
        self.update()
        
        success, msg = self.auth.send_otp_email(user)
        
        if success:
            self.show_info(f"OTP Sent to {self.auth.get_email_for_user(user)}")
            self.btn_send_otp.configure(text="Resend Code", state="normal")
            self.frame_otp.pack(fill="x", padx=20, pady=10)
        else:
            self.show_error(msg)
            self.btn_send_otp.configure(state="normal", text="Send OTP 📩")
    
    def on_verify(self):
        """Verify OTP and show main screen"""
        code = self.entry_otp.get()
        user = self.user_var.get()
        
        if self.auth.verify_otp(user, code):
            self.authenticated_user = user
            self.show_main_screen()
        else:
            self.show_error("Invalid or Expired Code.")
    
    def show_main_screen(self):
        """Show simple main screen"""
        self.frame_auth.destroy()
        
        # Store selected job board
        self.selected_job_board = self.job_board_var.get()
        
        # Main Layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Sidebar
        self.sidebar = ctk.CTkFrame(self, width=300)
        self.sidebar.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        ctk.CTkLabel(self.sidebar, text="Jobs Pro", font=("Roboto", 20, "bold")).pack(pady=20)
        ctk.CTkLabel(self.sidebar, text=f"Welcome, {self.authenticated_user}", text_color="gray").pack()
        
        # Show selected job board badge
        board_color = "#3B82F6" if self.selected_job_board == "Dice" else "#8B5CF6"  # Blue for Dice, Purple for Monster
        ctk.CTkLabel(
            self.sidebar, 
            text=f"🎯 {self.selected_job_board}", 
            font=("Roboto", 12, "bold"),
            text_color=board_color,
            fg_color=("gray85", "gray25"),
            corner_radius=8,
            padx=10,
            pady=5
        ).pack(pady=10)
        
        # Credentials - Dynamic based on job board
        creds_text = f"{self.selected_job_board} Credentials"
        ctk.CTkLabel(self.sidebar, text=creds_text, font=("Roboto", 14, "bold")).pack(anchor="w", padx=20, pady=(20, 5))
        
        # Pre-fill from YAML based on selected job board
        if self.selected_job_board == "Monster":
            creds_email = self.user_config.get('monster_credentials', {}).get('email', '')
            creds_password = self.user_config.get('monster_credentials', {}).get('password', '')
        else:
            creds_email = self.user_config.get('dice_credentials', {}).get('email', '')
            creds_password = self.user_config.get('dice_credentials', {}).get('password', '')
        
        # Fallback to user_profile email if no credentials found
        if not creds_email:
            creds_email = self.user_profile.get('email', '')
        
        self.email_entry = ctk.CTkEntry(self.sidebar, placeholder_text="Email")
        if creds_email:
            self.email_entry.insert(0, creds_email)
        self.email_entry.pack(fill="x", padx=20, pady=2)
        
        self.pass_entry = ctk.CTkEntry(self.sidebar, placeholder_text="Password", show="*")
        if creds_password and creds_password != "your_monster_password_here":
            self.pass_entry.insert(0, creds_password)
        self.pass_entry.pack(fill="x", padx=20, pady=2)
        
        # Search Settings
        ctk.CTkLabel(self.sidebar, text="Job Search", font=("Roboto", 14, "bold")).pack(anchor="w", padx=20, pady=(20, 5))
        
        self.key_entry = ctk.CTkEntry(self.sidebar, placeholder_text="Job Keywords (e.g., Python Developer)")
        self.key_entry.pack(fill="x", padx=20, pady=2)
        
        # Location
        self.loc_var = ctk.StringVar(value="Remote")
        ctk.CTkEntry(self.sidebar, placeholder_text="Location", textvariable=self.loc_var).pack(fill="x", padx=20, pady=2)
        
        # Options
        self.chk_easy = ctk.CTkCheckBox(self.sidebar, text="Easy Apply Only")
        self.chk_easy.select()
        self.chk_easy.pack(anchor="w", padx=20, pady=5)
        
        self.chk_auto = ctk.CTkSwitch(self.sidebar, text="Auto-Apply")
        self.chk_auto.pack(anchor="w", padx=20, pady=5)
        
        ctk.CTkLabel(self.sidebar, text="Limit:").pack(anchor="w", padx=20)
        self.combo_limit = ctk.CTkComboBox(self.sidebar, values=["5", "10", "15", "20"], width=80)
        self.combo_limit.set("10")
        self.combo_limit.pack(anchor="w", padx=20, pady=5)
        
        # Start Button
        self.btn_start = ctk.CTkButton(
            self.sidebar, 
            text="🚀 START", 
            height=40,
            fg_color="#10B981",
            hover_color="#059669",
            command=self.on_start
        )
        self.btn_start.pack(fill="x", padx=20, pady=20)
        
        # Log Output
        self.log_frame = ctk.CTkFrame(self, fg_color="#111827")
        self.log_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        
        ctk.CTkLabel(self.log_frame, text="Output", anchor="w").pack(fill="x", padx=10, pady=5)
        self.textbox = ctk.CTkTextbox(self.log_frame, font=("Consolas", 12), text_color="#22C55E", fg_color="black")
        self.textbox.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Redirect stdout
        sys.stdout = StreamLogger(self.textbox)
        print(f"✅ Welcome, {self.authenticated_user}. Ready to search jobs!")
    
    def on_start(self):
        """Start job search"""
        email = self.email_entry.get()
        pwd = self.pass_entry.get()
        
        if not email or not pwd:
            self.show_error("Please enter Email and Password.")
            return
        
        if not self.key_entry.get():
            self.show_error("Please enter Job Keywords.")
            return
        
        data = {
            'email': email,
            'password': pwd,
            'keyword': self.key_entry.get(),
            'location': self.loc_var.get(),
            'easy_apply': self.chk_easy.get() == 1,
            'auto_apply': self.chk_auto.get() == 1,
            'limit': int(self.combo_limit.get()),
        }
        
        self.btn_start.configure(state="disabled", text="Running...")
        Thread(target=self.run_search, args=(data,)).start()
    
    def run_search(self, data):
        """Run the job search"""
        try:
            job_board = self.selected_job_board.lower()
            print(f"Starting job search on {self.selected_job_board}...")
            
            # Build URL using the universal builder
            print("Generating search URL...")
            target_url = url_builder.build_job_url(
                job_board=job_board,
                keyword=data['keyword'],
                posted_date=data.get('posted_date', 'Last 7 days'),
                easy_apply=data['easy_apply'],
                employment_type=data.get('employment_type', 'Full time'),
                work_setting=data.get('work_setting', 'Remote'),
                location=data['location']
            )
            print(f"🎯 URL: {target_url}")
            
            # Login using the universal login function
            print(f"Logging in to {self.selected_job_board}...")
            driver = login.perform_job_board_login(job_board, data['email'], data['password'])
            
            # Navigate
            print("Opening search results...")
            driver.get(target_url)
            
            # Auto Apply with job board parameter
            if data['auto_apply']:
                print(f"Auto-applying to {data['limit']} jobs on {self.selected_job_board}...")
                apply_bot.start_applying(driver, max_limit=data['limit'], job_board=job_board)
            else:
                print(f" Browser is open with {self.selected_job_board} search results.")
                
        except Exception as e:
            print(f"Error: {e}")
        finally:
            self.btn_start.configure(state="normal", text="🚀 START")
    
    def show_error(self, msg):
        """Show error dialog"""
        dialog = ctk.CTkToplevel(self)
        dialog.geometry("300x150")
        ctk.CTkLabel(dialog, text="Error", text_color="red", font=("Bold", 16)).pack(pady=10)
        ctk.CTkLabel(dialog, text=msg, wraplength=250).pack(pady=10)
        ctk.CTkButton(dialog, text="Close", command=dialog.destroy).pack()
    
    def show_info(self, msg):
        """Show info dialog"""
        dialog = ctk.CTkToplevel(self)
        dialog.geometry("300x150")
        ctk.CTkLabel(dialog, text=" Success", text_color="green", font=("Bold", 16)).pack(pady=10)
        ctk.CTkLabel(dialog, text=msg, wraplength=250).pack(pady=10)
        ctk.CTkButton(dialog, text="OK", command=dialog.destroy).pack()

class StreamLogger:
    """Logger to redirect output to textbox"""
    def __init__(self, textbox):
        self.textbox = textbox
    def write(self, msg):
        if msg.strip():
            self.textbox.insert("end", msg + "\n")
            self.textbox.see("end")
    def flush(self):
        pass

if __name__ == "__main__":
    app = JobsProSimple()
    app.mainloop()
