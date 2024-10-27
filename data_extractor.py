import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.firefox.options import Options as FirefoxOptions
import logging

class DataExtractor:
    def __init__(self, use_proxy=False, use_vpn=False):
        self.use_proxy = use_proxy
        self.use_vpn = use_vpn
        self.driver = None
        self.setup_driver()

    def setup_driver(self):
        if self.use_proxy:
            chrome_options = Options()
            chrome_options.add_argument('--proxy-server=socks5://127.0.0.1:9050')
            self.driver = webdriver.Chrome(options=chrome_options)
        elif self.use_vpn:
            firefox_options = FirefoxOptions()
            firefox_options.add_argument('--proxy-server=socks5://127.0.0.1:9050')
            self.driver = webdriver.Firefox(options=firefox_options)
        else:
            self.driver = webdriver.Chrome()

    def scrape_website(self, url):
        """
        Scrapes the given URL and extracts all paragraph text.

        :param url: The URL of the website to scrape
        :return: A list of strings containing the text from all <p> tags
        """
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            paragraphs = soup.find_all('p')
            return [p.get_text() for p in paragraphs]
        except requests.RequestException as e:
            logging.error(f"Error scraping {url}: {e}")
            return []

    def search_engine(self, query, engine="google"):
        """
        Searches a specified query on a given search engine.

        :param query: The search term to use
        :param engine: The search engine to use (default is 'google')
        :return: A list of search result texts
        """
        try:
            if engine == "google":
                self.driver.get("https://www.google.com")
                search_box = self.driver.find_element(By.NAME, "q")
            elif engine == "bing":
                self.driver.get("https://www.bing.com")
                search_box = self.driver.find_element(By.NAME, "q")
            elif engine == "duckduckgo":
                self.driver.get("https://duckduckgo.com")
                search_box = self.driver.find_element(By.NAME, "q")
            else:
                logging.error(f"Unsupported search engine: {engine}")
                return []

            search_box.send_keys(query + Keys.RETURN)

            if engine == "google":
                WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, "search")))
                results = self.driver.find_elements(By.CSS_SELECTOR, "div.g")
            elif engine == "bing":
                WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, "b_results")))
                results = self.driver.find_elements(By.CSS_SELECTOR, "li.b_algo")
            elif engine == "duckduckgo":
                WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, "links")))
                results = self.driver.find_elements(By.CSS_SELECTOR, "div.result")

            return [result.text for result in results]

        except Exception as e:
            logging.error(f"Error using {engine} search: {e}")
            return []

    def search_usernames(self, username, platforms=["google", "bing", "twitter"]):
        """
        Searches for a username across multiple platforms.

        :param username: The username to search for
        :param platforms: List of platforms to search (default: ["google", "bing", "twitter"])
        :return: A dictionary of results by platform
        """
        results = {}
        for platform in platforms:
            if platform in ["google", "bing"]:
                results[platform] = self.search_engine(username, engine=platform)
            elif platform == "twitter":
                results[platform] = self.search_twitter(username)
            else:
                logging.warning(f"Unsupported platform: {platform}")
                results[platform] = []
        return results

    def search_twitter(self, username):
        """
        Searches for a username on Twitter.

        :param username: The username to search for
        :return: A list of search result texts from Twitter
        """
        try:
            self.driver.get(f"https://twitter.com/search?q={username}")
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.css-1dbjc4n")))
            results = self.driver.find_elements(By.CSS_SELECTOR, "div.css-1dbjc4n")
            return [result.text for result in results]
        except Exception as e:
            logging.error(f"Error searching Twitter for {username}: {e}")
            return []

    def close_driver(self):
        """Closes the WebDriver if it's active."""
        if self.driver:
            self.driver.quit()

# Setup logging configuration
logging.basicConfig(level=logging.ERROR)

# Example usage
if __name__ == "__main__":
    extractor = DataExtractor()
    search_results = extractor.search_usernames("exampleuser", platforms=["google", "bing", "twitter"])
    print(search_results)
    extractor.close_driver()
