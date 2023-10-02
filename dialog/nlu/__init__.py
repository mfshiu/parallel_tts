import os


from holon import logger
from holon.HolonicAgent import HolonicAgent
from dialog.nlu.chatgpt_nlu import ChatGptNlu
# from dialog.nlu.llama_nlu import LlamaNlu
 
class Nlu(HolonicAgent):
    def __init__(self, cfg):
        super().__init__(cfg)
        self.body_agents.append(ChatGptNlu(cfg))
        # self.body_agents.append(LlamaNlu(cfg))

        self.last_sentence = ""
        # self.__set_speaking(False)


    def _on_connect(self, client, userdata, flags, rc):
        client.subscribe("hearing.trans.text")
        client.subscribe("nlu.understand.knowledge")
        
        super()._on_connect(client, userdata, flags, rc)


    def _on_topic(self, topic, data):
        if "hearing.trans.text" == topic:
            logger.debug(f"{self.name} heared '{data}'")
            self.publish("nlu.understand.text", str((data, self.last_sentence)))
        elif "nlu.understand.knowledge" == topic:
            self.publish("dialog.knowledge", data)
            logger.info(f"Understand: {data}")

        super()._on_topic(topic, data)


# if __name__ == '__main__':
#     Helper.init_logging()
#     logger.info('***** Hearing start *****')
#     a = Hearing()
#     a.start()
