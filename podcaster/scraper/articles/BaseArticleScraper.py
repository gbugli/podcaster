from collections import defaultdict
import requests
from bs4 import BeautifulSoup
from time import perf_counter
from datetime import date, timedelta

class BaseArticleScraper:

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
        return f'BaseArticleScraper({self.basic_url})'
    
    def _extract_article(self, soup) -> list:
        '''
            Return the scraped information for an article.
        '''
        raise NotImplementedError()
    
    def scrape(self, url, track_time=False):
        '''
            Scrapes article for given news website.

            Args:
                url (str): Url to scrape
                track_time (bool): When True execution time is calculated.

            Returns:
                defaultdict(str): Scraped article data.
        '''
        if track_time:
            time0 = perf_counter()
        try:
            response = requests.get(url, headers=self.headers, timeout=(10, 50))
        except ConnectionResetError:
            print(f'Connection Error for {self._job_url}....')
            return {}
        
        soup = BeautifulSoup(response.text, 'html.parser')
        scraped_article = self._extract_article(soup)
        
        if not scraped_article:
            return None
        elif scraped_article and not scraped_article['content']:
            return None

        if track_time:
            print(f'Seconds to scrape artcile {url}: {perf_counter() - time0}')  # type: ignore
        return scraped_article