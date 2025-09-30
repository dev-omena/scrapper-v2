from bs4 import BeautifulSoup
from scraper.error_codes import ERROR_CODES
from scraper.communicator import Communicator
from scraper.datasaver import DataSaver
from scraper.base import Base
from scraper.common import Common
import requests
import re
from time import sleep

class Parser(Base):
    def __init__(self, driver) -> None:
        self.driver = driver
        self.finalData = []
        self.comparing_tool_tips = {
            "location": "Copy address",
            "phone": "Copy phone number",
            "website": "Open website",
            "booking": "Open booking link",
        }

    def init_data_saver(self):
        self.data_saver = DataSaver()

    def parse(self):
        """Our function to parse the html"""
        """This block will get element details sheet of a business. 
        Details sheet means that business details card when you click on a business in 
        serach results in google maps"""
        
        # Wait for content to load
        sleep(2)
        
        infoSheet = self.driver.execute_script(
            """return document.querySelector("[role='main']")"""
        )
        try:
            # Initialize data points
            (
                rating,
                totalReviews,
                address,
                websiteUrl,
                email,
                phone,
                hours,
                category,
                gmapsUrl,
                bookingLink,
                businessStatus,
            ) = (None, None, None, None, None, None, None, None, None, None, None)
            
            html = infoSheet.get_attribute("outerHTML")
            soup = BeautifulSoup(html, "html.parser")
            
            # Extract rating
            try:
                rating = soup.find("span", class_="ceNzKf").get("aria-label")
                rating = rating.replace("stars", "").strip()
            except:
                rating = None

            # Extract total reviews
            try:
                totalReviews = list(soup.find("div", class_="F7nice").children)
                totalReviews = totalReviews[1].get_text(strip=True)
            except:
                totalReviews = None

            # Extract name
            try:
                name = soup.select_one(".tAiQdd h1.DUwDvf").text.strip()
            except:
                name = None

            # Extract address - FIXED METHOD
            try:
                address_button = soup.find("button", {"data-item-id": "address"})
                if address_button:
                    address_div = address_button.find("div", class_="rogA2c")
                    if address_div:
                        address = address_div.get_text(strip=True)
            except:
                pass

            # Extract phone - FIXED METHOD
            try:
                # Look for button with data-item-id starting with "phone:"
                phone_buttons = soup.find_all("button", class_="CsEnBe")
                for btn in phone_buttons:
                    data_item_id = btn.get("data-item-id", "")
                    if data_item_id.startswith("phone:"):
                        phone_div = btn.find("div", class_="rogA2c")
                        if phone_div:
                            phone = phone_div.get_text(strip=True)
                            break
            except:
                pass

            # Extract website URL - FIXED METHOD
            try:
                # Look for link with data-item-id="authority"
                website_link = soup.find("a", {"data-item-id": "authority"})
                if website_link:
                    websiteUrl = website_link.get("href")
            except Exception as e:
                Communicator.show_message(f"Website extraction error: {str(e)}")
                websiteUrl = None

            # Extract Email
            try:
                if websiteUrl:
                    email = self.find_mail(websiteUrl)
            except Exception as e:
                Communicator.show_message(f"Email extraction error: {str(e)}")
                email = None

            # Extract booking link
            try:
                bookingTag = soup.find(
                    "a", {"aria-label": lambda x: x and "Open booking link" in x}
                )
                if bookingTag:
                    bookingLink = bookingTag.get("href")
            except:
                bookingLink = None

            # Extract hours of operation
            try:
                hours = soup.find("div", class_="t39EBf").get_text(strip=True)
            except:
                hours = None

            # Extract category
            try:
                category = soup.find("button", class_="DkEaL").text.strip()
            except:
                category = None

            # Extract Google Maps URL
            try:
                gmapsUrl = self.driver.current_url
            except:
                gmapsUrl = None

            # Extract business status
            try:
                businessStatus = (
                    soup.find("span", class_="ZDu9vd")
                    .findChildren("span", recursive=False)[0]
                    .get_text(strip=True)
                )
            except:
                businessStatus = None

            data = {
                "Category": category,
                "Name": name,
                "Phone": phone,
                "Google Maps URL": gmapsUrl,
                "Website": websiteUrl,
                "email": email,
                "Business Status": businessStatus,
                "Address": address,
                "Total Reviews": totalReviews,
                "Booking Links": bookingLink,
                "Rating": rating,
                "Hours": hours,
            }
            
            # Debug output
            Communicator.show_message(f"Scraped: {name} | Phone: {phone} | Website: {websiteUrl}")
            
            self.finalData.append(data)
            
        except Exception as e:
            Communicator.show_error_message(
                f"Error occurred while parsing a location. Error is: {str(e)}",
                ERROR_CODES["ERR_WHILE_PARSING_DETAILS"],
            )

    # find email
    def find_mail(self, url):
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
            }
            
            # Fix: Use the actual URL, not the original variable
            source_code = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
            curr = source_code.url
            original_curr = curr
            plain_text = source_code.text
            
            match = re.findall(
                r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", plain_text
            )
            
            if not match:
                urls = [original_curr + "/contact/", original_curr + "/Contact/"]
                for cu in urls:
                    try:
                        source_code = requests.get(cu, headers=headers, timeout=10)
                        plain_text = source_code.text
                        match = re.findall(
                            r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", plain_text
                        )
                        if match:
                            break
                    except:
                        continue
            
            if not match:
                match = re.findall(
                    r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", original_curr
                )
            
            # Filter out invalid emails
            match = [
                email
                for email in set(match)
                if re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9-]+\.[a-zA-Z]{2,}$", email)
                and not email.endswith(('.png', '.jpg', '.jpeg', '.gif', '.svg'))
            ]
            
            email = ", ".join(match[:3])  # Limit to first 3 emails
            return email
            
        except Exception as e:
            Communicator.show_message(f"Error in find_mail: {e}")
        return ""

    def main(self, allResultsLinks):
        Communicator.show_message(
            "Scrolling is done. Now going to scrape each location"
        )
        print(f"DEBUG: Parser.main() called with {len(allResultsLinks)} links")
        Communicator.show_message(f"DEBUG: Parser received {len(allResultsLinks)} links to process")
        try:
            for idx, resultLink in enumerate(allResultsLinks):
                if Common.close_thread_is_set():
                    self.driver.quit()
                    return
                
                Communicator.show_message(f"Scraping location {idx + 1} of {len(allResultsLinks)}")
                self.openingurl(url=resultLink)
                sleep(2)  # Give page time to load
                self.parse()
                
        except Exception as e:
            Communicator.show_message(
                f"Error occurred while parsing the locations. Error: {str(e)}"
            )
        finally:
            self.init_data_saver()
            self.data_saver.save(datalist=self.finalData)