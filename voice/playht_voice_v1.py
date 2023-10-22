from datetime import datetime as dt
import json
import os
import requests
import threading
import time

from playsound import playsound

import app_config
import helper
from holon.HolonicAgent import HolonicAgent
from voice.speaker import Speaker


logger = helper.get_logger()


class PlayHTVoiceV1(HolonicAgent):
    def __init__(self, cfg):
        super().__init__(cfg)
        # self.head_agents.append(Speaker(cfg))


    def __tts(self, text):
        url = "https://api.play.ht/api/v1/convert"
        payload = {
            "content": [text],
            # "voice": "cmn-TW-Wavenet-B"
            "voice": "zh-CN-YunyeNeural",
            "narrationStyle": "sad"
        }
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "AUTHORIZATION": f"{app_config.playht_secret_key}", #"25c86565a13e41e6baba3979c8f90c5a",
            "X-USER-ID": f"{app_config.playht_user_id}", #"RAE0rqSL3GRV3xgSEj4l33BTVC23"
        }

        voice_url = None
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200 or response.status_code == 201:
            resp = json.loads(response.text)
            logger.debug(f"resp: {resp}")
            get_voice_url = f"https://play.ht/api/v1/articleStatus?transcriptionId={resp['transcriptionId']}"
            # get_headers = {
            #     "accept": "application/json",
            #     "content-type": "application/json",
            #     "AUTHORIZATION": f"{app_config.playht_secret_key}", #"25c86565a13e41e6baba3979c8f90c5a",
            #     "X-USER-ID": f"{app_config.playht_user_id}", #"RAE0rqSL3GRV3xgSEj4l33BTVC23"
            # }
            response = requests.get(get_voice_url, headers=headers)
            resp = json.loads(response.text)
            logger.debug(f"resp2: {resp}")
            while not resp["converted"]:
                time.sleep(.1)
                response = requests.get(get_voice_url, headers=headers)
                resp = json.loads(response.text)
                logger.debug(f"resp2: {resp}")
            voice_url = resp["audioUrl"]
            logger.debug(f"voice_url: {voice_url}")
        else:
            logger.error(f"Request failed with status code: {response.status_code}")

        return voice_url


    def __speak(self, voice_url):
        try:
            response = requests.get(voice_url)
            temp_filename = dt.now().strftime(f"speak-%m%d-%H%M-%S.mp3")
            voice_filepath = f"{app_config.output_dir}/{temp_filename}"
            with open(voice_filepath, "wb") as f:
                f.write(response.content)
            voice_filepath = os.path.abspath(voice_filepath).replace('\\', '/')
            logger.debug(f"voice_filepath: {voice_filepath}")
            playsound(voice_filepath)
            os.remove(voice_filepath)
            
        except Exception as ex:
            logger.exception(ex)           


    def _on_connect(self):
        self._subscribe("voice.text")

        super()._on_connect()


    def _on_topic(self, topic, data):
        if "voice.text" == topic and data:
            try:
                self._publish("voice.speaking")
                
                def play_voice():
                    logger.debug("Start tts")
                    # start_time = time.time()
                    #
                    voice_url = self.__tts(text=data)
                    if voice_url:
                        # logger.debug(f"Elapsed tts time: {(time.time() - start_time):.4f} seconds")
                        self.__speak(voice_url)
                        # logger.debug(f"Elapsed speak time: {(time.time() - start_time):.4f} seconds")
                    else:
                        logger.error(f"Cannot get voice url.")
                    
                    self._publish("voice.spoken")

                threading.Thread(target=play_voice).start()
                # play_voice()

            except Exception as ex:
                logger.error(ex)

        super()._on_topic(topic, data)
