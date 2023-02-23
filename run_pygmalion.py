#Load pygmalion model and run it on a localhost
from pygmalion.prompting import build_prompt_for
from pygmalion.model import run_raw_inference
import typing as t
import logging


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def inference_fn(model,tokenizer,history: str, user_input: str,
                     generation_settings: t.Dict[str, t.Any],
                     char_settings: t.Dict[str,t.Any],
                     history_length = 8,
                     count = 0,
                     ) -> str:
 
    char_name = char_settings["char_name"]
    char_persona = char_settings["char_persona"]
    char_greeting = char_settings["char_greeting"]
    world_scenario = char_settings["world_scenario"]
    example_dialogue = char_settings["example_dialogue"]

    #print(char_persona)
    if count == 0 and char_greeting is not None:
        return f"{char_greeting}"

    prompt = build_prompt_for(history=history,
                                user_message=user_input,
                                char_name=char_name,
                                char_persona=char_persona,
                                example_dialogue=example_dialogue,
                                world_scenario=world_scenario,
                                history_lenght=history_length)

    model_output = run_raw_inference(model, tokenizer, prompt,
                                            user_input, **generation_settings)

    #remove last line and keep the last line before
    last_line = model_output.splitlines()[-1]
    list_lines = model_output.splitlines()
    if last_line.startswith("You:"):
        bot_message = list_lines[-2]
    else:
        bot_message = last_line

    #remove the char name at the beginning of the line
    bot_message = bot_message.replace(f"{char_name}: ","")

    return bot_message