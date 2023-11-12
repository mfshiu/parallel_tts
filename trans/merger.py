import os


from holon.HolonicAgent import HolonicAgent
import helper
import openai

from helper import CircularQueue
 

logger = helper.get_logger()


class Merger(HolonicAgent):
    def __init__(self, cfg):
        super().__init__(cfg)
        # self.body_agents.append(ChatGptNlu(cfg))
        
        openai.api_key = cfg.get("openai_api_key")
        
        self._queue = CircularQueue(size=10)
        self._raw_text = ""
        self._medium_text = ""
        self._merged_text = ""


    def _on_connect(self):
        self._subscribe("hearing.trans.text")
        
        super()._on_connect()
        
        
    def __connect_fragments(self, merged_text, medium_text, raw_text):
        logger.debug(f"merged_text: {merged_text}")
        logger.debug(f"medium_text: {medium_text}")
        logger.debug(f"raw_text: {raw_text}")
        logger.debug(f"Connecting by ChatGPT...")
        
#         system_message = f"""You will receive three ordered sentences from a user.
# Please connect the sentences in order to form a complete sentence.
# Don’t make any changes to the first sentence.
# The order of the sentences cannot be changed.
# Only respond with the new sentence and do not provide any explanations."""
        system_message = f"""Receive three ordered sentences from a user,
connect them in order to form a complete sentence without altering the first sentence or changing their order. 
Respond only with the new sentence and provide no explanations."""
        messages =  [  
            {'role':'system', 'content': system_message},    
            {'role':'user', 'content': f"1. {merged_text}\n2. {medium_text}\n3. {raw_text}"}]

        completion = openai.ChatCompletion.create(
            model="gpt-4",
            # model="gpt-3.5-turbo",
            temperature=0,
            messages=messages
        )        
        # logger.debug(f"completion: {completion}")
        content = completion['choices'][0]['message']['content']
        
        return content


    def _on_message(self, topic:str, payload):
        if "hearing.trans.text" == topic:
            logger.debug("="*20)
            data = self._convert_to_text(payload)
            raw_text = data.strip() if data else ""
            if not self._medium_text:
                self._medium_text = raw_text
            elif not raw_text:
                self._merged_text += self._medium_text
                self._medium_text = ""
            else:                
                if len(self._merged_text) > 40:
                    merged_text_0 = self._merged_text[0:-40]
                    merged_text_1 = self._merged_text[-40:]
                else:
                    merged_text_0 = ""
                    merged_text_1 = self._merged_text
                    
                completed_text = self.__connect_fragments(
                    merged_text=merged_text_1, 
                    medium_text=self._medium_text, 
                    raw_text=raw_text)
                logger.debug(f"completed_text: {completed_text}")
                
                len_merged_text = len(merged_text_1)
                len_diff = len(completed_text) - len_merged_text                    
                seperator = len_merged_text + len_diff//2
                logger.debug(f"len_merged_text: {len_merged_text}, len_diff: {len_diff}, seperator: {seperator}")
                self._merged_text = merged_text_0 + completed_text[:seperator]
                self._medium_text = completed_text[seperator:]
                
            logger.debug(f"self._merged_text: {self._merged_text}")
            logger.debug(f"self._medium_text: {self._medium_text}")


# if __name__ == '__main__':
#     Helper.init_logging()
#     logger.info('***** Hearing start *****')
#     a = Hearing()
#     a.start()
