import time 
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions 
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, NoSuchWindowException

def check_servientrega_status(tracking_number):
    """
    Automates the browser to check the Servientrega tracking status 
    by navigating directly to the results URL.
    """
    
    url = f"https://mobile.servientrega.com/WebSitePortal/RastreoEnvioDetalle.html?Guia={tracking_number}"
    
    # Configuration for running the Chrome browser
    options = ChromeOptions() 
    
    options.add_argument('--headless')      
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument("--window-size=1920,1080")
    
    # Initialize the WebDriver
    driver = webdriver.Chrome(options=options) 

    try:
        print(f"Checking tracking number: {tracking_number}...")
        
        # 1. DIRECT NAVIGATION: Go straight to the results page
        driver.get(url)
        
        # --- Locators confirmed from HTML inspection ---
        STATUS_LABEL_ID = "lblEstadoActual" 
        
        # 2. Wait for the status text to appear (45s max timeout)
        status_element = WebDriverWait(driver, 45).until( 
            EC.visibility_of_element_located((By.ID, STATUS_LABEL_ID))
        )
        
        # 3. Extract the status text
        status_text = status_element.text.strip()
        
        if not status_text:
             # Fallback to checking the parent H1 element
             h1_xpath = "//div[@class='tittle_cotizador']/div[1]/h1"
             h1_element = driver.find_element(By.XPATH, h1_xpath)
             status_text = h1_element.text.strip()
        
        return status_text

    except TimeoutException:
        return "ERROR: Status check timed out. Tracking information took too long to load or site structure changed."
    except NoSuchElementException:
        return "ERROR: Could not find the required status element. The tracking number may be invalid or the site structure changed."
    except NoSuchWindowException:
        return "ERROR: Browser window closed unexpectedly. Check if Chrome is installed correctly."
    except Exception as e:
        return f"ERROR: An unknown error occurred - {e}"
    finally:
        driver.quit()

# --- TESTING BLOCK ---

if __name__ == "__main__":
    test_tracking_number = "2259180939" 
    
    print("\nStarting Servientrega tracking check (Direct URL Method)...")
    status = check_servientrega_status(test_tracking_number)
    
    print(f"\nTracking Number: {test_tracking_number}")
    print(f"Final Status: {status}")
    print("\nTesting complete.")

# ---------------------