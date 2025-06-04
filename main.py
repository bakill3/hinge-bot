import time
import random
from appium import webdriver
from appium.options.android import UiAutomator2Options
from selenium.common.exceptions import NoSuchElementException

# ---- SETUP ----
options = UiAutomator2Options()
options.platform_name = "Android"
options.device_name = "127.0.0.1:21503"
options.app_package = "co.hinge.app"
options.app_activity = "co.hinge.app.MainActivity"
options.automation_name = "UiAutomator2"
options.no_reset = True

driver = webdriver.Remote(
    command_executor='http://127.0.0.1:4723/wd/hub',
    options=options
)

def random_scroll():
    """Simulate human scroll behavior before liking."""
    if random.random() < 0.7:  # 70% chance to scroll before like
        print("Simulating a scroll to look more human...")
        size = driver.get_window_size()
        start_y = int(size["height"] * random.uniform(0.7, 0.8))
        end_y = int(size["height"] * random.uniform(0.3, 0.5))
        x = int(size["width"] * random.uniform(0.45, 0.55))
        driver.swipe(x, start_y, x, end_y, duration=random.randint(350, 900))
        time.sleep(random.uniform(0.5, 1.4))

def like_and_confirm():
    random_scroll()
    # 15% chance to skip this profile as "anti-ban"
    if random.random() < 0.15:
        print("Randomly decided to skip this profile to look more human.")
        ignore_profile()
        return False

    try:
        like_btn = driver.find_element("accessibility id", "Gostar")
        like_btn.click()
        print("Liked a profile!")
        time.sleep(random.uniform(0.7, 1.7))
        try:
            confirm_btn = driver.find_element("accessibility id", "Enviar gosto")
            confirm_btn.click()
            print("Sent a Like!")
            time.sleep(random.uniform(0.7, 1.2))
        except NoSuchElementException:
            print("No confirmation button (Enviar gosto) found, probably not needed.")
        return True
    except NoSuchElementException:
        print("Like button ('Gostar') not found.")
        return False

def ignore_profile():
    """Try to click the 'Ignorar [name]' button. Fallback to swipe if not found."""
    print("Trying to ignore/skip this profile...")
    try:
        # Find ANY button that starts with "Ignorar" (dynamic name)
        buttons = driver.find_elements("xpath", "//android.widget.Button[starts-with(@content-desc, 'Ignorar')]")
        if buttons:
            buttons[0].click()
            print("Ignored a profile using 'Ignorar' button!")
            time.sleep(random.uniform(0.6, 1.4))
        else:
            print("No 'Ignorar' button found, falling back to swipe left.")
            swipe_left()
    except Exception as e:
        print(f"Error during ignore_profile: {e}")
        swipe_left()

def swipe_left():
    print("Swiping left...")
    size = driver.get_window_size()
    start_x = int(size["width"] * 0.8)
    end_x = int(size["width"] * 0.2)
    y = int(size["height"] * 0.5)
    driver.swipe(start_x, y, end_x, y, duration=500)
    time.sleep(random.uniform(0.7, 1.3))

try:
    while True:
        liked = like_and_confirm()
        if not liked:
            ignore_profile()
        # Random wait to mimic real usage
        time.sleep(random.uniform(2, 3.5))
except KeyboardInterrupt:
    print("Stopped by user.")
finally:
    driver.quit()
