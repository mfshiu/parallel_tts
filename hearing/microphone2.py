import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from datetime import datetime as dt
import threading
import time

import numpy as np
import pyaudio
import wave

import app_config
import helper
from holon.HolonicAgent import HolonicAgent


logger = helper.get_logger()

# Voice recording parameters
CHUNK = 2048
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
RECORD_SECONDS = 5
MAX_RECORD_SECONDS = 10 * 60
SILENCE_THRESHOLD = (RATE // CHUNK) * 0.28

class Microphone2(HolonicAgent):
    def __init__(self, cfg=None):
        helper.ensure_directory(cfg.get("output_dir"))
        self.__set_speaking(False)
        self.share_frames = []
        logger.debug(f"Init Microphone done.")
        super().__init__(cfg)


    def __set_speaking(self, is_speaking):
        self.speaking = is_speaking
        logger.warning(f"SPEAKING: {self.speaking}")


    def _on_connect(self):
        self._subscribe("voice.speaking")
        self._subscribe("voice.spoken")

        super()._on_connect()


    def _on_message(self, topic:str, payload):
        if "voice.speaking" == topic:
            self.__set_speaking(True)
        elif "voice.spoken" == topic:
            self.__set_speaking(False)


    def __compute_frames_mean(frames):
        def to_shorts(bytes):
            data = np.frombuffer(bytes, dtype=np.int16)
            return [x if x <= 32767 else 32767 - x for x in data]
        
        if not frames:
            return 0
        
        data = [x for x in to_shorts(frames) if x >= 0]
        audio_mean = 0 if len(data) == 0 else sum([int(x) for x in data]) // len(data)
        return audio_mean
    

    def __record_to_limit(self, audio_stream, limit_seconds):
        logger.debug("Record to silence..")

        frames = []
        voice_count = 0

        total_frames = int(RATE / CHUNK * limit_seconds)
        for _ in range(0, total_frames):
            if not self._is_running() or self.speaking:
                # frames = []
                break
            try:
                sound_raw = audio_stream.read(CHUNK)
            except Exception as ex:
                logger.error("Read audio stream error!\n%s", str(ex))
                break
            frames.append(sound_raw)

            mean = Microphone2.__compute_frames_mean(sound_raw)
            if mean < 200:
                print('.', end='', flush=True)
            else:
                voice_count += 1
                print('^', end='', flush=True)

        return frames if voice_count > total_frames // 10 else []


    def _record(self):
        audio = pyaudio.PyAudio()
        audio_stream = audio.open(format=FORMAT, channels=CHANNELS,
                            rate=RATE, input=True,
                            frames_per_buffer=CHUNK)
        
        while self._is_running():
            frames = self.__record_to_limit(audio_stream, 3)
            if frames and self._is_running()and not self.speaking:
                wave_path = None
                # logger.debug(f"self.speaking: {self.speaking}, frames_mean: {frames_mean}")
                if frames and len(frames) >= SILENCE_THRESHOLD//2: #and frames_mean >= 500:
                    
                    def write_wave_file(wave_path, wave_data):
                        logger.debug(f"Write to file: {wave_path}...")
                        wf = wave.open(wave_path, 'wb')
                        wf.setnchannels(CHANNELS)
                        wf.setsampwidth(audio.get_sample_size(FORMAT))
                        wf.setframerate(RATE)
                        wf.writeframes(b''.join(frames))
                        wf.close()
                        self._publish("microphone.wave_path", wave_path)                

                    filename = dt.now().strftime(f"record-%m%d-%H%M-%S.wav")
                    wave_path = os.path.join(app_config.output_dir, filename)
                    threading.Thread(target=write_wave_file, args=(wave_path, b''.join(frames),)).start()
            

        # Stop recording
        audio_stream.stop_stream()
        audio_stream.close()
        audio.terminate()


    def _running(self):
        while self._is_running():
            try:
                self._record()
            except Exception as ex:
                logger.exception(ex)
            time.sleep(.1)


if __name__ == '__main__':
    logger.info('***** Microphone start *****')
    a = Microphone2()
    a.start()
