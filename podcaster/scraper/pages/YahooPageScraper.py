from .BasePageScraper import BasePageScraper
from urllib.parse import urljoin
from datetime import date, datetime, timedelta

class YahooPageScraper(BasePageScraper):
    '''
        PageScraper implementation for ansa website.
    '''
    def __init__(self):
        website_name = 'Yahoo Finance'
        basic_url = 'https://finance.yahoo.com/'
        language = 'English'
        super().__init__(website_name, basic_url, language)

    def _lookup_term(self, category) -> list:
        '''
            Return the index term for a given category.
        '''
        term_dict = {
            'technology': 'tech',
            'crypto': 'crypto',
            'latest': 'latest-news',
            'economics': None,
            'politics': None,
            'world': None,
        }
        return term_dict[category]
    
    def _construct_url(self, category, page_index) -> list:
        term = self._lookup_term(category)
        if not term:
            return None
        url = urljoin(self.basic_url, f'/topic/{term}')
        return url
    
    def _extract_date(self, date_str):
        today = date.today()
        date_str = date_str.lower().strip()
        if 'minutes' in date_str or 'hours' in date_str:
            return today
        elif 'yesterday' in date_str:
            return today - timedelta(days=1)
        elif 'days' in date_str:
            days = int(date_str.split(' ')[0])
            date_obj = today - timedelta(days=days)
            return date_obj
        return today
    
    def _extract_articles(self, soup, ref_date) -> tuple:
        scraped_articles = []
        min_date = date(9999,1,1)

        articles = soup.select('div[class*="content"]')
        for article in articles:
            try:
                title = article.find('a').attrs['title'].strip()
                sub_header = article.find('p').text.strip()
                href = article.find('a').attrs['href']
            except Exception as e:
                continue
            try:
                date_obj = self._extract_date(article.select('div[class*="publishing"] i')[0].next_sibling.strip())
            except Exception as e:
                date_obj = date.today()
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
             
        keep_scraping = False
        scraped_articles = sorted(scraped_articles, key=lambda x: x['date'])
        return keep_scraping, scraped_articles

# if __name__ == "__main__":
#     scraper = YahooPageScraper()
#     print(f"Scraping {scraper}")
#     print(scraper.scrape(category='technology', lookback=3))