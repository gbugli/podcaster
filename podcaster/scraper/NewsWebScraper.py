import os
import sys
import django
from podcaster.config import config

# project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
project_root = config.get('projectRoot')
sys.path.append(project_root)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from concurrent.futures import ThreadPoolExecutor
from collections import defaultdict
from datetime import datetime
import threading
from .articles import *
from .pages import *
from itertools import product
import numpy as np
import pickle
from time import time
import logging
from newsfeed.utils import save_article, query_articles

# Add project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

def init_logger():
    os.makedirs('log', exist_ok = True)
    logging.basicConfig(filename=os.path.join('log', f'thread_info_{datetime.now().strftime("%Y%m%d_%H_%M_%S")}.log'),
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.INFO)
    logger = logging.getLogger(__name__)
    logger.addHandler(logging.StreamHandler(sys.stdout))

    return logger

class NewsWebScraper:

    def __init__(self, websites='all', output_path=None, threads_n=5, random_seed=69, logger=None):
        if not logger:
            self.logger = init_logger()
        else:
            self.logger = logger
        self._websites = websites if websites else 'all'
        self._output_path = output_path if output_path else '.'
        self._file_name = f'scraped_articles_{datetime.now().strftime("%Y%m%d_%H_%M_%S")}.pkl'
        self._thread_local = threading.local()
        self._threads_n = threads_n
        self._random_seed = random_seed
        # self._lock = threading.Lock()
        self._ref_websites ={
            'ansa': [AnsaPageScraper(), AnsaArticleScraper()],
            'bbc': [BBCPageScraper(), BBCArticleScraper()],
            'cbs': [CBSPageScraper(), CBSArticleScraper()],
            'skytg24': [SkyPageScraper(), SkyArticleScraper()],
            'yahoo': [YahooPageScraper(), YahooArticleScraper()],
        }

    def _scrape_website_article(self, thread_name, batch, lookback):
        self._thread_local.name = thread_name
        self._thread_local.existing_ref = None
        self._thread_local.scraped_articles = []

        self.logger.info(f"Thread[{self._thread_local.name}] starts")
        for website, category, article in batch:
            self.logger.info(f'Thread[{self._thread_local.name}] scraping: {article["href"]}')
            _, news_scraper = self._ref_websites.get(website.lower(), [None, None])
            
            time_article0 = time()
            if news_scraper:
               scraped_article = news_scraper.scrape(article['href'])

            if not scraped_article:
               self.logger.warning(f"Thread[{self._thread_local.name}] couldn't scrape {article['href']}")
               continue

            language = news_scraper.language.lower()[:2]
            full_article = {k:v for k,v in article.items()}
            full_article['content'] = scraped_article['content']
            full_article['content_len'] = len(scraped_article['content'])
            full_article['source_name'] = news_scraper.website_name
            full_article['source_url'] = news_scraper.basic_url
               
            if not full_article.get('sub_header', None):
                full_article['sub_header'] = scraped_article.get('sub_header', '')
            
            self._thread_local.scraped_articles.append((category, language, full_article))

            self.logger.info(f"Thread[{self._thread_local.name}] has scraped {len(self._thread_local.scraped_articles)} pages out of {len(batch)}")
            self.logger.info(f'Thread[{self._thread_local.name}] seconds to scrape {article["href"]}: {time()- time_article0}')              

        return self._thread_local.scraped_articles

    def _scrape_website_listing(self, thread_name, batch, lookback):
        self._thread_local.name = thread_name
        self._thread_local.existing_ref = None
        self._thread_local.found_articles = []

        self.logger.info(f"Thread[{self._thread_local.name}] starts")
        for website, category in batch:
            self.logger.info(f'Thread[{self._thread_local.name}] scraping: {category} on {website}')

            listing_scraper, _ = self._ref_websites.get(website.lower(), [None, None])

            time_pages0 = time()
            if listing_scraper:
                articles_refs = listing_scraper.scrape(category=category, lookback=lookback)
                articles_refs = sorted(articles_refs, key=lambda x: x['date'])
            if articles_refs:
                self._thread_local.found_articles.append((website, category, articles_refs))
            else:
                self.logger.warning(f"Thread[{self._thread_local.name}] found no articles for {category} on {website}")
                continue

            self.logger.info(f"Thread[{self._thread_local.name}] has scraped {len(self._thread_local.found_articles)} pages out of {len(batch)}")
            self.logger.info(f'Thread[{self._thread_local.name}] seconds to scrape {category} on {website}: {time()- time_pages0}')

        return self._thread_local.found_articles

    def scrape(self, categories=None, lookback=None):
        scraped_articles = defaultdict(dict)
        scraped_listings = {}
        all_categories = ['technology', 'crypto', 'latest', 'economics', 'politics', 'world']
        tot_articles = 0
        if not categories:
            categories = all_categories
        elif isinstance(categories, str) and categories.lower()=='all':
            categories = all_categories
        elif isinstance(categories, list):
            categories = [category.lower() for category in categories]
            if not all([cat in all_categories for cat in categories]):
                raise ValueError(f"categories must be either 'all' or in the following list: {all_categories}")
        else:
            raise TypeError('categories must either be of type list or "all"')
        
        if isinstance(self._websites, list):
            websites = self._websites
        elif self._websites == 'all':
            websites = list(self._ref_websites.keys())
        else:
            raise ValueError("Wrong value for website entry")
        
        combinations = list(product(websites, categories))
        combinations_batches = np.array_split(combinations, self._threads_n)
        batches_names = [f"Thread{str(n)}" for n in range(0, self._threads_n)]

        with ThreadPoolExecutor() as executor:
            futures_iterator = executor.map(
                lambda batch, name: self._scrape_website_listing(name, batch, lookback),
                combinations_batches, batches_names
            )

            for result in futures_iterator:
                for target in result:
                    website, category, articles_refs = target
                    scraped_listings[(website, category)] = articles_refs
                    tot_articles += len(articles_refs)
        
        self.logger.info(f"Scraped a total of {tot_articles} articles")

        articles = [(*k, source) for k,v in scraped_listings.items() for source in v]
        articles_batches = np.array_split(articles, self._threads_n)
        batches_names = [f"Thread{str(n)}" for n in range(0, self._threads_n)]

        with ThreadPoolExecutor() as executor:
            arts_futures_iterator = executor.map(
                lambda batch, name: self._scrape_website_article(name, batch, lookback),
                articles_batches, batches_names
            )

            for result in arts_futures_iterator:
                for target in result:
                    category, language, article = target
                    if scraped_articles.get(category, None):
                        if scraped_articles[category].get(language, None):
                            scraped_articles[category][language].append(article)
                        else:
                            scraped_articles[category][language] = [article]
                    else:
                        scraped_articles[category][language] = [article]

            #### Temporary until I get concurrency in writing to db
            self.logger.info('Saving scraped articles to db')
            saved = 0
            modified = 0
            errored = 0
            for category,v in scraped_articles.items():
                for language, articles_loop in v.items():
                    for article in articles_loop:
                        scraped_article = article.copy()

                        scraped_article['language'] = language
                        scraped_article['category'] = category

                        article_obj, created, updated = save_article(scraped_article)
                        if created:
                            saved += 1
                        if updated:
                            modified += 1
                        if (not updated) and (not created):
                            errored += 1
                            self.logger.error(f'Error updloading {article_obj} to db')
            self.logger.info(f'Saved {saved} out of {saved + modified + errored} articles scraped, {modified} updated and {errored} errored out.')
            # self.logger.info(f'Saving to {os.path.join(self._output_path, "scraped_articles", self._file_name)}')
            # pickle.dump(scraped_articles, open(os.path.join(self._output_path, "scraped_articles", self._file_name), 'wb+'))
                        
        return scraped_articles