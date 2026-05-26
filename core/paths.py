import os
import shutil
import sys


def app_support_dir():
    return os.path.join(os.path.expanduser("~"), "Library", "Application Support", "ApplyAI")


def bundled_data_dirs():
    """Project + .app bundle locations (checked before Application Support)."""
    candidates = []

    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    candidates.append(os.path.join(project_root, "data"))

    if getattr(sys, "frozen", False):
        exe = getattr(sys, "executable", "")
        if exe:
            candidates.append(
                os.path.normpath(
                    os.path.join(os.path.dirname(exe), "..", "Resources", "data")
                )
            )
        meipass = getattr(sys, "_MEIPASS", None)
        if meipass:
            candidates.append(os.path.join(meipass, "data"))

    seen = set()
    ordered = []
    for path in candidates:
        norm = os.path.normpath(path)
        if norm not in seen:
            seen.add(norm)
            ordered.append(norm)
    return ordered


def data_dir_candidates():
    """General config search order (credentials, profile, etc.)."""
    dirs = bundled_data_dirs()
    asp = app_support_dir()
    if asp not in dirs:
        dirs = dirs + [asp]
    return dirs


def find_data_file(filename):
    for base in data_dir_candidates():
        path = os.path.join(base, filename)
        if os.path.isfile(path):
            return path
    return None


def _read_users_yaml(path):
    import yaml

    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    users = data.get("users")
    return users if isinstance(users, dict) else {}


def _has_real_emails(users):
    return any(
        isinstance(email, str) and email.strip() and "@example.com" not in email.lower()
        for email in users.values()
    )


def load_authorized_users_map():
    """
    Load name → email for OTP. Prefer real emails from bundled/project yaml,
    not Application Support copy seeded from template (you@example.com).
    """
    fallback = {}

    for base in bundled_data_dirs():
        path = os.path.join(base, "authorized_users.yaml")
        if not os.path.isfile(path):
            continue
        users = _read_users_yaml(path)
        if not users:
            continue
        if _has_real_emails(users):
            return users
        if not fallback:
            fallback = users

    asp = app_support_dir()
    os.makedirs(asp, exist_ok=True)
    asp_path = os.path.join(asp, "authorized_users.yaml")
    if os.path.isfile(asp_path):
        users = _read_users_yaml(asp_path)
        if users and _has_real_emails(users):
            return users
        if users and not fallback:
            fallback = users
        # Replace stale placeholder file from an older app version
        if users and not _has_real_emails(users):
            for base in bundled_data_dirs():
                src = os.path.join(base, "authorized_users.yaml")
                if os.path.isfile(src) and _has_real_emails(_read_users_yaml(src)):
                    shutil.copy2(src, asp_path)
                    return _read_users_yaml(asp_path)

    if fallback:
        return fallback

    for base in bundled_data_dirs():
        path = os.path.join(base, "authorized_users.template.yaml")
        if os.path.isfile(path):
            users = _read_users_yaml(path)
            if users:
                return users

    return {}


def load_smtp_config():
    """
    SMTP settings for OTP email. Env vars override file.
    Returns dict: email, app_password, host, port (empty strings if unset).
    """
    host = "smtp.gmail.com"
    port = 465
    email = os.environ.get("JOBSPRO_SMTP_EMAIL", "").strip()
    password = os.environ.get("JOBSPRO_SMTP_APP_PASSWORD", "").strip()

    if not email or not password:
        path = find_data_file("smtp_config.yaml")
        if path:
            try:
                import yaml

                with open(path, encoding="utf-8") as f:
                    data = yaml.safe_load(f) or {}
                block = data.get("smtp") if isinstance(data.get("smtp"), dict) else data
                email = (block.get("email") or block.get("sender_email") or "").strip()
                password = (
                    block.get("app_password")
                    or block.get("password")
                    or ""
                ).strip()
                host = (block.get("host") or host).strip() or host
                port = int(block.get("port") or port)
            except Exception as e:
                print(f"⚠️ Could not load smtp_config.yaml: {e}")

    password = password.replace(" ", "")
    return {
        "email": email,
        "app_password": password,
        "host": host,
        "port": port,
    }


def ensure_app_support_authorized_users():
    """Create Application Support config from bundle or template if nothing exists yet."""
    asp = app_support_dir()
    os.makedirs(asp, exist_ok=True)
    dest = os.path.join(asp, "authorized_users.yaml")
    if os.path.isfile(dest):
        return dest

    for name in ("authorized_users.yaml", "authorized_users.template.yaml"):
        for base in bundled_data_dirs():
            src = os.path.join(base, name)
            if os.path.isfile(src):
                shutil.copy2(src, dest)
                return dest
    return None
