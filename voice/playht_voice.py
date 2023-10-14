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


logger = helper.get_logger()


class PlayHTVoice(HolonicAgent):
    def __init__(self, cfg):
        super().__init__(cfg)


    def __tts(self, text):
        url = "https://play.ht/api/v2/tts"
        headers = {
            "AUTHORIZATION": f"Bearer {app_config.playht_secret_key}",
            "X-USER-ID": f"{app_config.playht_user_id}",
            "accept": "text/event-stream",
            "content-type": "application/json",
        }
        data = {
            "text": text,
            "voice": "larry",
            "quality": "premium",
            "output_format": "mp3",
            "speed": 1,
            "sample_rate": 24000
        }

        voice_url = None
        response = requests.post(url, headers=headers, json=data, stream=True)
        if response.status_code == 200:
            event = None
            data = None

            for line in response.iter_lines(decode_unicode=True):
                line = line.strip()
                logger.debug(f"line: {line}")
                if not line:
                    continue
                
                key, value = tuple([pair.strip() for pair in line.split(":", 1)])
                if key == "event":
                    event = value
                elif key == "data":
                    try:
                        data = json.loads(value)
                    except Exception as ex:
                        logger.error(ex)

                if event and data:
                    if event == "completed":
                        voice_url = data["url"]
                    event = None
                    data = None
        else:
            logger.error(f"Request failed with status code: {response.status_code}")

        return voice_url


    def __speak(self, voice_url):
        response = requests.get(voice_url)
        temp_filename = dt.now().strftime(f"speak-%m%d-%H%M-%S.mp3")
        temp_filepath = os.path.join(app_config.output_dir, temp_filename)
        with open(temp_filepath, "wb") as f:
            f.write(response.content)
            
        try:
            playsound(temp_filepath)
        except Exception as ex:
            logger.exception(ex)
            
        os.remove(temp_filepath)


    def _on_connect(self):
        self._subscribe("voice.text")

        super()._on_connect()


    def _on_topic(self, topic, data):
        if "voice.text" == topic and data:
            try:
                self._publish("voice.speaking")
                
                def play_voice():
                    logger.debug("Start tts")
                    start_time = time.time()
                    #
                    voice_url = self.__tts(text=data)
                    logger.debug(f"Elapsed tts time: {(time.time() - start_time):.4f} seconds")
                    self.__speak(voice_url)
                    logger.debug(f"Elapsed speak time: {(time.time() - start_time):.4f} seconds")
                    
                    self._publish("voice.spoken")

                threading.Thread(target=play_voice).start()

            except Exception as ex:
                logger.error(ex)

        super()._on_topic(topic, data)
