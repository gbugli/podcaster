from .BasePageScraper import BasePageScraper
from urllib.parse import urljoin
import re
from datetime import date, datetime
import locale

MONTH_MAP = {
    'gen': 'jan', 'feb': 'feb', 'mar': 'mar', 'apr': 'apr',
    'mag': 'may', 'giu': 'jun', 'lug': 'jul', 'ago': 'aug',
    'set': 'sep', 'ott': 'oct', 'nov': 'nov', 'dic': 'dec'
}

class SkyPageScraper(BasePageScraper):
    '''
        PageScraper implementation for ansa website.
    '''
    def __init__(self):
        website_name = 'SkyTG24'
        basic_url = 'https://tg24.sky.it/'
        language = 'Italian'
        super().__init__(website_name, basic_url, language)

    def _lookup_term(self, category) -> list:
        '''
            Return the index term for a given category.
        '''
        term_dict = {
            'technology': None,
            'economics': 'economia',
            'politics': 'politica',
            'world': 'mondo',
            'crypto': None,
            'latest': None,
        }
        return term_dict[category]
    
    def _construct_url(self, category, page_index) -> list:
        term = self._lookup_term(category)
        if not term:
            return None
        index = f'?pag={page_index}' * (page_index > 1)
        url = urljoin(self.basic_url, f'/{term}{index}')
        print(f'scraping {url}')
        return url
    
    def _extract_date(self, date_str):
        today = date.today()
        date_str = date_str.lower().split('-')[0].strip()
        year = today.year
        day, month = date_str.split(' ')
        month_us = MONTH_MAP[month]
        date_obj = datetime.strptime(f'{day} {month_us} {year}', '%d %b %Y').date()
        if date_obj > today:
            year -= 1
            date_obj = datetime.strptime(f'{day} {month_us} {year}', '%b %d %Y').date()
        return date_obj
    
    def _extract_articles(self, soup, ref_date) -> tuple:
        scraped_articles = []
        min_date = date(9999,1,1)

        articles = soup.find_all('article')
        for article in articles:
            title = article.find('h2', attrs={'class': re.compile('\w+__title$')}).text.strip()
            try:
                sub_header = article.find('p', attrs={'class': re.compile('\w+__abstract$')}).text.strip()
            except AttributeError:
                continue
            href = article.find_parent('a').attrs['href']
            date_obj = self._extract_date(article.find('time', attrs={'class': re.compile('\w+__date$')}).text.strip())
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
#     scraper = SkyPageScraper()
#     print(f"Scraping {scraper}")
#     print(scraper.scrape(category='economics', lookback=3))