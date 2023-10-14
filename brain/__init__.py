from holon.HolonicAgent import HolonicAgent
from brain.navi import Navigator
from brain.greeting import Greeting
from brain.demo_handler import DemoHandler
from brain.controller import Controller
from brain.conscious import Conscious


class Brain(HolonicAgent):
    def __init__(self, cfg):
        super().__init__(cfg)
        self.head_agents.append(Conscious(cfg))
        self.head_agents.append(Controller(cfg))
        self.body_agents.append(DemoHandler(cfg))
        # self.body_agents.append(Greeting(cfg))


    def _on_connect(self):
        super()._on_connect()


    def _on_topic(self, topic, data):
        super()._on_topic(topic, data)
