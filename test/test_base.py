# tests/test_base.py
import time
import unittest
from selenium.webdriver.common.by import By 
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Import TestConfig directly
from test_config import TestConfig

class BaseTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.driver = TestConfig.setup_driver()
        TestConfig.create_screenshot_dir()
    
    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, 'driver') and cls.driver:
            cls.driver.quit()
    
    def setUp(self):
        self.driver.get(TestConfig.BASE_URL)
        self.wait = WebDriverWait(self.driver, TestConfig.WAIT_TIMEOUT)
    
    def take_screenshot(self, name):
        """Take screenshot for debugging"""
        filename = f"{TestConfig.SCREENSHOT_DIR}/{name}_{int(time.time())}.png"
        self.driver.save_screenshot(filename)
        return filename
    
    def wait_for_element(self, by, value, timeout=None):
        """Wait for element to be present"""
        wait = WebDriverWait(self.driver, timeout or TestConfig.WAIT_TIMEOUT)
        return wait.until(EC.presence_of_element_located((by, value)))
    
    def wait_for_text(self, by, value, text, timeout=None):
        """Wait for element to contain specific text"""
        wait = WebDriverWait(self.driver, timeout or TestConfig.WAIT_TIMEOUT)
        return wait.until(EC.text_to_be_present_in_element((by, value), text))