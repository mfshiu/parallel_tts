# Copyright (c) Meta Platforms, Inc. and affiliates.
# This software may be used and distributed according to the terms of the Llama 2 Community License Agreement.

from typing import Optional

import fire

from llama import Llama


def main(
    ckpt_dir: str,
    tokenizer_path: str,
    temperature: float = 0,
    top_p: float = 0.9,
    max_seq_len: int = 1024,
    max_batch_size: int = 8,
    max_gen_len: Optional[int] = None,
):
    generator = Llama.build(
        ckpt_dir=ckpt_dir,
        tokenizer_path=tokenizer_path,
        max_seq_len=max_seq_len,
        max_batch_size=max_batch_size,
    )

    user_prompt = "I would like to go to the park."
    user_prompt = "Could you give me an apple?"
    user_prompt = "I spilled a drink on the table please help clean it up."
    user_prompt = "I want to know the price of this car."
    user_prompt = "¿ Cómo está usted?"
    delimiter = "####"
    dialogs = [
        [
            # {"role": "system", "content": "You are a sentence analyzer."},
            {
                "role": "system",
                "content": f"""\
You will receive an instruction from a user.
The user's directive will be separated by {delimiter} characters.
Please categorize the instruction into major and minor categories.
And provide your output in JSON format with key values: primary (major category) and secondary (minor category).
Just output the JSON value, don't output any other text.

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
""",
            },
            {"role": "user", "content": f"{delimiter}{user_prompt}{delimiter}"},
        ],
    ]
    results = generator.chat_completion(
        dialogs,  # type: ignore
        max_gen_len=max_gen_len,
        temperature=temperature,
        top_p=top_p,
    )

    for dialog, result in zip(dialogs, results):
        for msg in dialog:
            print(f"{msg['role'].capitalize()}: {msg['content']}\n")
        print(
            f"> {result['generation']['role'].capitalize()}: {result['generation']['content']}"
        )
        print("\n==================================\n")


if __name__ == "__main__":
    fire.Fire(main)
