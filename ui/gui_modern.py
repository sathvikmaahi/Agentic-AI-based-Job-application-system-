"""
ApplyAI - Modern Job Application Assistant
Beautiful, user-friendly interface with modern design
"""
import customtkinter as ctk
import tkinter as tk
from tkinter import font
from threading import Thread
import sys
import os
import yaml
import time

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import Core
from core import auth_manager
from core import apply_bot
from core import login
from core import url_builder

# Modern Color Scheme
COLORS = {
    "bg_dark": "#0F172A",      # Deep navy
    "bg_card": "#1E293B",      # Slate
    "primary": "#6366F1",      # Indigo
    "primary_hover": "#4F46E5", # Darker indigo
    "secondary": "#8B5CF6",    # Purple
    "accent": "#10B981",       # Emerald
    "accent_hover": "#059669",   # Darker emerald
    "warning": "#F59E0B",      # Amber
    "danger": "#EF4444",       # Red
    "text": "#F8FAFC",         # White
    "text_muted": "#94A3B8",   # Gray
    "border": "#334155",       # Border color
}

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

class ApplyAI(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Window Setup
        self.title("ApplyAI - Smart Job Application Assistant")
        self.geometry("1100x800")
        self.configure(fg_color=COLORS["bg_dark"])
        
        # Set theme
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("dark-blue")
        
        # Load Configs
        self.user_config = load_user_config()
        self.user_profile = load_user_profile()
        
        # Managers
        self.auth = auth_manager.AuthManager()
        
        # State
        self.authenticated_user = None
        self.is_running = False
        self.selected_job_board = "Dice"
        
        # Show Login
        self.show_login_screen()
    
    def show_login_screen(self):
        """Modern login screen with beautiful design"""
        # Clear window
        for widget in self.winfo_children():
            widget.destroy()
        
        # Main container
        self.login_frame = ctk.CTkFrame(self, fg_color=COLORS["bg_dark"])
        self.login_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        # Logo/Icon placeholder (using emoji for now)
        ctk.CTkLabel(
            self.login_frame, 
            text="🚀", 
            font=("SF Pro Display", 72),
            text_color=COLORS["primary"]
        ).pack(pady=(0, 10))
        
        # App Name
        ctk.CTkLabel(
            self.login_frame, 
            text="ApplyAI", 
            font=("SF Pro Display", 36, "bold"),
            text_color=COLORS["text"]
        ).pack()
        
        # Tagline
        ctk.CTkLabel(
            self.login_frame, 
            text="Smart Job Application Assistant", 
            font=("SF Pro Text", 14),
            text_color=COLORS["text_muted"]
        ).pack(pady=(0, 30))
        
        # Card container
        card = ctk.CTkFrame(
            self.login_frame, 
            fg_color=COLORS["bg_card"],
            corner_radius=20,
            border_width=1,
            border_color=COLORS["border"]
        )
        card.pack(padx=40, pady=20, fill="both")
        
        # User Selection Section
        ctk.CTkLabel(
            card, 
            text="👤 Select User", 
            font=("SF Pro Text", 12, "bold"),
            text_color=COLORS["text_muted"]
        ).pack(anchor="w", padx=25, pady=(20, 8))
        
        _names = list(auth_manager.AUTHORIZED_USERS.keys())
        if not _names:
            _names = ["UserOne"]
        self.user_var = ctk.StringVar(value=_names[0])
        self.combo_user = ctk.CTkComboBox(
            card, 
            values=_names,
            variable=self.user_var,
            width=300,
            height=40,
            font=("SF Pro Text", 14),
            dropdown_font=("SF Pro Text", 13),
            fg_color=COLORS["bg_dark"],
            border_color=COLORS["border"],
            button_color=COLORS["primary"],
            button_hover_color=COLORS["primary_hover"]
        )
        self.combo_user.pack(padx=25, pady=(0, 15))
        
        # Name Entry Section
        ctk.CTkLabel(
            card, 
            text="📝 Your Name", 
            font=("SF Pro Text", 12, "bold"),
            text_color=COLORS["text_muted"]
        ).pack(anchor="w", padx=25, pady=(10, 8))
        
        self.entry_name = ctk.CTkEntry(
            card, 
            placeholder_text="Enter your full name",
            width=300,
            height=40,
            font=("SF Pro Text", 14),
            fg_color=COLORS["bg_dark"],
            border_color=COLORS["border"],
            placeholder_text_color=COLORS["text_muted"]
        )
        if self.user_profile.get('full_name'):
            self.entry_name.insert(0, self.user_profile['full_name'])
        self.entry_name.pack(padx=25, pady=(0, 15))
        
        # Job Board Selection Section
        ctk.CTkLabel(
            card, 
            text="🎯 Select Job Board", 
            font=("SF Pro Text", 12, "bold"),
            text_color=COLORS["text_muted"]
        ).pack(anchor="w", padx=25, pady=(10, 8))
        
        # Job Board Radio Buttons
        board_frame = ctk.CTkFrame(card, fg_color="transparent")
        board_frame.pack(padx=25, pady=(0, 15), fill="x")
        
        self.job_board_var = ctk.StringVar(value="Dice")
        
        self.radio_dice = ctk.CTkRadioButton(
            board_frame, 
            text=" 🎲  Dice", 
            variable=self.job_board_var, 
            value="Dice",
            font=("SF Pro Text", 14),
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
            border_color=COLORS["border"]
        )
        self.radio_dice.pack(side="left", padx=(0, 30))
        
        self.radio_monster = ctk.CTkRadioButton(
            board_frame, 
            text=" 👾  Monster", 
            variable=self.job_board_var, 
            value="Monster",
            font=("SF Pro Text", 14),
            fg_color=COLORS["secondary"],
            hover_color=COLORS["primary_hover"],
            border_color=COLORS["border"]
        )
        self.radio_monster.pack(side="left")
        
        # Send OTP Button
        self.btn_send_otp = ctk.CTkButton(
            card, 
            text="Send OTP 📩", 
            width=300,
            height=45,
            font=("SF Pro Text", 15, "bold"),
            fg_color=COLORS["warning"], 
            hover_color="#D97706",
            text_color="white",
            corner_radius=10,
            command=self.on_send_otp
        )
        self.btn_send_otp.pack(padx=25, pady=(20, 10))
        
        # OTP Entry Section (Hidden initially)
        self.otp_frame = ctk.CTkFrame(card, fg_color="transparent")
        
        ctk.CTkLabel(
            self.otp_frame, 
            text="🔐 Enter Verification Code", 
            font=("SF Pro Text", 12, "bold"),
            text_color=COLORS["text_muted"]
        ).pack(anchor="w", pady=(15, 8))
        
        self.entry_otp = ctk.CTkEntry(
            self.otp_frame, 
            placeholder_text="6-digit code", 
            justify="center", 
            font=("SF Mono", 18, "bold"),
            width=300,
            height=45,
            fg_color=COLORS["bg_dark"],
            border_color=COLORS["border"],
            placeholder_text_color=COLORS["text_muted"]
        )
        self.entry_otp.pack(pady=(0, 15))
        
        self.btn_verify = ctk.CTkButton(
            self.otp_frame, 
            text="Verify & Continue →", 
            width=300,
            height=45,
            font=("SF Pro Text", 15, "bold"),
            fg_color=COLORS["accent"],
            hover_color=COLORS["accent_hover"],
            text_color="white",
            corner_radius=10,
            command=self.on_verify
        )
        self.btn_verify.pack(pady=(0, 10))
        
        # Footer
        ctk.CTkLabel(
            self.login_frame, 
            text="🔒 Secure • Automated • Efficient", 
            font=("SF Pro Text", 11),
            text_color=COLORS["text_muted"]
        ).pack(pady=(30, 10))
    
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
            self.show_success(f"OTP sent to {self.auth.get_email_for_user(user)}")
            self.btn_send_otp.configure(text="Resend Code", state="normal")
            self.otp_frame.pack(fill="x", padx=25, pady=10)
        else:
            self.show_error(msg)
            self.btn_send_otp.configure(state="normal", text="Send OTP 📩")
    
    def on_verify(self):
        """Verify OTP and show main screen"""
        code = self.entry_otp.get()
        user = self.user_var.get()
        
        if self.auth.verify_otp(user, code):
            self.authenticated_user = user
            self.selected_job_board = self.job_board_var.get()
            self.show_main_screen()
        else:
            self.show_error("Invalid or expired code. Please try again.")
    
    def show_main_screen(self):
        """Show modern main dashboard"""
        # Clear window
        for widget in self.winfo_children():
            widget.destroy()
        
        # Configure grid
        self.grid_columnconfigure(0, weight=0)  # Sidebar
        self.grid_columnconfigure(1, weight=1)  # Main content
        self.grid_rowconfigure(0, weight=1)
        
        # Sidebar
        self.sidebar = ctk.CTkFrame(
            self, 
            width=320,
            fg_color=COLORS["bg_card"],
            corner_radius=0
        )
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)
        
        # Sidebar Header
        header_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkLabel(
            header_frame, 
            text="🚀", 
            font=("SF Pro Display", 40),
            text_color=COLORS["primary"]
        ).pack(anchor="w")
        
        ctk.CTkLabel(
            header_frame, 
            text="ApplyAI", 
            font=("SF Pro Display", 20, "bold"),
            text_color=COLORS["text"]
        ).pack(anchor="w")
        
        # User Info Card
        user_card = ctk.CTkFrame(
            self.sidebar,
            fg_color=COLORS["bg_dark"],
            corner_radius=12,
            border_width=1,
            border_color=COLORS["border"]
        )
        user_card.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(
            user_card,
            text=f"👋 Welcome back,",
            font=("SF Pro Text", 11),
            text_color=COLORS["text_muted"]
        ).pack(anchor="w", padx=15, pady=(12, 0))
        
        ctk.CTkLabel(
            user_card,
            text=self.authenticated_user,
            font=("SF Pro Text", 16, "bold"),
            text_color=COLORS["text"]
        ).pack(anchor="w", padx=15, pady=(0, 12))
        
        # Job Board Badge
        board_color = COLORS["primary"] if self.selected_job_board == "Dice" else COLORS["secondary"]
        board_emoji = "🎲" if self.selected_job_board == "Dice" else "👾"
        
        board_badge = ctk.CTkFrame(
            user_card,
            fg_color=board_color,
            corner_radius=8
        )
        board_badge.pack(anchor="w", padx=15, pady=(0, 12))
        
        ctk.CTkLabel(
            board_badge,
            text=f"{board_emoji}  {self.selected_job_board}",
            font=("SF Pro Text", 11, "bold"),
            text_color="white"
        ).pack(padx=10, pady=4)
        
        # Credentials Section
        ctk.CTkLabel(
            self.sidebar,
            text="🔐 CREDENTIALS",
            font=("SF Pro Text", 11, "bold"),
            text_color=COLORS["text_muted"]
        ).pack(anchor="w", padx=20, pady=(20, 10))
        
        # Pre-fill credentials based on job board
        if self.selected_job_board == "Monster":
            creds_email = self.user_config.get('monster_credentials', {}).get('email', '')
            creds_password = self.user_config.get('monster_credentials', {}).get('password', '')
        else:
            creds_email = self.user_config.get('dice_credentials', {}).get('email', '')
            creds_password = self.user_config.get('dice_credentials', {}).get('password', '')
        
        if not creds_email:
            creds_email = self.user_profile.get('email', '')
        
        # Email Entry
        self.email_entry = ctk.CTkEntry(
            self.sidebar,
            placeholder_text="Email address",
            width=280,
            height=40,
            font=("SF Pro Text", 13),
            fg_color=COLORS["bg_dark"],
            border_color=COLORS["border"]
        )
        if creds_email:
            self.email_entry.insert(0, creds_email)
        self.email_entry.pack(padx=20, pady=5)
        
        # Password Entry
        self.pass_entry = ctk.CTkEntry(
            self.sidebar,
            placeholder_text="Password",
            show="•",
            width=280,
            height=40,
            font=("SF Pro Text", 13),
            fg_color=COLORS["bg_dark"],
            border_color=COLORS["border"]
        )
        if creds_password and creds_password != "your_monster_password_here":
            self.pass_entry.insert(0, creds_password)
        self.pass_entry.pack(padx=20, pady=5)
        
        # Search Settings Section
        ctk.CTkLabel(
            self.sidebar,
            text="🔍 JOB SEARCH",
            font=("SF Pro Text", 11, "bold"),
            text_color=COLORS["text_muted"]
        ).pack(anchor="w", padx=20, pady=(25, 10))
        
        # Keywords Entry
        self.key_entry = ctk.CTkEntry(
            self.sidebar,
            placeholder_text="Job keywords (e.g., Python Developer)",
            width=280,
            height=40,
            font=("SF Pro Text", 13),
            fg_color=COLORS["bg_dark"],
            border_color=COLORS["border"]
        )
        self.key_entry.pack(padx=20, pady=5)
        
        # Location Entry
        self.loc_var = ctk.StringVar(value="Remote")
        self.loc_entry = ctk.CTkEntry(
            self.sidebar,
            placeholder_text="Location",
            textvariable=self.loc_var,
            width=280,
            height=40,
            font=("SF Pro Text", 13),
            fg_color=COLORS["bg_dark"],
            border_color=COLORS["border"]
        )
        self.loc_entry.pack(padx=20, pady=5)
        
        # Options Frame
        options_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        options_frame.pack(fill="x", padx=20, pady=10)
        
        # Easy Apply Checkbox
        self.chk_easy = ctk.CTkCheckBox(
            options_frame,
            text=" Easy Apply Only",
            font=("SF Pro Text", 12),
            fg_color=COLORS["accent"],
            hover_color=COLORS["accent_hover"],
            border_color=COLORS["border"]
        )
        self.chk_easy.select()
        self.chk_easy.pack(anchor="w", pady=5)
        
        # Auto Apply Switch
        self.chk_auto = ctk.CTkSwitch(
            options_frame,
            text=" Auto-Apply Mode",
            font=("SF Pro Text", 12),
            progress_color=COLORS["accent"],
            button_color=COLORS["accent"],
            button_hover_color=COLORS["accent_hover"]
        )
        self.chk_auto.pack(anchor="w", pady=5)
        
        # Limit Selection
        limit_frame = ctk.CTkFrame(options_frame, fg_color="transparent")
        limit_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(
            limit_frame,
            text="Application Limit:",
            font=("SF Pro Text", 12),
            text_color=COLORS["text_muted"]
        ).pack(side="left")
        
        self.combo_limit = ctk.CTkComboBox(
            limit_frame,
            values=["5", "10", "15", "20", "30"],
            width=80,
            font=("SF Pro Text", 12),
            fg_color=COLORS["bg_dark"],
            border_color=COLORS["border"],
            button_color=COLORS["primary"]
        )
        self.combo_limit.set("10")
        self.combo_limit.pack(side="right")
        
        # Start Button
        self.btn_start = ctk.CTkButton(
            self.sidebar,
            text="🚀 Start Applying",
            height=50,
            font=("SF Pro Text", 16, "bold"),
            fg_color=COLORS["accent"],
            hover_color=COLORS["accent_hover"],
            text_color="white",
            corner_radius=12,
            command=self.on_start
        )
        self.btn_start.pack(fill="x", padx=20, pady=(30, 20))
        
        # Main Content Area
        self.main_frame = ctk.CTkFrame(
            self,
            fg_color=COLORS["bg_dark"],
            corner_radius=0
        )
        self.main_frame.grid(row=0, column=1, sticky="nsew")
        
        # Output Header
        output_header = ctk.CTkFrame(
            self.main_frame,
            fg_color=COLORS["bg_card"],
            corner_radius=0,
            height=60
        )
        output_header.pack(fill="x")
        output_header.pack_propagate(False)
        
        ctk.CTkLabel(
            output_header,
            text="📋 Activity Log",
            font=("SF Pro Text", 16, "bold"),
            text_color=COLORS["text"]
        ).pack(side="left", padx=20, pady=15)
        
        # Status indicator
        self.status_label = ctk.CTkLabel(
            output_header,
            text="● Ready",
            font=("SF Pro Text", 12),
            text_color=COLORS["accent"]
        )
        self.status_label.pack(side="right", padx=20, pady=15)
        
        # Output Text Area
        self.textbox = ctk.CTkTextbox(
            self.main_frame,
            font=("SF Mono", 12),
            text_color=COLORS["text"],
            fg_color=COLORS["bg_dark"],
            border_width=0,
            corner_radius=0,
            wrap="word"
        )
        self.textbox.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Configure text tags for colors
        self.textbox.tag_config("success", foreground=COLORS["accent"])
        self.textbox.tag_config("error", foreground=COLORS["danger"])
        self.textbox.tag_config("warning", foreground=COLORS["warning"])
        self.textbox.tag_config("info", foreground=COLORS["primary"])
        
        # Redirect stdout
        sys.stdout = StreamLogger(self.textbox)
        print(f"✅ Welcome to ApplyAI, {self.authenticated_user}!")
        print(f"🎯 Job Board: {self.selected_job_board}")
        print("💡 Enter your credentials and job search details, then click 'Start Applying'")
    
    def on_start(self):
        """Start job search"""
        email = self.email_entry.get()
        pwd = self.pass_entry.get()
        
        if not email or not pwd:
            self.show_error("Please enter your email and password.")
            return
        
        if not self.key_entry.get():
            self.show_error("Please enter job keywords.")
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
        
        self.btn_start.configure(state="disabled", text="⏳ Running...")
        self.status_label.configure(text="● Running", text_color=COLORS["warning"])
        Thread(target=self.run_search, args=(data,)).start()
    
    def run_search(self, data):
        """Run the job search"""
        try:
            job_board = self.selected_job_board.lower()
            print(f"\n{'='*50}")
            print(f"🚀 Starting job search on {self.selected_job_board}")
            print(f"{'='*50}\n")
            
            # Build URL
            print("📍 Generating search URL...")
            target_url = url_builder.build_job_url(
                job_board=job_board,
                keyword=data['keyword'],
                posted_date=data.get('posted_date', 'Last 7 days'),
                easy_apply=data['easy_apply'],
                employment_type=data.get('employment_type', 'Full time'),
                work_setting=data.get('work_setting', 'Remote'),
                location=data['location']
            )
            print(f"🔗 {target_url}\n")
            
            # Login
            print(f"🔐 Logging into {self.selected_job_board}...")
            driver = login.perform_job_board_login(job_board, data['email'], data['password'])
            
            # Navigate — Monster flags direct jumps to heavy search URLs; ease in + detect block page
            print("🌐 Opening search results...\n")
            if job_board == "monster":
                if not login.monster_open_search_results(driver, target_url):
                    print("⛔ Stopping: fix the block or try again later before auto-apply.")
                    return
            else:
                driver.get(target_url)
            
            # Auto Apply
            if data['auto_apply']:
                print(f"🤖 Auto-applying to {data['limit']} jobs...\n")
                apply_bot.start_applying(driver, max_limit=data['limit'], job_board=job_board)
            else:
                print(f"✅ Browser is open with {self.selected_job_board} search results.")
                
        except Exception as e:
            print(f"\n❌ Error: {e}\n")
        finally:
            self.btn_start.configure(state="normal", text="🚀 Start Applying")
            self.status_label.configure(text="● Ready", text_color=COLORS["accent"])
    
    def show_error(self, msg):
        """Show error dialog"""
        dialog = ctk.CTkToplevel(self)
        dialog.geometry("400x200")
        dialog.title("Error")
        dialog.configure(fg_color=COLORS["bg_dark"])
        
        ctk.CTkLabel(
            dialog, 
            text="❌ Error", 
            text_color=COLORS["danger"], 
            font=("SF Pro Display", 20, "bold")
        ).pack(pady=(20, 10))
        
        ctk.CTkLabel(
            dialog, 
            text=msg, 
            wraplength=350,
            font=("SF Pro Text", 13),
            text_color=COLORS["text"]
        ).pack(pady=10)
        
        ctk.CTkButton(
            dialog, 
            text="Close", 
            command=dialog.destroy,
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
            width=120,
            height=35
        ).pack(pady=20)
    
    def show_success(self, msg):
        """Show success dialog"""
        dialog = ctk.CTkToplevel(self)
        dialog.geometry("400x200")
        dialog.title("Success")
        dialog.configure(fg_color=COLORS["bg_dark"])
        
        ctk.CTkLabel(
            dialog, 
            text="✅ Success", 
            text_color=COLORS["accent"], 
            font=("SF Pro Display", 20, "bold")
        ).pack(pady=(20, 10))
        
        ctk.CTkLabel(
            dialog, 
            text=msg, 
            wraplength=350,
            font=("SF Pro Text", 13),
            text_color=COLORS["text"]
        ).pack(pady=10)
        
        ctk.CTkButton(
            dialog, 
            text="OK", 
            command=dialog.destroy,
            fg_color=COLORS["accent"],
            hover_color=COLORS["accent_hover"],
            width=120,
            height=35
        ).pack(pady=20)

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
    app = ApplyAI()
    app.mainloop()
