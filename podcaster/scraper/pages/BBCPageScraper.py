from .BasePageScraper import BasePageScraper
from urllib.parse import urljoin
import re
import json
from datetime import date, datetime

class BBCPageScraper(BasePageScraper):
    '''
        PageScraper implementation for ansa website.
    '''
    def __init__(self):
        website_name = 'BBC'
        basic_url = 'https://www.bbc.com/'
        language = 'English'
        super().__init__(website_name, basic_url, language)

    def _lookup_term(self, category) -> list:
        '''
            Return the index term for a given category.
        '''
        term_dict = {
            'technology': '3da03ce0-ee41-4427-a5d9-1294491e0448',
            'economics': 'daa2a2f9-0c9e-4249-8234-bae58f372d82',
            'politics': None,
            'world': 'e2cc1064-8367-4b1e-9fb7-aed170edc48f',
            'crypto': None,
            'latest': None,
        }
        return term_dict[category]
    
    def _construct_url(self, category, page_index) -> list:
        term = self._lookup_term(category)
        if not term:
            return None
        index = str(page_index - 1)
        url = f'https://web-cdn.api.bbci.co.uk/xd/content-collection/{term}?country=us&page={index}&size=25'
        return url
    
    def _extract_date(self, date_str):
        if date_str:
            date_obj = datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S.%fZ').date()
            return date_obj
        return None
    
    def _extract_articles(self, soup, ref_date) -> tuple:
        scraped_articles = []
        min_date = date(9999,1,1)

        articles = json.loads(soup.text)['data']
        for article in articles:
            title = article.get('title', None)
            href = urljoin(self.basic_url, article.get('path', None))
            sub_header = article.get('summary', None)
            date_obj = self._extract_date(article.get('firstPublishedAt', None))
            if date_obj:
                min_date = min(min_date, date_obj)

            if date_obj and date_obj < ref_date:
                continue

            scraped_articles.append({
                'id': self._generate_id(title),
                'title': title,
                'sub_header': sub_header,
                'href': href,
                'date': date_obj
            })
             
        keep_scraping = (min_date >= ref_date) if min_date != date(9999,1,1) else False
        scraped_articles = sorted(scraped_articles, key=lambda x: x['date'])
        return keep_scraping, scraped_articles
    
# if __name__ == "__main__":
#     scraper = BBCPageScraper()
#     print(f"Scraping {scraper}")
#     print(scraper.scrape(category='technology', lookback=3))