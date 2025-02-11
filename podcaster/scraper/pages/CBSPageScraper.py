from .BasePageScraper import BasePageScraper
from urllib.parse import urljoin
import re
from datetime import date, datetime

class CBSPageScraper(BasePageScraper):
    '''
        PageScraper implementation for CBS website.
    '''
    def __init__(self):
        website_name = 'CBS'
        basic_url = 'https://www.cbsnews.com/'
        language = 'English'
        super().__init__(website_name, basic_url, language)

    def _lookup_term(self, category) -> list:
        '''
            Return the index term for a given category.
        '''
        term_dict = {
            'technology': 'technology',
            'economics': 'us',
            'politics': 'politics',
            'world': 'world',
            'crypto': None,
            'latest': None,
        }
        return term_dict[category]
    
    def _construct_url(self, category, page_index) -> list:
        term = self._lookup_term(category)
        if not term:
            return None
        index = f'{page_index}' * (page_index > 1)
        url = urljoin(self.basic_url, f'{term}/{index}')
        return url
    
    def _extract_date(self, date_str):
        today = date.today()
        date_str = date_str.lower()
        if 'ago' in date_str:
            return today
        year = today.year
        if len(date_str.split(' ')) == 3:
            date_str = date_str.split(',')[0]
        date_obj = datetime.strptime(f'{date_str} {year}', '%b %d %Y').date()
        if date_obj > today:
            year -= 1
            date_obj = datetime.strptime(f'{date_str} {year}', '%b %d %Y').date()
        return date_obj
    
    def _extract_articles(self, soup, ref_date) -> tuple:
        scraped_articles = []
        min_date = date(9999,1,1)

        articles = soup.select('.list-river > .component__item-wrapper > .item--type-article')
        for article in articles:

            title = article.find('h4', attrs={'class': 'item__hed'}).text.strip()
            sub_header = article.find('p', attrs={'class': 'item__dek'}).text.strip()
            href = article.select('a')[0].attrs['href']
            date_obj = self._extract_date(article.find('li', attrs={'class': 'item__date'}).text)
            if date_obj:
                min_date = min(min_date, date_obj)

            if date_obj and date_obj < ref_date:
                continue

            scraped_articles.append({
                'id': self._generate_id(title),
                'title': title,
                'sub_header': sub_header,
                'href': href,
                'date': date_obj,
            })
             
        keep_scraping = (min_date >= ref_date) if min_date != date(9999,1,1) else False
        scraped_articles = sorted(scraped_articles, key=lambda x: x['date'])
        return keep_scraping, scraped_articles
    
# if __name__ == "__main__":
#     scraper = CBSPageScraper()
#     print(f"Scraping {scraper}")
#     print(scraper.scrape(category='world', lookback=3))