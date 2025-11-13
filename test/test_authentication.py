# tests/test_authentication.py
import unittest
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from test_base import BaseTest
from test_config import TestConfig

class TestAuthentication(BaseTest):
    
    def test_login_page_loads(self):
        """Test that login page loads correctly"""
        # Wait for login page
        TestConfig.wait_for_login_page(self.driver)
        
        # Take screenshot
        self.take_screenshot("login_page")
        
        # Try to find login form elements
        elements = TestConfig.find_login_elements(self.driver)
        
        self.assertTrue(elements['username'].is_displayed())
        self.assertTrue(elements['password'].is_displayed())
        self.assertTrue(elements['button'].is_displayed())
    
    def test_admin_login_success(self):
        """Test successful admin login"""
        # Wait for login page and find elements
        TestConfig.wait_for_login_page(self.driver)
        elements = TestConfig.find_login_elements(self.driver)
        
        # Fill login form
        elements['username'].send_keys("admin")
        elements['password'].send_keys(TestConfig.TEST_USERS["admin"]["password"])
        elements['button'].click()
        
        # Wait for successful login - try multiple success indicators
        success_indicators = [
            "//h1[contains(., 'Meli Catalog Assistant')]",
            "//*[contains(text(), 'User: admin')]",
            "//*[contains(text(), 'Welcome admin')]",
            ".stChatInput",  # Chat input means we're in the main app
            "//button[contains(., 'Logout')]"  # Logout button means we're logged in
        ]
        
        success_found = False
        for indicator in success_indicators:
            try:
                element = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, indicator))
                )
                print(f"✅ Login success detected with: {indicator}")
                success_found = True
                break
            except:
                continue
        
        if not success_found:
            # Take screenshot to see what went wrong
            self.take_screenshot("login_failed")
            # Check if there's an error message
            try:
                error = self.driver.find_element(By.CLASS_NAME, "stAlert")
                print(f"❌ Login failed with error: {error.text}")
            except:
                print("❌ Login failed - no error message found")
            
            self.fail("Admin login failed")
        
        self.take_screenshot("admin_login_success")
    
    def test_user_login_success(self):
        """Test successful user login"""
        TestConfig.wait_for_login_page(self.driver)
        elements = TestConfig.find_login_elements(self.driver)
        
        elements['username'].send_keys("user")
        elements['password'].send_keys(TestConfig.TEST_USERS["user"]["password"])
        elements['button'].click()
        
        # Wait for successful login
        success_indicators = [
            "//h1[contains(., 'Meli Catalog Assistant')]",
            "//*[contains(text(), 'User: user')]",
            ".stChatInput"
        ]
        
        for indicator in success_indicators:
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, indicator))
                )
                break
            except:
                continue
        else:
            self.take_screenshot("user_login_failed")
            self.fail("User login failed")
        
        # Verify admin tools are NOT visible to regular users
        admin_tools = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'Admin Tools')]")
        self.assertEqual(len(admin_tools), 0, "Admin tools should not be visible to regular users")
        
        self.take_screenshot("user_login_success")
    
    def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        TestConfig.wait_for_login_page(self.driver)
        elements = TestConfig.find_login_elements(self.driver)
        
        elements['username'].send_keys("invalid_user")
        elements['password'].send_keys("wrong_password")
        elements['button'].click()
        
        # Wait for error message - try multiple error indicators
        error_indicators = [
            "//*[contains(@class, 'stAlert')]",
            "//*[contains(@class, 'error')]",
            "//*[contains(text(), 'Invalid')]",
            "//*[contains(text(), 'Error')]",
            "//*[contains(text(), 'incorrect')]"
        ]
        
        error_found = False
        for indicator in error_indicators:
            try:
                error_element = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, indicator))
                )
                print(f"✅ Error message found: {error_element.text}")
                error_found = True
                break
            except:
                continue
        
        self.assertTrue(error_found, "No error message shown for invalid credentials")
        self.take_screenshot("login_invalid_credentials")
    
    def test_logout_functionality(self):
        """Test logout functionality"""
        # Login first
        self.test_admin_login_success()
        
        # Find and click logout button
        logout_indicators = [
            "//button[contains(., 'Logout')]",
            "//*[contains(text(), 'Logout')]",
            "//button[contains(., '🚪')]"  # Logout emoji
        ]
        
        logout_button = None
        for indicator in logout_indicators:
            try:
                logout_button = self.driver.find_element(By.XPATH, indicator)
                break
            except:
                continue
        
        self.assertIsNotNone(logout_button, "Logout button not found")
        logout_button.click()
        
        # Verify redirected to login page
        TestConfig.wait_for_login_page(self.driver)
        self.take_screenshot("logout_success")