# 🚀 ApplyAI - Smart Job Application Assistant

ApplyAI is an intelligent automation tool that helps you apply to jobs on Dice and Monster job boards effortlessly. Save hours of manual work and let ApplyAI handle the repetitive application process for you.

![ApplyAI Icon](assets/icon.png)

## ✨ Features

- 🤖 **Automated Job Applications** - Apply to multiple jobs with one click
- 🎯 **Multi-Platform Support** - Works with Dice and Monster job boards
- 🔐 **Secure OTP Authentication** - Protected access for authorized users
- 📱 **Modern UI** - Beautiful, user-friendly interface
- ⚡ **Fast & Efficient** - Optimized for speed with anti-detection measures
- 🎨 **Easy Apply Filter** - Only applies to jobs with one-click apply option
- 📊 **Activity Logging** - Real-time progress tracking

## 🖥️ System Requirements

### macOS
- macOS 10.14 (Mojave) or later
- Apple Silicon (M1/M2) or Intel processor
- Chrome browser installed
- Internet connection

### Windows (Coming Soon)
- Windows 10 or later
- Chrome browser installed
- Internet connection

## 📥 Installation

### macOS

1. **Download** the latest release from [Releases](https://github.com/YOUR_USERNAME/ApplyAI/releases)
2. **Extract** the ZIP file
3. **Right-click** on `ApplyAI.app` → Click "Open"
4. If you see a security warning, click "Open" in System Preferences → Security & Privacy
5. **Enter your credentials** and start applying!

⚠️ **Note**: macOS may show "Unidentified Developer" warning. This is normal for unsigned apps. Right-click → Open to proceed.

## 🚀 How to Use

1. **Launch ApplyAI**
2. **Select your user** from the dropdown
3. **Enter your full name**
4. **Choose Job Board**: Dice 🎲 or Monster 👾
5. **Click "Send OTP"** and check your email
6. **Enter the 6-digit code** and verify
7. **Enter your job board credentials** (Dice/Monster login)
8. **Set job search keywords** (e.g., "Python Developer")
9. **Choose location** (e.g., "Remote", "New York")
10. **Enable "Auto-Apply"** to automatically apply to jobs
11. **Set application limit** (recommended: 10-20 per session)
12. **Click "Start Applying"** and let ApplyAI work! 🤖

## 🔐 Security

- ✅ OTP-based authentication for app access
- ✅ Credentials stored locally on your machine only
- ✅ No data sent to external servers
- ✅ Anti-detection measures to protect your accounts

## ⚙️ Configuration

### Setting Up Credentials

Before using ApplyAI, update your credentials in the data files:

**`data/user_config.yaml`**:
```yaml
dice_credentials:
  email: "your-email@example.com"
  password: "your-password"
  remember_me: true

monster_credentials:
  email: "your-email@example.com"
  password: "your-password"
  remember_me: true
```

**`data/user_profile.yaml`**:
```yaml
full_name: "Your Name"
email: "your-email@example.com"
phone: "123-456-7890"
# ... other profile information
```

**OTP login (who receives the code):** copy `data/authorized_users.template.yaml` to `data/authorized_users.yaml` and set each display name → email. This file is not committed to git.

**SMTP (to send real OTP emails):** set `JOBSPRO_SMTP_EMAIL` and `JOBSPRO_SMTP_APP_PASSWORD` (Gmail app password). If unset, the app runs OTP in simulation mode and prints the code to the log.

See `docs/PROJECT_STRUCTURE.md` for the full repository layout.

## 🛠️ Building from Source

### Prerequisites
- Python 3.10+
- pip
- virtualenv

### Build Steps

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/ApplyAI.git
cd ApplyAI

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r docs/requirements.txt

# Run the app
python ui/main.py

# Build macOS app
bash build_mac_app.sh
```

## 📝 Important Notes

- **Rate Limiting**: ApplyAI includes delays to avoid being blocked by job boards
- **Application Limits**: Recommended max 20-30 applications per session
- **Job Board Policies**: Use responsibly and in accordance with job board Terms of Service
- **IP Blocking**: If you apply too aggressively, job boards may temporarily block your IP

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) for modern UI
- Powered by [Selenium](https://www.selenium.dev/) for browser automation
- Icon designed with 💜 for job seekers

## 📞 Support

If you encounter any issues or have questions:

1. Check the [Deployment Guide](docs/DEPLOYMENT_GUIDE.md)
2. Create an issue on GitHub
3. Contact: your-email@example.com

## ⚠️ Disclaimer

ApplyAI is designed to assist with job applications. Users are responsible for:
- Ensuring their use complies with job board Terms of Service
- Reviewing applications before submission
- Using the tool responsibly and ethically

The developers are not responsible for any account restrictions or bans resulting from misuse.

---

**Happy Job Hunting! 🎉**

Made with ❤️ to help job seekers save time and land their dream jobs.
