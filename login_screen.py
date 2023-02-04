import os,sys
import tkinter as tk
import tkinter.font as tkfont
import json

# Configuration
args = sys.argv[1:]

save_ids = os.path.exists("game_path.txt")

root = tk.Tk()
root.title("MonikA.I. Submod")
root.geometry("400x400")
root.resizable(False, False)

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
    USERNAME = username.get()
    PASSWORD = password.get()
    CHOOSE_CHARACTER = choose_character.get()
    USE_CHARACTER_AI = use_character_ai.get()
    USE_TTS = use_tts.get()
    GAME_PATH = game_path.get()
    DEBUG_MODE = debug_mode.get()
    CONTINUE_FROM_LAST = continue_from_last.get()
    KEEP_CONFIG = keep_config.get()
    root.destroy()

username = tk.StringVar()
password = tk.StringVar()
choose_character = tk.StringVar()
use_character_ai = tk.StringVar()
use_tts = tk.StringVar()
game_path = tk.StringVar()
debug_mode = tk.StringVar()
continue_from_last = tk.StringVar()
keep_config = tk.StringVar()


tk.Label(root, text="Choose Character").grid(row=3, column=0)
tk.Label(root, text="Use Character AI").grid(row=5, column=0)
tk.Label(root, text="Use TTS").grid(row=6, column=0)
tk.Label(root, text="Use Debug Mode").grid(row=7, column=0)
tk.Label(root, text="Continue from last chat").grid(row=8, column=0)

font = tkfont.Font(family="Helvetica", size=12, weight="bold")
#set font to keep config
tk.Label(root, text="Use Saved Config", font=font).grid(row=9, column=0)

tk.Entry(root, textvariable=choose_character).grid(row=3, column=1)

tk.Radiobutton(root, text="Yes", variable=use_character_ai, value=True).grid(row=5, column=1)
tk.Radiobutton(root, text="No", variable=use_character_ai, value=False).grid(row=5, column=2)

tk.Radiobutton(root, text="Yes", variable=use_tts, value=True).grid(row=6, column=1)
tk.Radiobutton(root, text="No", variable=use_tts, value=False).grid(row=6, column=2)

tk.Radiobutton(root, text="Yes", variable=debug_mode, value=True).grid(row=7, column=1)
tk.Radiobutton(root, text="No", variable=debug_mode, value=False).grid(row=7, column=2)

tk.Radiobutton(root, text="Yes", variable=continue_from_last, value=True).grid(row=8, column=1)
tk.Radiobutton(root, text="No", variable=continue_from_last, value=False).grid(row=8, column=2)

tk.Radiobutton(root, text="Yes", variable=keep_config, value=True).grid(row=9, column=1)
tk.Radiobutton(root, text="No", variable=keep_config, value=False).grid(row=9, column=2)

tk.Button(root, text="Submit", command=get_input).grid(row=10, column=0)

if save_ids:
    #Make button appear if the previous one was clicked
    def on_select(v):
        global GAME_PATH
        if v == True:            
            tk.Label(root, text="Change Game Path").grid(row=4, column=0)
            tk.Entry(root, textvariable=game_path).grid(row=4, column=3)

            tk.Label(root, text="Change email").grid(row=0, column=0)
            tk.Entry(root, textvariable=username).grid(row=0, column=3)

            tk.Label(root, text="Change password").grid(row=1, column=0)
            tk.Entry(root, textvariable=password,show='*').grid(row=1, column=3)
        else:
            with open("game_path.txt", "r") as f:
                string = f.read()
                GAME_PATH,USERNAME,PASSWORD = string.split(";")
            #Write GAME_PATH in the box
            tk.Label(root, text="Change Game Path").grid(row=4, column=0)
            tk.Entry(root, textvariable=game_path).grid(row=4, column=3)
            game_path.set(GAME_PATH)

            tk.Label(root, text="Change email").grid(row=0, column=0)
            tk.Entry(root, textvariable=username).grid(row=0, column=3)
            username.set(USERNAME)

            tk.Label(root, text="Change password").grid(row=1, column=0)
            tk.Entry(root, textvariable=password,show='*').grid(row=1, column=3)
            password.set(PASSWORD)

    tk.Label(root, text="Change Game Path").grid(row=4, column=0)
    change_game_path = tk.BooleanVar()

    yes_change = tk.Radiobutton(root, text="Yes", variable=change_game_path, value=True)
    yes_change.grid(row=4, column=1)
    yes_change.config(command=lambda: on_select(True))

    no_change = tk.Radiobutton(root, text="No", variable=change_game_path, value=False)
    no_change.grid(row=4, column=2)
    no_change.config(command=lambda: on_select(False))

    tk.Label(root, text="Change email").grid(row=0, column=0)
    change_email = tk.BooleanVar()

    yes_change = tk.Radiobutton(root, text="Yes", variable=change_email, value=True)
    yes_change.grid(row=0, column=1)
    yes_change.config(command=lambda: on_select(True))

    no_change = tk.Radiobutton(root, text="No", variable=change_email, value=False)
    no_change.grid(row=0, column=2)
    no_change.config(command=lambda: on_select(False))

    tk.Label(root, text="Change password").grid(row=1, column=0)
    change_password = tk.BooleanVar()

    yes_change = tk.Radiobutton(root, text="Yes", variable=change_password, value=True)
    yes_change.grid(row=1, column=1)
    yes_change.config(command=lambda: on_select(True))

    no_change = tk.Radiobutton(root, text="No", variable=change_password, value=False)
    no_change.grid(row=1, column=2)
    no_change.config(command=lambda: on_select(False))

else:
    game_path = tk.StringVar()
    tk.Label(root, text="Game Path").grid(row=4, column=0)
    tk.Entry(root, textvariable=game_path).grid(row=4, column=1)

    username = tk.StringVar()
    tk.Label(root, text="Email").grid(row=0, column=0)
    tk.Entry(root, textvariable=username).grid(row=0, column=1)

    password = tk.StringVar()
    tk.Label(root, text="Password").grid(row=1, column=0)
    tk.Entry(root, textvariable=password, show='*').grid(row=1, column=1)
    
root.mainloop()

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

#Write game_path to a file
if GAME_PATH != "" and USERNAME != "" and PASSWORD != "":
    with open("game_path.txt", "w") as f:
        f.write(GAME_PATH + ";" + USERNAME + ";" + PASSWORD)

USE_TTS = int(USE_TTS)
USE_CHARACTER_AI = int(USE_CHARACTER_AI)
DEBUG_MODE = int(DEBUG_MODE)
CONTINUE_FROM_LAST = int(CONTINUE_FROM_LAST)

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
}

with open("config.json", "w") as f:
    json.dump(CONFIG, f)