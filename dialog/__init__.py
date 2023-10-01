from holon.HolonicAgent import HolonicAgent
from dialog.nlu import Nlu

class DialogSystem(HolonicAgent):
    def __init__(self, cfg):
        super().__init__(cfg)
        self.body_agents.append(Nlu(cfg))
