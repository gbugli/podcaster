from .BaseArticleScraper import BaseArticleScraper
from urllib.parse import urljoin
import re
from datetime import date

class AnsaArticleScraper(BaseArticleScraper):
    '''
        ArticleScraper implementation for Ansa website.
    '''
    def __init__(self):
        website_name = 'Ansa'
        basic_url = 'https://www.ansa.it/'
        language = 'Italian'
        super().__init__(website_name, basic_url, language)

    def _extract_article(self, soup) -> dict:
        try:
            title = soup.find('h1', attrs={'class':'post-single-title'}).text.strip()
            sub_header = soup.find('div', attrs={'class':'post-single-summary'}).text.strip()
            content = '\n'.join([paragraph.text.strip() for paragraph in soup.select('.article-main p')])
        except Exception as e:
            return None

        return {
            'title': title,
            'sub_header': sub_header,
            'content': content,
        }
    
# if __name__ == "__main__":
#     url = 'https://www.ansa.it/sito/notizie/politica/2024/11/27/salvini-non-e-successo-nulla-nessun-problema-in-maggioranza_6b9e9ff2-430a-4201-802c-8807218e9b08.html'
#     scraper = AnsaArticleScraper()
#     print(scraper.scrape(url))
