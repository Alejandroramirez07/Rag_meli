# tests/test_element_finder.py
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class ElementFinder:
    @staticmethod
    def find_chat_input(driver, timeout=10):
        """Find chat input with multiple strategies"""
        selectors = [
            ".stChatInput input",
            "input[data-testid='stChatInput']",
            "input[placeholder*='message']",
            "input[placeholder*='question']",
            "input[placeholder*='type']",
            "textarea",  # Sometimes it's a textarea
            "//input | //textarea",  # Any input or textarea
        ]
        
        for selector in selectors:
            try:
                if selector.startswith("//"):
                    element = WebDriverWait(driver, timeout).until(
                        EC.presence_of_element_located((By.XPATH, selector))
                    )
                else:
                    element = WebDriverWait(driver, timeout).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                print(f"✅ Chat input found with: {selector}")
                return element
            except:
                continue
        
        # Take screenshot for debugging
        driver.save_screenshot("chat_input_not_found.png")
        raise Exception("Chat input not found with any selector")
    
    @staticmethod
    def find_sidebar_elements(driver, timeout=10):
        """Find sidebar elements"""
        elements = {}
        
        # User info
        user_selectors = [
            "//*[contains(text(), 'User:')]",
            "//*[contains(text(), 'admin')]",
            "//*[contains(text(), 'user')]",
            ".sidebar [data-testid='stSidebar'] *"
        ]
        
        for selector in user_selectors:
            try:
                elements['user'] = driver.find_element(By.XPATH, selector)
                print(f"✅ User element found with: {selector}")
                break
            except:
                continue
        
        return elements
    
    @staticmethod
    def find_admin_tools(driver, timeout=10):
        """Find admin tools elements"""
        admin_selectors = [
            "//*[contains(text(), 'Admin Tools')]",
            "//*[contains(text(), 'Data Management')]",
            "//*[contains(text(), 'System Management')]",
            "//button[contains(., 'Re-ingest')]"
        ]
        
        for selector in admin_selectors:
            try:
                element = WebDriverWait(driver, timeout).until(
                    EC.presence_of_element_located((By.XPATH, selector))
                )
                print(f"✅ Admin element found with: {selector}")
                return element
            except:
                continue
        
        return None