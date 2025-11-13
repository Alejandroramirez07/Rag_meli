# tests/test_config.py
import os
import time
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.firefox import GeckoDriverManager

class TestConfig:
    BASE_URL = "http://localhost:8501"
    WAIT_TIMEOUT = 30
    SCREENSHOT_DIR = "test_screenshots"
    
    # Test credentials - UPDATE THESE TO MATCH YOUR ACTUAL PASSWORDS!
    TEST_USERS = {
        "admin": {"password": "admin", "role": "admin"},  # CHANGE THIS
        "user": {"password": "user", "role": "user"}      # CHANGE THIS
    }
    
    @classmethod
    def setup_driver(cls):
        """Setup Firefox driver with better error handling"""
        firefox_options = Options()
        firefox_options.add_argument("--headless")
        firefox_options.add_argument("--width=1920")
        firefox_options.add_argument("--height=1080")
        firefox_options.add_argument("--no-sandbox")
        
        try:
            service = Service(GeckoDriverManager().install())
            driver = webdriver.Firefox(service=service, options=firefox_options)
            print("✅ Firefox driver started with webdriver-manager")
        except Exception as e:
            print(f"⚠️  webdriver-manager failed: {e}")
            try:
                driver = webdriver.Firefox(options=firefox_options)
                print("✅ Firefox driver started with system Firefox")
            except Exception as e2:
                print(f"❌ All Firefox options failed: {e2}")
                raise Exception("Could not start Firefox. Please install Firefox browser.")
        
        driver.implicitly_wait(cls.WAIT_TIMEOUT)
        return driver
    
    @classmethod
    def create_screenshot_dir(cls):
        """Create directory for test screenshots"""
        if not os.path.exists(cls.SCREENSHOT_DIR):
            os.makedirs(cls.SCREENSHOT_DIR)
    
    @classmethod
    def wait_for_login_page(cls, driver, timeout=30):
        """Wait for login page to load with multiple element checks"""
        wait = WebDriverWait(driver, timeout)
        
        # Try multiple possible login page indicators
        selectors = [
            "//h1[contains(., 'Login')]",
            "//h1[contains(., 'Meli Catalog Assistant')]",
            "//input[@type='password']",
            "//button[contains(., 'Login')]",
            "//input[contains(@placeholder, 'username')]",
            "//input[contains(@placeholder, 'user')]"
        ]
        
        for selector in selectors:
            try:
                element = wait.until(EC.presence_of_element_located((By.XPATH, selector)))
                print(f"✅ Login page element found: {selector}")
                return True
            except:
                continue
        
        raise Exception("Login page not detected")
    
    @classmethod
    def find_login_elements(cls, driver):
        """Find login form elements with multiple selector strategies"""
        elements = {}
        
        # Username field selectors
        username_selectors = [
            "input[placeholder*='username']",
            "input[placeholder*='user']", 
            "input[type='text']",
            "input[name*='user']",
            ".stTextInput input:first-of-type"
        ]
        
        # Password field selectors  
        password_selectors = [
            "input[type='password']",
            "input[placeholder*='password']",
            ".stTextInput input[type='password']"
        ]
        
        # Login button selectors
        button_selectors = [
            "//button[contains(., 'Login')]",
            "//button[@type='submit']",
            "//div[contains(@class, 'stButton')]//button"
        ]
        
        # Find username field
        for selector in username_selectors:
            try:
                elements['username'] = driver.find_element(By.CSS_SELECTOR, selector)
                print(f"✅ Username field found with: {selector}")
                break
            except:
                continue
        
        # Find password field
        for selector in password_selectors:
            try:
                elements['password'] = driver.find_element(By.CSS_SELECTOR, selector)
                print(f"✅ Password field found with: {selector}")
                break
            except:
                continue
        
        # Find login button
        for selector in button_selectors:
            try:
                elements['button'] = driver.find_element(By.XPATH, selector)
                print(f"✅ Login button found with: {selector}")
                break
            except:
                continue
        
        if not all(key in elements for key in ['username', 'password', 'button']):
            missing = [key for key in ['username', 'password', 'button'] if key not in elements]
            raise Exception(f"Could not find login elements: {missing}")
        
        return elements