import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import multiprocessing
import signal

from holon import config
import app_config
from hearing.trans import Transcriptionist
import helper


logger = helper.get_logger()


if __name__ == '__main__':
    print('***** RunTrans start *****')

    def signal_handler(signal, frame):
        print("signal_handler")
    signal.signal(signal.SIGINT, signal_handler)

    cfg = config()
    cfg.mqtt_address = app_config.mqtt_address
    cfg.mqtt_port = app_config.mqtt_port
    cfg.mqtt_keepalive = app_config.mqtt_keepalive
    cfg.mqtt_username = app_config.mqtt_username
    cfg.mqtt_password = app_config.mqtt_password
    cfg.log_level = app_config.log_level
    cfg.log_dir = app_config.log_dir    
    os.environ["OPENAI_API_KEY"] = app_config.openai_api_key
    
    # helper.init_logging(log_dir=cfg.log_dir, log_level=cfg.log_level)
    multiprocessing.set_start_method('spawn')

    a = Transcriptionist(cfg)
    a.start()

    # time.sleep(5)
    # a.terminate()
