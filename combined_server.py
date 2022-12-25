from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import numpy as np
import cv2
import os
import subprocess
from pydub import AudioSegment
import asyncio
from playwright.async_api import async_playwright
import nest_asyncio
import argparse
from text_emotion import get_emotion
import json

from facial_analysis import FacialImageProcessing
import torch
from PIL import Image
from torchvision import transforms

#from speech_to_text import stt
import speech_recognition as sr
import whisper

auth_dict = json.load(open("auth.json"))
USERNAME = auth_dict["USERNAME"]
PASSWORD = auth_dict["PASSWORD"]
nest_asyncio.apply()
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

#Argparse for game path, chatbot path, use character ai or not, use chatbot or not, use emotion detection or not
parser = argparse.ArgumentParser(description='Add some arguments.')
parser.add_argument('--game_path', type=str, default='C:\SAMUEL\ddlc-win\DDLC-1.1.1-pc',
                    help='path to game')
parser.add_argument('--chatbot_path', type=str, default="output-large-3",
                    help='path to chatbot')
parser.add_argument('--use_character_ai', type=bool, default=True,
                    help='use character ai')
parser.add_argument('--use_chatbot', type=bool, default=False,
                    help='use chatbot')
parser.add_argument('--use_emotion_detection', type=bool, default=True, 
                    help='use emotion detection')
parser.add_argument('--use_audio', type=bool, default=True,
                    help='use audio')
parser.add_argument('--emotion_time', type=int, default=10,
                    help='time between camera captures')
parser.add_argument('--display_browser', type=bool, default=False,
                    help='displaying browser or not when using character ai,\
                    useful for debugging')
parser.add_argument('--choose_character', type=str, default="0",
                    help='character to chat with')
parser.add_argument('--monika_feeling', type=str, default=False,
                    help='choose whether or not to display the emotion detected from the chat')

args = parser.parse_args()

GAME_PATH = args.game_path
CHATBOT_PATH = args.chatbot_path
USE_CHARACTER_AI = args.use_character_ai
USE_CHATBOT = args.use_chatbot
USE_EMOTION_DETECTION = args.use_emotion_detection
USE_AUDIO = args.use_audio
EMOTION_TIME = args.emotion_time
DISPLAY_BROWSER = args.display_browser
CHOOSE_CHARACTER = args.choose_character
MONIKA_FEELING = args.monika_feeling

characters_pages = {
    "0": '[href="/chat?char=e9UVQuLURpLyCdhi8OjSKSLwKIiE0U-nEqXDeAjk538"]',
    "1": '[href="/chat?char=EdSSlsl49k3wnwvMvK4eCh4yOFBaGTMJ7Q9CxtG2DiU"]'
}

# Global variables 
clients = {}
addresses = {}

if USE_CHATBOT:
    tokenizer = AutoTokenizer.from_pretrained(CHATBOT_PATH)
    chat_model = AutoModelForCausalLM.from_pretrained(CHATBOT_PATH)

HOST = '127.0.0.1'
PORT = 12346
BUFSIZE = 1024
ADDRESS = (HOST, PORT)
SERVER = socket(AF_INET, SOCK_STREAM)
SERVER.bind(ADDRESS)

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

###Load the emotion model#####
emotion_model = torch.load('models/enet_b2_7.pt').to(device)

###Load the speech recognizer#####
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

# prevents openCL usage and unnecessary logging messages
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

# dictionary which assigns each label an emotion (alphabetical order)
emotion_dict = {0: "Angry", 1: "Disgusted", 2: "Fearful", 3: "Happy", 4: "Neutral", 5: "Sad", 6: "Surprised"}

def listen():
	""" Wait for incoming connections """
	print("Waiting for connection...")
	while True:
		client, client_address = SERVER.accept()
		print("%s:%s has connected." % client_address)
		addresses[client] = client_address
		Thread(target = call, args = (client,)).start()

async def launch():
    apw = await async_playwright().start()
    if DISPLAY_BROWSER:
        browser = await apw.firefox.launch(headless=False)
    else:
        browser = await apw.firefox.launch()
    page =  await browser.new_page()
    await page.goto("https://character-ai.us.auth0.com/u/login?state=hKFo2SA2UWpDVjJLanBBRHRtUkl5ZGxKanhyelloRzVCaDd0NaFur3VuaXZlcnNhbC1sb2dpbqN0aWTZIDRaTUtMQkt4UTNKU2tfbnVWbGxyUUZvZURpTW5ld0x0o2NpZNkgZHlEM2dFMjgxTXFnSVNHN0Z1SVhZaEwyV0VrbnFaenY")
    await page.click("button[type=button]")
    await page.click("[id=rcc-confirm-button]")
    await page.click('[class="btn btn-primary btn-sm"]')
    await page.click('[class=" btn border"]')
    await page.fill("input#username",USERNAME)
    await page.fill("input#password",PASSWORD)
    try:
        await page.click("button[type=submit]") #If there is no captcha
        await page.click('[href="/chats"]',timeout=10000)
    except:
        await page.fill("input#password",PASSWORD)
        while not await page.is_visible('[href="/chats"]'):
            await asyncio.sleep(1)
        await page.click('[href="/chats"]')
    char_page = characters_pages[CHOOSE_CHARACTER]
    if await page.is_visible(char_page):
        await page.click(char_page)
    else:
        await page.click('[href="/search?"]')
        await page.fill("input#search-input","monika")
        await page.click('[class="btn btn-primary"]')
        await page.click(char_page)
    await page.click('[class="col-auto px-2 dropdown"]')
    await page.click('text=Save and Start New Chat')
    return page

def call(client):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    loop.run_until_complete(listenToClient(client))
    loop.close()

#Launch the game
subprocess.Popen(GAME_PATH+'\DDLC.exe')

async def listenToClient(client):
    """ Get client username """
    name = "User"
    clients[client] = name
    
    while True:
        received_msg = client.recv(BUFSIZE).decode("utf-8") #Message indicating the mode used (chatbot,camera_int or camera)
        #print("Received: "+ received_msg)
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
                #received_msg = stt()

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

            if USE_CHATBOT:
                new_user_input_ids = tokenizer.encode(received_msg + tokenizer.eos_token, return_tensors='pt')
                bot_input_ids = torch.cat([chat_history_ids[:, bot_input_ids.shape[-1]:][-2:], new_user_input_ids], dim=-1) if step > 2 else new_user_input_ids
                chat_history_ids = chat_model.generate(
                    bot_input_ids,
                    max_length=100,
                    pad_token_id=tokenizer.eos_token_id,  
                    no_repeat_ngram_size=3,
                    num_beams=20,    
                    early_stopping=True,
                    num_return_sequences=1,
                )

                msg = tokenizer.decode(chat_history_ids[:, bot_input_ids.shape[-1]:][0], skip_special_tokens=True)
                msg = msg.encode("utf-8")
                sendMessage(msg)

            if USE_CHARACTER_AI:
                if step == 0:
                    try:
                        page = asyncio.run(launch())
                        sendMessage("server_ok".encode("utf-8"))
                    except:
                        sendMessage("server_error".encode("utf-8"))
                        continue
                if os.path.exists(GAME_PATH+'/game/Submods/AI_submod/audio/out.ogg'):
                    os.remove(GAME_PATH+'/game/Submods/AI_submod/audio/out.ogg')
                if received_msg == "QUIT":
                    await page.fill("textarea","I'll be right back")
                else:
                    await page.fill("textarea",received_msg)
                while True:
                    try:
                        await page.click('[class="btn py-0"]')
                        break
                    except:
                        pass
                while True:
                    if not await page.is_disabled('[class="btn py-0"]'):
                        query = await page.query_selector_all(('[class="markdown-wrapper markdown-wrapper-last-msg swiper-no-swiping"]'))
                        msg = await query[0].inner_html()
                        
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
                            #Text to speech, save wav to wav_audios folder
                            if USE_AUDIO:
                                msg_audio = msg.replace("\n"," ")
                                msg_audio = msg_audio.replace("{i}","")
                                msg_audio = msg_audio.replace("{/i}",".")
                                msg_audio = msg_audio.replace("~","!")
                                subprocess.check_call(['tts', '--text', msg_audio, '--model_name', 'tts_models/multilingual/multi-dataset/your_tts', '--speaker_wav', 'audios/talk_13.wav', '--language_idx', 'en', '--out_path', GAME_PATH + '/game/Submods/AI_submod/audio/out.wav'])
                                f = open(GAME_PATH+'/game/Submods/AI_submod/audio/out.wav', 'rb')
                                AudioSegment.from_wav(f).export(GAME_PATH+'/game/Submods/AI_submod/audio/out.ogg', format='ogg')
                                f.close()
                                os.remove(GAME_PATH+'/game/Submods/AI_submod/audio/out.wav')

                            #Emotion detection
                            if MONIKA_FEELING: 
                                emotion = get_emotion(msg)
                                emotion = emotion.encode("utf-8")
                            else:
                                emotion = "".encode("utf-8")
                            msg = msg.encode("utf-8")   
                            msg_to_send = msg + b"/g" + emotion
                            print("Sent: "+ msg_to_send.decode("utf-8"))
                            sendMessage(msg_to_send)
                        break
                    
        elif received_msg == "camera_int":
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
            counter = received_msg[6:]
            counter = int(counter)
            if counter % EMOTION_TIME == 0:
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