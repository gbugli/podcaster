from .BaseArticleScraper import BaseArticleScraper
from urllib.parse import urljoin
import re
from datetime import date

class SkyArticleScraper(BaseArticleScraper):
    '''
        ArticleScraper implementation for SkyTG24 website.
    '''
    def __init__(self):
        website_name = 'SkyTG24'
        basic_url = 'https://tg24.sky.it/'
        language = 'Italian'
        super().__init__(website_name, basic_url, language)
        
    def _extract_article(self, soup) -> dict:
        try:
            title = soup.find('h1', attrs={'class': re.compile('\w+__title$')}).text.strip()
            content = '\n'.join([paragraph.text.strip() for paragraph in soup.select('div[class*="article-section"]')])
        except Exception as e:
            return None

        return {
            'title': title,
            'content': content,
        }
    
# if __name__ == "__main__":
#     url = 'https://tg24.sky.it/economia/2024/11/29/problemi-bancomat-oggi'
#     scraper = SkyArticleScraper()
#     print(scraper.scrape(url))