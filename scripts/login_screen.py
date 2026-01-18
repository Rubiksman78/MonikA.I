import os
import sys
import tkinter as tk
import json

# Configuration
args = sys.argv[1:]

root = tk.Tk()
root.title("MonikA.I. Submod")
root.geometry("900x500")

#colors
doki_white = "#F9F3F9"
doki_dark_pink = '#F9B7DB'
doki_light_pink = '#F4DCEA'
doki_purple = '#AB6999'
menu_background_pink = '#EC9DC8'

bg_image = tk.PhotoImage(file=r"images\login\login_background.png")
background_label = tk.Label(root, image=bg_image)
background_label.place(x=0, y=0, relwidth=1, relheight=1)

def load_from_json(variable, entry):
    try:
        with open("config.json", "r") as file:
            config = json.load(file)
        variable_to_insert = config[variable]
        entry.delete(0, tk.END)
        entry.insert(0, variable_to_insert)
    except (FileNotFoundError, KeyError):
        pass

def get_input():
    global GAME_PATH, USE_TTS, LAUNCH_YOURSELF, OLLAMA_MODEL
    global USE_ACTIONS, USE_EMOTIONS, TTS_MODEL, USE_SPEECH_RECOGNITION
    global VOICE_SAMPLE_TORTOISE, VOICE_SAMPLE_COQUI
    
    USE_TTS = use_tts.get()
    GAME_PATH = game_path.get()
    LAUNCH_YOURSELF = launch_yourself.get()
    OLLAMA_MODEL = ollama_model.get()
    USE_ACTIONS = use_actions.get()
    USE_EMOTIONS = use_emotions.get() # Capture the new value
    TTS_MODEL = tts_model.get()
    USE_SPEECH_RECOGNITION = use_speech_recognition.get()
    VOICE_SAMPLE_TORTOISE = voice_sample_tortoise.get()
    VOICE_SAMPLE_COQUI = voice_sample_coqui.get()
    root.destroy()

other_frame = tk.LabelFrame(
    root,
    bg=menu_background_pink,
    text="General Settings",
    fg='white',
    font=("Helvetica", 16, "bold"),
    bd=5
)
other_frame.place(anchor="c", relx=.5, rely=0.4)

bold_font = ('helvetic', 10, 'bold')
aspect_params = {
    "bg": menu_background_pink,
    "activeforeground": 'white',
    "fg": 'white',
    "activebackground": doki_light_pink,
    "selectcolor": doki_purple,
    "font": bold_font
}

# Variables for other settings
use_tts = tk.StringVar()
game_path = tk.StringVar()
launch_yourself = tk.StringVar()
ollama_model = tk.StringVar()
use_actions = tk.StringVar()
use_emotions = tk.StringVar() # Variable for the new option
tts_model = tk.StringVar()
use_speech_recognition = tk.StringVar()
voice_sample_tortoise = tk.StringVar()  
voice_sample_coqui = tk.StringVar()

# General Settings Labels and Inputs
tk.Label(other_frame, text="Game Path", bg=menu_background_pink, fg='white', font=bold_font).grid(row=1, column=0)
tk.Label(other_frame, text="Ollama Model", bg=menu_background_pink, fg='white', font=bold_font).grid(row=2, column=0)
tk.Label(other_frame, text="Launch Yourself", bg=menu_background_pink, fg='white', font=bold_font).grid(row=1, column=3)
tk.Label(other_frame, text="Use Actions", bg=menu_background_pink, fg='white', font=bold_font).grid(row=3, column=0)
tk.Label(other_frame, text="Use Emotions", bg=menu_background_pink, fg='white', font=bold_font).grid(row=4, column=0) # New Label
tk.Label(other_frame, text="Use TTS", bg=menu_background_pink, fg='white', font=bold_font).grid(row=5, column=0)
tk.Label(other_frame, text="TTS model", bg=menu_background_pink, fg='white', font=bold_font).grid(row=5, column=3)
tk.Label(other_frame, text="Use Speech Recognition", bg=menu_background_pink, fg='white', font=bold_font).grid(row=6, column=0)
tk.Label(other_frame, text="Tortoise Voice Sample", bg=menu_background_pink, fg='white', font=bold_font).grid(row=7, column=0)
tk.Label(other_frame, text="Voice Sample", bg=menu_background_pink, fg='white', font=bold_font).grid(row=7, column=3)

tk.Radiobutton(other_frame, text="Yes", variable=launch_yourself, value=True, **aspect_params).grid(row=1, column=4)
tk.Radiobutton(other_frame, text="No", variable=launch_yourself, value=False, **aspect_params).grid(row=1, column=5)

tk.Radiobutton(other_frame, text="Yes", variable=use_actions, value=True, **aspect_params).grid(row=3, column=1)
tk.Radiobutton(other_frame, text="No", variable=use_actions, value=False, **aspect_params).grid(row=3, column=2)

# New Radio Buttons for Emotions
tk.Radiobutton(other_frame, text="Yes", variable=use_emotions, value=True, **aspect_params).grid(row=4, column=1)
tk.Radiobutton(other_frame, text="No", variable=use_emotions, value=False, **aspect_params).grid(row=4, column=2)

tk.Radiobutton(other_frame, text="Yes", variable=use_tts, value=True, **aspect_params).grid(row=5, column=1)
tk.Radiobutton(other_frame, text="No", variable=use_tts, value=False, **aspect_params).grid(row=5, column=2)

tk.Radiobutton(other_frame, text="Yes", variable=use_speech_recognition, value=True, **aspect_params).grid(row=6, column=1)
tk.Radiobutton(other_frame, text="No", variable=use_speech_recognition, value=False, **aspect_params).grid(row=6, column=2)

# Textual Inputs
game_path_entry = tk.Entry(other_frame, textvariable=game_path, width=25, bg=doki_white, fg='black')
game_path_entry.grid(row=1, column=1)

load_from_json("GAME_PATH", game_path_entry)

ollama_model_entry = tk.Entry(other_frame, textvariable=ollama_model, width=25, bg=doki_white, fg='black')
ollama_model_entry.grid(row=2, column=1)

load_from_json("OLLAMA_MODEL", ollama_model_entry)

tts_menu = tk.OptionMenu(other_frame, tts_model, "Your TTS", "XTTS", "Tortoise TTS")
tts_menu.config(bg=doki_white, fg='black')
tts_menu.grid(row=5, column=4) # Adjusted row

# Voice sample selections
all_voices_tortoise = os.listdir("tortoise_audios")
all_voices_tortoise = [x for x in all_voices_tortoise if not x.endswith(".txt")]
voice_menu = tk.OptionMenu(other_frame, voice_sample_tortoise, *all_voices_tortoise)
voice_menu.config(bg=doki_white, fg='black')
voice_menu.grid(row=8, column=1) # Adjusted row

all_voices_coquiai = os.listdir("coquiai_audios")
all_voices_coquiai = [x for x in all_voices_coquiai if x.endswith(".wav")]
if len(all_voices_coquiai) == 0:
    all_voices_coquiai = ["No voices found"]
voice_menu = tk.OptionMenu(other_frame, voice_sample_coqui, *all_voices_coquiai)
voice_menu.config(bg=doki_white, fg='black')
voice_menu.grid(row=8, column=4) # Adjusted row

aspect_params = {
    "bg": menu_background_pink,
    "activeforeground": 'white',
    "fg": 'white',
    "activebackground": doki_light_pink,
    "selectcolor": doki_purple,
    "font": bold_font
}


button_background = tk.PhotoImage(file=r"images\login\button_background.png")
button = tk.Button(root, image=button_background, height=40, width=214, command=get_input, bd=0)
button.place(relx=0.5, rely=0.9, anchor=tk.CENTER)

if not os.path.exists("config.json"):
    # Set default values
    launch_yourself.set(False)
    use_tts.set(False)
    use_actions.set(False)
    use_emotions.set(False) # Default for new option
    tts_model.set("Your TTS")
    use_speech_recognition.set(False)
    voice_sample_tortoise.set("Choose a Tortoise voice sample")
    voice_sample_coqui.set("Choose a voice sample")
else:
    with open("config.json", "r") as f:
        config = json.load(f)
    # Load existing settings
    GAME_PATH = config.get("GAME_PATH", "")
    OLLAMA_MODEL = config.get("OLLAMA_MODEL", "")
    USE_TTS = config.get("USE_TTS", False)
    LAUNCH_YOURSELF = config.get("LAUNCH_YOURSELF", False)
    USE_ACTIONS = config.get("USE_ACTIONS", False)
    USE_EMOTIONS = config.get("USE_EMOTIONS", False) # Load new option
    TTS_MODEL = config.get("TTS_MODEL", "Your TTS")
    USE_SPEECH_RECOGNITION = config.get("USE_SPEECH_RECOGNITION", False)
    VOICE_SAMPLE_COQUI = config.get("VOICE_SAMPLE_COQUI", "Choose a voice sample")
    VOICE_SAMPLE_TORTOISE = config.get("VOICE_SAMPLE_TORTOISE", "Choose a Tortoise voice sample")
    # Set saved values
    launch_yourself.set(LAUNCH_YOURSELF)
    use_tts.set(USE_TTS)
    use_actions.set(USE_ACTIONS)
    use_emotions.set(USE_EMOTIONS) # Set GUI for new option
    tts_model.set(TTS_MODEL)
    use_speech_recognition.set(USE_SPEECH_RECOGNITION)
    voice_sample_tortoise.set(VOICE_SAMPLE_TORTOISE)
    voice_sample_coqui.set(VOICE_SAMPLE_COQUI)

def on_closing():
    root.destroy()
    raise SystemExit

root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()

# Convert string from radio buttons to boolean-like integers
USE_TTS = int(eval(str(USE_TTS)))
LAUNCH_YOURSELF = int(eval(str(LAUNCH_YOURSELF)))
USE_ACTIONS = int(eval(str(USE_ACTIONS)))
USE_EMOTIONS = int(eval(str(USE_EMOTIONS))) # Convert new option
USE_SPEECH_RECOGNITION = int(eval(str(USE_SPEECH_RECOGNITION)))

CONFIG = {
    "GAME_PATH": GAME_PATH,
    "OLLAMA_MODEL": OLLAMA_MODEL,
    "USE_TTS": USE_TTS,
    "LAUNCH_YOURSELF": LAUNCH_YOURSELF,
    "USE_ACTIONS": USE_ACTIONS,
    "USE_EMOTIONS": USE_EMOTIONS, # Add to config dict
    "TTS_MODEL": TTS_MODEL,
    "USE_SPEECH_RECOGNITION": USE_SPEECH_RECOGNITION,
    "VOICE_SAMPLE_TORTOISE": VOICE_SAMPLE_TORTOISE,
    "VOICE_SAMPLE_COQUI": VOICE_SAMPLE_COQUI,
}

with open("config.json", "w") as f:
    json.dump(CONFIG, f)
