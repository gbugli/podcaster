from .BaseArticleScraper import BaseArticleScraper
from urllib.parse import urljoin
from datetime import date

class YahooArticleScraper(BaseArticleScraper):
    '''
        ArticleScraper implementation for Yahoo Finance website.
    '''
    def __init__(self):
        website_name = 'Yahoo Finance'
        basic_url = 'https://finance.yahoo.com/'
        language = 'English'
        super().__init__(website_name, basic_url, language)

    def _extract_article(self, soup) -> dict:
        try:
            title = soup.select_one('.cover-title').text.strip()
            content = '\n'.join([paragraph.text.strip() for paragraph in soup.select('.body p')])
        except Exception as e:
            print('Check Yahoo article parsing logic!!!!')
            return None

        return {
            'title': title,
            'content': content,
        }
    
# if __name__ == "__main__":
#     url = 'https://finance.yahoo.com/news/activist-elliott-builds-significant-stake-191646726.html'
#     scraper = YahooArticleScraper()
#     print(scraper.scrape(url))