"""
Improved scraper with better search handling and debugging
"""

import time
from time import sleep
from scraper.base import Base
from scraper.improved_scroller import ImprovedScroller
import undetected_chromedriver as uc
from settings import DRIVER_EXECUTABLE_PATH
from scraper.communicator import Communicator
import urllib.parse

class ImprovedBackend(Base):
    
    def __init__(self, searchquery, outputformat, healdessmode):
        self.searchquery = searchquery
        self.headlessMode = healdessmode
        self.outputformat = outputformat
        
        self.init_driver()
        self.scroller = ImprovedScroller(driver=self.driver)
        self.init_communicator()

    def init_communicator(self):
        Communicator.set_backend_object(self)

    def init_driver(self):
        options = uc.ChromeOptions()
        if self.headlessMode == 1:
            options.headless = True

        # Add Chrome options for Railway compatibility
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-extensions')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        options.add_argument('--disable-blink-features=AutomationControlled')
        
        # Add options to minimize consent pages
        options.add_argument('--disable-features=VizDisplayCompositor')
        options.add_argument('--disable-ipc-flooding-protection')
        options.add_argument('--disable-hang-monitor')
        options.add_argument('--disable-prompt-on-repost')
        options.add_argument('--disable-domain-reliability')
        options.add_argument('--disable-background-networking')
        options.add_argument('--disable-sync')
        options.add_argument('--disable-translate')
        options.add_argument('--disable-logging')
        options.add_argument('--disable-permissions-api')
        options.add_argument('--disable-notifications')
        options.add_argument('--disable-plugins-discovery')
        options.add_argument('--disable-preconnect')
        options.add_argument('--disable-background-timer-throttling')
        options.add_argument('--disable-renderer-backgrounding')
        options.add_argument('--disable-backgrounding-occluded-windows')
        
        # Disable images for faster loading
        prefs = {"profile.managed_default_content_settings.images": 2}
        options.add_experimental_option("prefs", prefs)

        Communicator.show_message("Initializing Chrome driver...")
        
        try:
            if DRIVER_EXECUTABLE_PATH is not None:
                self.driver = uc.Chrome(
                    driver_executable_path=DRIVER_EXECUTABLE_PATH, options=options)
            else:
                self.driver = uc.Chrome(options=options)
        except NameError:
            self.driver = uc.Chrome(options=options)
        
        Communicator.show_message("Chrome driver initialized successfully")
        self.driver.maximize_window()
        self.driver.implicitly_wait(self.timeout)

    def format_search_query(self, query):
        """Format search query for better Google Maps results"""
        # Remove extra spaces and format
        query = ' '.join(query.split())
        
        # Add location context if not present
        location_indicators = ['في', 'in', 'at', 'near', 'close to']
        has_location = any(indicator in query.lower() for indicator in location_indicators)
        
        if not has_location:
            Communicator.show_message("Adding location context to search query...")
            # You can customize this based on your needs
            query = f"{query} near me"
        
        return query

    def mainscraping(self):
        try:
            # Format the search query
            formatted_query = self.format_search_query(self.searchquery)
            Communicator.show_message(f"Formatted search query: {formatted_query}")
            
            # URL encode the query
            encoded_query = urllib.parse.quote_plus(formatted_query)
            link_of_page = f"https://www.google.com/maps/search/{encoded_query}/"
            
            Communicator.show_message(f"Searching: {link_of_page}")
            
            # Navigate to the search page
            self.openingurl(url=link_of_page)
            
            Communicator.show_message("Page loaded, starting search...")
            sleep(3)  # Give more time for the page to load
            
            # Check if we're on the right page
            current_url = self.driver.current_url
            Communicator.show_message(f"Current URL: {current_url}")
            
            # Check for any error messages or redirects
            page_title = self.driver.title
            Communicator.show_message(f"Page title: {page_title}")
            
            # Handle Google consent page
            if "consent.google.com" in current_url or "Voordat je verdergaat" in page_title:
                Communicator.show_message("Detected Google consent page, attempting to accept...")
                consent_start_time = time.time()
                consent_timeout = 30  # 30 seconds timeout for consent handling
                
                try:
                    # Try to find and click accept button (multiple languages and methods)
                    accept_selectors = [
                        # English buttons
                        "button[aria-label*='Accept']",
                        "button[aria-label*='I agree']",
                        "button[aria-label*='Agree']",
                        "button[aria-label*='Accept all']",
                        "button[aria-label*='I accept']",
                        "button[aria-label*='Accept all cookies']",
                        # Dutch buttons
                        "button[aria-label*='Accepteren']",
                        "button[aria-label*='Akkoord']",
                        "button[aria-label*='Alles accepteren']",
                        # Generic buttons
                        "button[type='submit']",
                        "button[data-value='Accept']",
                        "button[data-value='Agree']",
                        # Text-based selectors
                        "//button[contains(text(), 'Accept')]",
                        "//button[contains(text(), 'Agree')]",
                        "//button[contains(text(), 'Accepteren')]",
                        "//button[contains(text(), 'Akkoord')]",
                        "//button[contains(text(), 'I agree')]",
                        "//button[contains(text(), 'Accept all')]",
                        "//button[contains(text(), 'Alles accepteren')]",
                        # Form buttons
                        "form button",
                        "div[role='button']",
                        # ID-based selectors
                        "#accept",
                        "#agree",
                        "#accept-all"
                    ]
                    
                    consent_clicked = False
                    for selector in accept_selectors:
                        # Check timeout
                        if time.time() - consent_start_time > consent_timeout:
                            Communicator.show_message("Consent handling timeout reached")
                            break
                            
                        try:
                            if selector.startswith("//"):
                                # XPath selector
                                button = self.driver.find_element("xpath", selector)
                            elif ":contains(" in selector:
                                # Use XPath for text content
                                text = selector.split(':contains(')[1].split(')')[0]
                                xpath = f"//button[contains(text(), '{text}')]"
                                button = self.driver.find_element("xpath", xpath)
                            else:
                                # CSS selector
                                button = self.driver.find_element("css selector", selector)
                            
                            if button and button.is_displayed():
                                Communicator.show_message(f"Found consent button: {selector}")
                                # Try multiple click methods
                                try:
                                    button.click()
                                except:
                                    try:
                                        self.driver.execute_script("arguments[0].click();", button)
                                    except:
                                        self.driver.execute_script("arguments[0].dispatchEvent(new MouseEvent('click', {bubbles: true}));", button)
                                
                                sleep(3)
                                consent_clicked = True
                                break
                        except Exception as e:
                            Communicator.show_message(f"Selector {selector} failed: {str(e)}")
                            continue
                    
                    if not consent_clicked:
                        Communicator.show_message("Could not find consent button, trying alternative approach...")
                        # Try to find any clickable element on the page
                        try:
                            all_buttons = self.driver.find_elements("tag name", "button")
                            for button in all_buttons:
                                if button.is_displayed():
                                    button_text = button.text.lower()
                                    if any(word in button_text for word in ['accept', 'agree', 'accepteren', 'akkoord', 'ok', 'continue']):
                                        Communicator.show_message(f"Found alternative button: {button_text}")
                                        button.click()
                                        sleep(3)
                                        break
                        except Exception as e:
                            Communicator.show_message(f"Alternative approach failed: {str(e)}")
                    
                    # Wait for redirect to actual search page
                    sleep(3)
                    current_url = self.driver.current_url
                    Communicator.show_message(f"After consent, current URL: {current_url}")
                    
                except Exception as e:
                    Communicator.show_message(f"Error handling consent page: {str(e)}")
            
            # Check if we're still on consent page
            if "consent.google.com" in self.driver.current_url:
                Communicator.show_message("Still on consent page, trying alternative approach...")
                
                # Try multiple alternative approaches
                alternative_urls = [
                    f"https://www.google.com/maps/search/{encoded_query}/@25.2854,51.5310,12z",
                    f"https://maps.google.com/maps/search/{encoded_query}/",
                    f"https://www.google.com/maps/search/{encoded_query}/?hl=en",
                    f"https://www.google.com/maps/search/{encoded_query}/?hl=ar"
                ]
                
                for i, alt_url in enumerate(alternative_urls):
                    try:
                        Communicator.show_message(f"Trying alternative URL {i+1}: {alt_url}")
                        self.driver.get(alt_url)
                        sleep(3)
                        
                        current_url = self.driver.current_url
                        Communicator.show_message(f"After alternative URL, current URL: {current_url}")
                        
                        if "consent.google.com" not in current_url:
                            Communicator.show_message("Successfully bypassed consent page!")
                            break
                    except Exception as e:
                        Communicator.show_message(f"Alternative URL {i+1} failed: {str(e)}")
                        continue
                
                # If still on consent page, try to get page source for debugging
                if "consent.google.com" in self.driver.current_url:
                    Communicator.show_message("All alternative URLs failed, getting page source for debugging...")
                    try:
                        page_source = self.driver.page_source
                        # Look for any buttons in the page source
                        if "button" in page_source.lower():
                            Communicator.show_message("Found buttons in page source, trying to extract...")
                            # Try to find buttons using BeautifulSoup
                            from bs4 import BeautifulSoup
                            soup = BeautifulSoup(page_source, 'html.parser')
                            buttons = soup.find_all('button')
                            Communicator.show_message(f"Found {len(buttons)} buttons on the page")
                            
                            for i, button in enumerate(buttons[:5]):  # Check first 5 buttons
                                button_text = button.get_text(strip=True)
                                button_attrs = button.attrs
                                Communicator.show_message(f"Button {i+1}: text='{button_text}', attrs={button_attrs}")
                        else:
                            Communicator.show_message("No buttons found in page source")
                    except Exception as e:
                        Communicator.show_message(f"Error analyzing page source: {str(e)}")
            
            # Start scrolling and scraping
            self.scroller.scroll()
            
        except Exception as e:
            Communicator.show_message(f"Error occurred while scraping. Error: {str(e)}")
            # Try to get more debug information
            try:
                current_url = self.driver.current_url
                page_source = self.driver.page_source[:500]  # First 500 chars
                Communicator.show_message(f"Debug - Current URL: {current_url}")
                Communicator.show_message(f"Debug - Page source preview: {page_source}")
            except:
                pass

        finally:
            try:
                Communicator.show_message("Closing the driver")
                self.driver.close()
                self.driver.quit()
            except:
                pass

            Communicator.end_processing()
            Communicator.show_message("Scraping session completed")
