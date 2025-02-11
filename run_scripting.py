import os
import sys
import logging
from datetime import date, datetime
from podcaster.writer.combining import generate_summaries_and_scripts
from podcaster.config import config
import pytz

if __name__ == "__main__":
    logging.basicConfig(filename=os.path.join('log', f'scripting_{datetime.now().strftime("%Y%m%d_%H_%M_%S")}.log'),
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.INFO)
    logger = logging.getLogger(__name__)
    logger.addHandler(logging.StreamHandler(sys.stdout))

    multi_host = config.get('numberHosts') > 1
    root_path = config.get('projectRoot')

    dt = config.get('date')
    timezone = pytz.timezone(config.get('timezone'))

    today = datetime.now(timezone).date() if not dt else None #implement second part
    today_str = today.strftime('%Y%m%d')
    topic_thresholds = config.get('topic_thresholds')

    logger.info(f"Running for date {today.strftime('%d-%m-%Y')}")

    generate_summaries_and_scripts(topic_thresholds, today, multi_host=multi_host, root_path=root_path, logger=logger)