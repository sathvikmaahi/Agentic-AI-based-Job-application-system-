import time
import random
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def interruptible_sleep(seconds, stop_event):
    """
    Sleeps for 'seconds' in small chunks, checking stop_event frequently.
    Returns True if stopped, False if completed naturally.
    """
    step = 0.5
    waited = 0
    while waited < seconds:
        if stop_event and stop_event.is_set():
            return True
        time.sleep(min(step, seconds - waited))
        waited += step
    return False

def _collect_monster_easy_apply_links(driver):
    """
    Fallback: find Monster job detail links whose card/list row mentions Easy Apply.
    Uses only valid CSS/XPath (no :contains in CSS).
    """
    job_links = []
    seen = set()
    # Common patterns for job detail URLs on Monster
    xpath_candidates = (
        "//a[contains(@href,'/job-openings/')]"
        "|//a[contains(@href,'monster.com/jobs/')]"
        "|//a[contains(@href,'/jobs/')]"
    )
    for link in driver.find_elements(By.XPATH, xpath_candidates):
        try:
            href = link.get_attribute("href") or ""
            if not href or "monster.com" not in href:
                continue
            low = href.lower()
            if "/jobs/search" in low or "/jobsearch" in low:
                continue
            if "/job-openings/" not in low and "/jobs/" not in low:
                continue
            # Walk up to find a container that still says Easy Apply
            el = link
            for _ in range(12):
                try:
                    txt = el.text or ""
                    if "Easy Apply" in txt:
                        if href not in seen:
                            seen.add(href)
                            job_links.append(href)
                        break
                    el = el.find_element(By.XPATH, "..")
                except Exception:
                    break
        except Exception:
            continue
    return job_links


def click_next_page(driver):
    """Helper to find and click the next page button."""
    print("\n🔎 Checking for Next Page...")
    try:
        # Strategy: Find ALL elements that look like "Next" buttons
        next_candidates = driver.find_elements(By.XPATH, "//*[@aria-label='Next'] | //button[contains(., 'Next')] | //span[text()='Next']")
        
        for btn in next_candidates:
            if btn.is_displayed():
                print("➡️ Found visible Next button. Clicking...")
                driver.execute_script("arguments[0].click();", btn)
                time.sleep(5) 
                return True
        print("🛑 Next button not found or not visible.")
        return False
    except:
        return False

def start_applying(driver, max_limit=30, start_page=1, stop_event=None, user_data=None, job_board="dice"):
    """
    Scans the current search results page for Easy Apply jobs and applies to them.
    Logic mirrored from user's Playwright script, adapted for Selenium.
    
    Args:
        driver: Selenium webdriver
        max_limit: Maximum number of applications to send in this session (default 30)
        start_page: Page to start from
        stop_event: Threading event to stop the process
        user_data: User profile data for form filling
        job_board: 'dice' or 'monster' - determines which selectors to use
    """
    print(f"\n🤖 STARTING AUTO-APPLY ROBOT for {job_board.upper()} (Limit: {max_limit} jobs)...")
    
    if job_board.lower() == "monster":
        return start_applying_monster(driver, max_limit, start_page, stop_event, user_data)
    else:
        return start_applying_dice(driver, max_limit, start_page, stop_event, user_data)


def start_applying_dice(driver, max_limit=30, start_page=1, stop_event=None, user_data=None):
    
    # Store main window handle
    main_window = driver.current_window_handle
    
    page_count = 1
    MAX_PAGES = 10 # Safety limit
    
    # --- SKIP LOGIC ---
    if start_page > 1:
        print(f"⏩ Skipping to Page {start_page}...")
        while page_count < start_page:
            if stop_event and stop_event.is_set():
                print("🛑 Process Stopped by User during skip.")
                return
            
            # Check if we should stop
            if stop_event and stop_event.is_set():
                print("🛑 Process Stopped by User during skip.")
                return

            success = click_next_page(driver)
            if not success:
                print(f"⚠️ Could not reach page {start_page}. Stopping at page {page_count}.")
                break
            page_count += 1
            
            # Small sleep between skips, interruptible
            if interruptible_sleep(2, stop_event): return

    total_applied = 0     # Total apps sent this session
    since_break_count = 0 # Apps sent since last break
    
    while page_count <= MAX_PAGES:
        # Check Total Limit at start of page (double check)
        if total_applied >= max_limit:
            print(f"🛑 Daily Limit of {max_limit} reached! Stopping.")
            break
            
        if stop_event and stop_event.is_set():
            print("🛑 Process Stopped by User.")
            break

        print(f"\n📄 Processing Page {page_count}...")
        
        # 1. Wait for results to load
        print("⏳ Waiting for job cards...")
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "a[href*='/job-detail/']"))
            )
        except:
            print("⚠️ No jobs found or page took too long.")
            break # Stop if page doesn't load

        # 2. Collect Easy Apply Job URLs
        print("🔍 Scanning for 'Easy Apply' jobs...")
        
        # Updated Strategy: Find all valid job links, then check if their parent container has "Easy Apply"
        js_script = """
        var jobs = [];
        var links = document.querySelectorAll('a[href*="/job-detail/"]');
        
        links.forEach(link => {
            var p = link.parentElement;
            for(var i=0; i<7; i++) {
                if (p && p.innerText && p.innerText.includes('Easy Apply')) {
                    jobs.push(link.href);
                    break; 
                }
                if(p) p = p.parentElement;
            }
        });
        return [...new Set(jobs)];
        """
        
        try:
            # Wait a moment for dynamic content to settle
            if interruptible_sleep(3, stop_event): return
            job_links = driver.execute_script(js_script)
        except Exception as e:
            print(f"❌ Error scanning jobs: {e}")
            break

        print(f"🎯 Found {len(job_links)} Easy Apply jobs on this page.")
        
        # 3. Loop and Apply (Process current page)
        for i, link in enumerate(job_links):
            # CHECK LIMIT
            if total_applied >= max_limit:
                print(f"🛑 Daily Limit of {max_limit} reached! Stopping.")
                return # Exit completely
            
            # CHECK BREAK (Every 5 apps)
            if since_break_count >= 5:
                print(f"☕ Took 5 actions. Time for a coffee break...")
                break_time = 90 # 1.5 minutes fixed
                print(f"💤 Pausing for {break_time/60:.1f} minutes...")
                if interruptible_sleep(break_time, stop_event):
                     print("🛑 Break interrupted by Stop.")
                     return
                since_break_count = 0 # Reset break counter
                print("▶️ Break over! Resuming work...")

            print(f"\n➡️ [Page {page_count} - {i+1}/{len(job_links)}] Processing: {link}")
            print(f"   📊 Progress: {total_applied + 1} / {max_limit}")
            
            # Navigate to Job (Single Tab Mode)
            try:
                # Go to the job page in the current window
                driver.get(link)
                
                # --- APPLY FLOW ---
                success = apply_to_single_job(driver, stop_event, user_data)
                
                if success:
                    total_applied += 1
                    since_break_count += 1
                
            except Exception as e:
                print(f"⚠️ Failed to process job: {e}")
            
            finally:
                # --- RETURN TO SEARCH PAGE ---
                print("   🔙 Returning to Search Results...")
                
                # Retry loop to getting back to the search page (pop history stack)
                # We need to go back until we see the Job Cards again.
                found_search = False
                for _ in range(5): # Try 'Back' up to 5 times
                    try:
                        # Check if we see job cards?
                        # Using a short timeout because we expect it to be fast if we are there
                        WebDriverWait(driver, 2).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, "a[href*='/job-detail/']"))
                        )
                        found_search = True
                        break # We are back!
                    except:
                        # Not found yet, go back
                        driver.back()
                        if interruptible_sleep(1, stop_event): return 
                
                if not found_search:
                    print("⚠️ WARNING: Could not return to search results automatically.")
                    # Fallback: We might need to reload the page or break
                    # But for now we continue, the next iteration might fail, triggering the outer try/except
            
            # Switch Logic Removed (Stay in same window)
            
            # --- HUMAN DELAY ---
            # --- HUMAN DELAY ---
            if i < len(job_links) - 1 and total_applied < max_limit:
                delay = 7 # Fixed 7 seconds logic
                print(f"💤 Sleeping for {delay:.2f} seconds to be safe...")
                if interruptible_sleep(delay, stop_event): return

        # --- PAGINATION LOGIC (Replaced with Helper) ---
        if not click_next_page(driver):
            print("🛑 No 'Next Page' button found or end of results.")
            break
        page_count += 1
            
    print("🎉 Auto-Apply Batch Complete (All Pages)!")

def fill_smart_form(driver, user_data):
    """
    Fills visible inputs (Name, Email, etc.) and handles Radio Buttons.
    """
    try:
        # 1. TEXT INPUTS
        if user_data:
            inputs = driver.find_elements(By.CSS_SELECTOR, "input[type='text'], input[type='email'], input[type='tel'], input[type='number']")
            for inp in inputs:
                if not inp.is_displayed(): continue
                
                # Check current value
                val = inp.get_attribute("value")
                if val and len(val) > 0: continue # Already filled
                
                # Try to guess label
                label_txt = "" 
                try:
                    label_txt = (inp.get_attribute("name") or "") + (inp.get_attribute("placeholder") or "") + (inp.get_attribute("aria-label") or "")
                except: pass
                label_txt = label_txt.lower()
                
                # A. Standard User Data
                filled = False
                mappings = {
                    'name': user_data['name'],
                    'first': user_data['name'].split()[0],
                    'last': ' '.join(user_data['name'].split()[1:]) if ' ' in user_data['name'] else '',
                    'email': user_data['email'],
                    'phone': user_data['phone'],
                    'mobile': user_data['phone'],
                    'city': 'New York'
                }
                
                for key, value in mappings.items():
                    if key in label_txt:
                        try:
                            # Avoid overwriting "Last Name" when matching "Name" if we can be specfic, 
                            # but simple match is okay for now.
                            if "first" in key and "last" in label_txt: continue
                            
                            inp.clear()
                            inp.send_keys(value)
                            print(f"   📝 Auto-filled {key}...")
                            filled = True
                            break
                        except: pass
                
                if filled: continue
                
                # B. Experience / Numeric Guessing
                # If it asks for "years", "experience", "how long", or is number type
                if "years" in label_txt or "experience" in label_txt or inp.get_attribute("type") == "number":
                    try:
                        rand_exp = str(random.randint(7, 10))
                        inp.send_keys(rand_exp)
                        print(f"   🎲 Randomly filled experience: {rand_exp}")
                    except: pass

        # 2. RADIO BUTTONS & DROPDOWNS (Fallback)
        # Strategy: Find unchecked radio groups and click logical 'Yes' or Random
        try:
             # Find all radio inputs
             radios = driver.find_elements(By.CSS_SELECTOR, "input[type='radio']")
             
             # Group by name
             groups = {}
             for r in radios:
                 name = r.get_attribute("name")
                 if not name: continue
                 if name not in groups: groups[name] = []
                 groups[name].append(r)
                 
             for name, buttons in groups.items():
                 # Check if any is selected
                 is_selected = any(r.is_selected() for r in buttons)
                 if is_selected: continue
                 
                 # None selected. Try to find "Yes"
                 clicked = False
                 for r in buttons:
                     try:
                         # Check label or value
                         # This requires finding the label/span often next to it. 
                         # Simplified: check value att
                         val = r.get_attribute("value").lower()
                         if "yes" in val:
                             driver.execute_script("arguments[0].click();", r)
                             clicked = True
                             break
                     except: pass
                 
                 if not clicked and buttons:
                     # RANDOM FALLBACK
                     target = random.choice(buttons)
                     try:
                        driver.execute_script("arguments[0].click();", target)
                        print("   🎲 Randomly selected a radio option.")
                     except: pass
        except:
             pass
        
    except Exception as e:
        # print(f"Form fill error: {e}")
        pass

def answer_yes_questions(driver):
    """
    Finds and clicks ALL 'Yes' options instantly using JS.
    """
    try:
        # Script to find and click all "Yes" radios/labels at once
        js_script = """
        var count = 0;
        // 1. Inputs with value 'yes'
        var radios = document.querySelectorAll("input[type='radio'][value*='yes' i], input[type='radio'][value*='True' i]");
        radios.forEach(r => {
            if(!r.checked) { r.click(); count++; }
        });
        
        // 2. Labels containing "Yes"
        var labels = document.evaluate("//label[contains(translate(., 'YES', 'yes'), 'yes')]", document, null, XPathResult.UNORDERED_NODE_SNAPSHOT_TYPE, null);
        for(var i=0; i<labels.snapshotLength; i++) {
             var el = labels.snapshotItem(i);
             // simplistic check, might click wrong things but usually safe on these forms
             if(el.offsetParent !== null) { el.click(); count++; }
        }
        return count;
        """
        driver.execute_script(js_script)
        # No sleep need, we want speed
    except Exception as e:
        pass

def check_if_applied(driver):
    """
    Returns True if detecting ANY 'Applied' indicator.
    """
    try:
        # 1. Look for buttons that say "Applied"
        # 2. Look for text "Application Sent"
        # 3. Look for "Easy Apply" (if NOT found, maybe we applied?) -> No, that's risky.
        
        # Aggressive text search in buttons
        btns = driver.find_elements(By.XPATH, "//button | //a[@role='button']")
        for btn in btns:
            if not btn.is_displayed(): continue
            txt = (btn.text or btn.get_attribute("innerText") or "").strip().lower()
            if "applied" in txt or "application sent" in txt:
                print(f"   🚫 Detected 'Applied' status: '{txt}'")
                return True
                
        # Check specific Dice "Applied" span often found in the header
        if len(driver.find_elements(By.XPATH, "//span[contains(text(), 'Applied')]")) > 0:
             return True
             
    except: pass
    return False

def apply_to_single_job(driver, stop_event=None, user_data=None):
    """
    Handles the Apply -> Next -> Submit flow for a single open tab.
    """
    # --- ROBUST LOOP STRATEGY ---
    # Instead of expecting Step 1 -> Step 2, we loop and react to what we see.
    # Max time to spend trying to apply: 60 seconds
    max_duration = 60
    start_time = time.time()
    
    # Track state
    clicked_submit = False
    circle_back_check = False # To distinguish pre-applied vs post-submit applied
    
    print("   🔄 Entering Smart Apply Loop (Max 60s)...")
    
    while (time.time() - start_time) < max_duration:
        # Check Stop
        if stop_event and stop_event.is_set(): return False
        
        # 0. Check Success OR Already Applied (Fast Fail)
        if "Application Sent" in driver.page_source or "success" in driver.current_url:
            print("   🎉 Application Sent Detected!")
            return True
            
        if check_if_applied(driver):
            # If we see "Applied" button, we are done? 
            # Wait, if we see it on the first loop, it means we skip.
            # If we see it after clicking Submit, it means success.
            # Let's assume if we haven't clicked Submit yet, it's a skip.
            if not circle_back_check: # Only if fresh
                 return False # SKIP
            else:
                 return True # SUCCESS
                 
        # 1. Answer Questions & Fill Forms (Always try this first)
        answer_yes_questions(driver)
        fill_smart_form(driver, user_data)
        
        # 2. Find Action Buttons
        # Priorities: Submit > Next > Apply/Continue
        
        try:
            # --- CHECK FOR SUBMIT ---
            submit_btns = driver.find_elements(By.XPATH, "//button[.//span[contains(text(), 'Submit')]] | //button[text()='Submit']")
            visible_submit = [b for b in submit_btns if b.is_displayed()]
            
            if visible_submit:
                print("   ✅ Found SUBMIT button. Clicking...")
                driver.execute_script("arguments[0].click();", visible_submit[0])
                circle_back_check = True
                # Wait for success
                if interruptible_sleep(5, stop_event): return False
                continue # Loop back to check success
                
            # --- CHECK FOR NEXT ---
            next_btns = driver.find_elements(By.XPATH, "//button[.//span[contains(text(), 'Next')]] | //button[text()='Next']")
            visible_next = [b for b in next_btns if b.is_displayed()]
            
            if visible_next:
                print("   ➡️ Found NEXT button. Clicking...")
                driver.execute_script("arguments[0].click();", visible_next[0])
                if interruptible_sleep(3, stop_event): return False
                continue
                
            # --- CHECK FOR APPLY / EASY APPLY / CONTINUE ---
            # We look for this mainly at the start, but sometimes it appears late.
            # Avoid clicking if we definitely already clicked it? 
            # Actually, sometimes you have to click "Apply" then "Continue" which looks same.
            
            apply_candidates = driver.find_elements(By.XPATH, 
                "//button[@data-testid='apply-button'] | //a[contains(., 'Apply')] | //button[contains(., 'Apply')] | //a[contains(., 'Continue')] | //button[contains(., 'Continue')]")
            
            visible_apply = [b for b in apply_candidates if b.is_displayed()]
            
            # Filter out "Applied" (disabled)
            valid_apply = []
            for btn in visible_apply:
                txt = btn.text or btn.get_attribute('innerText')
                if "Applied" in txt: continue
                # Also check disabled attribute
                if btn.get_attribute("disabled"): continue
                valid_apply.append(btn)
                
            if valid_apply:
                 # Check if we are just staring at the 'Easy Apply' button indefinitely?
                 # We can add a simple debouncer or just click it.
                 # Let's simple click.
                 print("   🖱️ Found APPLY/CONTINUE button. Clicking...")
                 driver.execute_script("arguments[0].click();", valid_apply[0])
                 if interruptible_sleep(3, stop_event): return False
                 continue
                 
        except Exception as e:
            # Stale element or other minor error, just loop
            pass
            
        # If we are here, we didn't find any buttons this iteration.
        # Wait a bit and try again (Loading...)
        print("   ⏳ Waiting for buttons...")
        if interruptible_sleep(2, stop_event): return False
        
    print("   ⚠️ Timed out waiting for flow to complete.")
    return False


def start_applying_monster(driver, max_limit=30, start_page=1, stop_event=None, user_data=None):
    """
    Scans Monster.com search results for Easy Apply jobs and applies to them.
    """
    print(f"\n🤖 STARTING AUTO-APPLY ROBOT FOR MONSTER (Limit: {max_limit} jobs)...")
    
    # Store main window handle
    main_window = driver.current_window_handle
    
    page_count = 1
    MAX_PAGES = 10 # Safety limit
    
    # --- SKIP LOGIC ---
    if start_page > 1:
        print(f"⏩ Skipping to Page {start_page}...")
        while page_count < start_page:
            if stop_event and stop_event.is_set():
                print("🛑 Process Stopped by User during skip.")
                return
            
            success = click_next_page_monster(driver)
            if not success:
                print(f"⚠️ Could not reach page {start_page}. Stopping at page {page_count}.")
                break
            page_count += 1
            
            # Small sleep between skips, interruptible
            if interruptible_sleep(2, stop_event): return

    total_applied = 0     # Total apps sent this session
    since_break_count = 0 # Apps sent since last break
    
    while page_count <= MAX_PAGES:
        # Check Total Limit at start of page (double check)
        if total_applied >= max_limit:
            print(f"🛑 Daily Limit of {max_limit} reached! Stopping.")
            break
            
        if stop_event and stop_event.is_set():
            print("🛑 Process Stopped by User.")
            break

        print(f"\n📄 Processing Monster Page {page_count}...")
        
        # 1. Wait for results to load
        print("⏳ Waiting for job cards...")
        try:
            # Monster DOM changes often — use several possible roots
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((
                    By.CSS_SELECTOR,
                    "[data-test-id='job-card'], [data-testid='job-card'], .job-card, "
                    "[data-cy='job-card'], article[data-job-id], .job-tile, .card-content"
                ))
            )
        except Exception:
            print("⚠️ No jobs found or page took too long.")
            break # Stop if page doesn't load

        # 2. Collect Easy Apply Job URLs
        print("🔍 Scanning for 'Easy Apply' jobs on Monster...")
        
        # NOTE: querySelector does NOT support :contains() (jQuery-only). Use innerText + valid selectors only.
        js_script = """
        var jobs = [];
        var cards = document.querySelectorAll(
            '[data-test-id="job-card"], [data-testid="job-card"], [data-cy="job-card"], ' +
            '.job-card, article[data-job-id], .job-tile, article'
        );
        cards.forEach(function(card) {
            var text = (card.innerText || '');
            if (text.indexOf('Easy Apply') === -1) { return; }
            var link = card.querySelector(
                'a[href*="/job-openings/"], a[href*="/jobs/"], ' +
                'a[href*="job-openings"], h2 a, .title a, [data-test-id="job-title"] a'
            );
            if (link && link.href) {
                jobs.push(link.href);
                return;
            }
            var all = card.querySelectorAll('a[href*="monster.com"]');
            for (var i = 0; i < all.length; i++) {
                var h = (all[i].href || '').toLowerCase();
                if (h.indexOf('/jobs/search') !== -1) { continue; }
                if (h.indexOf('/job-openings/') !== -1 || h.indexOf('/jobs/') !== -1) {
                    jobs.push(all[i].href);
                    return;
                }
            }
        });
        return Array.from(new Set(jobs));
        """
        
        try:
            # Wait a moment for dynamic content to settle
            if interruptible_sleep(3, stop_event): return
            job_links = driver.execute_script(js_script)
            
            # If JS didn't find jobs, try alternative approach (Python + DOM)
            if not job_links:
                job_links = _collect_monster_easy_apply_links(driver)
        except Exception as e:
            print(f"❌ Error scanning Monster jobs: {e}")
            try:
                job_links = _collect_monster_easy_apply_links(driver)
            except Exception as e2:
                print(f"❌ Fallback scan failed: {e2}")
                job_links = []

        print(f"🎯 Found {len(job_links)} Easy Apply jobs on this page.")
        
        # 3. Loop and Apply (Process current page)
        for i, link in enumerate(job_links):
            # CHECK LIMIT
            if total_applied >= max_limit:
                print(f"🛑 Daily Limit of {max_limit} reached! Stopping.")
                return # Exit completely
            
            # CHECK BREAK (Every 5 apps)
            if since_break_count >= 5:
                print(f"☕ Took 5 actions. Time for a coffee break...")
                break_time = 90 # 1.5 minutes fixed
                print(f"💤 Pausing for {break_time/60:.1f} minutes...")
                if interruptible_sleep(break_time, stop_event):
                     print("🛑 Break interrupted by Stop.")
                     return
                since_break_count = 0 # Reset break counter
                print("▶️ Break over! Resuming work...")

            print(f"\n➡️ [Page {page_count} - {i+1}/{len(job_links)}] Processing: {link}")
            print(f"   📊 Progress: {total_applied + 1} / {max_limit}")
            
            # Navigate to Job (Single Tab Mode)
            try:
                # Go to the job page in the current window
                driver.get(link)
                
                # --- APPLY FLOW ---
                success = apply_to_single_job_monster(driver, stop_event, user_data)
                
                if success:
                    total_applied += 1
                    since_break_count += 1
                
            except Exception as e:
                print(f"⚠️ Failed to process job: {e}")
            
            finally:
                # --- RETURN TO SEARCH PAGE ---
                print("   🔙 Returning to Search Results...")
                
                # Retry loop to getting back to the search page
                found_search = False
                for _ in range(5): # Try 'Back' up to 5 times
                    try:
                        # Check if we see job cards (same broad selectors as initial wait)
                        WebDriverWait(driver, 2).until(
                            EC.presence_of_element_located((
                                By.CSS_SELECTOR,
                                "[data-test-id='job-card'], [data-testid='job-card'], .job-card, "
                                "[data-cy='job-card'], article[data-job-id], .job-tile"
                            ))
                        )
                        found_search = True
                        break # We are back!
                    except:
                        # Not found yet, go back
                        driver.back()
                        if interruptible_sleep(1, stop_event): return 
                
                if not found_search:
                    print("⚠️ WARNING: Could not return to search results automatically.")
            
            # --- HUMAN DELAY ---
            if i < len(job_links) - 1 and total_applied < max_limit:
                delay = 7 # Fixed 7 seconds logic
                print(f"💤 Sleeping for {delay:.2f} seconds to be safe...")
                if interruptible_sleep(delay, stop_event): return

        # --- PAGINATION LOGIC ---
        if not click_next_page_monster(driver):
            print("🛑 No 'Next Page' button found or end of results.")
            break
        page_count += 1
            
    print("🎉 Monster Auto-Apply Batch Complete (All Pages)!")


def click_next_page_monster(driver):
    """Helper to find and click the next page button on Monster."""
    print("\n🔎 Checking for Next Page on Monster...")
    try:
        # Monster pagination selectors
        next_candidates = driver.find_elements(
            By.XPATH, 
            "//button[@aria-label='Next'] | //a[@aria-label='Next'] | //button[contains(., 'Next')] | //a[contains(., 'Next')] | //*[contains(@class, 'next')]"
        )
        
        for btn in next_candidates:
            if btn.is_displayed() and not btn.get_attribute("disabled"):
                print("➡️ Found visible Next button. Clicking...")
                driver.execute_script("arguments[0].click();", btn)
                time.sleep(5) 
                return True
        print("🛑 Next button not found or not visible.")
        return False
    except:
        return False


def apply_to_single_job_monster(driver, stop_event=None, user_data=None):
    """
    Handles the Apply flow for a single Monster job.
    Order matches Dice: start Easy Apply / Continue, then Next, then Submit — avoid
    matching 'Easy Apply' as a generic 'Apply' in the submit step.
    """
    max_duration = 90
    start_time = time.time()
    
    circle_back_check = False
    
    print("   🔄 Entering Monster Smart Apply Loop (Max 90s)...")
    
    while (time.time() - start_time) < max_duration:
        # Check Stop
        if stop_event and stop_event.is_set(): return False
        
        # 0. Check Success OR Already Applied (Fast Fail)
        if "Application Sent" in driver.page_source or "success" in driver.current_url.lower():
            print("   🎉 Application Sent Detected!")
            return True
            
        if check_if_applied_monster(driver):
            if not circle_back_check:
                 return False # SKIP
            else:
                 return True # SUCCESS
                 
        # 1. Answer Questions & Fill Forms (Always try this first)
        answer_yes_questions(driver)
        fill_smart_form(driver, user_data)
        
        # 2. Find Action Buttons — Easy Apply first, then Next/Continue, then Submit
        try:
            # --- EASY APPLY (must run before generic "Apply" matching) ---
            easy_apply_btns = driver.find_elements(
                By.XPATH,
                "//button[contains(normalize-space(.), 'Easy Apply')] | "
                "//a[contains(normalize-space(.), 'Easy Apply')] | "
                "//button[@data-test-id='easy-apply-button'] | "
                "//*[@data-testid='easy-apply-button']"
            )
            visible_easy = []
            for b in easy_apply_btns:
                if not b.is_displayed():
                    continue
                txt = (b.text or b.get_attribute("innerText") or "").strip()
                if "Applied" in txt or b.get_attribute("disabled"):
                    continue
                visible_easy.append(b)
            if visible_easy:
                print("   🖱️ Found EASY APPLY button. Clicking...")
                driver.execute_script("arguments[0].click();", visible_easy[0])
                circle_back_check = True
                if interruptible_sleep(3, stop_event): return False
                continue

            # --- NEXT / CONTINUE ---
            next_btns = driver.find_elements(
                By.XPATH,
                "//button[contains(., 'Next')] | //button[contains(., 'Continue')] | "
                "//a[contains(., 'Continue')]"
            )
            visible_next = [b for b in next_btns if b.is_displayed()]
            if visible_next:
                print("   ➡️ Found NEXT/CONTINUE button. Clicking...")
                driver.execute_script("arguments[0].click();", visible_next[0])
                circle_back_check = True
                if interruptible_sleep(3, stop_event): return False
                continue

            # --- SUBMIT (exclude Easy Apply) ---
            submit_btns = driver.find_elements(
                By.XPATH,
                "//button[contains(., 'Submit')] | //input[@type='submit'] | "
                "//button[@data-test-id='submit-button'] | //button[@type='submit']"
            )
            visible_submit = []
            for b in submit_btns:
                if not b.is_displayed():
                    continue
                txt = (b.text or b.get_attribute("innerText") or "").strip()
                if "Easy Apply" in txt:
                    continue
                visible_submit.append(b)
            if visible_submit:
                print("   ✅ Found SUBMIT button. Clicking...")
                driver.execute_script("arguments[0].click();", visible_submit[0])
                circle_back_check = True
                if interruptible_sleep(5, stop_event): return False
                continue

            # --- GENERIC APPLY (not Easy Apply) ---
            apply_btns = driver.find_elements(
                By.XPATH,
                "//button[contains(., 'Apply')] | //a[contains(., 'Apply')]"
            )
            valid_apply = []
            for btn in apply_btns:
                if not btn.is_displayed():
                    continue
                txt = (btn.text or btn.get_attribute("innerText") or "").strip()
                if "Easy Apply" in txt or "Applied" in txt:
                    continue
                if btn.get_attribute("disabled"):
                    continue
                valid_apply.append(btn)
            if valid_apply:
                print("   🖱️ Found APPLY button. Clicking...")
                driver.execute_script("arguments[0].click();", valid_apply[0])
                circle_back_check = True
                if interruptible_sleep(3, stop_event): return False
                continue

        except Exception:
            pass
            
        print("   ⏳ Waiting for buttons...")
        if interruptible_sleep(2, stop_event): return False
        
    print("   ⚠️ Timed out waiting for flow to complete.")
    return False


def check_if_applied_monster(driver):
    """
    Returns True if detecting an 'Applied' status in primary UI controls (not job body text).
    """
    try:
        for xpath in (
            "//button[normalize-space(translate(., 'APPLIED', 'applied'))='applied']",
            "//a[contains(., 'Already applied') or contains(., 'already applied')]",
            "//*[contains(@class,'applied')][self::button or self::a]",
        ):
            for el in driver.find_elements(By.XPATH, xpath):
                try:
                    if not el.is_displayed():
                        continue
                    txt = (el.text or el.get_attribute("innerText") or "").strip().lower()
                    if txt in ("applied", "already applied") or "application submitted" in txt:
                        print(f"   🚫 Detected 'Applied' status: '{txt}'")
                        return True
                except Exception:
                    continue
    except Exception:
        pass
    return False


