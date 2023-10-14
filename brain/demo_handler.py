import ast
import threading

import helper
from holon.HolonicAgent import HolonicAgent
from brain import brain_helper


logger = helper.get_logger()


class DemoHandler(HolonicAgent):
    def __init__(self, cfg):
        super().__init__(cfg)


    def _on_connect(self):
        self._subscribe("demo.knowledge")

        threading.Timer(1, lambda: self._publish('brain.register_subject', 'demo')).start()
        super()._on_connect()


    def _on_topic(self, topic, data):
        if "demo.knowledge" == topic:
            knowledge = ast.literal_eval(data)

            step = int(knowledge[0][1]) - 1
            speak_texts = [
                """I understand, getting up multiple times at night can affect your sleep quality. 
If you're willing, I can help you track your urination habits and provide the information 
to your doctor for reference.""",
                """It's breakfast time now, and I can prepare breakfast for you. 
What would you like to eat today?""",
                """Alright, I'll prepare oatmeal porridge for you and your favorite bananas. 
I'll also make sure to cut them into small, easy-to-chew pieces. After breakfast, 
would you like to go for a walk?""",
                """I understand. If you're feeling uncomfortable or in pain, I recommend resting. 
I can give your knees a gentle massage, or we can do some light stretching exercises 
to alleviate the pain. What do you think?""",
                """Very well, I'll guide you through some gentle exercises. 
Please make sure to follow my pace, and let me know 
if you feel uncomfortable or in pain at any time.""",
            ]
            brain_helper.speak(self, speak_texts[step])

        super()._on_topic(topic, data)


    def terminate(self):
        self._publish('brain.unregister_subject', 'greeting')
        super().terminate()