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
from webdriver_manager.chrome import ChromeDriverManager

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
        
        # Add Chrome binary path for DigitalOcean
        options.binary_location = "/opt/google/chrome/chrome"
        
        if self.headlessMode == 1:
            options.headless = True

        # Essential Chrome options
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-extensions')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--no-first-run')
        options.add_argument('--no-default-browser-check')
        options.add_argument('--disable-popup-blocking')
        
        # Disable images for faster loading
        prefs = {
            "profile.managed_default_content_settings.images": 2,
            "profile.default_content_setting_values.notifications": 2
        }
        options.add_experimental_option("prefs", prefs)

        Communicator.show_message("Initializing Chrome driver...")
        
        try:
            # Get Chrome version
            import subprocess
            import re
            
            chrome_version_full = None
            chrome_major_version = None
            
            try:
                chrome_version_output = subprocess.check_output(["/opt/google/chrome/chrome", "--version"]).decode().strip()
                Communicator.show_message(f"Chrome version: {chrome_version_output}")
                print(f"DEBUG: Chrome version output: {chrome_version_output}")
                
                # Extract version number (e.g., "141.0.7390.54" from "Google Chrome 141.0.7390.54")
                version_match = re.search(r'(\d+)\.(\d+)\.(\d+)\.(\d+)', chrome_version_output)
                if version_match:
                    chrome_version_full = version_match.group(0)
                    chrome_major_version = int(version_match.group(1))
                    Communicator.show_message(f"Detected Chrome version: {chrome_version_full} (major: {chrome_major_version})")
                    print(f"DEBUG: Parsed Chrome version: {chrome_version_full}, major: {chrome_major_version}")
            except Exception as e:
                Communicator.show_message(f"Could not determine Chrome version: {str(e)}")
                print(f"DEBUG: Error getting Chrome version: {str(e)}")
            
            # Strategy 1: Let undetected_chromedriver handle everything (BEST for latest Chrome)
            Communicator.show_message("Using undetected_chromedriver auto-mode (recommended for Chrome 141+)...")
            print("DEBUG: Attempting undetected_chromedriver auto-mode")
            
            try:
                # undetected_chromedriver will automatically download the correct driver
                self.driver = uc.Chrome(
                    options=options,
                    version_main=chrome_major_version if chrome_major_version else None
                )
                Communicator.show_message("Chrome driver initialized successfully (auto-mode)")
                print("DEBUG: undetected_chromedriver auto-mode succeeded")
                
            except Exception as uc_error:
                Communicator.show_message(f"Auto-mode failed: {str(uc_error)}")
                print(f"DEBUG: undetected_chromedriver auto-mode failed: {str(uc_error)}")
                
                # Strategy 2: Try WebDriver Manager with specific version
                if chrome_major_version:
                    try:
                        Communicator.show_message(f"Trying WebDriver Manager for Chrome {chrome_major_version}...")
                        print(f"DEBUG: Trying WebDriver Manager with version {chrome_major_version}")
                        
                        # Try to get the specific driver version
                        from webdriver_manager.core.utils import ChromeType
                        driver_path = ChromeDriverManager(chrome_type=ChromeType.GOOGLE).install()
                        
                        Communicator.show_message(f"ChromeDriver path: {driver_path}")
                        print(f"DEBUG: ChromeDriver path: {driver_path}")
                        
                        self.driver = uc.Chrome(
                            driver_executable_path=driver_path,
                            options=options
                        )
                        Communicator.show_message("Chrome driver initialized with WebDriver Manager")
                        print("DEBUG: WebDriver Manager succeeded")
                        
                    except Exception as wdm_error:
                        Communicator.show_message(f"WebDriver Manager failed: {str(wdm_error)}")
                        print(f"DEBUG: WebDriver Manager failed: {str(wdm_error)}")
                        
                        # Strategy 3: Manual path as last resort
                        if DRIVER_EXECUTABLE_PATH is not None:
                            Communicator.show_message("Trying manual ChromeDriver path...")
                            self.driver = uc.Chrome(
                                driver_executable_path=DRIVER_EXECUTABLE_PATH,
                                options=options
                            )
                            Communicator.show_message("Chrome driver initialized (manual path)")
                        else:
                            raise wdm_error
                else:
                    raise uc_error
                    
        except Exception as e:
            error_msg = f"Chrome driver initialization failed: {str(e)}"
            Communicator.show_message(error_msg)
            print(f"ERROR: {error_msg}")
            
            # Provide helpful error message
            if "version" in str(e).lower():
                Communicator.show_message("TIP: Chrome and ChromeDriver versions must match!")
                Communicator.show_message("Try: pip install --upgrade undetected-chromedriver")
            
            raise e
        
        self.driver.maximize_window()
        self.driver.implicitly_wait(self.timeout)

    def format_search_query(self, query):
        """Format search query for better Google Maps results"""
        # Remove extra spaces and format
        query = ' '.join(query.split())
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
            
            # Single wait time - reduced from multiple waits
            sleep(5)  # One consolidated wait for page to fully load
            
            # Check if we're on the right page
            current_url = self.driver.current_url
            Communicator.show_message(f"Current URL: {current_url}")
            
            # Check for any error messages or redirects
            page_title = self.driver.title
            Communicator.show_message(f"Page title: {page_title}")
            
            # Handle Google consent page
            if "consent.google.com" in current_url:
                Communicator.show_message("WARNING: Detected consent page - Google may be blocking automated access")
                print("DEBUG: On consent page - this is a blocking issue")
                
                # Try to click reject/accept buttons
                try:
                    # Try to find and click accept button
                    accept_selectors = [
                        "button[aria-label*='Accept']",
                        "button[aria-label*='agree']",
                        "button[aria-label*='Agree']",
                        "button:contains('Accept')",
                        "form[action*='consent'] button[type='submit']"
                    ]
                    
                    for selector in accept_selectors:
                        try:
                            button = self.driver.find_element("css selector", selector)
                            if button:
                                button.click()
                                sleep(2)
                                
                                if "consent.google.com" not in self.driver.current_url:
                                    Communicator.show_message("Successfully bypassed consent page!")
                                    break
                        except:
                            continue
                    
                except Exception as e:
                    print(f"DEBUG: Could not bypass consent: {str(e)}")
                
                # If still on consent page, we can't proceed
                if "consent.google.com" in self.driver.current_url:
                    Communicator.show_message("ERROR: Cannot bypass consent page. Google is blocking automated access.")
                    Communicator.show_message("Suggestion: Try running without headless mode or from a different IP/location.")
                    return
            
            # Start scrolling and scraping
            Communicator.show_message("DEBUG: About to call scroller.scroll()")
            print("DEBUG: About to call scroller.scroll()")
            self.scroller.scroll()
            Communicator.show_message("DEBUG: Scroller.scroll() completed")
            print("DEBUG: Scroller.scroll() completed")
            
        except Exception as e:
            Communicator.show_message(f"Error occurred while scraping. Error: {str(e)}")
            import traceback
            traceback.print_exc()
            
            # Try to get more debug information
            try:
                current_url = self.driver.current_url
                page_source = self.driver.page_source[:500]
                Communicator.show_message(f"Debug - Current URL: {current_url}")
                print(f"DEBUG - Page source preview: {page_source}")
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