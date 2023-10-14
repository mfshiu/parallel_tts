from holon.HolonicAgent import HolonicAgent
from dialog.nlu import Nlu

class DialogSystem(HolonicAgent):
    def __init__(self, config):
        super().__init__(config)
        
        self.body_agents.append(Nlu(config))
