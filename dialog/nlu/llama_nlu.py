import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import ast
import json
import re
import os

from llama import Llama

import helper
from holon import logger
from holon.HolonicAgent import HolonicAgent


logger = helper.get_logger()
# logger = helper.init_logging(guide_config.log_dir, guide_config.log_level)
# os.environ["CUDA_VISIBLE_DEVICES"] = "0"


class LlamaNlu(HolonicAgent):
    __generator = None


    def __init__(self, cfg):
        super().__init__(cfg)


    def __get_generator(self):
        if not LlamaNlu.__generator:
            self.ckpt_dir = "dialog/nlu/llama/llama-2-7b-chat/"
            self.tokenizer_path = "dialog/nlu/llama/tokenizer.model"
            self.max_seq_len = 512
            self.max_batch_size = 6
            LlamaNlu.__generator = Llama.build(
                ckpt_dir=self.ckpt_dir,
                tokenizer_path=self.tokenizer_path,
                max_seq_len=self.max_seq_len,
                max_batch_size=self.max_batch_size,
            )
        return LlamaNlu.__generator


    def _on_connect(self, client, userdata, flags, rc):
        client.subscribe("nlu.understand.text")
        client.subscribe("nlu.greeting.text")
        
        logger.info("Llama is connected MQTT")
        _ = self.__get_generator()
        super()._on_connect(client, userdata, flags, rc)


    def _on_topic(self, topic, data):
        logger.info(f"Llama is got topic: {topic}")

        if "nlu.understand.text" == topic:
            prompt, last_sentence = ast.literal_eval(data)
            knowledge = self._understand(prompt, last_sentence)
            self.publish("nlu.understand.knowledge", str(knowledge))
        elif "nlu.greeting.text" == topic:
            user_greeting, is_happy = ast.literal_eval(data)
            response = self._response_greeting(user_greeting, is_happy)
            self.publish("nlu.greeting.response", response)

        super()._on_topic(topic, data)


    def _run_begin(self):
        super()._run_begin()


    def _understand(self, prompt, last_sentence=None):
        classfy_delimiter = "####"
        classfy_system_message = f"""
You will receive an instruction from a user.
The user's directive will be separated by {classfy_delimiter} characters.
Please categorize the instruction into major and minor categories.
And provide your output in json format with key values: primary (major category) and secondary (minor category).

Primary (main category): go somewhere, get items, clean up the mess, provide information, greeting or unsupported categories.

minor categories of greeting:
normal
happy

minor categories of go somewhere:
go to a park
go to a entrance
go to a toilet
go to a export
go to a restaurant

minor categories of get items:
take a book
take a glass of water
take the remote control
take a fruit
take some items

minor categories of clean up the mess:
clear the table
clean up the ground
clean windows
clean others 

minor categories of provide information:
product specification
price
reviews
restaurant suggestion
others
talk to real people
"""


        def get_triplet_system_message(pos):
            return f"""You are a sentence analyzer.
Convert user's sentence to ({pos}) format following the rules below:
1. Response only one word.
2. If there is no subject, infer the subject.
3. Respond ONLY in the requested format: ({pos}), without any other wrods.
4. Answer in English"""


        def parse_classification(text):
            try:
                json_text_match = re.search(r'{.*}', text, re.DOTALL)
                if json_text_match:
                    json_text = json_text_match.group(0)
                    logger.debug(f"json_text: {json_text}")
                    primary, secondary = json.loads(json_text).values()
                    # print(f"primary: {primary}, secondary: {secondary[0]}")
                    if isinstance(secondary, dict):
                        classification = (primary, list(secondary[0].values())[0])
                    elif isinstance(secondary, list):
                        classification = (primary, secondary[0])
                    else:
                        classification = (primary, secondary)
                else:
                    primary_re = r'Primary \(main category\):\s*(\w+)'
                    secondary_re = r'Secondary \(minor category\):\s*(\w+)'

                    # Search for primary and secondary categories
                    primary_match = re.search(primary_re, text)
                    secondary_match = re.search(secondary_re, text)
                    if primary_match and secondary_match:
                        primary_category = primary_match.group(1)
                        secondary_category = secondary_match.group(1)
                        classification = (primary_category, secondary_category)
                    else:
                        classification = ('unsupported', 'unsupported')
            except Exception as ex:
                logger.exception(ex)
                classification = ('unsupported', 'unsupported')

            return classification
        

        if last_sentence:
            positive_dialog = [
                {"role": "system", "content": f"""Someone say: '{last_sentence}'
    Is the user's response a positive sentence or word? Respond with either 'yes' or 'no.'"""},
                {"role": "user", "content": "I am not sure yet."},
            ]
        else:
            positive_dialog = [
                {"role": "system", "content": "Is the user's text a positive sentence or word? Respond with either 'yes' or 'no.'"},
                {"role": "user", "content": f"{prompt}"},
            ]
        classfy_dialog = [
            {"role": "system", "content": classfy_system_message},
            {"role": "user", "content": f"{prompt}"},
        ]
        subject_dialog = [
                {"role": "system", "content": get_triplet_system_message('subject')},
                {"role": "user", "content": f"Analyze: \"{prompt}\", response only one word."},
            ]
        predict_dialog = [
                {"role": "system", "content": get_triplet_system_message('verb')},
                {"role": "user", "content": f"Analyze: \"{prompt}\", response only one word."},
            ]
        object_dialog = [
                {"role": "system", "content": get_triplet_system_message('object')},
                {"role": "user", "content": f"Analyze: \"{prompt}\", response only one word."},
            ]

        dialogs = [
            positive_dialog,
            classfy_dialog,
            subject_dialog,
            predict_dialog,
            object_dialog,
        ]


        results = self.__get_generator().chat_completion(
            dialogs,  # type: ignore
            # max_gen_len=200,
            temperature=0,
            # top_p=.9,
        )

        contents = []
        for i, result in enumerate(results):
            content = result['generation']['content'].lower()
            contents.append(content)
            logger.debug(f"contents[{i}]: {content}")

        _positivity = 'yes' in contents[0]

        _classification = parse_classification(contents[1])

        try:
            result = re.search(r'\((.*?)\)', contents[2])
            _subject = result.group(1) if result else None
        except Exception as ex:
            logger.exception(ex)
            _subject = None

        try:
            result = re.search(r'\((.*?)\)', contents[3])
            _predict = result.group(1) if result else None
        except Exception as ex:
            logger.exception(ex)
            _predict = None

        try:
            result = re.search(r'\((.*?)\)', contents[4])
            _object = result.group(1) if result else None
        except Exception as ex:
            logger.exception(ex)
            _object = None

        return _classification, (_subject, _predict, _object, _positivity), (prompt, last_sentence)


    def _response_greeting(self, user_greeting, is_happy=False):
        if is_happy:
            dialogs = [
                [
                    {"role": "system", "content": "Always respond with brief, upbeat sentences, but avoid using actions or emojis."},
                    {"role": "user", "content": user_greeting},
                ],
            ]
        else:
            dialogs = [
                [
                    {"role": "system", "content": "Always answer a short sentence without action."},
                    {"role": "user", "content": user_greeting},
                ],
            ]

        results = self.__get_generator().chat_completion(
            dialogs,
            temperature=.8,
        )
        response = results[0]['generation']['content']
        response = helper.remove_emojis(response)
        return response.replace('\n', '').strip()


if __name__ == '__main__':
    prompt = "Hello, nice to meet you."
    result = LlamaNlu._response_greeting(prompt, True)
    logger.debug(f"result: {result}")


if __name__ == 'x__main__':
    # prompt = "I need to go to the bathroom."
    # last_sentence = "The windows is very dirty, clean it please."
    # prompt = "Ok, I will go."
    prompt = "I would like to go to the park."
    result = LlamaNlu._understand(prompt)
    logger.debug(f"result: {result}")
