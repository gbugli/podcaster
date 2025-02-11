from datetime import datetime, date
from podcaster.config import config
from podcaster.sound.postprocessing import post_process
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

    topics  = config.get('topic_thresholds').keys()

    root_path = config.get('projectRoot')
    song_path = os.path.join(root_path, config.get('songPath'))

    dt = config.get('date')
    timezone = pytz.timezone(config.get('timezone'))

    today = datetime.now(timezone).date() if not dt else None #implement second part
    today_str = today.strftime('%Y%m%d')

    podcast_audio = post_process(song_path, date_obj=today, topics=topics, format="wav")