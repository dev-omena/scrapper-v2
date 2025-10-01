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
    
    def handle_direct_place_redirect(self):
        """Handle case where Google Maps redirects to a single place instead of search results"""
        try:
            current_url = self.driver.current_url
            
            # Check if we're on a place page instead of search results
            if '/maps/place/' in current_url:
                Communicator.show_message("Detected redirect to single place, going back to search results...")
                print("DEBUG: On a place page, need to go back to search results")
                
                # Click the back button or search button to get back to results
                try:
                    # Try to find and click the back/close button
                    back_button_selectors = [
                        "button[aria-label*='Back']",
                        "button[aria-label*='Close']",
                        "button[jsaction*='back']",
                        "button.gm2-button-icon[aria-label]"
                    ]
                    
                    for selector in back_button_selectors:
                        try:
                            back_btn = self.driver.find_element("css selector", selector)
                            if back_btn:
                                print(f"DEBUG: Found back button with selector: {selector}")
                                back_btn.click()
                                time.sleep(2)
                                
                                # Check if we're now on search results
                                new_url = self.driver.current_url
                                if '/maps/search/' in new_url:
                                    Communicator.show_message("Successfully returned to search results")
                                    print("DEBUG: Back to search results page")
                                    return True
                                break
                        except:
                            continue
                    
                    # If clicking back didn't work, try browser back
                    if '/maps/place/' in self.driver.current_url:
                        print("DEBUG: Trying browser back")
                        self.driver.back()
                        time.sleep(2)
                        
                        if '/maps/search/' in self.driver.current_url:
                            Communicator.show_message("Used browser back to return to search results")
                            return True
                    
                except Exception as e:
                    print(f"DEBUG: Error clicking back: {str(e)}")
                
                # If we still can't get back to search results, the current place is the only result
                if '/maps/place/' in self.driver.current_url:
                    Communicator.show_message("Only one result found, will scrape this single place")
                    print("DEBUG: Only single result exists")
                    # Add this single place URL to results
                    self.all_results_links.append(self.driver.current_url)
                    return True
                    
        except Exception as e:
            print(f"ERROR in handle_direct_place_redirect: {str(e)}")
            import traceback
            traceback.print_exc()
        
        return False
    
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
                
                # Check if we were redirected to a place page
                if '/maps/place/' in current_url:
                    print("DEBUG: Detected place page redirect")
                    Communicator.show_message("Detected redirect to place page, handling...")
                    if self.handle_direct_place_redirect():
                        # If we successfully handled it, continue waiting for results
                        current_url = self.driver.current_url
                        if len(self.all_results_links) > 0:
                            # We have the single result, return a dummy element
                            return "SINGLE_RESULT"
                    else:
                        continue
                
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
                            # Verify this is actually a results list, not a single place page
                            html = element.get_attribute('outerHTML')
                            
                            # Check for indicators of search results vs single place
                            if 'role="feed"' in html or 'hfpxzc' in html:
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
            if element == "SINGLE_RESULT":
                # We already have the single result in all_results_links
                return []
            
            html_content = element.get_attribute('outerHTML')
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Try to find links with the hfpxzc class (Google Maps result links)
            result_links = soup.find_all('a', class_='hfpxzc')
            
            valid_links = []
            for link in result_links:
                href = link.get('href', '')
                if href and href not in valid_links:
                    valid_links.append(href)
            
            # If no hfpxzc links found, try all links
            if len(valid_links) == 0:
                all_links = soup.find_all('a', href=True)
                
                for link in all_links:
                    href = link.get('href', '')
                    
                    # Filter for valid Google Maps place links
                    if '/maps/place/' in href or 'place/' in href:
                        # Clean up the link if needed
                        if href.startswith('http'):
                            if href not in valid_links:
                                valid_links.append(href)
                        elif href.startswith('/'):
                            full_url = f"https://www.google.com{href}"
                            if full_url not in valid_links:
                                valid_links.append(full_url)
            
            print(f"DEBUG: Extracted {len(valid_links)} valid links from element")
            if len(valid_links) > 0:
                print(f"DEBUG: First link sample: {valid_links[0][:100]}")
            
            return valid_links
            
        except Exception as e:
            print(f"ERROR extracting links: {str(e)}")
            import traceback
            traceback.print_exc()
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
        
        if scrollAbleElement is None:
            Communicator.show_message("ERROR: Could not find search results container")
            print("ERROR: Could not find search results container")
            return
        
        # Check if we already have a single result from redirect handling
        if scrollAbleElement == "SINGLE_RESULT":
            print(f"DEBUG: Single result already collected: {len(self.all_results_links)} links")
            Communicator.show_message(f"Single result found, proceeding to scraping...")
            
            if len(self.all_results_links) > 0:
                print(f"DEBUG: Starting parsing with single result")
                self.start_parsing()
            return
        
        # Save page source for debugging
        try:
            with open('/tmp/page_source.html', 'w', encoding='utf-8') as f:
                f.write(self.driver.page_source)
            print("DEBUG: Page source saved to /tmp/page_source.html")
        except Exception as e:
            print(f"DEBUG: Could not save page source: {str(e)}")
        
        # Extract initial links
        initial_links = self.extract_links_from_element(scrollAbleElement)
        self.all_results_links.extend(initial_links)
        print(f"DEBUG: Initial extraction found {len(initial_links)} links")
        Communicator.show_message(f"DEBUG: Initial extraction found {len(initial_links)} links")
        
        if len(initial_links) == 0:
            # Try alternative extraction method
            print("DEBUG: No links found with primary method, trying alternative...")
            try:
                # Get all anchor tags from the page
                all_anchors = self.driver.find_elements("css selector", "a")
                print(f"DEBUG: Found {len(all_anchors)} total anchor tags on page")
                
                for anchor in all_anchors:
                    try:
                        href = anchor.get_attribute('href')
                        if href and '/maps/place/' in href:
                            if href not in self.all_results_links:
                                self.all_results_links.append(href)
                    except:
                        continue
                
                print(f"DEBUG: Alternative method found {len(self.all_results_links)} links")
                Communicator.show_message(f"Alternative extraction found {len(self.all_results_links)} links")
            except Exception as e:
                print(f"ERROR in alternative extraction: {str(e)}")
        
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