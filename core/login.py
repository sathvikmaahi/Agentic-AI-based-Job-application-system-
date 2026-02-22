import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager

def human_type_and_click(driver, element, text):
    """
    Simulates typing text into an element. Keys are sent securely and directly.
    Clicks are performed via Javascript to ensure they work even if the window is minimized.
    """
    # 1. Click (Javascript - Safe for Minimized)
    driver.execute_script("arguments[0].click();", element)
    time.sleep(random.uniform(0.3, 0.7)) 
    
    # 2. Type character by character
    element.clear()
    for char in text:
        element.send_keys(char)
        # Random delay between keystrokes (50ms to 200ms)
        time.sleep(random.uniform(0.05, 0.2)) 
    
    # Optional: Small pause after finishing typing
    time.sleep(random.uniform(0.5, 1.0))

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
        # Small pause to ensure animation/focus transition is done
        time.sleep(1) 
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
    Uses anti-detection measures to avoid bot detection.
    """
    print("🚀 Launching Browser for Monster Login...")
    
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
    
    # Additional privacy options
    options.add_argument("--disable-web-security")
    options.add_argument("--disable-features=IsolateOrigins,site-per-process")
    
    # Automatically handle the ChromeDriver installation
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    # Execute CDP commands to prevent detection
    driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
        'source': '''
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });
            window.chrome = { runtime: {} };
        '''
    })

    try:
        # 1. Load the login page
        print("🔗 Navigating to Monster login page...")
        driver.get("https://www.monster.com/profile/detail")
        
        # Wait for page to load and check if already logged in
        time.sleep(2)
        
        # Check if we're already on profile page (already logged in)
        if "profile/detail" in driver.current_url and "sign-in" not in driver.current_url:
            print("🎉 Already logged in to Monster!")
            return driver

        # 2. Click Sign In link if on landing page
        try:
            sign_in_links = driver.find_elements(By.LINK_TEXT, "Sign In") or driver.find_elements(By.XPATH, "//a[contains(text(), 'Sign In')]")
            if sign_in_links:
                print("➡️ Clicking Sign In link...")
                driver.execute_script("arguments[0].click();", sign_in_links[0])
                time.sleep(1)
        except:
            pass  # May already be on login page

        # 3. Enter Email - FAST
        print("👤 Entering email...")
        try:
            # Try different selectors for email input
            email_selectors = [
                (By.ID, "email"),
                (By.NAME, "email"),
                (By.CSS_SELECTOR, "input[type='email']"),
                (By.XPATH, "//input[@placeholder*='email' or @placeholder*='Email']"),
            ]
            
            email_input = None
            for by, selector in email_selectors:
                try:
                    email_input = WebDriverWait(driver, 3).until(
                        EC.presence_of_element_located((by, selector))
                    )
                    break
                except:
                    continue
            
            if not email_input:
                raise Exception("Could not find email input field")
            
            fast_type_and_click(driver, email_input, email)
        except Exception as e:
            print(f"⚠️ Email input issue: {e}")
            raise

        # 4. Click Continue/Next button
        print("➡️ Clicking Continue...")
        try:
            continue_selectors = [
                "button[type='submit']",
                "button:contains('Continue')",
                "button:contains('Next')",
                "input[type='submit']",
            ]
            
            for selector in continue_selectors:
                try:
                    buttons = driver.find_elements(By.CSS_SELECTOR, selector)
                    for btn in buttons:
                        if btn.is_displayed():
                            driver.execute_script("arguments[0].click();", btn)
                            time.sleep(1)
                            break
                except:
                    continue
        except:
            pass

        # 5. Enter Password - FAST
        print("🔑 Entering password...")
        try:
            password_selectors = [
                (By.ID, "password"),
                (By.NAME, "password"),
                (By.CSS_SELECTOR, "input[type='password']"),
            ]
            
            password_input = None
            for by, selector in password_selectors:
                try:
                    password_input = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((by, selector))
                    )
                    break
                except:
                    continue
            
            if not password_input:
                raise Exception("Could not find password input field")
            
            fast_type_and_click(driver, password_input, password)
        except Exception as e:
            print(f"⚠️ Password input issue: {e}")
            raise

        # 6. Click Sign In button
        print("✅ Clicking Sign In...")
        time.sleep(0.5)
        try:
            signin_selectors = [
                "button[type='submit']",
                "button:contains('Sign In')",
                "button:contains('Login')",
                "input[type='submit']",
            ]
            
            for selector in signin_selectors:
                try:
                    buttons = driver.find_elements(By.CSS_SELECTOR, selector)
                    for btn in buttons:
                        if btn.is_displayed():
                            driver.execute_script("arguments[0].click();", btn)
                            time.sleep(2)
                            break
                except:
                    continue
        except:
            pass

        # 7. Wait for successful login
        print("⏳ Waiting for Monster Dashboard...")
        time.sleep(3)
        
        # Check if login was successful
        if "sign-in" not in driver.current_url and "login" not in driver.current_url:
            print("🎉 Monster Login Successful!")
            return driver
        else:
            # Try one more time with a longer wait
            time.sleep(3)
            if "sign-in" not in driver.current_url and "login" not in driver.current_url:
                print("🎉 Monster Login Successful!")
                return driver
            else:
                raise Exception("Login may have failed - still on login page")

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