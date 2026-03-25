import os
import ssl
import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager


def _configure_ssl_certificates():
    """
    Use certifi's CA bundle for urllib/SSL. Fixes macOS and PyInstaller builds where
    HTTPS to fetch ChromeDriver fails with CERTIFICATE_VERIFY_FAILED.
    """
    try:
        import certifi

        ca = certifi.where()
        if not ca or not os.path.isfile(ca):
            return
        os.environ["SSL_CERT_FILE"] = ca
        os.environ["REQUESTS_CA_BUNDLE"] = ca
        os.environ["CURL_CA_BUNDLE"] = ca

        def _default_https_context():
            return ssl.create_default_context(cafile=ca)

        ssl._create_default_https_context = _default_https_context
    except Exception:
        pass


_configure_ssl_certificates()


def monster_page_looks_blocked(driver) -> bool:
    """True if Monster shows the 'Access is temporarily restricted' interstitial."""
    try:
        src = driver.page_source or ""
        if "Access is temporarily restricted" in src:
            return True
        low = src.lower()
        if "unusual activity from your device or network" in low:
            return True
        if "automated (bot) activity" in low:
            return True
    except Exception:
        pass
    return False


def _print_monster_block_help(driver=None):
    print("\n❌ Monster blocked this browser session (their anti-bot / risk system).")
    print("   This is decided on their servers (IP + behavior + automation signals).")
    print("   Try: another network (phone hotspot), wait 30–60 min, or use Monster")
    print("   manually in regular Chrome; ensure the app uses undetected-chromedriver (no SSL fallback).")
    if driver:
        try:
            import re

            src = driver.page_source or ""
            m = re.search(r"Reference ID:\s*([a-f0-9-]+)", src, re.I)
            if m:
                print(f"   Reference ID: {m.group(1)}")
        except Exception:
            pass


def _monster_home_warmup(driver):
    """Visit homepage first so the session starts like a normal browser entry."""
    print("🏠 Opening Monster homepage first (reduces 'deep link' bot signals)...")
    driver.get("https://www.monster.com/")
    time.sleep(random.uniform(1.2, 2.2))
    if monster_page_looks_blocked(driver):
        _print_monster_block_help(driver)
        raise RuntimeError("Monster blocked before login.")
    try:
        driver.execute_script("window.scrollTo(0, Math.min(500, document.body.scrollHeight));")
        time.sleep(random.uniform(0.35, 0.75))
    except Exception:
        pass


def monster_open_search_results(driver, target_url) -> bool:
    """
    Ease into the search URL: open /jobs, pause, then load the full query.
    Returns False if Monster shows the restriction page (caller should not auto-apply).
    """
    if monster_page_looks_blocked(driver):
        _print_monster_block_help(driver)
        return False

    print("🌐 Easing into job search (Monster watches for scripted jumps)...")
    driver.get("https://www.monster.com/jobs")
    time.sleep(random.uniform(2.5, 5.0))

    if monster_page_looks_blocked(driver):
        _print_monster_block_help(driver)
        return False

    try:
        driver.execute_script("window.scrollTo(0, 350);")
        time.sleep(random.uniform(1.0, 2.2))
    except Exception:
        pass

    print("🔍 Loading your filtered search...")
    driver.get(target_url)
    time.sleep(random.uniform(2.0, 3.5))

    if monster_page_looks_blocked(driver):
        _print_monster_block_help(driver)
        return False
    return True


def _create_monster_chrome_driver():
    """
    Monster uses strong bot detection. Prefer undetected-chromedriver (patches ChromeDriver).
    Falls back to stock Selenium + webdriver-manager with lighter flags.
    """
    try:
        import undetected_chromedriver as uc

        options = uc.ChromeOptions()
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-popup-blocking")
        # Visible, normal-sized window — minimized / odd sizes can score as automation
        options.add_argument("--window-size=1280,840")
        options.add_argument("--lang=en-US,en")
        # Do NOT add --disable-web-security, --disable-features=..., or a fake user-agent;
        # those often worsen fingerprint scores vs real Chrome.

        driver = uc.Chrome(options=options, use_subprocess=True)
        driver.set_page_load_timeout(90)
        return driver, True
    except Exception as e:
        print(f"⚠️ undetected-chromedriver failed ({e}); falling back to standard Chrome.")
        err = str(e)
        if "CERTIFICATE" in err or "SSL" in err:
            print(
                "   SSL tip: pip install --upgrade certifi; on macOS also run "
                "“Install Certificates.command” from your Python folder in Applications."
            )

    options = webdriver.ChromeOptions()
    options.add_argument("--disable-notifications")
    options.add_argument("--window-size=1280,840")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.set_page_load_timeout(90)
    driver.execute_cdp_cmd(
        "Page.addScriptToEvaluateOnNewDocument",
        {
            "source": """
                Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
                window.chrome = { runtime: {} };
            """
        },
    )
    return driver, False

def human_type_and_click(driver, element, text):
    """
    Types into an element with short random delays (fast enough for daily use; still not one instant burst).
    """
    driver.execute_script("arguments[0].click();", element)
    time.sleep(random.uniform(0.08, 0.18))

    element.clear()
    for char in text:
        element.send_keys(char)
        time.sleep(random.uniform(0.01, 0.035))

    time.sleep(random.uniform(0.08, 0.2))

def perform_login(email, password):
    """
    Launches the browser, logs into Dice.com, and returns the driver.
    """
    print("🚀 Launching Browser for Login...")
    
    # Setup Chrome options with anti-detection measures
    options = webdriver.ChromeOptions()
    options.add_argument("--start-minimized") # Open in Taskbar (Silent)
    options.add_argument("--disable-notifications") # Block popup alerts
    
    # Anti-detection measures
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    # User agent to look like regular Chrome
    options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    # Automatically handle the ChromeDriver installation
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    # Execute CDP commands to prevent detection
    driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
        'source': '''
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            window.chrome = { runtime: {} };
        '''
    })

    try:
        # 1. Load the login page
        print("🔗 Navigating to login page...")
        driver.get("https://www.dice.com/dashboard/login")

        # 2. Enter Email
        print("👤 Entering email (Human Style)...")
        email_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "email"))
        )
        human_type_and_click(driver, email_input, email)

        # 3. Click Continue
        print("➡️ Clicking Continue...")
        continue_btn = driver.find_element(By.CSS_SELECTOR, "button[data-testid='sign-in-button']")
        # Use JS click to bypass overlays (like cookie banners)
        driver.execute_script("arguments[0].click();", continue_btn)

        # 4. Enter Password
        print("🔑 Entering password (Human Style)...")
        password_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "password"))
        )
        human_type_and_click(driver, password_input, password)

        # 5. Click Sign In
        print("✅ Clicking Sign In...")
        time.sleep(random.uniform(0.2, 0.45))
        sign_in_btn = driver.find_element(By.CSS_SELECTOR, "button[data-testid='submit-password']")
        # Use JS click here as well for robustness
        driver.execute_script("arguments[0].click();", sign_in_btn)

        # 6. Wait for Home Feed
        print("⏳ Waiting for Dashboard...")
        WebDriverWait(driver, 20).until(
            EC.url_contains("home-feed")
        )
        print("🎉 Login Successful!")
        
        return driver

    except Exception as e:
        print(f"❌ Login Failed: {e}")
        # Keep browser open for debugging if needed, or close it:
        # driver.quit() 
        raise e


def fast_type_and_click(driver, element, text):
    """
    Fast typing with slight randomization to avoid bot detection.
    """
    import random
    
    # Click the element
    driver.execute_script("arguments[0].click();", element)
    time.sleep(random.uniform(0.1, 0.3))
    
    # Clear field
    element.clear()
    time.sleep(random.uniform(0.1, 0.2))
    
    # Type with very small random delays (not too fast to trigger bot detection)
    for char in text:
        element.send_keys(char)
        time.sleep(random.uniform(0.01, 0.05))  # 10-50ms between keystrokes
    
    time.sleep(random.uniform(0.2, 0.4))


def perform_monster_login(email, password):
    """
    Launches the browser, logs into Monster.com, and returns the driver.
    Uses undetected-chromedriver when available (stronger vs bot detection than stock Selenium).
    """
    print("🚀 Launching Browser for Monster Login...")
    driver, _using_uc = _create_monster_chrome_driver()

    try:
        time.sleep(random.uniform(0.25, 0.55))
        _monster_home_warmup(driver)

        # 1. Load Monster — profile often redirects to sign-in when logged out
        print("🔗 Navigating to Monster login page...")
        driver.get("https://www.monster.com/profile/detail")
        time.sleep(random.uniform(0.7, 1.3))
        if monster_page_looks_blocked(driver):
            _print_monster_block_help(driver)
            raise RuntimeError("Monster blocked on profile/login page.")

        # Check if we're already on profile (logged in)
        cur = (driver.current_url or "").lower()
        if "profile/detail" in cur and "sign-in" not in cur and "login" not in cur:
            print("🎉 Already logged in to Monster!")
            return driver

        # 2. Sign In link if still on marketing / home shell
        try:
            sign_in_links = driver.find_elements(By.LINK_TEXT, "Sign In") or driver.find_elements(
                By.XPATH, "//a[contains(text(), 'Sign In')]"
            )
            if sign_in_links:
                print("➡️ Clicking Sign In link...")
                driver.execute_script("arguments[0].click();", sign_in_links[0])
                time.sleep(random.uniform(0.35, 0.65))
        except Exception:
            pass

        # 3. Email
        print("👤 Entering email...")
        email_input = None
        email_selectors = [
            (By.ID, "email"),
            (By.NAME, "email"),
            (By.CSS_SELECTOR, "input[type='email']"),
            (By.XPATH, "//input[@placeholder*='email' or @placeholder*='Email']"),
            (By.CSS_SELECTOR, "input[autocomplete='username']"),
        ]
        for by, selector in email_selectors:
            try:
                email_input = WebDriverWait(driver, 12).until(
                    EC.element_to_be_clickable((by, selector))
                )
                break
            except Exception:
                continue

        if not email_input:
            raise Exception("Could not find email input field (blocked or wrong page?)")

        human_type_and_click(driver, email_input, email)
        time.sleep(random.uniform(0.12, 0.28))

        # 4. Continue / Next
        print("➡️ Clicking Continue...")
        continue_clicked = False
        for xpath in (
            "//button[@type='submit']",
            "//input[@type='submit']",
            "//button[contains(normalize-space(.),'Continue')]",
            "//button[contains(normalize-space(.),'Next')]",
            "//*[@role='button'][contains(normalize-space(.),'Continue')]",
        ):
            try:
                for btn in driver.find_elements(By.XPATH, xpath):
                    if btn.is_displayed():
                        driver.execute_script("arguments[0].click();", btn)
                        time.sleep(random.uniform(0.35, 0.65))
                        continue_clicked = True
                        break
                if continue_clicked:
                    break
            except Exception:
                continue

        # 5. Password
        print("🔑 Entering password...")
        password_input = None
        password_selectors = [
            (By.ID, "password"),
            (By.NAME, "password"),
            (By.CSS_SELECTOR, "input[type='password']"),
            (By.CSS_SELECTOR, "input[autocomplete='current-password']"),
        ]
        for by, selector in password_selectors:
            try:
                password_input = WebDriverWait(driver, 15).until(
                    EC.element_to_be_clickable((by, selector))
                )
                break
            except Exception:
                continue

        if not password_input:
            raise Exception("Could not find password input field")

        human_type_and_click(driver, password_input, password)
        time.sleep(random.uniform(0.15, 0.35))

        # 6. Sign In
        print("✅ Clicking Sign In...")
        signin_clicked = False
        for xpath in (
            "//button[@type='submit']",
            "//input[@type='submit']",
            "//button[contains(normalize-space(.),'Sign In')]",
            "//button[contains(normalize-space(.),'Log In')]",
            "//button[contains(normalize-space(.),'Login')]",
        ):
            try:
                for btn in driver.find_elements(By.XPATH, xpath):
                    if btn.is_displayed():
                        driver.execute_script("arguments[0].click();", btn)
                        time.sleep(random.uniform(0.9, 1.5))
                        signin_clicked = True
                        break
                if signin_clicked:
                    break
            except Exception:
                continue

        # 7. Wait for redirect away from auth host/path
        print("⏳ Waiting for Monster session...")
        time.sleep(random.uniform(1.2, 2.0))

        cur = (driver.current_url or "").lower()
        if "sign-in" not in cur and "login" not in cur:
            print("🎉 Monster Login Successful!")
            return driver

        time.sleep(1.2)
        cur = (driver.current_url or "").lower()
        if "sign-in" not in cur and "login" not in cur:
            print("🎉 Monster Login Successful!")
            return driver

        raise Exception(
            "Login may have failed or Monster blocked automation. "
            "Try: pip install undetected-chromedriver && use normal (not minimized) window; "
            "complete any CAPTCHA manually in the opened browser."
        )

    except Exception as e:
        print(f"❌ Monster Login Failed: {e}")
        raise e


def perform_job_board_login(job_board, email, password):
    """
    Universal login function that routes to the appropriate job board.
    
    Args:
        job_board: 'dice' or 'monster'
        email: User email
        password: User password
    
    Returns:
        Selenium webdriver instance
    """
    if job_board.lower() == "monster":
        return perform_monster_login(email, password)
    else:
        return perform_login(email, password)