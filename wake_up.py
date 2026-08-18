import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

STREAMLIT_URL = os.environ.get("STREAMLIT_APP_URL", "https://ai-risk-issue-dashboard.streamlit.app/")

def main():
    options = Options()
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    driver = webdriver.Chrome(options=options)
    try:
        print(f"Accessing {STREAMLIT_URL}...")
        driver.get(STREAMLIT_URL)
        time.sleep(5)
        
        # Look for the Streamlit 'Wake up' button
        wait = WebDriverWait(driver, 10)
        wake_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'get this app back up')]"))
        )
        wake_button.click()
        print("Wake-up button clicked successfully! ✅")
        time.sleep(5)
        
    except TimeoutException:
        print("No wake-up button found. The app is likely already awake. 👍")
    except Exception as e:
        print(f"An error occurred: {e}")
        exit(1)
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
