from .BaseArticleScraper import BaseArticleScraper
from urllib.parse import urljoin
import re
from datetime import date

class CBSArticleScraper(BaseArticleScraper):
    '''
        ArticleScraper implementation for CBS website.
    '''
    def __init__(self):
        website_name = 'CBS'
        basic_url = 'https://www.cbsnews.com/'
        language = 'English'
        super().__init__(website_name, basic_url, language)

    def _extract_article(self, soup) -> dict:
        try:
            title = soup.find('h1', attrs={'class':'content__title'}).text.strip()
            content = '\n'.join([paragraph.text.strip() for paragraph in soup.select('.content__body > p')])
        except Exception as e:
            return None

        return {
            'title': title,
            'content': content,
        }


# if __name__ == "__main__":
#     url = 'https://www.cbsnews.com/news/canada-files-lawsuit-against-google-over-advertising-business/'
#     scraper = CBSArticleScraper()
#     print(scraper.scrape(url))