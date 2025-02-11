from .BaseArticleScraper import BaseArticleScraper
from urllib.parse import urljoin
import re
from datetime import date

class BBCArticleScraper(BaseArticleScraper):
    '''
        ArticleScraper implementation for BBC website.
    '''
    def __init__(self):
        website_name = 'BBC'
        basic_url = 'https://www.bbc.com/'
        language = 'English'
        super().__init__(website_name, basic_url, language)

    def _extract_article(self, soup) -> dict:
        try:
            title = soup.find('div',attrs={'data-component':'headline-block'}).text.strip()
            content = '\n'.join([paragraph.text.strip() for paragraph in soup.find_all('div',attrs={'data-component':'text-block'})])
        except Exception as e:
            return None

        return {
            'title': title,
            'content': content,
        }
    
# if __name__ == "__main__":
#     url = 'https://www.bbc.com/news/articles/c748ww9y9nno'
#     scraper = BBCArticleScraper()
#     print(scraper.scrape(url))