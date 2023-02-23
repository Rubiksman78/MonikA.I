import os,sys
import tkinter as tk
import tkinter.font as tkfont
import json
import yaml
# Configuration
args = sys.argv[1:]

save_ids = os.path.exists("save_text.txt")

root = tk.Tk()
root.title("MonikA.I. Submod")
root.geometry("600x400")
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
    global KEEP_CONFIG
    global USE_CAMERA
    global TIME_INTERVALL
    global USE_PYG
    global PYG_MODEL
    global LAUNCH_YOURSELF
    global USE_ACTIONS
    USERNAME = username.get()
    PASSWORD = password.get()
    CHOOSE_CHARACTER = choose_character.get()
    USE_CHARACTER_AI = use_character_ai.get()
    USE_TTS = use_tts.get()
    GAME_PATH = game_path.get()
    LAUNCH_YOURSELF = launch_yourself.get()
    DEBUG_MODE = debug_mode.get()
    CONTINUE_FROM_LAST = continue_from_last.get()
    KEEP_CONFIG = keep_config.get()
    USE_CAMERA = use_camera.get()
    TIME_INTERVALL = time_intervall.get()
    USE_PYG = use_pyg.get()
    PYG_MODEL = pyg_model.get()
    USE_ACTIONS = use_actions.get()
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
keep_config = tk.StringVar()
use_camera = tk.StringVar()
time_intervall = tk.StringVar()
use_pyg = tk.StringVar()
pyg_model = tk.StringVar()
use_actions = tk.StringVar()

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
tk.Label(other_frame, text="Use Pygmalion Bot",bg='#333333',fg='white').grid(row=4, column=0)
tk.Label(other_frame, text="Pygmalion Model",bg='#333333',fg='white').grid(row=4, column=3)
tk.Label(other_frame, text="Use Camera",bg='#333333',fg='white').grid(row=5, column=0)
tk.Label(other_frame, text="Time Intervall For Camera",bg='#333333',fg='white').grid(row=5,column=3)

font = tkfont.Font(family="Helvetica", size=12, weight="bold")
tk.Label(other_frame, text="Use Saved Config", font=font,bg='#333333',fg='white').grid(row=10, column=0)

#Textual Inputs
tk.Entry(char_ai_frame, textvariable=username,width=25).grid(row=0, column=1)
tk.Entry(char_ai_frame, textvariable=password,show='*',width=25).grid(row=1, column=1)
tk.Entry(other_frame, textvariable=game_path,width=25).grid(row=1, column=1)
tk.Entry(other_frame, textvariable=time_intervall,width=10).grid(row=5, column=4)

#Scrollable Inputs
char_menu = tk.OptionMenu(char_ai_frame, choose_character, "0", "1")
char_menu.config( bg='white',fg='black')
char_menu.grid(row=2, column=4)

pyg_menu = tk.OptionMenu(other_frame, pyg_model, "350m","1.3b","2.7b","6b")
pyg_menu.config( bg='white',fg='black')
pyg_menu.grid(row=4, column=4)

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

tk.Radiobutton(other_frame, text="Yes", variable=use_pyg, value=True,bg='#333333',activeforeground='white',fg='white',activebackground="#333333",selectcolor='#333333').grid(row=4, column=1)
tk.Radiobutton(other_frame, text="No", variable=use_pyg, value=False,bg='#333333',activeforeground='white',fg='white',activebackground="#333333",selectcolor='#333333').grid(row=4, column=2)

tk.Radiobutton(other_frame, text="Yes", variable=use_camera, value=True,bg='#333333',activeforeground='white',fg='white',activebackground="#333333",selectcolor='#333333').grid(row=5, column=1)
tk.Radiobutton(other_frame, text="No", variable=use_camera, value=False,bg='#333333',activeforeground='white',fg='white',activebackground="#333333",selectcolor='#333333').grid(row=5, column=2)

tk.Radiobutton(other_frame, text="Yes", variable=keep_config, value=True,bg='#333333',activeforeground='white',fg='white',activebackground="#333333",selectcolor='#333333').grid(row=10, column=1)
tk.Radiobutton(other_frame, text="No", variable=keep_config, value=False,bg='#333333',activeforeground='white',fg='white',activebackground="#333333",selectcolor='#333333').grid(row=10, column=2)

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

#Set default values
launch_yourself.set(0)
time_intervall.set("10")
use_character_ai.set(0)
use_tts.set(0)
debug_mode.set(0)
continue_from_last.set(0)
choose_character.set("0")
use_camera.set(0)
keep_config.set(0)
use_pyg.set(0)
pyg_model.set("2.7b")
use_actions.set(0)

root.mainloop()

#Save config for use saved config option
KEEP_CONFIG = int(KEEP_CONFIG)
if KEEP_CONFIG:
    if not os.path.exists("config.json"):
        raise Exception("config.json not found")
    with open("config.json", "r") as f:
        config = json.load(f)
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
        USE_PYG = config["USE_PYG"]
        LAUNCH_YOURSELF = config["LAUNCH_YOURSELF"]
        USE_ACTIONS = config["USE_ACTIONS"]

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
USE_PYG = int(USE_PYG)
LAUNCH_YOURSELF = int(LAUNCH_YOURSELF)
USE_ACTIONS = int(USE_ACTIONS)

#Save model chosen in pygmalion config
with open("pygmalion/pygmalion_config.yml", "r") as f:
    config_pyg = yaml.safe_load(f)
config_pyg["model_name"] = "PygmalionAI/pygmalion-" + PYG_MODEL
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
    "USE_PYG": USE_PYG,
    "LAUNCH_YOURSELF": LAUNCH_YOURSELF,
    "USE_ACTIONS": USE_ACTIONS
}

with open("config.json", "w") as f:
    json.dump(CONFIG, f)