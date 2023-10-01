import ast
import threading

from helper import logger
from holon.HolonicAgent import HolonicAgent
from brain import brain_helper

class Navigator(HolonicAgent):
    def __init__(self, cfg):
        super().__init__(cfg)
        self.state = 0


    def _on_connect(self, client, userdata, flags, rc):
        client.subscribe("go somewhere.knowledge")        
        threading.Timer(2, lambda: self.publish('brain.register_subject', 'go somewhere')).start()

        super()._on_connect(client, userdata, flags, rc)


    def __set_state(self, new_state):
        self.state = new_state
        logger.debug(f"New state: {new_state}")
       
    
    def __process_navi(self, knowledge):
        logger.debug(f"state: {self.state}, knowledge: '{knowledge}'")
        triplet = knowledge[1]
        if self.state == 0:
            self.target = triplet[2]
            brain_helper.speak(self, f"How about going to Dragon {self.target}?")
            self.__set_state(1)
        elif self.state == 1:
            if triplet[3]:
                brain_helper.speak(self, f"OK, let's go.")
                def arrive():
                    self.__set_state(0)
                    brain_helper.speak(self, f"We arrive the Dragon {self.target}.")
                    self.publish('brain.subject_done')
                threading.Timer(6, lambda: arrive()).start()
                self.__set_state(2)
            else:
                brain_helper.speak(self, f"Let me know if you want to go to the {self.target}.")
                self.__set_state(0)
                self.publish('brain.subject_done')
        elif self.state == 2:
            brain_helper.speak(self, f"We are on our way to Dragon {self.target}.")


    def _on_topic(self, topic, data):
        if "go somewhere.knowledge" == topic:
            knowledge = ast.literal_eval(data)
            self.__process_navi(knowledge)

        super()._on_topic(topic, data)


    def terminate(self):
        self.publish('brain.unregister_subject', 'greeting')
        super().terminate()
