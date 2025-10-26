import platform
from bs4 import BeautifulSoup # bs4 is used to parse HTML content
                              # BeautifulSoup is used to extract data from HTML and XML files.
from loguru import logger
from sympy import content, use

from llm_engineering.domain.documents import ArticleDocument

from .base import BaseSeleniumCrawler

class MediumCrawler(BaseSeleniumCrawler):
    model = ArticleDocument # specify the document model for Medium articles

    def set_extra_driver_options(self, options) -> None:
      """
      Loads the existing 'Profile 2' Chrome profile 
      to reuse cookies and maintain login sessions 
      like "مرا به خاط بسپار" in a website.
      """        
      options.add_argument(r"--profile-directory=Profile 2")

    def extract(self, link: str, **kwargs) -> None:
        old_model = self.model.find(link=link)
        if old_model is not None:
            logger.info(f"Article already exists in the database: {link}")

            return
       
        logger.info(f"Starting scrapping Medium article: {link}")

        self.driver.get(link) # using selenium to open the link and load dynamic content
        self.scroll_page() # scroll the page to load all content

        # using BeautifulSoup to parse the loaded page source
        soup = BeautifulSoup(self.driver.page_source, "html.parser")

        # Extracting the article title
        #it is a list of h1 tags with class "pw-post-title"
        title = soup.find_all("h1", class_ = "pw-post-title")

        # Extracting the article subtitle
        # it is a list of h2 tags with class "pw-subtitle- paragraph"
        subtitle = soup.find_all("h2", class_ = "pw-subtitle- paragraph")

        data = {
            "Title": title[0].string if title else None,
            "Subtitle": subtitle[0].string if subtitle else None,
            "Content": soup.get_text(),
        }
        self.driver.quit() # close the selenium driver

        user = kwargs["user"]
        instance = self.model(
            platform="medium",
            content=data,
            link=link,
            author_id = user.id,
            author_full_name=user.full_name,
        )
        instance.save()
        logger.info(f"Article saved to database: {link}")