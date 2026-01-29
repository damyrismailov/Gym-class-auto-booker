from selenium import webdriver
from selenium.common import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
import os
import time


ADMIN_EMAIL = "admin@test.com"
ADMIN_PASSWORD = "admin123"
ACCOUNT_EMAIL="damyr@test.com"
ACCOUNT_PW="damyrtest"
GYM_URL="https://appbrewery.github.io/gym/"

chrome_options = webdriver.ChromeOptions()
chrome_options.add_experimental_option("detach", True)
user_data_dir = os.path.join(os.getcwd(), "chrome_profile")
chrome_options.add_argument(f"--user-data-dir={user_data_dir}")
driver = webdriver.Chrome(options=chrome_options)
driver.get(GYM_URL)

wait = WebDriverWait(driver, 2)
# login_button = driver.find_element(By.ID, "login-button")
# login_button.click()
#
# #Admin log
# email_input = wait.until(ec.presence_of_element_located((By.ID, "email-input")))
# email_input.clear()
# email_input.send_keys(ADMIN_EMAIL)
#
# password_input = driver.find_element(By.ID, "password-input")
# password_input.clear()
# password_input.send_keys(ADMIN_PASSWORD)
#
# submit_button = driver.find_element(By.ID, "submit-button")
# submit_button.click()
#
# wait.until(ec.presence_of_element_located((By.ID, "main-content")))
# # wait.until(ec.element_to_be_clickable((By.ID, "advance-3-days"))).click()
# # all_advances = wait.until(ec.presence_of_all_elements_located((By.CSS_SELECTOR, "button[id^='advance-']")))
# # for advance in all_advances:
# #     print(advance.text)
# #     if "+3 Days" in advance.text:
# #         print("Advance")
# #         advance.click()

def retry(func, retries=10, description=None):
    for i in range(retries):
        print(f"Trying {description}. Attempt: {i + 1}")
        try:
            return func()
        except TimeoutException:
            if i == retries - 1:
                raise
            time.sleep(1)
def login():
    wait.until(ec.presence_of_element_located((By.ID, "login-button"))).click()
    email_input = wait.until(ec.presence_of_element_located((By.ID, "email-input")))
    email_input.clear()
    email_input.send_keys(ACCOUNT_EMAIL)
    password_input = wait.until(ec.presence_of_element_located((By.ID, "password-input")))
    password_input.clear()
    password_input.send_keys(ACCOUNT_PW)
    driver.find_element(By.ID, "submit-button").click()
    wait.until(ec.presence_of_element_located((By.ID, "schedule-page")))
def book_class(booking_button):
    booking_button.click()
    wait.until(lambda d: booking_button.text == "Booked")
retry(login, description="login")

classes_booked = 0
waitlists_joined = 0
Already_booked_waitlisted = 0
processed_classes = []

class_cards = driver.find_elements(By.CSS_SELECTOR,"div[id^='class-card-']")
for card in class_cards:
    day_group = card.find_element(By.XPATH, "./ancestor::div[contains(@id, 'day-group-')]")
    day = day_group.find_element(By.TAG_NAME,"h2").text
    if "Wed" in day or "Fri" in day:
        time_text = card.find_element(By.CSS_SELECTOR, "p[id^='class-time-']").text
        if "6:00 PM" in time_text:
            class_name = card.find_element(By.CSS_SELECTOR, "h3[id^='class-name-']").text
            booking_button = card.find_element(By.CSS_SELECTOR, "button[id^='book-button-']")
            class_info = f"{class_name} on {day}"

            if booking_button.text == "Booked":
                print(f"✓ Already booked: {class_info}")
                Already_booked_waitlisted += 1
                processed_classes.append(f"[Booked] {class_info}")

            elif booking_button.text == "Waitlisted":
                print(f"The {class_info} is waitlisted")
                Already_booked_waitlisted += 1
                processed_classes.append(f"[Waitlisted] {class_info}")

            elif booking_button.text == "Book Class":
                retry(lambda: book_class(booking_button), description="Booking")
                print(f"✓ Successfully booked: {class_info}")
                classes_booked += 1
                processed_classes.append(f"[New Booking] {class_info}")
                time.sleep(0.5)

            elif booking_button.text == "Join Waitlist":
                retry(lambda: book_class(booking_button), description="Waitlisting")
                print(f"The {class_info} joined on waitlist")
                waitlists_joined += 1
                processed_classes.append(f"[New Waitlist] {class_info}")
                time.sleep(0.5)
total_booked = classes_booked + waitlists_joined + Already_booked_waitlisted
print(f"\n--- Total Wednesday/Friday 6pm classes: {total_booked} ---")
print("\n--- VERIFYING ON MY BOOKINGS PAGE ---")

def get_my_bookings():
    driver.find_element(By.ID, "my-bookings-link").click()
    wait.until(ec.presence_of_element_located((By.ID, "my-bookings-page")))
    cards = driver.find_elements(By.CSS_SELECTOR, "div[id*='card-']")
    if not cards:
        raise TimeoutException("No booking cards found - page may not have loaded")
    return cards

verified_classes = 0
all_cards = retry(lambda: get_my_bookings(), description="get_my_bookings")
for card in all_cards:
    try:
        when_paragraph = card.find_element(By.XPATH, ".//p[strong[text()='When:']]")
        when_text = when_paragraph.text
        if ("Wed" in when_text or "Fri" in when_text) and "6:00 PM" in when_text:
            class_name = card.find_element(By.TAG_NAME, "h3").text
            print(f"  ✓ Verified: {class_name}")
            verified_classes += 1
    except NoSuchElementException:
        pass


print(f"\n--- VERIFICATION RESULT ---")
print(f"Expected: {total_booked} bookings")
print(f"Found: {verified_classes} bookings")

if total_booked == verified_classes:
    print("✅ SUCCESS: All bookings verified!")
else:
    print(f"❌ MISMATCH: Missing {total_booked - verified_classes} bookings")

# booked_classes = driver.find_elements(By.CSS_SELECTOR,"h3[id^='booking-class-name-")
# waitlists_joined = driver.find_elements(By.CSS_SELECTOR,"h3[id^='waitlist-class-name-")
# total_classes =  len(booked_classes) + len(waitlists_joined) + Already_booked_waitlisted
# print(f"\n--- Total Tuesday/Wednesday 6pm classes: {total_classes} ---\n")
# print("--- VERIFYING ON MY BOOKINGS PAGE ---")
# for class_name in booked_classes:
#     print(f"✓ Verified: {class_name.text}")
# for class_name in waitlists_joined:
#     print(f"✓ Verified: Spin Class {class_name.text}")
# print("\n--- VERIFICATION RESULT ---")
# print(f"Expected: {len(processed_classes)} bookings")
# print(f"Found: {total_classes} bookings")
# if len(processed_classes) == total_classes:
#     print("✅ SUCCESS: All bookings verified!")
# elif len(processed_classes) != total_classes:
#     print(f"❌ MISMATCH: Missing {len(processed_classes) - total_classes} bookings")
            # print("--- BOOKING SUMMARY ---")
            # print(f"Classes booked: {classes_booked}")
            # print(f"Waitlists joined: {waitlists_joined}")
            # print(f"Already booked/waitlisted: {Already_booked_waitlisted}")
            # print(f"Total Tuesday 6 pm classes processed: {classes_booked + waitlists_joined + Already_booked_waitlisted}\n")

            # print("--- DETAILED CLASS LIST ---")
            # for class_detail in processed_classes:
            #     print(f"  • {class_detail}")

