import ast
import threading
import time

import helper
from holon.HolonicAgent import HolonicAgent
from brain import brain_helper


logger = helper.get_logger()


class Conscious(HolonicAgent):
    def __init__(self, cfg):
        self._init = False
        super().__init__(cfg)


    def _on_connect(self):
        super()._on_connect()


    def _on_topic(self, topic, data):
        super()._on_topic(topic, data)


    def _live(self):
        if not self._init:
            self._init = True
            time.sleep(3)
            # brain_helper.speak(self, "Good morning, Mr. Zhang. It's a sunny day today, perfect for a walk! How did you sleep last night?")
            brain_helper.speak(self, "早上好，張先生。今天天氣晴，適合散步呢！您今天睡得怎麼樣？")
            # time.sleep(20)
            # self._init = False
        
        
    def _running(self):
        while self._is_running():
            try:
                self._live()
                time.sleep(.1)
            except Exception as ex:
                logger.exception(ex)
