import ast
import threading

import helper
from holon.HolonicAgent import HolonicAgent
from brain import brain_helper


logger = helper.get_logger()


class Greeting(HolonicAgent):
    def __init__(self, cfg):
        super().__init__(cfg)


    def _on_connect(self):
        self._subscribe("greeting.knowledge")
        self._subscribe("nlu.greeting.response")

        threading.Timer(1, lambda: self._publish('brain.register_subject', 'greeting')).start()
        super()._on_connect()


    def _on_topic(self, topic, data):
        logger.debug(f"Got topic: {topic}")
        
        if "greeting.knowledge" == topic:
            knowledge = ast.literal_eval(data)

            happy = (knowledge[0][1] == 'happy')
            self._publish("nlu.greeting.text", str((knowledge[2][0], happy)))

        elif "nlu.greeting.response" == topic:
            brain_helper.speak(self, data)
            self._publish('brain.subject_done')

        super()._on_topic(topic, data)


    def terminate(self):
        self._publish('brain.unregister_subject', 'greeting')
        super().terminate()