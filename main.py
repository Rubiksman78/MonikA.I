from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
import os,sys
import subprocess
from playwright.sync_api import sync_playwright
import time
import simpleaudio as sa

from tts_api import my_TTS

import speech_recognition as sr
import whisper
import torch
import numpy as np

import IPython.display as ipd
from login_screen import CONFIG

GAME_PATH = CONFIG["GAME_PATH"]
USE_TTS = CONFIG["USE_TTS"]
USE_CHARACTER_AI = CONFIG["USE_CHARACTER_AI"]
DEBUG_MODE = CONFIG["DEBUG_MODE"]
CONTINUE_FROM_LAST = CONFIG["CONTINUE_FROM_LAST"]
USERNAME = CONFIG["USERNAME"]
PASSWORD = CONFIG["PASSWORD"]
CHOOSE_CHARACTER = CONFIG["CHOOSE_CHARACTER"]

class HiddenPrints:
    def __enter__(self):
        self._original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout.close()
        sys.stdout = self._original_stdout


characters_pages = {
    "0": 'https://beta.character.ai/chat?char=e9UVQuLURpLyCdhi8OjSKSLwKIiE0U-nEqXDeAjk538',
    "1": 'https://beta.character.ai/chat?char=EdSSlsl49k3wnwvMvK4eCh4yOFBaGTMJ7Q9CxtG2DiU'
}

GAME_PATH = GAME_PATH.replace("\\", "/")
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

#Launch the game
subprocess.Popen(GAME_PATH+'/DDLC.exe')

#########Load the TTS model##########
with HiddenPrints():
    if USE_TTS:
        model = my_TTS(model_name="tts_models/multilingual/multi-dataset/your_tts")
#####################################

####Load the speech recognizer#####
english = True
def init_stt(model="base", english=True,energy=300, pause=0.8, dynamic_energy=False):
    if model != "large" and english:
        model = model + ".en"
    audio_model = whisper.load_model(model)    
    r = sr.Recognizer()
    r.energy_threshold = energy
    r.pause_threshold = pause
    r.dynamic_energy_threshold = dynamic_energy
    return r,audio_model

r,audio_model = init_stt()
#####################################


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
                                if step > 0:
                                    play_obj.stop()
                                msg_audio = msg.replace("\n"," ")
                                msg_audio = msg_audio.replace("{i}","")
                                msg_audio = msg_audio.replace("{/i}",".")
                                msg_audio = msg_audio.replace("~","!")
                                with HiddenPrints():
                                    audio = model.tts(text=msg_audio,speaker_wav='audios/talk_13.wav', language='en')
                                audio = ipd.Audio(audio, rate=16000)
                                play_obj = sa.play_buffer(audio.data, 1, 2, 16000)                   
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