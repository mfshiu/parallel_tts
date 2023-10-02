import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from datetime import datetime as dt
import threading
import time

import numpy as np
import pyaudio
import wave

import helper
from holon.HolonicAgent import HolonicAgent
import app_config


logger = helper.get_logger()

# Voice recording parameters
CHUNK = 2048
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
RECORD_SECONDS = 5
MAX_RECORD_SECONDS = 10 * 60
SILENCE_THRESHOLD = (RATE // CHUNK) * 0.28

class Microphone(HolonicAgent):
    def __init__(self, cfg=None):
        helper.ensure_directory(app_config.output_dir)
        self.__set_speaking(False)
        logger.debug(f"Init Microphone done.")
        super().__init__(cfg)


    def __set_speaking(self, is_speaking):
        self.speaking = is_speaking
        logger.warning(f"SPEAKING: {self.speaking}")


    def _on_connect(self, client, userdata, flags, rc):
        client.subscribe("voice.speaking")
        client.subscribe("voice.spoken")

        super()._on_connect(client, userdata, flags, rc)


    def _on_topic(self, topic, data):
        logger.debug(f"Got topic: {topic}")
        
        if "voice.speaking" == topic:
            self.__set_speaking(True)
        elif "voice.spoken" == topic:
            self.__set_speaking(False)

        super()._on_topic(topic, data)


    def __compute_frames_mean(frames):
        def to_shorts(bytes):
            data = np.frombuffer(bytes, dtype=np.int16)
            return [x if x <= 32767 else 32767 - x for x in data]
        
        if not frames:
            return 0
        
        data = [x for x in to_shorts(frames) if x >= 0]
        audio_mean = 0 if len(data) == 0 else sum([int(x) for x in data]) // len(data)
        return audio_mean
    

    def __wait_voice(self, audio_stream):
        first_frames = []
        # logger.debug(f"for 60 second... (is speaking: {self.speaking})")
        
        for _ in range(0, int(RATE / CHUNK * 60)):
            if not self.is_running() or self.speaking:
                # logger.warning(f"User is speaking, or system is terminating.")
                first_frames = []
                break

            try:
                sound_raw = audio_stream.read(CHUNK)
            except Exception as ex:
                logger.error("Read audio stream error!\n%s", str(ex))
                break

            if not Microphone.__compute_frames_mean(sound_raw) < 200:
                first_frames.append(sound_raw)  # found voice
                if len(first_frames) > 2:
                    break                       # ready to record
            elif len(first_frames):
                    first_frames.clear()

        frames_len = len(first_frames)
        # logger.debug(f'Frame length: {frames_len}')
        return first_frames if frames_len else None
    

    def __record_to_silence(self, audio_stream):
        frames = []
        silence_count = 0
        total_mean = 0

        for _ in range(0, int(RATE / CHUNK * MAX_RECORD_SECONDS)):
            if not self.is_running() or self.speaking:
                frames = []
                break
            try:
                sound_raw = audio_stream.read(CHUNK)
            except Exception as ex:
                logger.error("Read audio stream error!\n%s", str(ex))
                break
            frames.append(sound_raw)

            mean = Microphone.__compute_frames_mean(sound_raw)
            total_mean += mean
            if mean < 200:
                silence_count += 1
                print('.', end='', flush=True)
            else:
                silence_count = 0
                print('^', end='', flush=True)
                # print(f'{mean}', end='', flush=True)
            if silence_count > SILENCE_THRESHOLD*1:
                print()
                logger.debug(f"silence_count:{silence_count}, frames: {len(frames)}")
                break

        frames_mean = 0
        if len(frames):
            frames_mean = total_mean // len(frames)
            # logger.debug(f"frames: {frames}")
            # logger.debug(f'frames mean: {frames_mean}')

        return frames, frames_mean


    def _record(self):
        audio = pyaudio.PyAudio()
        audio_stream = audio.open(format=FORMAT, channels=CHANNELS,
                            rate=RATE, input=True,
                            frames_per_buffer=CHUNK)
        
        frames = self.__wait_voice(audio_stream)
        frames_mean = 0
        if frames:
            other_frames, frames_mean = self.__record_to_silence(audio_stream)
            frames.extend(other_frames)
        frames_len = len(frames) if frames else 0
        # logger.debug(f'Frames mean: {frames_mean}, Frames length: {frames_len}')

        # Stop recording
        audio_stream.stop_stream()
        audio_stream.close()
        audio.terminate()

        wave_path = None
        if self.is_running() or not self.speaking:
            if frames and frames_len >= SILENCE_THRESHOLD//2 and frames_mean > 200:
                
                def write_wave_file(wave_path, wave_data):
                    logger.info(f"Write to file: {wave_path}...")
                    wf = wave.open(wave_path, 'wb')
                    wf.setnchannels(CHANNELS)
                    wf.setsampwidth(audio.get_sample_size(FORMAT))
                    wf.setframerate(RATE)
                    wf.writeframes(b''.join(frames))
                    wf.close()
                    
                    topic = "microphone.wave_path"
                    self.publish(topic, wave_path)                
                    logger.debug(f"publish: {topic} / {wave_path}")
                    # test
                    #playsound(wave_path)
                    #os.remove(wave_path)

                filename = dt.now().strftime(f"record-%m%d-%H%M-%S.wav")
                wave_path = os.path.join(app_config.output_dir, filename)
                threading.Thread(target=write_wave_file, args=(wave_path, b''.join(frames),)).start()

        return wave_path


    def _running(self):
        while self.is_running():
            try:
                wave_path = self._record()
                if not wave_path:
                    time.sleep(.1)
            except Exception as ex:
                logger.exception(ex)


if __name__ == '__main__':
    logger.info('***** Microphone start *****')
    a = Microphone()
    a.start()
