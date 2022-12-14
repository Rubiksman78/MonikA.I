from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
#from transformers.models.blenderbot import BlenderbotTokenizer, BlenderbotForConditionalGeneration
from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
import numpy as np
import cv2
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, Flatten
from tensorflow.keras.layers import Conv2D
from tensorflow.keras.layers import MaxPooling2D
import os
import subprocess
import tempfile
from pydub import AudioSegment
import time

use_bb = False
GAME_PATH = 'C:\SAMUEL\ddlc-win\DDLC-1.1.1-pc\DDLC.exe'
# Global variables 
clients = {}
addresses = {}

tokenizer = AutoTokenizer.from_pretrained("output-large-2")
chat_model = AutoModelForCausalLM.from_pretrained("output-large-2")

HOST = '127.0.0.1'
PORT = 12346
BUFSIZE = 1024
ADDRESS = (HOST, PORT)
SERVER = socket(AF_INET, SOCK_STREAM)
SERVER.bind(ADDRESS)

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

#Launch DDLC Game and wait for it to load
subprocess.Popen(GAME_PATH)

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
		Thread(target = listenToClient, args = (client,)).start()

def listenToClient(client):
    """ Get client username """
    name = "User"
    clients[client] = name
    while True:
        received_msg = client.recv(BUFSIZE).decode("utf-8")
        if received_msg == "chatbot":
            received_msg = client.recv(BUFSIZE).decode("utf-8")
            received_msg , step = received_msg.split("/g")
            step = int(step)
        
            new_user_input_ids = tokenizer.encode(received_msg + tokenizer.eos_token, return_tensors='pt')
            bot_input_ids = torch.cat([chat_history_ids[:, bot_input_ids.shape[-1]:][-4:], new_user_input_ids], dim=-1) if step > 4 else new_user_input_ids
            #bot_input_ids = new_user_input_ids
            chat_history_ids = chat_model.generate(
                bot_input_ids,
                max_length=40,
                pad_token_id=tokenizer.eos_token_id,  
                no_repeat_ngram_size=3,
                do_sample=True, 
                top_k=50, 
                top_p=0.95,
                repetition_penalty=1.1
            )

            msg = tokenizer.decode(chat_history_ids[:, bot_input_ids.shape[-1]:][0], skip_special_tokens=True)
            """
            if msg.count('!') > 3:
                msg = msg.replace('!', ' ')
            if msg.count('?') > 3:
                msg = msg.replace('?', ' ')
            """

            #Text to speech, save wav to wav_audios folder
            """
            subprocess.check_call(['tts', '--text', msg, '--model_name', 'tts_models/multilingual/multi-dataset/your_tts', '--speaker_wav', 'audios/talk_13.wav', '--language_idx', 'en', '--out_path', 'C:/SAMUEL/ddlc-win/DDLC-1.1.1-pc/game/Submods/AI_submod/audio/out.wav'])
            f = open('C:/SAMUEL/ddlc-win/DDLC-1.1.1-pc/game/Submods/AI_submod/audio/out.wav', 'rb')
            AudioSegment.from_wav(f).export('C:/SAMUEL/ddlc-win/DDLC-1.1.1-pc/game/Submods/AI_submod/audio/out.ogg', format='ogg')
            f.close()
            os.remove('C:/SAMUEL/ddlc-win/DDLC-1.1.1-pc/game/Submods/AI_submod/audio/out.wav')    
            """

            msg = msg.encode()
            sendMessage(msg)

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