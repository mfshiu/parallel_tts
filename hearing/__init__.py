import os

import helper
from holon.HolonicAgent import HolonicAgent
# from hearing.microphone import Microphone
from hearing.microphone3 import Microphone3 as Microphone


logger = helper.get_logger()


class Hearing(HolonicAgent):
    def __init__(self, cfg):
        super().__init__(cfg)
        self.head_agents.append(Microphone(cfg))


    def _on_connect(self):
        self._subscribe("microphone.wave_path")

        super()._on_connect()


    # def _on_topic(self, topic, data):
    def _on_message(self, topic:str, payload):
        if "microphone.wave_path" == topic:
            filepath = self._convert_to_text(payload)
            logger.debug(f"wave_path:{filepath}")
            try:
                with open(filepath, "rb") as file:
                    file_content = file.read()
                logger.debug(f'publish: hearing.voice')
                os.remove(filepath)
                self._publish("hearing.voice", file_content)
            except Exception as ex:
                logger.exception(ex)
