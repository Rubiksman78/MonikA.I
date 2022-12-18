from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
import numpy as np
import cv2
import os
import subprocess
import tempfile
from pydub import AudioSegment
import time
import asyncio
from playwright.async_api import async_playwright
import nest_asyncio
import argparse
from text_emotion import get_emotion
from tensorflow import keras
import json

auth_dict = json.load(open("auth.json"))
USERNAME = auth_dict["USERNAME"]
PASSWORD = auth_dict["PASSWORD"]
nest_asyncio.apply()

#Argparse for game path, chatbot path, use character ai or not, use chatbot or not, use emotion detection or not
parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('--game_path', type=str, default='C:\SAMUEL\ddlc-win\DDLC-1.1.1-pc',
                    help='path to game')
parser.add_argument('--chatbot_path', type=str, default="output-large-3",
                    help='path to chatbot')
parser.add_argument('--use_character_ai', type=bool, default=True,
                    help='use character ai')
parser.add_argument('--use_chatbot', type=bool, default=False,
                    help='use chatbot')
parser.add_argument('--use_emotion_detection', type=bool, default=False, 
                    help='use emotion detection')
parser.add_argument('--use_audio', type=bool, default=False,
                    help='use audio')

args = parser.parse_args()

GAME_PATH = args.game_path
CHATBOT_PATH = args.chatbot_path
USE_CHARACTER_AI = args.use_character_ai
USE_CHATBOT = args.use_chatbot
USE_EMOTION_DETECTION = args.use_emotion_detection
USE_AUDIO = args.use_audio

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

#Launch DDLC Game and wait for it to load

if USE_EMOTION_DETECTION:
    # load model
    emotion_model = keras.models.load_model('mobilenet_7.h5')

# prevents openCL usage and unnecessary logging messages
cv2.ocl.setUseOpenCL(False)

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
    browser = await apw.firefox.launch(headless=False)
    page =  await browser.new_page()
    await page.goto("https://character-ai.us.auth0.com/u/login?state=hKFo2SA2UWpDVjJLanBBRHRtUkl5ZGxKanhyelloRzVCaDd0NaFur3VuaXZlcnNhbC1sb2dpbqN0aWTZIDRaTUtMQkt4UTNKU2tfbnVWbGxyUUZvZURpTW5ld0x0o2NpZNkgZHlEM2dFMjgxTXFnSVNHN0Z1SVhZaEwyV0VrbnFaenY")
    await page.click("button[type=button]")
    await page.click("[id=rcc-confirm-button]")
    await page.click('[class="btn btn-primary btn-sm"]')
    await page.click('[class=" btn border"]')
    await page.fill("input#username",USERNAME)
    await page.fill("input#password",PASSWORD)
    await page.click("button[type=submit]")
    await page.click('[href="/chats"]')
    await page.click('[href="/chat?char=e9UVQuLURpLyCdhi8OjSKSLwKIiE0U-nEqXDeAjk538"]')
    await page.click('[class="col-auto px-2 dropdown"]')
    await page.click('text=Save and Start New Chat')
    return page

def call(client):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    loop.run_until_complete(listenToClient(client))
    loop.close()

subprocess.Popen(GAME_PATH+'\DDLC.exe')

async def listenToClient(client):
    """ Get client username """
    name = "User"
    clients[client] = name
    if USE_CHARACTER_AI:
        page = asyncio.run(launch())
    while True:
        received_msg = client.recv(BUFSIZE).decode("utf-8")
        if received_msg == "chatbot":
            
            received_msg = client.recv(BUFSIZE).decode("utf-8")
            received_msg , step = received_msg.split("/g")
            step = int(step)
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
                        #done_msg = "DONE"
                        #sendMessage(done_msg.encode("utf-8"))
                        query = await page.query_selector_all(('[class="markdown-wrapper markdown-wrapper-last-msg swiper-no-swiping"]'))
                        msg = await query[0].inner_html()
                        
                        #replace <em> with {i} and </em> with {/i}
                        msg = msg.replace("<em>","{i}")
                        msg = msg.replace("</em>","{/i}")
                        #remove <div> and </div>, <p> and </p>
                        msg = msg.replace("<div>","")
                        msg = msg.replace("</div>","")
                        msg = msg.replace("<p>","\n")
                        msg = msg.replace("</p>","")
                        msg = msg.replace("<del>","")
                        msg = msg.replace("</del>","")

                        if received_msg != "QUIT":
                            #Text to speech, save wav to wav_audios folder
                            if USE_AUDIO:
                                msg_audio = msg.replace("\n"," ")
                                subprocess.check_call(['tts', '--text', msg_audio, '--model_name', 'tts_models/multilingual/multi-dataset/your_tts', '--speaker_wav', 'audios/talk_13.wav', '--language_idx', 'en', '--out_path', GAME_PATH + '/game/Submods/AI_submod/audio/out.wav'])
                                f = open(GAME_PATH+'/game/Submods/AI_submod/audio/out.wav', 'rb')
                                AudioSegment.from_wav(f).export(GAME_PATH+'/game/Submods/AI_submod/audio/out.ogg', format='ogg')
                                f.close()
                                os.remove(GAME_PATH+'/game/Submods/AI_submod/audio/out.wav') 
                            emotion = get_emotion(msg)
                            emotion = emotion.encode("utf-8")
                            msg = msg.encode("utf-8")   
                            sendMessage(msg + b"/g" + emotion)
                        break
                    """"
                    
                    msg = await query[-1].inner_text()
                    #wait until line is finished
                    #split words    
                    words = msg.split(" ")
                    #get last word
                    last_word = words[-1]
                    with open("log.txt","a") as f:
                        f.write(repr(msg) + "\n")
                    #Check if there is '\n' in last word and if the previous last word didn't have '\n'
                    lines = msg.split("\n")
                    #remove empty lines
                    lines = [line for line in lines if line != ""]
                    if last_word.count("\n") > 0 and not previous_last:
                        msg = lines[-2]
                        if msg != previous_msg:
                            previous_last = True
                            print([repr(line) for line in lines])
                            print("Current msg: " + msg)
                            print("Previous msg: " + previous_msg)
                            print("Last word: " + last_word)
                            print("\n")
                            previous_msg = msg
                            msg = msg.encode("utf-8")
                            sendMessage(msg)
                    else:
                        previous_last = False
                        previous_msg = msg
                    """
                    
                
            """
            if msg.count('!') > 3:
                msg = msg.replace('!', ' ')
            if msg.count('?') > 3:
                msg = msg.replace('?', ' ')
            """

        elif received_msg == "camera":
            # start the webcam feed
            cap = cv2.VideoCapture(0)
            # Find haar cascade to draw bounding box around face
            ret, frame = cap.read()
            if not ret:
                break
            facecasc = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
            gray = np.array(frame, dtype='uint8')
            faces = facecasc.detectMultiScale(gray,scaleFactor=1.3, minNeighbors=5)

            emotion = None
            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y-50), (x+w, y+h+10), (255, 0, 0), 2)
                roi_gray = gray[y:y + h, x:x + w]
                cropped_img = np.expand_dims(np.expand_dims(cv2.resize(roi_gray, (224, 224)), -1), 0)
                prediction = emotion_model.predict(cropped_img)
                maxindex = int(np.argmax(prediction))
                emotion  = emotion_dict[maxindex]

            if emotion == None:
                emotion = "No"

            msg = emotion.lower()
            
            cap.release()
            cv2.destroyAllWindows()

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