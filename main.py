from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
import os
import subprocess
from playwright.sync_api import sync_playwright
import sys
import tkinter as tk
import tkinter.font as tkfont
import time
#TTS add
import simpleaudio as sa

from tts_api import TTS

import speech_recognition as sr
import whisper
import torch
import numpy as np

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

# tk.Label(root, text="Username").grid(row=0, column=0)
# tk.Label(root, text="Password").grid(row=1, column=0)
tk.Label(root, text="Choose Character").grid(row=3, column=0)
tk.Label(root, text="Use Character AI").grid(row=5, column=0)
tk.Label(root, text="Use TTS").grid(row=6, column=0)
tk.Label(root, text="Use Debug Mode").grid(row=7, column=0)
tk.Label(root, text="Continue from last chat").grid(row=8, column=0)

font = tkfont.Font(family="Helvetica", size=12, weight="bold")
#set font to keep config
tk.Label(root, text="Use Saved Config", font=font).grid(row=9, column=0)

# tk.Entry(root, textvariable=username).grid(row=0, column=1)
# tk.Entry(root, textvariable=password, show='*').grid(row=1, column=1)
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

# characters_pages = {
#     "0": '[href="/chat?char=e9UVQuLURpLyCdhi8OjSKSLwKIiE0U-nEqXDeAjk538"]',
#     "1": '[href="/chat?char=EdSSlsl49k3wnwvMvK4eCh4yOFBaGTMJ7Q9CxtG2DiU"]'
# }

characters_pages = {
    "0": 'https://beta.character.ai/chat?char=e9UVQuLURpLyCdhi8OjSKSLwKIiE0U-nEqXDeAjk538',
    "1": 'https://beta.character.ai/chat?char=EdSSlsl49k3wnwvMvK4eCh4yOFBaGTMJ7Q9CxtG2DiU'
}

USE_TTS = int(USE_TTS)
USE_CHARACTER_AI = int(USE_CHARACTER_AI)
DEBUG_MODE = int(DEBUG_MODE)
CONTINUE_FROM_LAST = int(CONTINUE_FROM_LAST)

#Save config to a json file
config = {
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
    json.dump(config, f)

#Convert GAME_PATH to Linux format
GAME_PATH = GAME_PATH.replace("\\", "/")
# Global variables 
clients = {}
addresses = {}
HOST = '127.0.0.1'
PORT = 12346
BUFSIZE = 1024
ADDRESS = (HOST, PORT)
SERVER = socket(AF_INET, SOCK_STREAM)
SERVER.bind(ADDRESS)
queued = False
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

class my_TTS(TTS):
    def __init__(self, *args, **kwargs):
        super(my_TTS, self).__init__(*args, **kwargs)
    
    def tts(self, text: str, speaker: str = None, language: str = None,speaker_wav: str = None, reference_wav: str = None, style_wav: str = None, style_text: str = None, reference_speaker_name: str = None):
        """Synthesize text to speech."""

        wav = self.synthesizer.tts(
            text=text,
            speaker_name=speaker,
            language_name=language,
            speaker_wav=speaker_wav,
            reference_wav=reference_wav,
            style_wav=style_wav,
            style_text=style_text,
            reference_speaker_name=reference_speaker_name,
        )
        return wav

    def tts_to_file(self, text: str, speaker: str = None, language: str = None, file_path: str = "output.wav", speaker_wav: str = None, reference_wav: str = None, style_wav: str = None, style_text: str = None, reference_speaker_name: str = None):
        wav = self.tts(text=text, speaker=speaker, language=language,speaker_wav=speaker_wav, reference_wav=reference_wav, style_wav=style_wav, style_text=style_text, reference_speaker_name=reference_speaker_name)
        self.synthesizer.save_wav(wav=wav, path=file_path)

model = my_TTS(model_name="tts_models/multilingual/multi-dataset/your_tts")

####Load the speech recognizer#####
english = True
def init_stt(model="base", english=True,energy=300, pause=0.8, dynamic_energy=False):
    if model != "large" and english:
        model = model + ".en"
    audio_model = whisper.load_model(model)    
    
    #load the speech recognizer and set the initial energy threshold and pause threshold
    r = sr.Recognizer()
    r.energy_threshold = energy
    r.pause_threshold = pause
    r.dynamic_energy_threshold = dynamic_energy

    return r,audio_model

r,audio_model = init_stt()

def listen():
	""" Wait for incoming connections """
	print("Waiting for connection...")
	while True:
		client, client_address = SERVER.accept()
		print("%s:%s has connected." % client_address)
		addresses[client] = client_address
		Thread(target = call, args = (client,)).start()

def first_start(context):
    page = context.new_page()
    page.goto("https://character-ai.us.auth0.com/u/login?state=hKFo2SAxWUlJZGZBR1dSdXo1M2VfQm9qT21KeGJJV2oxcVAwR6Fur3VuaXZlcnNhbC1sb2dpbqN0aWTZIEVwaVNsaGh3YU5MSzJiYXo5ZDg2c09GR05VaGQza3Zvo2NpZNkgZHlEM2dFMjgxTXFnSVNHN0Z1SVhZaEwyV0VrbnFaenY")
    queue_and_things(page)
    page.wait_for_selector('[id="#AcceptButton"]',timeout=5000000)
    page.click('[id="#AcceptButton"]')
    page.click('[class="btn btn-primary btn-sm"]',timeout=5000)
    page.click('[class=" btn border"]',timeout=5000)
    page.fill("input#username",USERNAME,timeout=5000)
    page.fill("input#password",PASSWORD,timeout=5000)
    page.click("button[type=submit]")
    page.wait_for_load_state("networkidle")
    if not page.is_visible('[class="nav-icon-text-desktop text-wrap"]'):
        print("Something is wrong, captcha or wrong ids, try again with debug mode")
    page.wait_for_selector('[class="nav-icon-text-desktop text-wrap"]',timeout=50000)
    page.wait_for_load_state("networkidle")
    context.storage_state(path="storage.json")
    return page

def queue_and_things(page,queue_already_done=False):
    global queued
    if page.is_visible('[class="waitingrooms-text"]') and not queue_already_done:
        print("In queue")
        queued = True
        sendMessage("in_queue/g".encode("utf-8"))
    elif not queue_already_done:
        print("Not in queue")
        sendMessage("not_in_queue".encode("utf-8"))
        
def launch(context,pw,browser):
    global queued
    queue_already_done = False
    char_page = characters_pages[CHOOSE_CHARACTER]
    if not os.path.exists("storage.json"):
        page = first_start(context)
        queue_already_done = True
    else:
        context = browser.new_context(storage_state="storage.json")
        page = context.new_page()
    page.goto(char_page)
    queue_and_things(page,queue_already_done)
    if page.is_visible('[id="#AcceptButton"]'):
        page.click('[id="#AcceptButton"]',timeout=5000)
    page.wait_for_selector('[class="col-auto px-2 dropdown"]',timeout=5000000)
    context.storage_state(path="storage.json")
    if not CONTINUE_FROM_LAST:
        page.wait_for_timeout(500)
        page.click('[class="col-auto px-2 dropdown"]',timeout=5000)
        page.click('text=Save and Start New Chat',timeout=5000)
    return page

def call(client):
    thread = Thread(target=listenToClient, args=(client,), daemon=True)
    thread.start()

#Launch the game
subprocess.Popen(GAME_PATH+'/DDLC.exe')

def post_message(page, message):
    if message == "QUIT":
        page.fill("textarea","I'll be right back")
    else:
        page.fill("textarea",message)
    while True:
        try:
            page.click('[class="btn py-0"]')
            break
        except:
            pass
    
def listenToClient(client):
    """ Get client username """
    name = "User"
    clients[client] = name
    launched = False
    while True:
        received_msg = client.recv(BUFSIZE).decode("utf-8") #Message indicating the mode used (chatbot,camera_int or camera)
        received_msg = received_msg.split("/m")
        rest_msg = received_msg[1]
        received_msg = received_msg[0]
        if received_msg == "chatbot":
            if '/g' in rest_msg:
                received_msg , step = rest_msg.split("/g")
            else:
                received_msg = client.recv(BUFSIZE).decode("utf-8") #Message containing the user input
                received_msg , step = received_msg.split("/g")
            step = int(step)

            #Speech to text
            if received_msg == "begin_record":

                with sr.Microphone(sample_rate=16000) as source:
                    sendMessage("yes".encode("utf-8"))
                    #get and save audio to wav file
                    audio = r.listen(source)
                    torch_audio = torch.from_numpy(np.frombuffer(audio.get_raw_data(), np.int16).flatten().astype(np.float32) / 32768.0)
                    audio_data = torch_audio
                    if english:
                        result = audio_model.transcribe(audio_data,language='english')
                    else:
                        result = audio_model.transcribe(audio_data)
                    received_msg = result['text']

            print("User: "+received_msg)

            if USE_CHARACTER_AI:
                if not launched:
                    try:
                        pw = sync_playwright().start()
                        if DEBUG_MODE:
                            browser =  pw.firefox.launch(headless=False)
                            context = browser.new_context()
                        else:
                            browser =  pw.firefox.launch()
                            context = browser.new_context()
                        page = launch(context,pw,browser)
                        launched = True
                        sendMessage("server_ok".encode("utf-8"))
                        ok_ready = client.recv(BUFSIZE).decode("utf-8")
                    except:
                        sendMessage("server_error".encode("utf-8"))
                        pw.stop()
                        continue
                
                if os.path.exists(GAME_PATH+'/game/Submods/AI_submod/audio/out.ogg'):
                    os.remove(GAME_PATH+'/game/Submods/AI_submod/audio/out.ogg')
                time.sleep(2)
                
                post_message(page,received_msg)

                while True:
                    if not page.is_disabled('[class="btn py-0"]'):
                        query =  page.query_selector_all(('[class="markdown-wrapper markdown-wrapper-last-msg swiper-no-swiping"]'))
                        if len(query) > 0:
                            msg =  query[0].inner_html()
                        else:
                            post_message(page,received_msg)
                            continue
                        
                        msg = msg.replace("<em>","{i}")
                        msg = msg.replace("</em>","{/i}")
                        msg = msg.replace("<div>","")
                        msg = msg.replace("</div>","")
                        msg = msg.replace("<p>","\n")
                        msg = msg.replace("</p>","")
                        msg = msg.replace("<del>","")
                        msg = msg.replace("</del>","")
                        msg = msg.replace("<br>","")
                        msg = msg.replace("<br/>","")
                        msg = msg.replace('<div style="overflow-wrap: break-word;">',"")
                        msg = msg.replace("&lt;","<")
                        msg = msg.replace("&gt;",">")

                        if received_msg != "QUIT":       

                            #TTS addition
                            if USE_TTS:
                                print("Using TTS")
                                msg_audio = msg.replace("\n"," ")
                                msg_audio = msg_audio.replace("{i}","")
                                msg_audio = msg_audio.replace("{/i}",".")
                                msg_audio = msg_audio.replace("~","!")
                                #subprocess.check_call(['tts', '--text', msg_audio, '--model_name', 'tts_models/multilingual/multi-dataset/your_tts', '--speaker_wav', 'audios/talk_13.wav', '--language_idx', 'en', '--out_path', GAME_PATH + '/game/Submods/AI_submod/audio/out.wav'])
                                model.tts_to_file(text=msg_audio,speaker_wav='audios/talk_13.wav', language='en',file_path=GAME_PATH + '/game/Submods/AI_submod/audio/out.wav')
                                def playVoice():
                                    f = open(GAME_PATH+'/game/Submods/AI_submod/audio/out.wav', 'rb')
                                    audio = f.read()
                                    f.close()
                                    play_obj = sa.play_buffer(audio, 1, 2, 16000)
                                    play_obj.wait_done()
                                    
                                    os.remove(GAME_PATH+'/game/Submods/AI_submod/audio/out.wav')
                                thread_voice = Thread(target=playVoice, args=(), daemon=True)
                                thread_voice.start()    
                       
                            emotion = "".encode("utf-8")
                            msg = msg.encode("utf-8")   
                            msg_to_send = msg + b"/g" + emotion
                            print("Sent: "+ msg_to_send.decode("utf-8"))
                            sendMessage(msg_to_send)
                        break
                    
        else:
            counter = received_msg[6:]
            counter = int(counter)
            msg = "no_data"
            msg = msg.encode()
            sendMessage(msg)


def sendMessage(msg, name=""):
    """ send message to all users present in 
    the chat room"""
    for client in clients:
        client.send(bytes(name, "utf8") + msg)

if __name__ == "__main__":
    SERVER.listen(5)
    ACCEPT_THREAD = Thread(target=listen)
    ACCEPT_THREAD.start()
    ACCEPT_THREAD.join()
    SERVER.close()