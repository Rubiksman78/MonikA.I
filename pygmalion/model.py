import logging
import typing as t

import torch
import transformers

import yaml

logger = logging.getLogger(__name__)

with open("pygmalion/pygmalion_config.yml", "r") as f:
        PYG_CONFIG = yaml.safe_load(f)

USE_INT_8 = PYG_CONFIG["use_int_8"]

def build_model_and_tokenizer_for(
    model_name: str
) -> t.Tuple[transformers.AutoModelForCausalLM, transformers.AutoTokenizer]:
    '''Sets up the model and accompanying objects.'''

    logger.info(f"Loading tokenizer for {model_name}")
    tokenizer = transformers.AutoTokenizer.from_pretrained(model_name)

    bad_words_ids = [
        tokenizer(bad_word, add_special_tokens=False).input_ids
        for bad_word in _build_bad_words_list_for(model_name)
    ]
    logger.info(f"Loading the {model_name} model")
    model = transformers.AutoModelForCausalLM.from_pretrained(
        model_name,
        bad_words_ids=bad_words_ids,
        device_map="auto",
        load_in_8bit=USE_INT_8,
        torch_dtype=torch.float16,
        offload_folder="offload",
        # offload_state_dict=True,
        max_memory={0:"5890MiB","cpu":"99GiB"},
    )
    logger.info("Model and tokenizer are ready")
    return model, tokenizer


def run_raw_inference(model: transformers.AutoModelForCausalLM,
                      tokenizer: transformers.AutoTokenizer, prompt: str,
                      user_message: str, **kwargs: t.Any) -> str:
    '''
    Runs inference on the model, and attempts to returns only the newly
    generated text.

    :param model: Model to perform inference with.
    :param tokenizer: Tokenizer to tokenize input with.
    :param prompt: Input to feed to the model.
    :param user_message: The user's raw message, exactly as appended to the end
        of `prompt`. Used for trimming the original input from the model output.
    :return: Decoded model generation.
    '''
    tokenized_items = tokenizer(prompt, return_tensors="pt",truncation=True,max_length=1024,add_special_tokens=True).to("cuda")

    stopping_criteria_list = transformers.StoppingCriteriaList([
        _SentinelTokenStoppingCriteria(
            sentinel_token_ids=tokenizer(
                "\nYou:",
                add_special_tokens=False,
                return_tensors="pt",
            ).input_ids.to("cuda"),
            starting_idx=tokenized_items.input_ids.shape[-1])
    ])

    with torch.no_grad():
        logits = model.generate(stopping_criteria=stopping_criteria_list,
                                pad_token_id=tokenizer.eos_token_id,
                                **tokenized_items,
                                **kwargs)
    output = tokenizer.decode(logits[0], skip_special_tokens=True)

    logger.debug("Before trimming, model output was: `%s`", output)
    return output


def _build_bad_words_list_for(_model_name: str) -> t.List[str]:
    '''Builds a list of bad words for the given model.'''

    # NOTE(11b): This was implemented as a function because each model size
    # seems to have it quirks at the moment, but this is a rushed implementation
    # so I'm not handling that, hence the dumb return here.
    return ["Persona:", "Scenario:", "<START>"]


class _SentinelTokenStoppingCriteria(transformers.StoppingCriteria):

    def __init__(self, sentinel_token_ids: torch.LongTensor,
                 starting_idx: int):
        transformers.StoppingCriteria.__init__(self)
        self.sentinel_token_ids = sentinel_token_ids
        self.starting_idx = starting_idx

    def __call__(self, input_ids: torch.LongTensor,
                 _scores: torch.FloatTensor) -> bool:
        for sample in input_ids:
            trimmed_sample = sample[self.starting_idx:]
            # Can't unfold, output is still too tiny. Skip.
            if trimmed_sample.shape[-1] < self.sentinel_token_ids.shape[-1]:
                continue

            for window in trimmed_sample.unfold(
                    0, self.sentinel_token_ids.shape[-1], 1):
                if torch.all(torch.eq(self.sentinel_token_ids, window)):
                    return True
        return False
