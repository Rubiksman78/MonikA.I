########################################################################################################
# The RWKV Language Model - https://github.com/BlinkDL/RWKV-LM
########################################################################################################

import os, copy, types, gc, sys, json

current_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(f'{current_path}/../rwkv_pip_package/src')
import typing as t

import numpy as np
from prompt_toolkit import prompt
try:
    os.environ["CUDA_VISIBLE_DEVICES"] = sys.argv[1]
except:
    pass
np.set_printoptions(precision=4, suppress=True, linewidth=200)
args = types.SimpleNamespace()

import torch
import re
from rwkv.model import RWKV
from rwkv.utils import PIPELINE

from login_screen import CONFIG
import yaml

torch.backends.cudnn.benchmark = True
torch.backends.cudnn.allow_tf32 = True
torch.backends.cuda.matmul.allow_tf32 = True

# Tune these below (test True/False for all of them) to find the fastest setting:
# torch._C._jit_set_profiling_executor(True)
# torch._C._jit_set_profiling_mode(True)
# torch._C._jit_override_can_fuse_on_cpu(True)
# torch._C._jit_override_can_fuse_on_gpu(True)
# torch._C._jit_set_texpr_fuser_enabled(False)
# torch._C._jit_set_nvfuser_enabled(False)

with open("pygmalion/pygmalion_config.yml", "r") as f:
        PYG_CONFIG = yaml.safe_load(f)

MODEL_NAME = PYG_CONFIG["model_name"]
TEMPERATURE = PYG_CONFIG["temperature"]
TOP_P = PYG_CONFIG["top_p"]
REP_PENALTY = PYG_CONFIG["repetition_penalty"]
MAX_NEW_TOKENS = PYG_CONFIG["max_new_tokens"]
CHAR_JSON = PYG_CONFIG["char_json"]
STRATEGY = PYG_CONFIG["strategy"]

# args.strategy = 'cpu fp32'
args.strategy = STRATEGY
# args.strategy = 'cuda fp16 *12 -> cpu fp32'

os.environ["RWKV_JIT_ON"] = '1' # '1' or '0', please use torch 1.13+ and benchmark speed
os.environ["RWKV_CUDA_ON"] = '0' #  '1' : use CUDA kernel for seq mode (much faster)

args.MODEL_NAME = MODEL_NAME
args.ctx_len = 4096
CHAT_LEN_SHORT = 40
CHAT_LEN_LONG = MAX_NEW_TOKENS
FREE_GEN_LEN = 200

GEN_TEMP = TEMPERATURE
GEN_TOP_P = TOP_P
GEN_alpha_presence = REP_PENALTY # Presence Penalty
GEN_alpha_frequency = REP_PENALTY # Frequency Penalty
AVOID_REPEAT = '，。：？！'
########################################################################################################
BAD_CHARS_FOR_REGEX_REGEX = re.compile(r"[-\/\\^$*+?.()|[\]{}]")

def _sanitize_string_for_use_in_a_regex(string: str) -> str:
    '''Sanitizes `string` so it can be used inside of a regexp.'''
    return BAD_CHARS_FOR_REGEX_REGEX.sub(r"\\\g<0>", string)

def parse_messages_from_str(string: str, names: t.List[str]) -> t.List[str]:
    sanitized_names = [
        _sanitize_string_for_use_in_a_regex(name) for name in names
    ]

    speaker_regex = re.compile(rf"^({'|'.join(sanitized_names)}): ?",
                               re.MULTILINE)
    message_start_indexes = []
    for match in speaker_regex.finditer(string):
        message_start_indexes.append(match.start())

    prev_start_idx = message_start_indexes[0]
    messages = []

    for start_idx in message_start_indexes[1:]:
        message = string[prev_start_idx:start_idx].strip()
        messages.append(message)
        prev_start_idx = start_idx
    message = string[prev_start_idx:].strip()
    messages.append(message)
    return messages

def build_prompt_for(
    char_greeting: str,
    char_name: str,
    char_persona: t.Optional[str] = None,
    example_dialogue: t.Optional[str] = None,
    world_scenario: t.Optional[str] = None,
    history_lenght: int = 10,
) -> str:
    example_history = parse_messages_from_str(
        example_dialogue, ["You", char_name]) if example_dialogue else []

    prompt_turns = [
        *example_history[-history_lenght:],
        f"{char_name}: {char_greeting}",
    ]

    if world_scenario:
        prompt_turns.insert(
            0,
            f"Scenario: {world_scenario}",
        )

    if char_persona:
        prompt_turns.insert(
            0,
            f"{char_name}'s Persona: {char_persona}",
        )

    context_to_bot = f"Based on all of the above, you have to play the role of {char_name} and talk to the user. You have to be completely in character and respond to the user as {char_name} would."
    prompt_turns.append(context_to_bot)
    prompt_str = "\n\n".join(prompt_turns)
    return prompt_str

with open(f"char_json/{CHAR_JSON}","r") as f:
    char_settings = json.load(f)

char_name = char_settings["char_name"]
char_persona = char_settings["char_persona"]
char_greeting = char_settings["char_greeting"]
world_scenario = char_settings["world_scenario"]
example_dialogue = char_settings["example_dialogue"]

init_prompt = build_prompt_for(
    char_greeting=char_greeting,
    char_name=char_name,
    char_persona=char_persona,
    world_scenario=world_scenario,
    example_dialogue=example_dialogue,
)

init_prompt = init_prompt.strip().split('\n')
for c in range(len(init_prompt)):
    init_prompt[c] = init_prompt[c].strip().strip('\u3000').strip('\r')
init_prompt = '\n' + ('\n'.join(init_prompt)).strip() + '\n\n'

interface = ":"
user = "You"
bot = "Monika"

# Load Model
print(f'Loading model - {args.MODEL_NAME}')
model = RWKV(model=args.MODEL_NAME, strategy=args.strategy)
pipeline = PIPELINE(model, f"{current_path}/20B_tokenizer.json")

model_tokens = []
model_state = None

AVOID_REPEAT_TOKENS = []
for i in AVOID_REPEAT:
    dd = pipeline.encode(i)
    assert len(dd) == 1
    AVOID_REPEAT_TOKENS += dd

########################################################################################################

def run_rnn(tokens, newline_adj = 0):
    global model_tokens, model_state

    tokens = [int(x) for x in tokens]
    model_tokens += tokens
    out, model_state = model.forward(tokens, model_state)

    # print(f'### model ###\n{tokens}\n[{pipeline.decode(model_tokens)}]')

    out[0] = -999999999  # disable <|endoftext|>
    out[187] += newline_adj # adjust \n probability
    # if newline_adj > 0:
    #     out[15] += newline_adj / 2 # '.'
    if model_tokens[-1] in AVOID_REPEAT_TOKENS:
        out[model_tokens[-1]] = -999999999
    return out

all_state = {}
def save_all_stat(srv, name, last_out):
    n = f'{name}_{srv}'
    all_state[n] = {}
    all_state[n]['out'] = last_out
    all_state[n]['rnn'] = copy.deepcopy(model_state)
    all_state[n]['token'] = copy.deepcopy(model_tokens)

def load_all_stat(srv, name):
    global model_tokens, model_state
    n = f'{name}_{srv}'
    model_state = copy.deepcopy(all_state[n]['rnn'])
    model_tokens = copy.deepcopy(all_state[n]['token'])
    return all_state[n]['out']

########################################################################################################

# Run inference
print(f'\nRun prompt...')

out = run_rnn(pipeline.encode(init_prompt))
save_all_stat('', 'chat_init', out)
gc.collect()
torch.cuda.empty_cache()

srv_list = ['dummy_server']
for s in srv_list:
    save_all_stat(s, 'chat', out)

def reply_msg(msg):
    print(f'{bot}{interface} {msg}\n')

def on_message(message):
    global model_tokens, model_state

    srv = 'dummy_server'

    msg = message.replace('\\n','\n').strip()

    x_temp = GEN_TEMP
    x_top_p = GEN_TOP_P
    if ("-temp=" in msg):
        x_temp = float(msg.split("-temp=")[1].split(" ")[0])
        msg = msg.replace("-temp="+f'{x_temp:g}', "")
    if ("-top_p=" in msg):
        x_top_p = float(msg.split("-top_p=")[1].split(" ")[0])
        msg = msg.replace("-top_p="+f'{x_top_p:g}', "")
    if x_temp <= 0.2:
        x_temp = 0.2
    if x_temp >= 5:
        x_temp = 5
    if x_top_p <= 0:
        x_top_p = 0
    
    out = load_all_stat(srv, 'chat')
    new = f"{user}{interface} {msg}\n\n{bot}{interface}"
    out = run_rnn(pipeline.encode(new), newline_adj=-999999999)
    save_all_stat(srv, 'chat_pre', out)
    
    begin = len(model_tokens)
    occurrence = {}
    for i in range(999):
        if i <= 0:
            newline_adj = -999999999
        elif i <= CHAT_LEN_SHORT:
            newline_adj = (i - CHAT_LEN_SHORT) / 10
        elif i <= CHAT_LEN_LONG:
            newline_adj = 0
        else:
            newline_adj = (i - CHAT_LEN_LONG) * 0.25 # MUST END THE GENERATION

        for n in occurrence:
            out[n] -= (GEN_alpha_presence + occurrence[n] * GEN_alpha_frequency)
        token = pipeline.sample_logits(
            out,
            temperature=x_temp,
            top_p=x_top_p,
        )
        if token not in occurrence:
            occurrence[token] = 1
        else:
            occurrence[token] += 1
        occurrence[187] = 0
        
        out = run_rnn([token], newline_adj=newline_adj)
        send_msg = pipeline.decode(model_tokens[begin:])

        if f"\n{user}" in send_msg:
            send_msg = send_msg.replace(f"{user}{interface}", '\n\n')
            send_msg = send_msg.strip()
            break

        if f"\n{bot}" in send_msg:
            send_msg = send_msg.replace(f"{bot}{interface}", '\n\n')
            send_msg = send_msg.strip()
            break

        if '\n\n' in send_msg:
            send_msg = send_msg.strip()
            break
    str_rep = pipeline.decode(model_tokens[begin:])
    save_all_stat(srv, 'chat', out)
    return str_rep
