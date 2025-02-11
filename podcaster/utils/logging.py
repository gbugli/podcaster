from datetime import datetime
import logging
import os
import sys

class Logger:

    def __init__(self, handle_name) -> None:

        logging.basicConfig(filename=os.path.join('log', f'{handle_name}_{datetime.now().strftime("%Y%m%d_%H_%M_%S")}.log'),
                            filemode='a',
                            format='%(asctime)s,%(msecs)d %(levelname)s %(message)s',
                            datefmt='%H:%M:%S',
                            level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(logging.StreamHandler(sys.stdout))

    def info(self, msg, *args):
        return self.logger.info(msg, *args)
    
    def error(self, msg, *args):
        return self.logger.error(msg, *args)
    
    def warning(self, msg, *args):
        return self.logger.warning(msg, *args)
    
    def debug(self, msg, *args):
        return self.logger.debug(msg, *args)