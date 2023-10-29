# Version: 1

import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import signal

from abdi_config import AbdiConfig
import app_config
os.environ["OPENAI_API_KEY"] = app_config.openai_api_key
from tts_main import TtsMain
import helper


logger = helper.get_logger()


if __name__ == '__main__':
    logger.info(f'***** Parallel TTS start *****')

    def signal_handler(signal, frame):
        logger.warning("* System was interrupted. *")
    signal.signal(signal.SIGINT, signal_handler)

    TtsMain(AbdiConfig(options={
        "broker_type": app_config.broker_type,
        "host": app_config.mqtt_address,
        "port": app_config.mqtt_port,
        "keepalive": app_config.mqtt_keepalive,
        "username": app_config.mqtt_username,
        "password": app_config.mqtt_password,

        "input_dir": app_config.input_dir,
        "output_dir": app_config.output_dir,
        "openai_api_key": app_config.openai_api_key,
        "playht_user_id": app_config.playht_user_id,
        "playht_secret_key": app_config.playht_secret_key,
    })).start()
