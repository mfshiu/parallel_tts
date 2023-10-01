from datetime import datetime as dt
import os

from playsound import playsound

import guide_config
from holon.HolonicAgent import HolonicAgent
from holon import logger


class Speaker(HolonicAgent):
    def __init__(self, cfg):
        super().__init__(cfg)


    def _on_connect(self, client, userdata, flags, rc):
        client.subscribe("voice.wave")

        super()._on_connect(client, userdata, flags, rc)


    def _on_message(self, client, db, msg):
        if "voice.wave" == msg.topic:
            try:
                filename = dt.now().strftime(f"wave-%m%d-%H%M-%S.wav")
                filepath = os.path.join(guide_config.output_dir, filename)
                with open(filepath, "wb") as file:
                    file.write(msg.payload)
                logger.debug(f'playsound: {filepath}')
                playsound(filepath)
                os.remove(filepath)
            except Exception as ex:
                logger.exception(ex)
