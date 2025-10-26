import time
from abc import ABC, abstractmethod
from tempfile import mkdtemp

from click import option

"""
    
"""
import chromedriver_autoinstaller
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from llm_engineering.domain.documents import NoSQLBaseDocument

# Check if the current version of chromedriver exists
# and if it doesn't exist, download it automatically, 
# then add chromedriver to path
chromedriver_autoinstaller.install() 

class BaseCrawler(ABC):
    model: type[NoSQLBaseDocument]

    @abstractmethod
    # using ... to indicate an empty body for the abstract method
    # extract method must be implemented by subclasses
    def extract(self, link: str, **kwargs) -> None: ... 


class BaseSeleniumCrawler(BaseCrawler, ABC):
    def __init__(self, scroll_limit: int = 5) -> None:
        options = webdriver.ChromeOptions()
    
        # Running Chrome without opening a window and with new headless mode
        options.add_argument("--headless=new")

        # Running Chrome in environments without a graphical interface
        options.add_argument("--no-sandbox")

        # Overcome limited resource problems
        options.add_argument("--disable-dev-shm-usage")

        # Running Chrome with minimal logging
        options.add_argument("--log-level=3")

        #Allows popup windows (which are often blocked by default) to open
        options.add_argument("--disable-popup-blocking")

        #Prevents websites from showing desktop notifications
        options.add_argument("--disable-notifications")

        #Stops any installed browser extensions (like AdBlocker) from loading and running
        options.add_argument("--disable-extensions")

        #Disables background network activity, like pre-fetching pages or updating components
        options.add_argument("--disable-background-networking")

        #Ignores SSL certificate errors, allowing access to sites with invalid or self-signed certificates
        options.add_argument("--ignore-certificate-errors")

        #Creates a new, temporary profile for this session (isolating cookies, history, etc.)
        options.add_argument(f"--user-data-dir={mkdtemp()}")

        #Specifies a separate temporary folder for storing user application data
        options.add_argument(f"--data-path={mkdtemp()}")

        #Uses a new temporary folder specifically for storing cached files (images, scripts)
        options.add_argument(f"--disk-cache-dir={mkdtemp()}")
        
        #Opens port 9226 so you can remotely connect to and control/inspect the browser
        options.add_argument("--remote-debugging-port=9226")

        self.set_extra_driver_options(options) # Hook for subclasses to add more options

        self.scroll_limit = scroll_limit
        # Initialize the Chrome WebDriver with specified options
        self.driver = webdriver.Chrome(options=options)

    def set_extra_driver_options(self, options: Options) -> None:
        pass

    def login(self) -> None:
        pass

    def scroll_page(self) -> None:
        """Scroll through the LinkedIn page based on the scroll limit."""
        current_scroll = 0
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        while True:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(5)
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height or (self.scroll_limit and current_scroll >= self.scroll_limit):
                break
            last_height = new_height
            current_scroll += 1