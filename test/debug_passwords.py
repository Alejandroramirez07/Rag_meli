# tests/debug_passwords.py
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def debug_login():
    """Debug the login process to see what's happening"""
    options = Options()
    options.add_argument("--headless")
    
    driver = webdriver.Firefox(options=options)
    
    try:
        driver.get("http://localhost:8501")
        
        print("🔍 Debugging login process...")
        
        # Check what's on the page
        print("Page title:", driver.title)
        print("Current URL:", driver.current_url)
        
        # Try to find login elements
        try:
            username_field = driver.find_element(By.CSS_SELECTOR, "input[placeholder*='username']")
            print("✅ Username field found")
        except:
            print("❌ Username field NOT found")
            # Try other selectors
            selectors = [
                "input[type='text']",
                "input[name*='user']",
                "input",
                ".stTextInput input"
            ]
            for selector in selectors:
                try:
                    element = driver.find_element(By.CSS_SELECTOR, selector)
                    print(f"✅ Found element with selector: {selector}")
                    print(f"   Placeholder: {element.get_attribute('placeholder')}")
                    print(f"   Type: {element.get_attribute('type')}")
                    print(f"   Name: {element.get_attribute('name')}")
                except:
                    pass
        
        # Take screenshot to see what's visible
        driver.save_screenshot("debug_login.png")
        print("📸 Screenshot saved as debug_login.png")
        
    finally:
        driver.quit()

if __name__ == "__main__":
    debug_login()