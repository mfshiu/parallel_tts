import ast
import json
import os
import threading

import openai

import helper
from holon.HolonicAgent import HolonicAgent


logger = helper.get_logger()
openai.api_key = os.environ['OPENAI_API_KEY']


class DemoNlu(HolonicAgent):
    def __init__(self, cfg):
        super().__init__(cfg)


    def _on_connect(self):
        self._subscribe("nlu.understand.text")
        
        super()._on_connect()


    def _on_topic(self, topic, data):
        if "nlu.understand.text" == topic:
            prompt, last_sentence = ast.literal_eval(data)
            knowledge = self._understand(prompt, last_sentence)
            self._publish("nlu.understand.knowledge", str(knowledge))

        super()._on_topic(topic, data)
        

    def _understand(self, prompt, last_sentence=None):
        if "bathroom" in prompt or "廁所" in prompt:
            _classification = ("demo", "1")
        elif "What" in prompt or "什麼" in prompt:
            _classification = ("demo", "2")
        elif "fruit" in prompt or "水果" in prompt:
            _classification = ("demo", "3")
        elif "knees" in prompt or "膝蓋" in prompt:
            _classification = ("demo", "4")
        elif "exercises" in prompt or "運動" in prompt:
            _classification = ("demo", "5")
        else:
            _classification = ("demo", "0")

        return _classification, None, (prompt, last_sentence)
