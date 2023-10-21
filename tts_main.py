from holon.HolonicAgent import HolonicAgent

from abdi_config import AbdiConfig
from hearing import Hearing
import helper
from brain import Brain
from dialog import DialogSystem
# from voice.playht_voice import PlayHTVoice
from voice.playht_voice_v1 import PlayHTVoiceV1


logger = helper.get_logger()


class TtsMain(HolonicAgent):
    def __init__(self, config:AbdiConfig):
        super().__init__(config)
        
        self.head_agents.append(Brain(config))
        self.head_agents.append(Hearing(config))
        self.body_agents.append(DialogSystem(config))
        self.head_agents.append(PlayHTVoiceV1(config))
        
        logger.debug(f"Init TtsMain done.")


    def _on_connect(self):
        self._subscribe("parallel/hearing/heared")
        
        super()._on_connect()


    def _on_topic(self, topic, data):
        if "parallel/hearing/heared" == topic:
            if '系統關機' in data:
                self.terminate()

        super()._on_topic(topic, data)
