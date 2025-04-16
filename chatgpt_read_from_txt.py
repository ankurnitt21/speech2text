import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import threading

# Global lock to synchronize file access
file_lock = threading.Lock()

# Configuration
CHROMEDRIVER_PATH = r"C:\Users\ankur\PycharmProjects\InterviewCracker\chromedriver\chromedriver-win64\chromedriver.exe"
WAIT_TIMEOUT = 0.5  # Increased timeout for more reliability
MESSAGE_FILE = "messages.txt"
CHECK_INTERVAL = 1  # More frequent checks
#MAX_RETRIES = 3  # Max send attempts


def initialize_browser():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    return webdriver.Chrome(executable_path=CHROMEDRIVER_PATH, options=options)


def is_chatgpt_typing(driver):
    """Check if ChatGPT is currently typing by looking for the stop button"""
    try:
        stop_button = driver.find_elements(
            By.CSS_SELECTOR,
            "button[data-testid='stop-button']"
        )
        return len(stop_button) > 0 and stop_button[0].is_displayed()
    except:
        return False


def send_buffered_messages(driver, messages):
    """Send all buffered messages when ChatGPT is ready"""
    try:
        # Wait until ChatGPT stops typing (stop button disappears)
        while is_chatgpt_typing(driver):
            print("⏳ ChatGPT is typing, waiting...")
            time.sleep(1)

        # Find input box
        input_box = WebDriverWait(driver, WAIT_TIMEOUT).until(
            EC.presence_of_element_located((
                By.XPATH,
                "//*[@data-placeholder='Ask anything']/.. | "
                "//textarea[contains(@id, 'prompt')] | "
                "//div[@role='textbox']"
            ))
        )

        # Combine messages with double newlines
        combined_message = "\n\n".join(messages)
        input_box.clear()
        input_box.send_keys(combined_message)

        # Check for special submit buttons
        try:
            # Look for the arrow submit button (first SVG path)
            submit_arrow = driver.find_elements(
                By.XPATH,
                "//*[contains(@d, 'M15.1918 8.90615')]"
            )
            # Look for the voice button (second SVG path)
            voice_button = driver.find_elements(
                By.XPATH,
                "//button[@data-testid='composer-speech-button']"
            )

            if submit_arrow and submit_arrow[0].is_displayed() or (voice_button and voice_button[0].is_displayed()):
                print("🔼 Clicking arrow submit button")
                submit_arrow[0].click()

        except Exception as e:
            print(f"⚠️ Couldn't find special buttons, using Enter: {str(e)}")
            input_box.send_keys(Keys.RETURN)

        print(f"✉️ Sent {len(messages)} buffered messages")

        return True

    except Exception as e:
        print(f"❌ Failed to send messages: {str(e)}")
        return False

def monitor_file_and_chat(driver):
    """Monitor file and buffer messages"""
    global file_lock
    last_position = 0
    message_buffer = []

    if not os.path.exists(MESSAGE_FILE):
        print(f"⚠️ Creating message file: {MESSAGE_FILE}")
        open(MESSAGE_FILE, 'a').close()

    print(f"🔍 Monitoring '{MESSAGE_FILE}' for messages...")

    while True:
        try:
            with file_lock:
                with open(MESSAGE_FILE, 'r') as file:
                    file.seek(last_position)
                    new_content = file.read()
                    last_position = file.tell()

                    if new_content:
                        new_messages = [msg.strip() for msg in new_content.split('\n') if msg.strip()]
                        message_buffer.extend(new_messages)
                        print(f"📥 Buffered {len(new_messages)} new messages (Total: {len(message_buffer)})")

                        if message_buffer and send_buffered_messages(driver, message_buffer):
                            message_buffer = []  # Clear buffer on success

        except FileNotFoundError:
            print(f"⚠️ File missing, recreating: {MESSAGE_FILE}")
            open(MESSAGE_FILE, 'a').close()
        except Exception as e:
            print(f"⚠️ Error: {str(e)}")

        #time.sleep(CHECK_INTERVAL)


def run_chatgpt_automation():
    driver = None
    try:
        driver = initialize_browser()
        print("🚀 Browser launched")

        print("🌐 Loading ChatGPT...")
        driver.get("https://chat.openai.com")

        WebDriverWait(driver, 5).until(
            lambda d: "chat" in d.current_url.lower() or "login" in d.current_url.lower()
        )

        #handle_login(driver)
        monitor_file_and_chat(driver)

    except Exception as e:
        print(f"❌ Fatal error: {str(e)}")
    finally:
        if driver:
            print("🛑 Browser remains open")


if __name__ == "__main__":
    run_chatgpt_automation()