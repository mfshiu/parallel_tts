import os


from holon.HolonicAgent import HolonicAgent
import helper
from helper import CircularQueue
 

logger = helper.get_logger()


class Merger(HolonicAgent):
    def __init__(self, cfg):
        super().__init__(cfg)
        # self.body_agents.append(ChatGptNlu(cfg))
        
        self._queue = CircularQueue(size=10)
        self._raw_text = ""
        self._medium_text = ""
        self._merged_text = ""


    def _on_connect(self):
        self._subscribe("hearing.trans.text")
        
        super()._on_connect()


    def _on_topic(self, topic, data):
        if "hearing.trans.text" == topic:
            self._queue.enqueue(data)
            logger.debug(f"{self._queue}")

        super()._on_topic(topic, data)


# if __name__ == '__main__':
#     Helper.init_logging()
#     logger.info('***** Hearing start *****')
#     a = Hearing()
#     a.start()
