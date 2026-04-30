from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import imaplib
import email
from email.header import decode_header
import re
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import Select
import time

from datetime import datetime

def decode_mime_words(s):
    decoded = decode_header(s)
    return ''.join(
        str(part[0], part[1] or 'utf-8') if isinstance(part[0], bytes) else part[0]
        for part in decoded
    )

def get_otp_from_email(imap_email, app_password, log_callback=None):
    def log(message):
        if log_callback:
            log_callback(message)
        print(message)

    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(imap_email, app_password)
        mail.select("inbox")

        # Search for unseen messages from foreup
        status, data = mail.search(None, '(UNSEEN FROM "no-reply@foreupsoftware.com")')
        mail_ids = data[0].split()

        if not mail_ids:
            mail.logout()
            return None

        for mail_id in reversed(mail_ids):
            status, msg_data = mail.fetch(mail_id, "(RFC822)")
            raw_email = msg_data[0][1]
            msg = email.message_from_bytes(raw_email)

            from_ = decode_mime_words(msg.get("From", ""))
            
            # Extract body
            body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    content_type = part.get_content_type()
                    if content_type == "text/plain":
                        body = part.get_payload(decode=True).decode(errors="ignore")
                        break
            else:
                body = msg.get_payload(decode=True).decode(errors="ignore")

            # Find OTP: "Your booking code is: 123456"
            match = re.search(r"Your booking code is: (\d+)", body)
            if match:
                otp = match.group(1)
                log(f"Auto-OTP found in email: {otp}")
                # Mark as read
                mail.store(mail_id, '+FLAGS', '\\Seen')
                mail.logout()
                return otp

        mail.logout()
    except Exception as e:
        log(f"Email check error: {e}")
    return None

def parse_time(time_str):
    """Converts '9:30am' or '1:15pm' to minutes since midnight."""
    return datetime.strptime(time_str.lower().strip(), "%I:%M%p").hour * 60 + datetime.strptime(time_str.lower().strip(), "%I:%M%p").minute

def run_automation(email, password, course_name, target_year, target_month, target_day, start_time_str, end_time_str, players_needed, log_callback=None, otp_callback=None, price_callback=None, card_info=None, headless=False):
    def log(message):
        print(message)
        if log_callback:
            log_callback(message)

    chrome_options = Options()
    if headless:
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
    
    chrome_options.add_experimental_option("detach", True)
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.maximize_window()
    url = 'https://foreupsoftware.com/index.php/booking/19765/2431#/teetimes'
    log(f"Navigating to {url}...")
    driver.get(url)
    wait = WebDriverWait(driver, 10)
    
    start_mins = parse_time(start_time_str)
    end_mins = parse_time(end_time_str)

    try:
        # 1. Login Popup
        log("Opening login popup...")
        loginPopup = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "ul.navbar-right a.login")))
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", loginPopup)
        driver.execute_script("arguments[0].click();", loginPopup)

        # 2. Email Field
        log("Entering credentials...")
        emailfiled = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "input[name='email']")))
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", emailfiled)
        emailfiled.send_keys(email)

        # 3. Password Field
        passwordfield = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "input[name='password']")))
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", passwordfield)
        passwordfield.send_keys(password)

        # 4. Submit Button
        log("Logging in...")
        submitbutton = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[data-loading-text="Logging In..."]')))
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", submitbutton)
        driver.execute_script("arguments[0].click();", submitbutton)

        # 5. Non-Resident Button
        log("Selecting booking class (Non-Resident)...")
        nonresidential = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(normalize-space(),'Non Resident')]")))
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", nonresidential)
        driver.execute_script("arguments[0].click();", nonresidential)

        # 6. Course (Schedule) Selection
        log(f"Selecting course: {course_name}...")
        schedule_dropdown = wait.until(EC.presence_of_element_located((By.ID, "schedule_select")))
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", schedule_dropdown)
        select = Select(schedule_dropdown)
        select.select_by_visible_text(course_name)
        time.sleep(2) 

        # 7. Date Navigation (Month/Year)
        log(f"Navigating to {target_month} {target_year}...")
        datepicker = wait.until(EC.visibility_of_element_located((By.ID, "date")))
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", datepicker)
        
        target_month_year = f"{target_month} {target_year}"
        max_attempts = 12
        for i in range(max_attempts):
            current_month_year = driver.find_element(By.CSS_SELECTOR, "#date .datepicker-switch").text
            if current_month_year.strip().lower() == target_month_year.lower():
                break
            
            next_btn = driver.find_element(By.CSS_SELECTOR, "#date .next")
            driver.execute_script("arguments[0].click();", next_btn)
            time.sleep(0.5)

        # 8. Day Selection
        log(f"Selecting day {target_day}...")
        day_element = wait.until(EC.element_to_be_clickable((By.XPATH, f"//div[@id='date']//td[contains(@class, 'day') and not(contains(@class, 'old')) and not(contains(@class, 'new')) and text()='{target_day}']")))
        driver.execute_script("arguments[0].click();", day_element)
        time.sleep(2) 

        # 9. Time Slot Filtering
        log(f"Scanning for times between {start_time_str} and {end_time_str} for {players_needed} players...")
        
        time_tiles = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".time-tile")))
        found_slot = False
        
        for tile in time_tiles:
            try:
                slot_time_str = tile.find_element(By.CSS_SELECTOR, ".booking-start-time-label").text
                available_players = tile.find_element(By.CSS_SELECTOR, ".booking-slot-players span").text
                
                slot_mins = parse_time(slot_time_str)
                
                if start_mins <= slot_mins <= end_mins:
                    if int(available_players) >= int(players_needed):
                        log(f"Match found! Time: {slot_time_str}, Players available: {available_players}")
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", tile)
                        driver.execute_script("arguments[0].click();", tile)
                        
                        # 10. Select Number of Players
                        log(f"Selecting {players_needed} players...")
                        player_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, f"div[data-field='players'] a[data-value='{players_needed}']")))
                        driver.execute_script("arguments[0].click();", player_btn)
                        
                        # 11. OTP Handling
                        if otp_callback:
                            while True:
                                log("Waiting for OTP...")
                                otp_code = None
                                
                                # Try to get OTP from email first if credentials are provided
                                if imap_info and imap_info.get('email') and imap_info.get('pass'):
                                    log(f"Polling {imap_info['email']} for OTP...")
                                    for _ in range(30): # Poll for ~60 seconds
                                        otp_code = get_otp_from_email(imap_info['email'], imap_info['pass'], log_callback)
                                        if otp_code:
                                            break
                                        time.sleep(2)
                                
                                # Fallback to manual entry if auto-poll failed or no email info
                                if not otp_code:
                                    log("Auto-OTP not found. Requesting manual entry...")
                                    otp_code = otp_callback()
                                
                                log(f"Applying OTP: {otp_code}")
                                otp_input = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "input[name='reservation_confirmation_uid']")))
                                
                                # Clear existing value and type new one
                                otp_input.clear()
                                otp_input.send_keys(otp_code)
                                
                                # Click the Book Time button after entering OTP
                                try:
                                    # Use a more robust selector and handle potential stale element
                                    log("Waiting for 'Book Time' button...")
                                    time.sleep(1)
                                    book_time_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-loading-text='Booking time...']")))
                                    log("Clicking 'Book Time' button...")
                                    driver.execute_script("arguments[0].click();", book_time_btn)
                                except Exception as be:
                                    log(f"Warning: Book button error: {be}")
                                    try:
                                        # Fallback to general book button class
                                        alt_btn = driver.find_element(By.CSS_SELECTOR, ".js-book-button")
                                        driver.execute_script("arguments[0].click();", alt_btn)
                                    except:
                                        otp_input.send_keys(Keys.ENTER)
                                
                                time.sleep(4) # Wait for validation to complete or redirect
                                
                                # Check if the OTP input is still there or if an error message appeared
                                try:
                                    # Some sites show an error message like .alert-danger or similar
                                    # We'll check if the input is still visible/interactable
                                    if otp_input.is_displayed():
                                        log("OTP was incorrect or rejected. Please try again.")
                                        continue # Loop and ask again
                                    else:
                                        break # Input gone, assuming success
                                except:
                                    break # Input gone or error checking failed, assuming success
                        
                        # 12. Price Extraction & Confirmation
                        log("Extracting price and confirming...")
                        price_elem = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "h4.price")))
                        price_str = price_elem.text
                        log(f"Price found: {price_str}")
                        if price_callback:
                            price_callback(price_str)
                        
                        book_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.continue")))
                        driver.execute_script("arguments[0].click();", book_btn)
                        
                        # 13. Payment Details (in iframe)
                        if card_info:
                            log("Entering payment details...")
                            time.sleep(3) # Wait for iframe to load
                            
                            try:
                                # Switch to the payment iframe
                                log("Switching to payment iframe...")
                                wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, "element_iframe")))
                                
                                # 13.1 Card Number
                                cc_input = wait.until(EC.visibility_of_element_located((By.ID, "cardNumber")))
                                cc_input.send_keys(card_info['num'])
                                
                                # 13.2 Expiry (MMYY)
                                # Assuming MMYY format, e.g., '1226' for Dec 2026
                                mmyy = card_info['exp']
                                if len(mmyy) == 4:
                                    month = mmyy[:2]
                                    year = mmyy[2:] # '26' for 2026
                                    
                                    month_select = Select(driver.find_element(By.ID, "ddlExpirationMonth"))
                                    month_select.select_by_value(month)
                                    
                                    year_select = Select(driver.find_element(By.ID, "ddlExpirationYear"))
                                    year_select.select_by_value(year)
                                
                                # 13.3 CVV
                                cvv_input = driver.find_element(By.ID, "CVV")
                                cvv_input.send_keys(card_info['cvv'])
                                
                                # 13.4 Process Transaction
                                log("Clicking PROCESS TRANSACTION...")
                                process_btn = wait.until(EC.element_to_be_clickable((By.ID, "submit")))
                                driver.execute_script("arguments[0].click();", process_btn)
                                
                                # Switch back to main content
                                driver.switch_to.default_content()
                                log("Payment submitted successfully.")
                            except Exception as pe:
                                log(f"Payment processing error: {pe}")
                                driver.switch_to.default_content()

                        found_slot = True
                        log("Success! Booking process completed.")
                        return True
            except Exception as e:
                log(f"Error in slot processing: {e}")
                continue

        if not found_slot:
            log("No matching time slots found.")
            return False

        return False

    except Exception as e:
        log(f"Error occurred: {str(e)}")
        return None # Return None for technical error to trigger immediate retry
    # finally:
    #     driver.quit()

if __name__ == "__main__":
    # Example values for testing
    run_automation("your_email@example.com", "your_password", "Bethpage Black Course", "2026", "April", "30", "9:00am", "1:00pm", 4)