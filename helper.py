import logging
from logging.handlers import TimedRotatingFileHandler
import os
import re
from pathlib import Path


logger = logging.getLogger('ABDI')
__log_init = False


def ensure_directory(dir_path):
    if not os.path.exists(dir_path):
        os.mkdir(dir_path)
        logger.info(f"Directory '{dir_path}' created successfully.")


def get_logger():
    global __log_init
    global logger
    if not __log_init:
        import app_config
        logger = init_logging(log_dir=app_config.log_dir, log_level=app_config.log_level)
        __log_init = True
        
    return logger


def init_logging(log_dir, log_level=logging.DEBUG):
    formatter = logging.Formatter(
        '%(levelname)1.1s %(asctime)s %(module)15s:%(lineno)03d %(funcName)15s) %(message)s',
        datefmt='%H:%M:%S')
    
    Path(log_dir).mkdir(parents=True, exist_ok=True)
    log_path = os.path.join(log_dir, "abdi.log")
    file_handler = TimedRotatingFileHandler(log_path, when="d")
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    
    global logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)    
    logger.setLevel(log_level)

    return logger


def remove_emojis(text):
    emoji_pattern = re.compile("["
                           u"\U0001F600-\U0001F64F"  # emoticons
                           u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                           u"\U0001F680-\U0001F6FF"  # transport & map symbols
                           u"\U0001F700-\U0001F77F"  # alchemical symbols
                           u"\U0001F780-\U0001F7FF"  # Geometric Shapes Extended
                           u"\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
                           u"\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
                           u"\U0001FA00-\U0001FA6F"  # Chess Symbols
                           u"\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
                           u"\U00002702-\U000027B0"  # Dingbat symbols
                           u"\U000024C2-\U0001F251"  # Enclosed characters
                           "]+", flags=re.UNICODE)
    
    return emoji_pattern.sub(r'', text)




from collections import deque


class CircularQueue:
    def __init__(self, size):
        self.size = size
        self.queue = deque(maxlen=size)

    def enqueue(self, item):
        self.queue.append(item)

    def dequeue(self):
        if not self.is_empty():
            return self.queue.popleft()
        return None

    def is_empty(self):
        return len(self.queue) == 0

    def is_full(self):
        return len(self.queue) == self.size

    def peek(self):
        if not self.is_empty():
            return self.queue[0]
        return None

    def __str__(self):
        return str(list(self.queue))
