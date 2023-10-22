from pyht import Client
# from dotenv import load_dotenv
from pyht.client import TTSOptions
import os
# load_dotenv()

client = Client(
    user_id="RAE0rqSL3GRV3xgSEj4l33BTVC23",
    api_key="a0e5f8731539428bb52e1197963f043a",
)
options = TTSOptions(voice="s3://peregrine-voices/mel22/manifest.json")

count = 0
for chunk in client.tts("Can you tell me your account email or, ah your phone number?", options):
    if count >= 1:
        break
    count += 1
    # do something with the audio chunk
    # print(type(chunk))
    print(f"count: {count}")
    

