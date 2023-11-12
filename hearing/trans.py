import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
from datetime import datetime as dt
import queue
import time

import whisper
import torch

import app_config
from holon.HolonicAgent import HolonicAgent
import helper


logger = helper.get_logger()


class Transcriptionist(HolonicAgent):
    def __init__(self, cfg):
        helper.ensure_directory(app_config.input_dir)
        super().__init__(cfg)


    def _on_connect(self):
        self._subscribe("hearing.voice")
        super()._on_connect()


    def _on_message(self, topic:str, payload):
        if "hearing.voice" == topic:
            filename = dt.now().strftime(f"voice-%m%d-%H%M-%S.wav")
            wave_path = os.path.join(app_config.input_dir, filename)
            with open(wave_path, "wb") as file:
                file.write(payload)
            self.wave_queue.put(wave_path)


    def _run_begin(self):
        super()._run_begin()

        device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.warning(f'Device of Whisper:{device}')
        self.wave_queue = queue.Queue()

        #model_size = "tiny"
        #model_size = "base"
        model_size = "small"
        # model_size = "medium"
        #model_size = "large"
        logger.warning(f'Loading model: {model_size}')
        self.whisper_model = whisper.load_model(model_size, device=device)
        logger.info(f'Whisper model is loaded.')


    def _running(self):
        while self._is_running():
            if self.wave_queue.empty():
                time.sleep(.1)
                continue
            try:
                wave_path = self.wave_queue.get()
                logger.debug(f'transcribe path:{wave_path}')
                result = self.whisper_model.transcribe(wave_path)
                transcribed_text = result["text"]
                self._publish("hearing.trans.text", transcribed_text)        
                logger.info(f">>> \033[33m{transcribed_text}\033[0m")
                if os.path.exists(wave_path):
                    os.remove(wave_path)
                logger.debug(f'Remained waves: {self.wave_queue.qsize()}')
            except queue.Empty:
                pass
            except UnicodeEncodeError:
                logger.info(f">>> \033[33m{transcribed_text.encode('utf-8')}\033[0m")
            except Exception as ex:
                _, exc_value, _ = sys.exc_info()
                logger.error(exc_value)
