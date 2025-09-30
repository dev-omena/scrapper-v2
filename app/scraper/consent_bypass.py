"""
Aggressive consent page bypass for Google Maps scraper
"""
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from app.scraper.communicator import Communicator

class ConsentBypass:
    def __init__(self, driver):
        self.driver = driver
    
    def bypass_consent(self, encoded_query):
        """
        Aggressive consent page bypass with multiple strategies
        """
        current_url = self.driver.current_url
        page_title = self.driver.title
        
        if "consent.google.com" not in current_url and "Voordat je verdergaat" not in page_title:
            return True  # No consent page detected
        
        Communicator.show_message("Detected consent page, using aggressive bypass...")
        print("DEBUG: Detected consent page, using aggressive bypass")
        
        # Strategy 1: Multiple bypass URLs
        bypass_urls = [
            f"https://maps.google.com/maps/search/{encoded_query}/",
            f"https://www.google.com/maps/search/{encoded_query}/?hl=en",
            f"https://www.google.com/maps/search/{encoded_query}/?hl=ar",
            f"https://www.google.com/maps/search/{encoded_query}/@25.2854,51.5310,12z",
            f"https://maps.google.com/maps/search/{encoded_query}/?hl=en&gl=US",
            f"https://www.google.com/maps/search/{encoded_query}/?hl=en&gl=US"
        ]
        
        for i, url in enumerate(bypass_urls):
            try:
                Communicator.show_message(f"Trying bypass URL {i+1}/{len(bypass_urls)}")
                print(f"DEBUG: Trying bypass URL {i+1}: {url}")
                
                self.driver.get(url)
                time.sleep(2)
                
                current_url = self.driver.current_url
                page_title = self.driver.title
                
                print(f"DEBUG: After URL {i+1} - URL: {current_url}, Title: {page_title}")
                
                if "consent.google.com" not in current_url and "Voordat je verdergaat" not in page_title:
                    Communicator.show_message(f"Successfully bypassed consent with URL {i+1}!")
                    print(f"DEBUG: Successfully bypassed consent with URL {i+1}!")
                    return True
                    
            except Exception as e:
                Communicator.show_message(f"Bypass URL {i+1} failed: {str(e)}")
                print(f"DEBUG: Bypass URL {i+1} failed: {str(e)}")
                continue
        
        # Strategy 2: Quick button detection
        Communicator.show_message("All bypass URLs failed, trying quick button detection...")
        print("DEBUG: All bypass URLs failed, trying quick button detection")
        
        try:
            wait = WebDriverWait(self.driver, 2)  # 2 second timeout per selector
            
            quick_selectors = [
                "button[aria-label*='Accept']",
                "button[aria-label*='Accepteren']", 
                "button[aria-label*='Agree']",
                "button[aria-label*='Akkoord']",
                "//button[contains(text(), 'Accept')]",
                "//button[contains(text(), 'Accepteren')]",
                "//button[contains(text(), 'Agree')]",
                "//button[contains(text(), 'Akkoord')]"
            ]
            
            for selector in quick_selectors:
                try:
                    if selector.startswith("//"):
                        button = wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                    else:
                        button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                    
                    if button and button.is_displayed():
                        Communicator.show_message(f"Found consent button: {selector}")
                        print(f"DEBUG: Found consent button: {selector}")
                        
                        # Try to click
                        try:
                            button.click()
                            Communicator.show_message("Consent button clicked!")
                            print("DEBUG: Consent button clicked!")
                            time.sleep(2)
                            return True
                        except:
                            try:
                                self.driver.execute_script("arguments[0].click();", button)
                                Communicator.show_message("Consent button clicked via JavaScript!")
                                print("DEBUG: Consent button clicked via JavaScript!")
                                time.sleep(2)
                                return True
                            except:
                                continue
                                
                except TimeoutException:
                    continue
                except Exception as e:
                    continue
                    
        except Exception as e:
            Communicator.show_message(f"Quick button detection failed: {str(e)}")
            print(f"DEBUG: Quick button detection failed: {str(e)}")
        
        # Strategy 3: Force navigation
        Communicator.show_message("Trying force navigation...")
        print("DEBUG: Trying force navigation")
        
        try:
            # Try to navigate directly to the search results
            direct_url = f"https://www.google.com/maps/search/{encoded_query}/"
            self.driver.get(direct_url)
            time.sleep(3)
            
            current_url = self.driver.current_url
            if "consent.google.com" not in current_url:
                Communicator.show_message("Force navigation successful!")
                print("DEBUG: Force navigation successful!")
                return True
                
        except Exception as e:
            Communicator.show_message(f"Force navigation failed: {str(e)}")
            print(f"DEBUG: Force navigation failed: {str(e)}")
        
        Communicator.show_message("All consent bypass strategies failed, proceeding anyway...")
        print("DEBUG: All consent bypass strategies failed, proceeding anyway")
        return False

