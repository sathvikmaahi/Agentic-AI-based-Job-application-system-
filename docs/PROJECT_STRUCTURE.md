# Jobs Pro (ApplyAI) — repository layout

```
jobspro-/                    # project root
├── README.md                # → docs/README.md
├── LICENSE
├── setup.py                 # copies YAML templates into data/ on first run
├── build_mac_app.sh         # PyInstaller → dist/ApplyAI.app + Desktop copy
├── core/                    # automation & backend logic
│   ├── auth_manager.py      # OTP; reads data/authorized_users*.yaml
│   ├── login.py             # Dice / Monster browser login
│   ├── apply_bot.py         # Easy Apply loops (Dice / Monster)
│   └── url_builder.py       # search URL builders
├── ui/                      # desktop UI (CustomTkinter)
│   ├── main.py              # entry: launches gui_modern
│   ├── gui_modern.py        # primary UI
│   └── gui_simple.py        # alternate UI
├── data/                    # local config (see .gitignore)
│   ├── *.template.yaml      # tracked templates
│   ├── authorized_users.template.yaml
│   └── authorized_users.yaml  # optional; gitignored — real OTP user emails
├── docs/
│   ├── README.md
│   ├── requirements.txt
│   ├── DEPLOYMENT_GUIDE.md
│   └── PROJECT_STRUCTURE.md
└── assets/                  # icons + generate_icon.py
```

Build artifacts (`build/`, `dist/`, `*.spec`), virtualenv (`jobspro_env/`), and secrets are not committed.

### Configuration (not in git)

- **OTP users:** copy `data/authorized_users.template.yaml` to `data/authorized_users.yaml` and set real emails.
- **SMTP (real OTP email):** set environment variables `JOBSPRO_SMTP_EMAIL` and `JOBSPRO_SMTP_APP_PASSWORD` (Gmail app password).
