# Copyright (c) Meta Platforms, Inc. and affiliates.
# This software may be used and distributed according to the terms of the Llama 2 Community License Agreement.

from typing import Optional

import fire

from llama import Llama


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


def _understand(self, prompt, last_sentence=None):
    generator = Llama.build(
        ckpt_dir=ckpt_dir,
        tokenizer_path=tokenizer_path,
        max_seq_len=max_seq_len,
        max_batch_size=max_batch_size,
    )

    user_triplet_prompt = "I would like to go to a park."

    dialogs = [
        [
            {"role": "system", "content": "Is the user's text a positive sentence or word? Respond with either 'yes' or 'no.'"},
            {"role": "user", "content": "I was so happy"},
        ],
        [
            {"role": "system", "content": """Someone say: 'Would you like to go to the Dragon park?'
Is the user's response a positive sentence or word? Respond with either 'yes' or 'no.'"""},
            {"role": "user", "content": "I am not sure yet."},
        ],
        [
            {"role": "system", "content": classfy_system_message},
            # {"role": "user", "content": "I would like to go to a park."},
            {"role": "user", "content": "The windows is very dirty."},
        ],
        [
            {"role": "system", "content": get_triplet_system_message('subject')},
            {"role": "user", "content": f"Analyze: \"{user_triplet_prompt}\", response only one word."},
        ],
        [
            {"role": "system", "content": get_triplet_system_message('predict')},
            {"role": "user", "content": f"Analyze: \"{user_triplet_prompt}\", response only one word."},
        ],
        [
            {"role": "system", "content": get_triplet_system_message('object')},
            {"role": "user", "content": f"Analyze: \"{user_triplet_prompt}\", response only one word."},
        ],
    ]
    results = generator.chat_completion(
        dialogs,  # type: ignore
        max_gen_len=max_gen_len,
        temperature=temperature,
        top_p=top_p,
    )

    for dialog, result in zip(dialogs, results):
        print(f"{result['generation']['content']}")


def main(
    ckpt_dir: str,
    tokenizer_path: str,
    temperature: float = 0,
    top_p: float = 0.9,
    max_seq_len: int = 512,
    max_batch_size: int = 8,
    max_gen_len: Optional[int] = None,
):
    generator = Llama.build(
        ckpt_dir=ckpt_dir,
        tokenizer_path=tokenizer_path,
        max_seq_len=max_seq_len,
        max_batch_size=max_batch_size,
    )

    user_triplet_prompt = "I would like to go to a park."

    dialogs = [
        [
            {"role": "system", "content": "Is the user's text a positive sentence or word? Respond with either 'yes' or 'no.'"},
            {"role": "user", "content": "I was so happy"},
        ],
        [
            {"role": "system", "content": """Someone say: 'Would you like to go to the Dragon park?'
Is the user's response a positive sentence or word? Respond with either 'yes' or 'no.'"""},
            {"role": "user", "content": "I am not sure yet."},
        ],
        [
            {"role": "system", "content": classfy_system_message},
            # {"role": "user", "content": "I would like to go to a park."},
            {"role": "user", "content": "The windows is very dirty."},
        ],
        [
            {"role": "system", "content": get_triplet_system_message('subject')},
            {"role": "user", "content": f"Analyze: \"{user_triplet_prompt}\", response only one word."},
        ],
        [
            {"role": "system", "content": get_triplet_system_message('predict')},
            {"role": "user", "content": f"Analyze: \"{user_triplet_prompt}\", response only one word."},
        ],
        [
            {"role": "system", "content": get_triplet_system_message('object')},
            {"role": "user", "content": f"Analyze: \"{user_triplet_prompt}\", response only one word."},
        ],
    ]
    results = generator.chat_completion(
        dialogs,  # type: ignore
        max_gen_len=max_gen_len,
        temperature=temperature,
        top_p=top_p,
    )

    for dialog, result in zip(dialogs, results):
        print(f"{result['generation']['content']}")

    # for dialog, result in zip(dialogs, results):
    #     for msg in dialog:
    #         print(f"{msg['role'].capitalize()}: {msg['content']}\n")
    #     print(
    #         f"> {result['generation']['role'].capitalize()}: {result['generation']['content']}"
    #     )
    #     print("\n==================================\n")


if __name__ == "__main__":
    fire.Fire(main)
