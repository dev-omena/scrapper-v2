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
                
                # Strategy 1: Try browser back
                try:
                    print("DEBUG: Trying browser back...")
                    self.driver.back()
                    time.sleep(3)
                    
                    new_url = self.driver.current_url
                    print(f"DEBUG: After back, URL: {new_url}")
                    
                    if '/maps/search/' in new_url:
                        Communicator.show_message("Successfully returned to search results using back button")
                        print("DEBUG: Back button worked - now on search results")
                        return True
                    
                except Exception as e:
                    print(f"DEBUG: Browser back failed: {str(e)}")
                
                # Strategy 2: If we're still on a place page, this might be the ONLY result
                # Just scrape this one place
                if '/maps/place/' in self.driver.current_url:
                    Communicator.show_message("Only one result found - will scrape this single place")
                    print("DEBUG: Only single result exists, adding to list")
                    
                    # Add this single place URL to results
                    place_url = self.driver.current_url
                    if place_url not in self.all_results_links:
                        self.all_results_links.append(place_url)
                        print(f"DEBUG: Added single place: {place_url}")
                    
                    return True
                    
        except Exception as e:
            print(f"ERROR in handle_direct_place_redirect: {str(e)}")
            import traceback
            traceback.print_exc()
        
        return False
    
    def wait_for_search_results(self, timeout=60):
        """Wait for search results to load with better detection"""
        Communicator.show_message("Waiting for search results to load...")
        print("DEBUG: wait_for_search_results() started")
        
        # First, do a quick check without waiting
        print("DEBUG: Attempting immediate result detection...")
        try:
            quick_selectors = ["[role='feed']", ".m6QErb", "div.m6QErb"]
            for selector in quick_selectors:
                try:
                    element = self.driver.find_element("css selector", selector)
                    if element and element.is_displayed():
                        html = element.get_attribute('outerHTML')
                        if html and len(html) > 100:
                            print(f"DEBUG: Quick check found results immediately with {selector}")
                            Communicator.show_message(f"Results found immediately!")
                            return element
                except:
                    continue
        except Exception as e:
            print(f"DEBUG: Quick check failed: {str(e)}")
        
        print("DEBUG: Starting timed wait loop...")
        start_time = time.time()
        attempt = 0
        
        while time.time() - start_time < timeout:
            attempt += 1
            elapsed = int(time.time() - start_time)
            
            if attempt % 3 == 0:  # More frequent updates
                print(f"DEBUG: Wait attempt {attempt}, elapsed {elapsed}s")
                Communicator.show_message(f"Still waiting for results... ({elapsed}s)")
            
            try:
                # Check current URL
                current_url = self.driver.current_url
                
                if attempt % 5 == 0:
                    print(f"DEBUG: Current URL: {current_url[:100]}...")
                
                if "consent.google.com" in current_url:
                    Communicator.show_message("ERROR: Still on consent page - cannot access Google Maps")
                    print("ERROR: Still on consent page")
                    return None
                
                # Check if we were redirected to a place page
                if '/maps/place/' in current_url:
                    print("DEBUG: Detected place page redirect")
                    Communicator.show_message("Detected redirect to place page, handling...")
                    
                    if self.handle_direct_place_redirect():
                        current_url = self.driver.current_url
                        print(f"DEBUG: After handling redirect, URL: {current_url}")
                        
                        # Check if we now have results
                        if len(self.all_results_links) > 0:
                            print(f"DEBUG: Have {len(self.all_results_links)} results after redirect handling")
                            Communicator.show_message(f"Found {len(self.all_results_links)} result(s)")
                            return "SINGLE_RESULT"
                        
                        # If we're back on search page, continue looking for results
                        if '/maps/search/' in current_url:
                            print("DEBUG: Back on search page, continuing to look for results...")
                            time.sleep(2)  # Give page time to load
                            continue
                    
                    # If handling failed, wait and retry
                    time.sleep(1)
                    continue
                
                # Try multiple selectors for search results
                selectors = [
                    "[role='feed']",
                    ".m6QErb",
                    "div.m6QErb",
                    ".section-scrollbox",
                    "div[role='main']",
                    "[aria-label*='Results']",
                    ".section-layout"
                ]
                
                for selector in selectors:
                    try:
                        element = self.driver.find_element("css selector", selector)
                        
                        if element and element.is_displayed():
                            if attempt % 5 == 0:
                                print(f"DEBUG: Found element with selector: {selector}")
                            
                            # Get element info
                            try:
                                html = element.get_attribute('outerHTML')
                                
                                # Check if element has content
                                if html and len(html) > 100:
                                    Communicator.show_message(f"Found search results container using selector: {selector}")
                                    print(f"DEBUG: Returning results container (HTML length: {len(html)})")
                                    return element
                            except Exception as e:
                                if attempt % 10 == 0:
                                    print(f"DEBUG: Error getting element HTML: {str(e)}")
                                continue
                    except Exception as e:
                        continue
                
                # If no selector worked after 10 attempts, try aggressive approach
                if attempt >= 10 and attempt % 5 == 0:
                    print("DEBUG: No selectors worked, trying to find any results...")
                    try:
                        all_links = self.driver.find_elements("css selector", "a[href*='/maps/place/']")
                        print(f"DEBUG: Found {len(all_links)} place links on page")
                        
                        if len(all_links) > 0:
                            Communicator.show_message(f"Found {len(all_links)} results by scanning page links")
                            print("DEBUG: Will extract links directly from page")
                            body = self.driver.find_element("css selector", "body")
                            return body
                    except Exception as e:
                        print(f"DEBUG: Direct link search failed: {str(e)}")
                
                time.sleep(0.5)  # Shorter sleep for faster detection
                
            except Exception as e:
                print(f"ERROR in wait loop: {str(e)}")
                time.sleep(0.5)
        
        print(f"ERROR: Timeout after {timeout}s waiting for search results")
        Communicator.show_message("Timeout waiting for search results - trying last resort")
        
        # Last resort - check if we collected any results during redirect handling
        if len(self.all_results_links) > 0:
            print(f"DEBUG: Timeout but have {len(self.all_results_links)} results from redirect handling")
            Communicator.show_message(f"Proceeding with {len(self.all_results_links)} result(s) found")
            return "SINGLE_RESULT"
        
        # Try body extraction as final fallback
        try:
            print("DEBUG: Timeout - attempting last resort body extraction")
            body = self.driver.find_element("css selector", "body")
            return body
        except:
            return None
    
    def extract_links_from_element(self, element):
        """Extract all valid Google Maps place links from an element"""
        try:
            if element == "SINGLE_RESULT":
                # We already have the single result in all_results_links
                return []
            
            print("DEBUG: Starting link extraction...")
            html_content = element.get_attribute('outerHTML')
            print(f"DEBUG: Got HTML content, length: {len(html_content)}")
            
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Method 1: Try to find links with the hfpxzc class (Google Maps result links)
            result_links = soup.find_all('a', class_='hfpxzc')
            print(f"DEBUG: Method 1 (hfpxzc class): Found {len(result_links)} links")
            
            valid_links = []
            for link in result_links:
                href = link.get('href', '')
                if href and href not in valid_links:
                    valid_links.append(href)
                    print(f"DEBUG: Added link from hfpxzc: {href[:80]}...")
            
            # Method 2: If no hfpxzc links found, try data-item-id attribute
            if len(valid_links) == 0:
                print("DEBUG: Method 2 - trying data-item-id...")
                data_item_links = soup.find_all('a', attrs={'data-item-id': True})
                print(f"DEBUG: Found {len(data_item_links)} links with data-item-id")
                
                for link in data_item_links:
                    href = link.get('href', '')
                    if href and '/maps/place/' in href and href not in valid_links:
                        valid_links.append(href)
                        print(f"DEBUG: Added link from data-item-id: {href[:80]}...")
            
            # Method 3: If still no links, try all anchor tags with place URLs
            if len(valid_links) == 0:
                print("DEBUG: Method 3 - scanning all anchor tags...")
                all_links = soup.find_all('a', href=True)
                print(f"DEBUG: Found {len(all_links)} total anchor tags")
                
                for link in all_links:
                    href = link.get('href', '')
                    
                    # Filter for valid Google Maps place links
                    if '/maps/place/' in href:
                        # Clean up the link if needed
                        if href.startswith('http'):
                            if href not in valid_links:
                                valid_links.append(href)
                                print(f"DEBUG: Added place link: {href[:80]}...")
                        elif href.startswith('/'):
                            full_url = f"https://www.google.com{href}"
                            if full_url not in valid_links:
                                valid_links.append(full_url)
                                print(f"DEBUG: Added relative link: {full_url[:80]}...")
            
            # Method 4: Last resort - use Selenium to find elements directly
            if len(valid_links) == 0:
                print("DEBUG: Method 4 - using Selenium to find links...")
                try:
                    from selenium.webdriver.common.by import By
                    
                    # Try to find place links directly with Selenium
                    place_links = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='/maps/place/']")
                    print(f"DEBUG: Selenium found {len(place_links)} place links")
                    
                    for link_elem in place_links:
                        try:
                            href = link_elem.get_attribute('href')
                            if href and href not in valid_links:
                                valid_links.append(href)
                                print(f"DEBUG: Added Selenium link: {href[:80]}...")
                        except:
                            continue
                except Exception as e:
                    print(f"DEBUG: Selenium method failed: {str(e)}")
            
            print(f"DEBUG: Total extracted {len(valid_links)} valid links")
            if len(valid_links) > 0:
                print(f"DEBUG: First link: {valid_links[0][:100]}")
                Communicator.show_message(f"Extracted {len(valid_links)} business links")
            else:
                Communicator.show_message("Warning: No links extracted from current view")
            
            return valid_links
            
        except Exception as e:
            print(f"ERROR extracting links: {str(e)}")
            import traceback
            traceback.print_exc()
            return []
    
    def scroll(self):
        """Improved scrolling with better error handling and performance"""
        
        Communicator.show_message("DEBUG: Starting enhanced scroller.scroll() method")
        print("DEBUG: Starting enhanced scroller.scroll() method")
        
        # Make sure all_results_links is initialized
        self.all_results_links = []
        self.unique_links = set()  # Track unique links to avoid duplicates
        Communicator.show_message("DEBUG: Initialized all_results_links and unique_links tracker")
        print("DEBUG: Initialized all_results_links and unique_links tracker")
        
        # Check page state immediately (no additional sleep since mainscraping already waited)
        try:
            current_url = self.driver.current_url
            page_title = self.driver.title
            print(f"DEBUG: Page URL: {current_url}")
            print(f"DEBUG: Page title: {page_title}")
            Communicator.show_message(f"Current page: {page_title[:50]}...")
        except Exception as e:
            print(f"DEBUG: Could not get page info: {str(e)}")
        
        # Wait for search results to load
        Communicator.show_message("Looking for search results...")
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
        for link in initial_links:
            if link not in self.unique_links:
                self.unique_links.add(link)
                self.all_results_links.append(link)
        print(f"DEBUG: Initial extraction found {len(initial_links)} links, {len(self.all_results_links)} unique")
        Communicator.show_message(f"DEBUG: Initial extraction found {len(self.all_results_links)} unique links")
        
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
                            if href not in self.unique_links:
                                self.unique_links.add(href)
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
                
                # Add only unique links using set for faster lookup
                added_count = 0
                for link in new_links:
                    if link not in self.unique_links:
                        self.unique_links.add(link)
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