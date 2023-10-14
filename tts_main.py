from holon.HolonicAgent import HolonicAgent

from abdi_config import AbdiConfig
from hearing import Hearing
import helper
from dialog import DialogSystem


logger = helper.get_logger()


class TtsMain(HolonicAgent):
    def __init__(self, config:AbdiConfig):
        super().__init__(config)
        
        self.head_agents.append(Hearing(config))
        # self.body_agents.append(DialogSystem(config))
        # self.head_agents.append(PlayHTVoice(cfg))
        
        logger.debug(f"Init TtsMain done.")


    def _on_connect(self):
        self._subscribe("parallel/hearing/heared")
        
        super()._on_connect()


    def _on_topic(self, topic, data):
        if "parallel/hearing/heared" == topic:
            if '系統關機' in data:
                self.terminate()

        super()._on_topic(topic, data)
