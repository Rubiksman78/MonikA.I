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
import re

import cv2
from torchvision import transforms
from facial_analysis import FacialImageProcessing
from PIL import Image

import yaml
import json
from pygmalion.model import build_model_and_tokenizer_for
from run_pygmalion import inference_fn
import gc 

GAME_PATH = CONFIG["GAME_PATH"]
USE_TTS = CONFIG["USE_TTS"]
USE_CHARACTER_AI = CONFIG["USE_CHARACTER_AI"]
DEBUG_MODE = CONFIG["DEBUG_MODE"]
CONTINUE_FROM_LAST = CONFIG["CONTINUE_FROM_LAST"]
USERNAME = CONFIG["USERNAME"]
PASSWORD = CONFIG["PASSWORD"]
CHOOSE_CHARACTER = CONFIG["CHOOSE_CHARACTER"]
USE_CAMERA = CONFIG["USE_CAMERA"]
TIME_INTERVALL = CONFIG["TIME_INTERVALL"]
USE_PYG = CONFIG["USE_PYG"]

######LOAD PYGMALION CONFIG######
if USE_PYG:
    with open("pygmalion/pygmalion_config.yml", "r") as f:
        PYG_CONFIG = yaml.safe_load(f)

    with open(f"pygmalion/{PYG_CONFIG['char_json']}", "r") as f:
        char_settings = json.load(f)
    f.close()

    model_name = PYG_CONFIG["model_name"]
    gc.collect()
    torch.cuda.empty_cache()
    pyg_model, tokenizer = build_model_and_tokenizer_for(model_name)

    generation_settings = {
        "max_new_tokens": PYG_CONFIG["max_new_tokens"],
        "temperature": PYG_CONFIG["temperature"],
        "repetition_penalty": PYG_CONFIG["repetition_penalty"],
        "top_p": PYG_CONFIG["top_p"],
        "top_k": PYG_CONFIG["top_k"],
        "do_sample": PYG_CONFIG["do_sample"],
        "typical_p":PYG_CONFIG["typical_p"],
    }

    context_size = PYG_CONFIG["context_size"]

    with open("chat_history.txt", "a") as chat_history:
        chat_history.write("Conversation started at: " + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + "\n")
#################################


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

emoji_pattern = re.compile("["
    u"\U0001F600-\U0001F64F"  # emoticons
    u"\U0001F300-\U0001F5FF"  # symbols & pictographs
    u"\U0001F680-\U0001F6FF"  # transport & map symbols
    u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
    u"\U00002500-\U00002BEF"  # chinese char
    u"\U00002702-\U000027B0"
    u"\U00002702-\U000027B0"
    u"\U000024C2-\U0001F251"
    u"\U0001f926-\U0001f937"
    u"\U00010000-\U0010ffff"
    u"\u2640-\u2642"
    u"\u2600-\u2B55"
    u"\u200d"
    u"\u23cf"
    u"\u23e9"
    u"\u231a"
    u"\ufe0f"  # dingbats
    u"\u3030"
    "]+", flags=re.UNICODE)

uni_chr_re = re.compile(r'\\u[0-9a-fA-F]{4}')

#Launch the game
#subprocess.Popen(GAME_PATH+'/DDLC.exe', shell=True)

#########Load the emotion model##########
if USE_CAMERA:
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    emotion_model = torch.load('models/enet_b2_7.pt').to(device)
    emotion_model.eval()
    cv2.ocl.setUseOpenCL(False)
    IMG_SIZE = 256
    imgProcessing=FacialImageProcessing(False)
    test_transforms = transforms.Compose(
        [
            transforms.Resize((IMG_SIZE,IMG_SIZE)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                        std=[0.229, 0.224, 0.225])
        ]
    )
    emotion_dict = {0: "Angry", 1: "Disgusted", 2: "Fearful", 3: "Happy", 4: "Neutral", 5: "Sad", 6: "Surprised"}
############################################

#########Load the TTS model##########
with HiddenPrints():
    if USE_TTS:
        tts_model = my_TTS(model_name="tts_models/multilingual/multi-dataset/your_tts")
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
    pyg_count = 0
    if os.path.exists("char_history.txt"):
        history = open("char_history.txt","r").read()
        #Remove lines with the pattern "Conversation started at: 2023-02-14 14:14:17"
        history = re.sub(r"Conversation started at: \d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}","",history)
    else:
        history = ""
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

            if USE_CHARACTER_AI and not USE_PYG:
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
                            if USE_TTS:
                                print("Using TTS")
                                if step > 0:
                                    play_obj.stop()
                                msg_audio = msg.replace("\n"," ")
                                msg_audio = msg_audio.replace("{i}","")
                                msg_audio = msg_audio.replace("{/i}",".")
                                msg_audio = msg_audio.replace("~","!")
                                msg_audio = emoji_pattern.sub(r'', msg_audio)
                                msg_audio = uni_chr_re.sub(r'', msg_audio)
                                print("Sent: "+ msg_audio)
                                with HiddenPrints():
                                    audio = tts_model.tts(text=msg_audio,speaker_wav='audios/talk_13.wav', language='en')
                                audio = ipd.Audio(audio, rate=16000)
                                play_obj = sa.play_buffer(audio.data, 1, 2, 16000)                   
                            emotion = "".encode("utf-8")
                            msg = msg.encode("utf-8")   
                            msg_to_send = msg + b"/g" + emotion
                            sendMessage(msg_to_send)
                        break

            if USE_PYG and not USE_CHARACTER_AI:
                if os.path.exists(GAME_PATH+'/game/Submods/AI_submod/audio/out.ogg'):
                    os.remove(GAME_PATH+'/game/Submods/AI_submod/audio/out.ogg')
                time.sleep(2)
               
                while True: 
                    if pyg_count == 0:
                        sendMessage("not_in_queue".encode("utf-8"))
                        sendMessage("server_ok".encode("utf-8"))
                        ok_ready = client.recv(BUFSIZE).decode("utf-8")
                        bot_message = inference_fn(pyg_model,tokenizer,history, "",generation_settings,char_settings,history_length=context_size,count=pyg_count)
                    else:
                        bot_message = inference_fn(pyg_model,tokenizer,history, received_msg,generation_settings,char_settings,history_length=context_size,count=pyg_count)
                        history = history + "\n" + f"You: {received_msg}" + "\n" + f"{bot_message}"
                    if received_msg != "QUIT":       
                        if USE_TTS:
                            print("Using TTS")
                            if step > 0:
                                play_obj.stop()
                            msg_audio = bot_message.replace("\n"," ")
                            msg_audio = msg_audio.replace("{i}","")
                            msg_audio = msg_audio.replace("{/i}",".")
                            msg_audio = msg_audio.replace("~","!")
                            msg_audio = emoji_pattern.sub(r'', msg_audio)
                            msg_audio = uni_chr_re.sub(r'', msg_audio)
                            with HiddenPrints():
                                audio = tts_model.tts(text=msg_audio,speaker_wav='audios/talk_13.wav', language='en')
                            audio = ipd.Audio(audio, rate=16000)
                            play_obj = sa.play_buffer(audio.data, 1, 2, 16000)     
                        print("Sent: "+ bot_message)              
                        emotion = "".encode("utf-8")
                        msg = bot_message.encode("utf-8")   
                        msg_to_send = msg + b"/g" + emotion
                        sendMessage(msg_to_send)
                        pyg_count += 1
                        if pyg_count > 0:
                            with open("chat_history.txt", "a") as f:
                                f.write(f"You: {received_msg}" + "\n" + f'{char_settings["char_name"]}: {bot_message}' + "\n")
                    break
                    

        elif received_msg == "camera_int":
            if USE_CAMERA:
                # start the webcam feed
                cap = cv2.VideoCapture(0)
                # while True:
                #     # get the frame from the webcam
                #     ret, frame = cap.read()
                #     if not ret:
                #         break
                #     bounding_boxes, points = imgProcessing.detect_faces(frame)
                #     points = points.T
                #     emotion = None
                #     for bbox,p in zip(bounding_boxes, points):
                #         box = bbox.astype(np.int32)
                #         x1,y1,x2,y2=box[0:4]    
                #         face_img=frame[y1:y2,x1:x2,:]

                #         img_tensor = test_transforms(Image.fromarray(face_img))
                #         img_tensor.unsqueeze_(0)
                #         scores = emotion_model(img_tensor.to(device))
                #         scores=scores[0].data.cpu().numpy()
                #         emotion = emotion_dict[np.argmax(scores)]

                #         #Display camera feed
                #         #Filters to hide face (disable this if you want to see your face)
                #         # frame = cv2.GaussianBlur(frame,(23,23),50)
                #         # frame[y1-70:y2+70,x1-70:x2+70] = 0

                #         cv2.rectangle(frame,(x1,y1),(x2,y2),(0,255,0),2)
                #         cv2.putText(frame,emotion,(x1,y1),cv2.FONT_HERSHEY_SIMPLEX,1,(0,255,0),2)
                #         cv2.imshow('frame',frame)

                #         #quit if q is pressed
                #         if cv2.waitKey(1) & 0xFF == ord('q'):
                #             cap.release()
                #             cv2.destroyAllWindows()
                #             break
    
                ret, frame = cap.read()
                if not ret:
                    break
                bounding_boxes, points = imgProcessing.detect_faces(frame)
                points = points.T
                emotion = None
                for bbox,p in zip(bounding_boxes, points):
                    box = bbox.astype(np.int32)
                    x1,y1,x2,y2=box[0:4]    
                    face_img=frame[y1:y2,x1:x2,:]

                    img_tensor = test_transforms(Image.fromarray(face_img))
                    img_tensor.unsqueeze_(0)
                    scores = emotion_model(img_tensor.to(device))
                    scores=scores[0].data.cpu().numpy()
                    emotion = emotion_dict[np.argmax(scores)]
                    
                if emotion == None:
                    emotion = "No"

                msg = emotion.lower()
                
                cap.release()
                cv2.destroyAllWindows()

                msg = msg.encode()
                sendMessage(msg)
            else:
                msg = "no_data"
                msg = msg.encode()
                sendMessage(msg)

        else:
            if USE_CAMERA:
                counter = received_msg[6:]
                counter = int(counter)
                if counter % TIME_INTERVALL == 0:
                    # start the webcam feed
                    cap = cv2.VideoCapture(0)
                    ret, frame = cap.read()
                    if not ret:
                        break
                    bounding_boxes, points = imgProcessing.detect_faces(frame)
                    points = points.T
                    emotion = None
                    for bbox,p in zip(bounding_boxes, points):
                        box = bbox.astype(np.int32)
                        x1,y1,x2,y2=box[0:4]    
                        face_img=frame[y1:y2,x1:x2,:]

                        img_tensor = test_transforms(Image.fromarray(face_img))
                        img_tensor.unsqueeze_(0)
                        scores = emotion_model(img_tensor.to(device))
                        scores=scores[0].data.cpu().numpy()
                        emotion = emotion_dict[np.argmax(scores)]

                    if emotion == None:
                        emotion = "No"

                    msg = emotion.lower()
                    
                    cap.release()
                    cv2.destroyAllWindows()

                    msg = msg.encode()
                    sendMessage(msg)
                else:
                    msg = "no_data"
                    msg = msg.encode()
                    sendMessage(msg)
            else:
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
