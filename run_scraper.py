from podcaster.scraper import NewsWebScraper
from datetime import datetime
from podcaster.config import config
import logging
import os
import sys

if __name__ == "__main__":
    os.makedirs('log', exist_ok = True)

    logging.basicConfig(filename=os.path.join('log', f'thread_info_{datetime.now().strftime("%Y%m%d_%H_%M_%S")}.log'),
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.INFO)
    logger = logging.getLogger(__name__)
    logger.addHandler(logging.StreamHandler(sys.stdout))
    
    scraper = NewsWebScraper(threads_n=config.get('nthreads', 10), logger=logger)

    print(f"Scraping {scraper._websites}")
    articles = scraper.scrape(lookback=2)