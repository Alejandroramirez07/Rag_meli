import time
import unittest
from selenium.webdriver.common.by import By
from test_base import BaseTest
from test_config import TestConfig

class TestAdminFeatures(BaseTest):
    
    def setUp(self):
        super().setUp()
        self.login_as_admin()
    
    def login_as_admin(self):
        """Helper method to login as admin"""
        username_field = self.wait_for_element(By.CSS_SELECTOR, "input[placeholder*='username']")
        password_field = self.driver.find_element(By.CSS_SELECTOR, "input[type='password']")
        login_button = self.driver.find_element(By.XPATH, "//button[contains(., 'Login')]")
        
        username_field.send_keys("admin")
        password_field.send_keys(TestConfig.TEST_USERS["admin"]["password"])
        login_button.click()
        
        self.wait_for_element(By.XPATH, "//h1[contains(., 'Meli Catalog Assistant')]")
    
    def test_admin_tools_visible(self):
        """Test that admin tools are visible to admin users"""
        admin_section = self.wait_for_element(By.XPATH, "//*[contains(text(), 'Admin Tools')]")
        self.assertTrue(admin_section.is_displayed())
        
        # Check for specific admin tools
        data_management = self.driver.find_element(By.XPATH, "//*[contains(text(), 'Data Management')]")
        system_management = self.driver.find_element(By.XPATH, "//*[contains(text(), 'System Management')]")
        
        self.assertTrue(data_management.is_displayed())
        self.assertTrue(system_management.is_displayed())
        
        self.take_screenshot("admin_tools_visible")
    
    def test_data_management_operations(self):
        """Test data management operations"""
        # Expand Data Management section
        data_management = self.wait_for_element(By.XPATH, "//*[contains(text(), 'Data Management')]")
        data_management.click()
        
        # Test re-ingest button
        reingest_button = self.wait_for_element(By.XPATH, "//button[contains(., 'Re-ingest All')]")
        self.assertTrue(reingest_button.is_displayed())
        
        self.take_screenshot("data_management_expanded")
    
    def test_system_health_check(self):
        """Test system health check functionality"""
        # Expand System Management section
        system_management = self.wait_for_element(By.XPATH, "//*[contains(text(), 'System Management')]")
        system_management.click()
        
        # Click system health button
        health_button = self.wait_for_element(By.XPATH, "//button[contains(., 'System Health')]")
        health_button.click()
        
        # Wait for health check results
        time.sleep(2)
        
        self.take_screenshot("system_health_check")