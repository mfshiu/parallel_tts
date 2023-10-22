from datetime import datetime as dt
import os

from playsound import playsound

import app_config
import helper
from holon.HolonicAgent import HolonicAgent


logger = helper.get_logger()


class Speaker(HolonicAgent):
    def __init__(self, cfg):
        super().__init__(cfg)


    def _on_connect(self):
        self._subscribe("voice.file")
        self._subscribe("voice.wave")

        super()._on_connect()


    def _run_interval(self):
        logger.debug(f"xxx Run begin ...interval_loop")
        # print(".", end="")
    
    
    def _on_message(self, msg):
        if "voice.wave" == msg.topic:
            try:
                filename = dt.now().strftime(f"wave-%m%d-%H%M-%S.wav")
                filepath = os.path.join(app_config.output_dir, filename)
                with open(filepath, "wb") as file:
                    file.write(msg.payload)
                logger.debug(f'playsound: {filepath}')
                playsound(filepath)
                os.remove(filepath)
            except Exception as ex:
                logger.exception(ex)
        elif "voice.file" == msg.topic:
            try:
                filepath = msg.payload.decode('utf-8')
                logger.debug(f'playsound: {filepath}')
                playsound("D:/Work/NCU/Research/parallel_tts/_output/speak-1021-1948-51.mp3")
                # playsound(filepath)
                os.remove(filepath)
            except Exception as ex:
                logger.exception(ex)
