# Gym Class Auto-Booker – Selenium Network-Retry Demo

Python Selenium script that logs into a demo gym booking site, advances the schedule as an admin, then logs in as a normal user to automatically book (or join the waitlist for) specific evening classes. It also verifies that all expected bookings appear in the “My Bookings” page, even when the network randomly fails.

## Main features

- Opens the App Brewery gym demo site with Chrome using a dedicated `chrome_profile` so cookies and state can persist between runs.
- Uses two roles:
  - **Admin account** to log in and click the “advance 3 days” button so that the target classes appear.
  - **User account** to log in and actually book / waitlist the classes.
- Implements a `retry(func, retries=7, description=None)` helper that:
  - wraps Selenium actions that can fail under simulated network issues
  - retries on `TimeoutException` up to a fixed number of attempts
  - prints which attempt is currently running for easier debugging.
- Uses explicit waits (`WebDriverWait` + `expected_conditions`) instead of `time.sleep()` for:
  - login elements (email, password, submit button)
  - page transitions (`schedule-page`, `my-bookings-page`)
  - booking button state changes (waiting until text becomes `"Booked"`).
- Selects all visible class cards with CSS selectors like `div[id^='class-card-']` and filters them by:
  - day (`Wed` or `Fri` in the day heading)
  - time (`"6:00 PM"` in the time text)
- For each matching class card:
  - reads the class name from the `<h3>` tag
  - finds the associated booking button (`Book Class`, `Booked`, `Waitlisted`, `Join Waitlist`)
  - decides whether to book, join the waitlist, or just record an existing booking.
- Keeps counters for:
  - new bookings
  - classes joined via waitlist
  - classes already booked/waitlisted
  - detailed log for each processed class.
- Opens the **My Bookings** page and verifies:
  - how many relevant bookings are shown there for Wed/Fri 6pm
  - prints a summary and a final success/mismatch message (`✅ SUCCESS` vs. `❌ MISMATCH`).
- Designed to run with Chrome DevTools network simulation (e.g. 50% failure rate) so the retry logic actually gets tested.

## What I learned

- How to structure a larger Selenium script into functions (`login`, `book_class`, `get_my_bookings`, `retry`) instead of one huge procedural block.
- Using `WebDriverWait` and `expected_conditions` to wait for elements and states, making the script more stable than relying on fixed `sleep` calls.
- Writing a generic retry wrapper that re-runs fragile actions when the network or page load randomly fails.
- Using CSS selectors with attribute prefixes (e.g. `div[id^='class-card-']`) and XPath to navigate from a card to its day/time/class elements.
- Handling multiple button states (`Booked`, `Waitlisted`, `Book Class`, `Join Waitlist`) and updating counters based on the current text.
- Verifying automation results by reading a summary page and comparing expected vs. actual counts instead of trusting that clicks always worked.
- Working with a demo site under simulated bad network conditions to see how real systems can behave when connections are unreliable.

## How to run

1. Clone the repo:

   git clone https://github.com/<your-username>/gym-class-auto-booker.git  
   cd gym-class-auto-booker  

2. (Optional) Create and activate a virtual environment:

   python -m venv venv  
   source venv/bin/activate   (Windows: venv\Scripts\activate)  

3. Install dependencies:

   pip install -r requirements.txt  

4. Make sure you have a recent Chrome and Selenium setup:
   - Install Google Chrome if it is not already installed.  
   - Selenium will use `webdriver.Chrome()` (Selenium Manager) to locate the driver automatically in recent versions; no manual driver download is usually needed.

5. Adjust configuration at the top of `main.py` if needed:
   - `ADMIN_EMAIL` / `ADMIN_PASSWORD` – admin test credentials  
   - `ACCOUNT_EMAIL` / `ACCOUNT_PW` – user test credentials  
   - `GYM_URL` – demo site URL (default: `https://appbrewery.github.io/gym/`)

6. (Optional) Simulate network issues:
   - Open Chrome DevTools → Network tab.  
   - Enable a throttling profile or failure simulation (e.g. 50% failure rate) to test the retry logic in real conditions.

7. Run the script:

   python main.py  

   - The script logs in as admin (if that section is enabled) and advances the schedule.  
   - Then it logs in as the user, finds the Wed/Fri 6pm classes, and books or waitlists them.  
   - Finally, it opens the “My Bookings” page, verifies the number of bookings, and prints a detailed summary and verification result.
