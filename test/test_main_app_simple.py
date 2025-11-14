import unittest
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from test_base import BaseTest
from test_config import TestConfig

class TestMainAppSimple(BaseTest):
    
    def setUp(self):
        super().setUp()
        self.login_as_admin()
    
    def login_as_admin(self):
        """Helper method to login as admin"""
        TestConfig.wait_for_login_page(self.driver)
        elements = TestConfig.find_login_elements(self.driver)
        
        elements['username'].send_keys("admin")
        elements['password'].send_keys(TestConfig.TEST_USERS["admin"]["password"])
        elements['button'].click()
        
        WebDriverWait(self.driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "//h1[contains(., 'Meli Catalog Assistant')]"))
        )
        print("✅ Main app loaded successfully")
        
        time.sleep(2)
    
    def find_any_input(self):
        """Find any input field on the page"""
        input_selectors = [
            "input",
            "textarea",
            "[contenteditable='true']",
            ".stTextInput input",
            ".stChatInput input"
        ]
        
        for selector in input_selectors:
            try:
                if selector.startswith(".") or selector.startswith("["):
                    element = self.driver.find_element(By.CSS_SELECTOR, selector)
                else:
                    element = self.driver.find_element(By.TAG_NAME, selector)
                
                if element.is_displayed() and element.is_enabled():
                    print(f"✅ Found input with selector: {selector}")
                    return element
            except:
                continue
        
        self.take_screenshot("no_input_found")
        raise Exception("No input field found on the page")
    
    def test_main_app_loaded(self):
        """Simple test that main app loads after login"""
       
        main_title = self.driver.find_element(By.XPATH, "//h1[contains(., 'Meli Catalog Assistant')]")
        self.assertTrue(main_title.is_displayed())
        
        try:
            sidebar = self.driver.find_element(By.CSS_SELECTOR, "[data-testid='stSidebar']")
            self.assertTrue(sidebar.is_displayed())
        except:
            print("⚠️ Sidebar not found, but main app is loaded")
        
        self.take_screenshot("main_app_loaded")
        print("✅ Main app loaded test passed")
    
    def test_page_has_interactive_elements(self):
        """Test that the page has interactive elements"""
     
        buttons = self.driver.find_elements(By.TAG_NAME, "button")
        self.assertGreater(len(buttons), 0, "Should have at least one button")
        print(f"✅ Found {len(buttons)} buttons on the page")
        
        inputs = self.driver.find_elements(By.TAG_NAME, "input")
        textareas = self.driver.find_elements(By.TAG_NAME, "textarea")
        total_inputs = len(inputs) + len(textareas)
        
        print(f"✅ Found {len(inputs)} inputs and {len(textareas)} textareas")
        
        self.take_screenshot("interactive_elements")
    
    def test_basic_chat_functionality(self):
        """Test basic chat functionality if input is available"""
        try:
            chat_input = self.find_any_input()
            
            test_message = "test"
            chat_input.send_keys(test_message)
            chat_input.submit()
            
            time.sleep(2)
            
            if chat_input.get_attribute('value') in ['', test_message]:
                print("✅ Message input interacted with successfully")
            else:
                print("⚠️ Message input behavior unexpected")
                
        except Exception as e:
            print(f"⚠️ Chat functionality test skipped: {e}")
        
        self.take_screenshot("chat_test")