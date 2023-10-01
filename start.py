# Version: 1

import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import signal

from abdi_config import AbdiConfig
import guide_config
os.environ["OPENAI_API_KEY"] = guide_config.openai_api_key
from guide_main import GuideMain
import helper


logger = helper.get_logger()


if __name__ == '__main__':
    logger.info(f'***** Main System start *****')

    def signal_handler(signal, frame):
        logger.warning("\n***************************")
        logger.warning("* System was interrupted. *")
        logger.warning("***************************\n")
    signal.signal(signal.SIGINT, signal_handler)

    GuideMain(config(options={
        "broker_type": guide_config.broker_type,
        "host": guide_config.mqtt_address,
        "port": guide_config.mqtt_port,
        "keepalive": guide_config.mqtt_keepalive,
        "username": guide_config.mqtt_username,
        "password": guide_config.mqtt_password,
    })).start()
