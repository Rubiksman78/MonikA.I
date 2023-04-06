import os,sys
import tkinter as tk
import json
import yaml
# Configuration
args = sys.argv[1:]

save_ids = os.path.exists("save_text.txt")

root = tk.Tk()
root.title("MonikA.I. Submod")
root.geometry("900x500")
#root.resizable(False, False)
root.configure(background='#333333')

def get_input():
    global USERNAME
    global PASSWORD
    global CHOOSE_CHARACTER
    global GAME_PATH
    global USE_CHARACTER_AI
    global USE_TTS
    global DEBUG_MODE
    global CONTINUE_FROM_LAST
    global USE_CAMERA
    global TIME_INTERVALL
    global USE_LOCAL_CHATBOT
    global CHAT_MODEL
    global LAUNCH_YOURSELF
    global USE_ACTIONS
    global TTS_MODEL
    global USE_SPEECH_RECOGNITION
    global VOICE_SAMPLE_TORTOISE
    global VOICE_SAMPLE_COQUI
    global CHARACTER_JSON
    USERNAME = username.get()
    PASSWORD = password.get()
    CHOOSE_CHARACTER = choose_character.get()
    USE_CHARACTER_AI = use_character_ai.get()
    USE_TTS = use_tts.get()
    GAME_PATH = game_path.get()
    LAUNCH_YOURSELF = launch_yourself.get()
    DEBUG_MODE = debug_mode.get()
    CONTINUE_FROM_LAST = continue_from_last.get()
    USE_CAMERA = use_camera.get()
    TIME_INTERVALL = time_intervall.get()
    USE_LOCAL_CHATBOT = use_local_chatbot.get()
    CHAT_MODEL = chat_model.get()
    USE_ACTIONS = use_actions.get()
    TTS_MODEL = tts_model.get()
    USE_SPEECH_RECOGNITION = use_speech_recognition.get()
    VOICE_SAMPLE_TORTOISE = voice_sample_tortoise.get()
    VOICE_SAMPLE_COQUI = voice_sample_coqui.get()
    CHARACTER_JSON = character_json.get()
    root.destroy()

char_ai_frame = tk.LabelFrame(root,bg='#333333',text="Character AI",fg='white',font=("Helvetica", 16))
char_ai_frame.grid(row=4, column=0)

other_frame = tk.LabelFrame(root,bg='#333333',text="General Settings",fg='white',font=("Helvetica", 16))
other_frame.grid(row=5, column=0)

username = tk.StringVar()
password = tk.StringVar()
choose_character = tk.StringVar()
use_character_ai = tk.StringVar()
use_tts = tk.StringVar()
game_path = tk.StringVar()
launch_yourself = tk.StringVar()
debug_mode = tk.StringVar()
continue_from_last = tk.StringVar()
use_camera = tk.StringVar()
time_intervall = tk.StringVar()
use_local_chatbot = tk.StringVar()
chat_model = tk.StringVar()
use_actions = tk.StringVar()
tts_model = tk.StringVar()
use_speech_recognition = tk.StringVar()
voice_sample_tortoise = tk.StringVar()
voice_sample_coqui = tk.StringVar()
character_json = tk.StringVar()

#Character AI related
tk.Label(char_ai_frame, text="Email",bg='#333333',fg='white').grid(row=0, column=0)
tk.Label(char_ai_frame, text="Password",bg='#333333',fg='white').grid(row=1, column=0)
tk.Label(char_ai_frame, text="Use Character AI",bg='#333333',fg='white').grid(row=2, column=0)
tk.Label(char_ai_frame, text="Choose Character",bg='#333333',fg='white').grid(row=2, column=3)
tk.Label(char_ai_frame, text="Use Debug Mode",bg='#333333',fg='white').grid(row=3, column=0)
tk.Label(char_ai_frame, text="Continue from last chat",bg='#333333',fg='white').grid(row=4, column=0)

#General Settings
tk.Label(other_frame, text="Game Path",bg='#333333',fg='white').grid(row=1, column=0)
tk.Label(other_frame, text="Launch Yourself",bg='#333333',fg='white').grid(row=1, column=3)
tk.Label(other_frame, text="Use Actions",bg='#333333',fg='white').grid(row=2, column=0)
tk.Label(other_frame, text="Use TTS",bg='#333333',fg='white').grid(row=3, column=0)
tk.Label(other_frame, text="TTS model",bg='#333333',fg='white').grid(row=3, column=3)
tk.Label(other_frame, text="Use Local Chatbot",bg='#333333',fg='white').grid(row=4, column=0)
tk.Label(other_frame, text="Chatbot Model",bg='#333333',fg='white').grid(row=4, column=3)
tk.Label(other_frame, text="Use Camera",bg='#333333',fg='white').grid(row=5, column=0)
tk.Label(other_frame, text="Time Intervall For Camera",bg='#333333',fg='white').grid(row=5,column=3)
tk.Label(other_frame, text="Use Speech Recognition",bg='#333333',fg='white').grid(row=6, column=0)
tk.Label(other_frame, text="Voice Sample (Tortoise)",bg='#333333',fg='white').grid(row=7, column=0)
tk.Label(other_frame, text="Voice Sample (Your TTS)",bg='#333333',fg='white').grid(row=7, column=3)
tk.Label(other_frame, text="Character JSON",bg='#333333',fg='white').grid(row=8, column=0)

#Textual Inputs
tk.Entry(char_ai_frame, textvariable=username,width=25).grid(row=0, column=1)
tk.Entry(char_ai_frame, textvariable=password,show='*',width=25).grid(row=1, column=1)
tk.Entry(other_frame, textvariable=game_path,width=25).grid(row=1, column=1)
tk.Entry(other_frame, textvariable=time_intervall,width=10).grid(row=5, column=4)

#Scrollable Inputs
char_menu = tk.OptionMenu(char_ai_frame, choose_character, "0", "1")
char_menu.config( bg='white',fg='black')
char_menu.grid(row=2, column=4)

all_models = os.listdir("chatbot_models")
all_models = [x for x in all_models if not x.endswith(".txt")]
if len(all_models) == 0:
    all_models = ["No models found"]
chat_menu = tk.OptionMenu(other_frame, chat_model, *all_models)
chat_menu.config(bg='white',fg='black')
chat_menu.grid(row=4, column=4)

tts_menu = tk.OptionMenu(other_frame, tts_model, "Your TTS", "Tortoise TTS")
tts_menu.config( bg='white',fg='black')
tts_menu.grid(row=3, column=4)

all_voices_tortoise = os.listdir("tortoise_audios")
all_voices_tortoise = [x for x in all_voices_tortoise if not x.endswith(".txt")]
voice_menu = tk.OptionMenu(other_frame, voice_sample_tortoise, *all_voices_tortoise)
voice_menu.config( bg='white',fg='black')
voice_menu.grid(row=7, column=1)

all_voices_coquiai = os.listdir("coquiai_audios")
all_voices_coquiai = [x for x in all_voices_coquiai if x.endswith(".wav")]
if len(all_voices_coquiai) == 0:
    all_voices_coquiai = ["No voices found"]
voice_menu = tk.OptionMenu(other_frame, voice_sample_coqui, *all_voices_coquiai)
voice_menu.config( bg='white',fg='black')
voice_menu.grid(row=7, column=4)

all_characters = os.listdir("char_json")
all_characters = [x for x in all_characters if not x.endswith(".txt")]
character_menu = tk.OptionMenu(other_frame, character_json, *all_characters)
character_menu.config( bg='white',fg='black')
character_menu.grid(row=8, column=1)

#Yes/No Inputs
tk.Radiobutton(char_ai_frame, text="Yes", variable=use_character_ai, value=True,bg='#333333',activeforeground='white',fg='white',activebackground="#333333",selectcolor='#333333').grid(row=2, column=1)
tk.Radiobutton(char_ai_frame, text="No", variable=use_character_ai, value=False,bg='#333333',activeforeground='white',fg='white',activebackground="#333333",selectcolor='#333333').grid(row=2, column=2)

tk.Radiobutton(char_ai_frame, text="Yes", variable=debug_mode, value=True,bg='#333333',activeforeground='white',fg='white',activebackground="#333333",selectcolor='#333333').grid(row=3, column=1)
tk.Radiobutton(char_ai_frame, text="No", variable=debug_mode, value=False,bg='#333333',activeforeground='white',fg='white',activebackground="#333333",selectcolor='#333333').grid(row=3, column=2)

tk.Radiobutton(char_ai_frame, text="Yes", variable=continue_from_last, value=True,bg='#333333',activeforeground='white',fg='white',activebackground="#333333",selectcolor='#333333').grid(row=4, column=1)
tk.Radiobutton(char_ai_frame, text="No", variable=continue_from_last, value=False,bg='#333333',activeforeground='white',fg='white',activebackground="#333333",selectcolor='#333333').grid(row=4, column=2)

tk.Radiobutton(other_frame, text="Yes", variable=launch_yourself, value=True,bg='#333333',activeforeground='white',fg='white',activebackground="#333333",selectcolor='#333333').grid(row=1, column=4)
tk.Radiobutton(other_frame, text="No", variable=launch_yourself, value=False,bg='#333333',activeforeground='white',fg='white',activebackground="#333333",selectcolor='#333333').grid(row=1, column=5)

tk.Radiobutton(other_frame, text="Yes", variable=use_actions, value=True,bg='#333333',activeforeground='white',fg='white',activebackground="#333333",selectcolor='#333333').grid(row=2, column=1)
tk.Radiobutton(other_frame, text="No", variable=use_actions, value=False,bg='#333333',activeforeground='white',fg='white',activebackground="#333333",selectcolor='#333333').grid(row=2, column=2)

tk.Radiobutton(other_frame, text="Yes", variable=use_tts, value=True,bg='#333333',activeforeground='white',fg='white',activebackground="#333333",selectcolor='#333333').grid(row=3, column=1)
tk.Radiobutton(other_frame, text="No", variable=use_tts, value=False,bg='#333333',activeforeground='white',fg='white',activebackground="#333333",selectcolor='#333333').grid(row=3, column=2)

tk.Radiobutton(other_frame, text="Yes", variable=use_local_chatbot, value=True,bg='#333333',activeforeground='white',fg='white',activebackground="#333333",selectcolor='#333333').grid(row=4, column=1)
tk.Radiobutton(other_frame, text="No", variable=use_local_chatbot, value=False,bg='#333333',activeforeground='white',fg='white',activebackground="#333333",selectcolor='#333333').grid(row=4, column=2)

tk.Radiobutton(other_frame, text="Yes", variable=use_camera, value=True,bg='#333333',activeforeground='white',fg='white',activebackground="#333333",selectcolor='#333333').grid(row=5, column=1)
tk.Radiobutton(other_frame, text="No", variable=use_camera, value=False,bg='#333333',activeforeground='white',fg='white',activebackground="#333333",selectcolor='#333333').grid(row=5, column=2)

tk.Radiobutton(other_frame, text="Yes", variable=use_speech_recognition, value=True,bg='#333333',activeforeground='white',fg='white',activebackground="#333333",selectcolor='#333333').grid(row=6, column=1)
tk.Radiobutton(other_frame, text="No", variable=use_speech_recognition, value=False,bg='#333333',activeforeground='white',fg='white',activebackground="#333333",selectcolor='#333333').grid(row=6, column=2)

button = tk.Button(root, text="Submit", command=get_input,bg='#FF3399',fg='white')
button.place(relx=0.5, rely=0.95, anchor=tk.CENTER)

#Get IDs for autofill
if save_ids:
    with open("save_text.txt", "r") as f:
        string = f.read()
        GAME_PATH,USERNAME,PASSWORD = string.split(";")

    username.set(USERNAME)
    password.set(PASSWORD)
    game_path.set(GAME_PATH)

if not os.path.exists("config.json"):
    #Set default values
    launch_yourself.set(0)
    time_intervall.set("10")
    use_character_ai.set(0)
    use_tts.set(0)
    debug_mode.set(0)
    continue_from_last.set(0)
    choose_character.set("0")
    use_camera.set(0)
    use_local_chatbot.set(0)
    chat_model.set("No model set")
    use_actions.set(0)
    tts_model.set("Your TTS")
    use_speech_recognition.set(0)
    voice_sample_tortoise.set("Choose a Tortoise voice sample")
    voice_sample_coqui.set("Choose a YourTTS voice sample")
    character_json.set("Choose a character")
else:
    with open("config.json", "r") as f:
        config = json.load(f)
    if "USE_LOCAL_CHATBOT" not in config:
        os.remove("config.json")
        #Set default values
        launch_yourself.set(0)
        time_intervall.set("10")
        use_character_ai.set(0)
        use_tts.set(0)
        debug_mode.set(0)
        continue_from_last.set(0)
        choose_character.set("0")
        use_camera.set(0)
        use_local_chatbot.set(0)
        chat_model.set("No model set")
        use_actions.set(0)
        tts_model.set("Your TTS")
        use_speech_recognition.set(0)
        voice_sample_tortoise.set("Choose a Tortoise voice sample")
        voice_sample_coqui.set("Choose a YourTTS voice sample")
        character_json.set("Choose a character")
    else:
        GAME_PATH = config["GAME_PATH"]
        USERNAME = config["USERNAME"]
        PASSWORD = config["PASSWORD"]
        USE_TTS = config["USE_TTS"]
        USE_CHARACTER_AI = config["USE_CHARACTER_AI"]
        DEBUG_MODE = config["DEBUG_MODE"]
        CONTINUE_FROM_LAST = config["CONTINUE_FROM_LAST"]
        CHOOSE_CHARACTER = config["CHOOSE_CHARACTER"]
        USE_CAMERA = config["USE_CAMERA"]
        TIME_INTERVALL = config["TIME_INTERVALL"]
        USE_LOCAL_CHATBOT = config["USE_LOCAL_CHATBOT"]
        LAUNCH_YOURSELF = config["LAUNCH_YOURSELF"]
        USE_ACTIONS = config["USE_ACTIONS"]
        TTS_MODEL = config["TTS_MODEL"]
        CHAT_MODEL = config["CHAT_MODEL"]
        USE_SPEECH_RECOGNITION = config["USE_SPEECH_RECOGNITION"]
        VOICE_SAMPLE_TORTOISE = config["VOICE_SAMPLE_TORTOISE"]
        VOICE_SAMPLE_COQUI = config["VOICE_SAMPLE_COQUI"]
        CHARACTER_JSON = config["CHARACTER_JSON"]
        #Set saved values
        launch_yourself.set(LAUNCH_YOURSELF)
        time_intervall.set(TIME_INTERVALL)
        use_character_ai.set(USE_CHARACTER_AI)
        use_tts.set(USE_TTS)
        debug_mode.set(DEBUG_MODE)
        continue_from_last.set(CONTINUE_FROM_LAST)
        choose_character.set(CHOOSE_CHARACTER)
        use_camera.set(USE_CAMERA)
        use_local_chatbot.set(USE_LOCAL_CHATBOT)
        chat_model.set(CHAT_MODEL)
        use_actions.set(USE_ACTIONS)
        tts_model.set(TTS_MODEL)
        use_speech_recognition.set(USE_SPEECH_RECOGNITION)
        voice_sample_tortoise.set(VOICE_SAMPLE_TORTOISE)
        voice_sample_coqui.set(VOICE_SAMPLE_COQUI)
        character_json.set(CHARACTER_JSON)

root.mainloop()
#Write IDs to file for autofill
if GAME_PATH != "" or USERNAME != "" or PASSWORD != "":
    with open("save_text.txt", "w") as f:
        f.write(GAME_PATH + ";" + USERNAME + ";" + PASSWORD)

#Convert string to int (0 or 1, False or True)
USE_TTS = int(USE_TTS)
USE_CHARACTER_AI = int(USE_CHARACTER_AI)
DEBUG_MODE = int(DEBUG_MODE)
CONTINUE_FROM_LAST = int(CONTINUE_FROM_LAST)
USE_CAMERA = int(USE_CAMERA)
TIME_INTERVALL = int(TIME_INTERVALL)
USE_LOCAL_CHATBOT = int(USE_LOCAL_CHATBOT)
LAUNCH_YOURSELF = int(LAUNCH_YOURSELF)
USE_ACTIONS = int(USE_ACTIONS)
USE_SPEECH_RECOGNITION = int(USE_SPEECH_RECOGNITION)

if TTS_MODEL == "Tortoise TTS":
    voices_tortoise = os.listdir(f"tortoise_audios/{VOICE_SAMPLE_TORTOISE}")
    voices_tortoise = [x for x in voices_tortoise if x.endswith(".wav")]
    if not voices_tortoise:
        raise AssertionError(f"Tortoise TTS selected but no voice sample is found in tortoise_audios/{VOICE_SAMPLE_TORTOISE}")

#Save model chosen in pygmalion config
with open("pygmalion/pygmalion_config.yml", "r") as f:
    config_pyg = yaml.safe_load(f)
config_pyg["model_name"] = "chatbot_models/" + CHAT_MODEL
with open("pygmalion/pygmalion_config.yml", "w") as f:
    yaml.dump(config_pyg, f)

#Save config to a json file
CONFIG = {
    "GAME_PATH": GAME_PATH,
    "USE_TTS": USE_TTS,
    "USE_CHARACTER_AI": USE_CHARACTER_AI,
    "DEBUG_MODE": DEBUG_MODE,
    "CONTINUE_FROM_LAST": CONTINUE_FROM_LAST,
    "USERNAME": USERNAME,
    "PASSWORD": PASSWORD,
    "CHOOSE_CHARACTER": CHOOSE_CHARACTER,
    "USE_CAMERA": USE_CAMERA,
    "TIME_INTERVALL": TIME_INTERVALL,
    "USE_LOCAL_CHATBOT": USE_LOCAL_CHATBOT,
    "LAUNCH_YOURSELF": LAUNCH_YOURSELF,
    "USE_ACTIONS": USE_ACTIONS,
    "TTS_MODEL": TTS_MODEL,
    "CHAT_MODEL": CHAT_MODEL,
    "USE_SPEECH_RECOGNITION": USE_SPEECH_RECOGNITION,
    "VOICE_SAMPLE_TORTOISE": VOICE_SAMPLE_TORTOISE,
    "VOICE_SAMPLE_COQUI": VOICE_SAMPLE_COQUI,
    "CHARACTER_JSON": CHARACTER_JSON
}

with open("config.json", "w") as f:
    json.dump(CONFIG, f)
