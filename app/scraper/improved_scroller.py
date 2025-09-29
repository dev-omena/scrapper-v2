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
    
    def __init_parser(self):
        self.parser = Parser(self.driver)

    def start_parsing(self):
        self.__init_parser()
        self.parser.main(self.__allResultsLinks)
    
    def wait_for_search_results(self, timeout=30):
        """Wait for search results to load with better detection"""
        Communicator.show_message("Waiting for search results to load...")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                # Try multiple selectors for search results (fixed syntax)
                selectors = [
                    "[role='feed']",
                    "[data-value='Search results']",
                    ".m6QErb",
                    ".section-scrollbox",
                    ".section-layout-root"
                ]
                
                for selector in selectors:
                    try:
                        element = self.driver.execute_script(f"return document.querySelector('{selector}')")
                        if element:
                            Communicator.show_message(f"Found search results using selector: {selector}")
                            return element
                    except Exception as e:
                        Communicator.show_message(f"Error with selector {selector}: {str(e)}")
                        continue
                
                # Check if we're on a "no results" page
                no_results_selectors = [
                    ".section-no-results",
                    "[data-value='No results found']",
                    ".section-layout-root[data-value='No results found']"
                ]
                
                for selector in no_results_selectors:
                    no_results = self.driver.execute_script(f"return document.querySelector('{selector}')")
                    if no_results:
                        Communicator.show_message("No results found for this search query")
                        return None
                
                time.sleep(1)
                
            except Exception as e:
                Communicator.show_message(f"Error checking for results: {str(e)}")
                time.sleep(1)
        
        Communicator.show_message("Timeout waiting for search results")
        return None

    def scroll(self):
        """Improved scrolling with better error handling"""
        
        # Wait for search results to load
        scrollAbleElement = self.wait_for_search_results()
        
        if scrollAbleElement is None:
            Communicator.show_message("No results found for your search query on Google Maps")
            return

        Communicator.show_message("Starting scrolling to load more results...")
        
        last_height = 0
        scroll_attempts = 0
        max_scroll_attempts = 50  # Prevent infinite scrolling
        
        while scroll_attempts < max_scroll_attempts:
            if Common.close_thread_is_set():
                self.driver.quit()
                return

            try:
                # Find the scrollable element again (it might change)
                scrollAbleElement = self.driver.execute_script(
                    """return document.querySelector("[role='feed']") || 
                           document.querySelector(".m6QErb") ||
                           document.querySelector(".section-scrollbox")"""
                )
                
                if scrollAbleElement is None:
                    Communicator.show_message("Lost scrollable element, trying to find results...")
                    break
                
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
                
                if new_height == last_height:
                    # Check if we've reached the end
                    end_element = self.driver.execute_script(
                        """return document.querySelector(".PbZDve") || 
                               document.querySelector("[data-value='You've reached the end']") ||
                               document.querySelector(".section-layout-root[data-value='You've reached the end']")"""
                    )
                    
                    if end_element is None:
                        # Try clicking the last result to load more
                        try:
                            self.driver.execute_script(
                                "array=document.getElementsByClassName('hfpxzc');if(array.length>0)array[array.length-1].click();"
                            )
                            time.sleep(2)
                        except JavascriptException:
                            pass
                    else:
                        Communicator.show_message("Reached the end of results")
                        break
                else:
                    last_height = new_height
                    scroll_attempts = 0  # Reset counter if we're still scrolling
                    
                    # Extract results
                    allResultsListSoup = BeautifulSoup(
                        scrollAbleElement.get_attribute('outerHTML'), 'html.parser'
                    )
                    
                    allResultsAnchorTags = allResultsListSoup.find_all('a', class_='hfpxzc')
                    self.__allResultsLinks = [anchorTag.get('href') for anchorTag in allResultsAnchorTags]
                    
                    Communicator.show_message(f"Found {len(self.__allResultsLinks)} results so far...")
                
                scroll_attempts += 1
                
            except Exception as e:
                Communicator.show_message(f"Error during scrolling: {str(e)}")
                scroll_attempts += 1
                time.sleep(2)
        
        if scroll_attempts >= max_scroll_attempts:
            Communicator.show_message("Reached maximum scroll attempts")
        
        # Start parsing the results
        if hasattr(self, '__allResultsLinks') and self.__allResultsLinks:
            Communicator.show_message(f"Total results found: {len(self.__allResultsLinks)}")
            self.start_parsing()
        else:
            Communicator.show_message("No results to parse")
