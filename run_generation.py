from datetime import datetime, date
from podcaster.config import config
from podcaster.sound.generation import generate_raw_audio
import logging
import os
import sys
import pytz

if __name__ == "__main__":
    os.makedirs('log', exist_ok = True)

    logging.basicConfig(filename=os.path.join('log', f'thread_info_{datetime.now().strftime("%Y%m%d_%H_%M_%S")}.log'),
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.INFO)
    logger = logging.getLogger(__name__)
    logger.addHandler(logging.StreamHandler(sys.stdout))

    topic_thresholds = config.get('topic_thresholds')
    topics  = topic_thresholds.keys()

    root_path = config.get('projectRoot')

    dt = config.get('date')
    timezone = pytz.timezone(config.get('timezone'))

    today = datetime.now(timezone).date() if not dt else None #implement second part
    today_str = today.strftime('%Y%m%d')

    print(today)

    for topic in topics:
        topic_audio = generate_raw_audio(topic, today, logger=logger)