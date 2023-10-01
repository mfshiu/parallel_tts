import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from holon import config
from holon.HolonicAgent import HolonicAgent

from hearing import Hearing
import helper
from voice.conqui_voice import ConquiVoice
from voice.playht_voice import PlayHTVoice
from brain import Brain
from dialog import DialogSystem


logger = helper.get_logger()


class GuideMain(HolonicAgent):
    def __init__(self, cfg):
        super().__init__(cfg)
        self.body_agents.append(DialogSystem(cfg))
        self.head_agents.append(Hearing(cfg))
        self.body_agents.append(Brain(cfg))
        # self.head_agents.append(ConquiVoice(cfg))
        self.head_agents.append(PlayHTVoice(cfg))
        logger.debug(f"Init GuideMain done.")


    def _on_connect(self, client, userdata, flags, rc):
        client.subscribe("guide.hearing.heared_text")
        client.subscribe("dialog.nlu.triplet")

        # import guide_config
        # logger = helper.init_logging(log_dir=guide_config.log_dir, log_level=guide_config.log_level)
        logger.debug(f"Connect MQTT done.")
        super()._on_connect(client, userdata, flags, rc)


    def _on_topic(self, topic, data):
        if "guide.hearing.heared_text" == topic:
            if '系統關機' in data:
                self.terminate()

        super()._on_topic(topic, data)
