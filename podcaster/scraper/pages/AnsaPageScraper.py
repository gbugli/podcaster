from .BasePageScraper import BasePageScraper
from urllib.parse import urljoin
import re
from datetime import date

class AnsaPageScraper(BasePageScraper):
    '''
        PageScraper implementation for ansa website.
    '''
    def __init__(self):
        website_name = 'Ansa'
        basic_url = 'https://www.ansa.it/'
        language = 'Italian'
        super().__init__(website_name, basic_url, language)

    def _lookup_term(self, category) -> list:
        '''
            Return the index term for a given category.
        '''
        term_dict = {
            'technology': 'tecnologia',
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
        index = 'index' + f'_{page_index}' * (page_index > 1)
        if category == 'technology':
            index = term
        url = urljoin(self.basic_url, f'/sito/notizie/{term}/{index}.shtml')
        return url
    
    def _extract_date(self, url):
        pattern = r'/(\d{4}/\d{2}/\d{2})/'
        match = re.search(pattern, url)
        if match:
            date_str = match.group(1)
            year, month, day = map(int, date_str.split('/'))
            date_obj = date(year, month, day)
            return date_obj
        return None

    def _extract_articles(self, soup, ref_date) -> tuple:
        scraped_articles = []
        min_date = date(9999,1,1)

        articles = soup.select('.article-content > h2')
        for article in articles:

            title = article.text.strip()
            href = urljoin(self.basic_url, article.select('a')[0].attrs['href'])
            date_obj = self._extract_date(href)
            if date_obj:
                min_date = min(min_date, date_obj)

            if date_obj and date_obj < ref_date:
                continue

            scraped_articles.append({
                'id': self._generate_id(title),
                'title': title,
                'href': href,
                'date': date_obj
            })
             
        keep_scraping = (min_date >= ref_date) if min_date != date(9999,1,1) else False
        scraped_articles = sorted(scraped_articles, key=lambda x: x['date'])
        return keep_scraping, scraped_articles
    
# if __name__ == "__main__":
#     scraper = AnsaPageScraper()
#     print(f"Scraping {scraper}")
#     print(scraper.scrape(category='technology', lookback=3))