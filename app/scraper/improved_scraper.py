"""
Improved scraper with better search handling and debugging
"""

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
                try:
                    # Try to find and click accept button
                    accept_selectors = [
                        "button[aria-label*='Accept']",
                        "button[aria-label*='I agree']",
                        "button[aria-label*='Agree']",
                        "button[aria-label*='Accept all']",
                        "button[aria-label*='I accept']",
                        "button:contains('Accept')",
                        "button:contains('I agree')",
                        "button:contains('Agree')",
                        "button:contains('Accept all')",
                        "button:contains('I accept')"
                    ]
                    
                    for selector in accept_selectors:
                        try:
                            if ":contains(" in selector:
                                # Use XPath for text content
                                xpath = f"//button[contains(text(), '{selector.split(':contains(')[1].split(')')[0]}')]"
                                button = self.driver.find_element("xpath", xpath)
                            else:
                                button = self.driver.find_element("css selector", selector)
                            
                            if button:
                                Communicator.show_message(f"Found consent button: {selector}")
                                button.click()
                                sleep(2)
                                break
                        except:
                            continue
                    
                    # Wait for redirect to actual search page
                    sleep(3)
                    current_url = self.driver.current_url
                    Communicator.show_message(f"After consent, current URL: {current_url}")
                    
                except Exception as e:
                    Communicator.show_message(f"Error handling consent page: {str(e)}")
            
            # Check if we're still on consent page
            if "consent.google.com" in self.driver.current_url:
                Communicator.show_message("Still on consent page, trying alternative approach...")
                # Try to navigate directly to maps with different parameters
                alternative_url = f"https://www.google.com/maps/search/{encoded_query}/@25.2854,51.5310,12z"
                Communicator.show_message(f"Trying alternative URL: {alternative_url}")
                self.driver.get(alternative_url)
                sleep(3)
            
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
