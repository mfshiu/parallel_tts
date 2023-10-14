import os


from holon.HolonicAgent import HolonicAgent
# from dialog.nlu.chatgpt_nlu import ChatGptNlu
from dialog.nlu.demo_nlu import DemoNlu
# from dialog.nlu.llama_nlu import LlamaNlu
import helper
 

logger = helper.get_logger()


class Nlu(HolonicAgent):
    def __init__(self, cfg):
        super().__init__(cfg)
        # self.body_agents.append(ChatGptNlu(cfg))
        self.body_agents.append(DemoNlu(cfg))
        # self.body_agents.append(LlamaNlu(cfg))

        self.last_sentence = ""
        # self.__set_speaking(False)


    def _on_connect(self):
        self._subscribe("hearing.trans.text")
        self._subscribe("nlu.understand.knowledge")
        
        super()._on_connect()


    def _on_topic(self, topic, data):
        if "hearing.trans.text" == topic:
            logger.debug(f"{self.name} heared '{data}'")
            self._publish("nlu.understand.text", str((data, self.last_sentence)))
        elif "nlu.understand.knowledge" == topic:
            self._publish("dialog.knowledge", data)
            logger.info(f"Understand: {data}")

        super()._on_topic(topic, data)


# if __name__ == '__main__':
#     Helper.init_logging()
#     logger.info('***** Hearing start *****')
#     a = Hearing()
#     a.start()
