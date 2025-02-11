import requests
from bs4 import BeautifulSoup
from time import perf_counter
from datetime import date, timedelta
import hashlib
import time

class BasePageScraper:

    def __init__(self, website_name, basic_url, language) -> None:
        self.website_name = website_name
        self.basic_url = basic_url
        self.language = language
        self.headers ={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.5",
            "Referer": "https://duckduckgo.com/",
            "Sec-GPC": "1",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "cross-site",
            "Sec-Fetch-User": "?1",
            "Connection": "keep-alive"
        }

    def __str__(self):
        return str(self.basic_url)

    def _lookup_term(self, category) -> list:
        '''
            Return the index term for a given category.
        '''
        raise NotImplementedError()

    def _construct_url(self, category, page_index) -> list:
        '''
            Construct urls to scrape articles per category and multiple pages.
        '''
        raise NotImplementedError()
    
    def _extract_articles(self, soup) -> list:
        '''
            Extract articles from the news page.
        '''
        raise NotImplementedError()
    
    def _generate_id(self, title):
        hash_object = hashlib.md5(title.encode('utf-8'))
        # Get first 9 characters of the hexadecimal representation
        return hash_object.hexdigest()


    def scrape(self, category=None, lookback=None, track_time=False) -> list:
        '''
            Scrapes the news category pages.
            
            Args:
                track_time (bool): When True execution time is calculated.
                
            Returns:
                The extracted articles.
        '''
        extracted_articles = []
        extracted_ids = set()
        ref_date = date.today()
        keep_scraping = True
        page_index = 1

        if track_time:
            time0 = perf_counter()
        if lookback:
            ref_date -= timedelta(days=lookback)

        tries = 0
        while keep_scraping:
            if tries > 5:
                break
            url = self._construct_url(category, page_index)
            if not url:
                print(f'No articles for {category} on {self.basic_url}')
                return []
            try:
                response = requests.get(url, headers=self.headers, timeout=(10, 50))
            except Exception as e:
                tries += 1
                print(F"Failed to connect to {url}: {str(e)}")
                time.sleep(5)
            assert response.status_code in [200, 404], f'Failed to reach {url}, status code: {response.status_code}'
            if response.status_code == 404:
                break

            soup = BeautifulSoup(response.text, 'html.parser')
            keep_scraping, articles = self._extract_articles(soup, ref_date)
            unique_articles = [article for article in articles if article['id'] not in extracted_ids]
            extracted_articles.extend(unique_articles)
            extracted_ids.update([article['id'] for article in unique_articles])
            page_index += 1

        if track_time:
            print(f'Seconds to scrape articles listing {url}: {perf_counter() - time0}')  # type: ignore
        return extracted_articles