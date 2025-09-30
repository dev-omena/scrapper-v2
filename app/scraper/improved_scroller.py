"""
Improved scroller with better error handling and debugging
"""
import time
from scraper.communicator import Communicator
from scraper.common import Common
from bs4 import BeautifulSoup
from selenium.common.exceptions import JavascriptException
from scraper.parser import Parser

class ImprovedScroller:
    def __init__(self, driver) -> None:
        self.driver = driver
        # Initialize the results list in __init__ to ensure it persists
        self.all_results_links = []
    
    def __init_parser(self):
        self.parser = Parser(self.driver)
    
    def start_parsing(self):
        Communicator.show_message("DEBUG: Starting parsing process")
        print("DEBUG: Starting parsing process")
        print(f"DEBUG: all_results_links length before parsing: {len(self.all_results_links)}")
        Communicator.show_message(f"DEBUG: all_results_links length before parsing: {len(self.all_results_links)}")
        
        if len(self.all_results_links) == 0:
            Communicator.show_message("ERROR: No links to parse!")
            print("ERROR: No links to parse!")
            return
        
        self.__init_parser()
        print(f"DEBUG: About to call parser.main with {len(self.all_results_links)} links")
        Communicator.show_message(f"DEBUG: About to call parser.main with {len(self.all_results_links)} links")
        self.parser.main(self.all_results_links)
    
    def wait_for_search_results(self, timeout=30):
        """Wait for search results to load with better detection"""
        Communicator.show_message("Waiting for search results to load...")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                # Check if we're still on consent page
                current_url = self.driver.current_url
                if "consent.google.com" in current_url:
                    Communicator.show_message("ERROR: Still on consent page - cannot access Google Maps")
                    print("ERROR: Still on consent page")
                    return None
                
                # Try multiple selectors for search results
                selectors = [
                    "[role='feed']",
                    ".m6QErb",
                    ".section-scrollbox",
                    "div[role='main']"
                ]
                
                for selector in selectors:
                    try:
                        element = self.driver.find_element("css selector", selector)
                        
                        if element:
                            Communicator.show_message(f"Found search results using selector: {selector}")
                            print(f"DEBUG: Found results container with selector: {selector}")
                            return element
                    except Exception as e:
                        continue
                
                time.sleep(1)
                
            except Exception as e:
                Communicator.show_message(f"Error checking for results: {str(e)}")
                time.sleep(1)
        
        Communicator.show_message("Timeout waiting for search results")
        return None
    
    def extract_links_from_element(self, element):
        """Extract all valid Google Maps place links from an element"""
        try:
            html_content = element.get_attribute('outerHTML')
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Find all anchor tags
            all_links = soup.find_all('a', href=True)
            
            valid_links = []
            for link in all_links:
                href = link.get('href', '')
                
                # Filter for valid Google Maps place links
                if '/maps/place/' in href or 'place/' in href:
                    # Clean up the link if needed
                    if href.startswith('http'):
                        valid_links.append(href)
                    elif href.startswith('/'):
                        valid_links.append(f"https://www.google.com{href}")
            
            print(f"DEBUG: Extracted {len(valid_links)} valid links from element")
            return valid_links
            
        except Exception as e:
            print(f"ERROR extracting links: {str(e)}")
            return []
    
    def scroll(self):
        """Improved scrolling with better error handling"""
        
        Communicator.show_message("DEBUG: Starting scroller.scroll() method")
        print("DEBUG: Starting scroller.scroll() method")
        
        # Make sure all_results_links is initialized
        self.all_results_links = []
        Communicator.show_message("DEBUG: Initialized all_results_links")
        print("DEBUG: Initialized all_results_links")
        
        # Wait for search results to load
        scrollAbleElement = self.wait_for_search_results()
        
        # Temporary debug: save page source to file
        with open('/tmp/page_source.html', 'w', encoding='utf-8') as f:
            f.write(self.driver.page_source)
        print("DEBUG: Page source saved to /tmp/page_source.html")
        Communicator.show_message("DEBUG: Page source saved to /tmp/page_source.html")
        
        if scrollAbleElement is None:
            Communicator.show_message("ERROR: Could not find search results container")
            print("ERROR: Could not find search results container")
            return
        
        # Extract initial links
        initial_links = self.extract_links_from_element(scrollAbleElement)
        self.all_results_links.extend(initial_links)
        print(f"DEBUG: Initial extraction found {len(initial_links)} links")
        Communicator.show_message(f"DEBUG: Initial extraction found {len(initial_links)} links")
        
        Communicator.show_message("Starting scrolling to load more results...")
        
        last_height = 0
        scroll_attempts = 0
        max_scroll_attempts = 50
        no_new_results_count = 0
        
        while scroll_attempts < max_scroll_attempts:
            if Common.close_thread_is_set():
                self.driver.quit()
                return
            
            try:
                # Find the scrollable element
                scrollAbleElement = None
                scrollable_selectors = ["[role='feed']", ".m6QErb", ".section-scrollbox"]
                
                for selector in scrollable_selectors:
                    try:
                        scrollAbleElement = self.driver.find_element("css selector", selector)
                        if scrollAbleElement:
                            break
                    except:
                        continue
                
                if scrollAbleElement is None:
                    Communicator.show_message("Lost scrollable element")
                    print("ERROR: Lost scrollable element")
                    break
                
                # Get current count
                current_count = len(self.all_results_links)
                
                # Scroll down
                self.driver.execute_script(
                    "arguments[0].scrollTo(0, arguments[0].scrollHeight);",
                    scrollAbleElement,
                )
                time.sleep(2)
                
                # Get new scroll height
                new_height = self.driver.execute_script(
                    "return arguments[0].scrollHeight", scrollAbleElement
                )
                
                # Extract new links
                new_links = self.extract_links_from_element(scrollAbleElement)
                
                # Add only unique links
                added_count = 0
                for link in new_links:
                    if link not in self.all_results_links:
                        self.all_results_links.append(link)
                        added_count += 1
                
                print(f"DEBUG: Added {added_count} new links. Total: {len(self.all_results_links)}")
                Communicator.show_message(f"Found {len(self.all_results_links)} results so far...")
                
                # Check if we added new results
                if added_count == 0:
                    no_new_results_count += 1
                else:
                    no_new_results_count = 0
                
                # If no new results for 3 consecutive scrolls, check if we're at the end
                if no_new_results_count >= 3:
                    Communicator.show_message("No new results found, checking if at end...")
                    print("DEBUG: No new results for 3 scrolls")
                    
                    # Check for end marker
                    try:
                        end_markers = [
                            "You've reached the end",
                            "reached the end",
                            ".PbZDve"
                        ]
                        
                        page_text = self.driver.page_source.lower()
                        if any(marker.lower() in page_text for marker in end_markers):
                            Communicator.show_message("Reached the end of results")
                            print("DEBUG: Reached end of results")
                            break
                    except:
                        pass
                    
                    # If we have results, break
                    if len(self.all_results_links) > 0:
                        break
                
                scroll_attempts += 1
                
            except Exception as e:
                Communicator.show_message(f"Error during scrolling: {str(e)}")
                print(f"ERROR during scrolling: {str(e)}")
                import traceback
                traceback.print_exc()
                scroll_attempts += 1
                time.sleep(2)
        
        Communicator.show_message("Scrolling completed")
        print(f"DEBUG: Scrolling completed. Total results: {len(self.all_results_links)}")
        Communicator.show_message(f"DEBUG: Total results collected: {len(self.all_results_links)}")
        
        # Print first few links for debugging
        if len(self.all_results_links) > 0:
            print(f"DEBUG: First 3 links: {self.all_results_links[:3]}")
            Communicator.show_message(f"DEBUG: Sample links collected successfully")
        
        # Start parsing
        print(f"DEBUG: Checking if we have results to parse")
        print(f"DEBUG: all_results_links count: {len(self.all_results_links)}")
        
        if len(self.all_results_links) > 0:
            Communicator.show_message(f"Total results found: {len(self.all_results_links)}")
            print(f"DEBUG: Starting parsing with {len(self.all_results_links)} links")
            self.start_parsing()
        else:
            Communicator.show_message("No results to parse - no links were collected")
            print("ERROR: No results to parse - all_results_links is empty")