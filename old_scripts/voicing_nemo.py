from socket import AF_INET, SOCK_STREAM
import socket
from threading import Thread
import torch
import nest_asyncio
import IPython.display as ipd
import simpleaudio as sa
import re
import asyncio

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

nest_asyncio.apply()

from new_tts_infer import infer,get_best_ckpt_from_last_run
from nemo.collections.tts.models import HifiGanModel
from nemo.collections.tts.models import FastPitchModel

GAME_PATH = "/mnt/c/SAMUEL/ddlc-win/DDLC-1.1.1-pc"
#vocoder = HifiGanModel.from_pretrained("tts_hifigan")
vocoder = HifiGanModel.load_from_checkpoint("hifigan_ft/HifiGan/2023-01-02_14-20-41/checkpoints/HifiGan--val_loss=0.4200-epoch=167-last.ckpt")
vocoder = vocoder.eval().to(device)

new_speaker_id = 9017
duration_mins = 5
mixing = False
original_speaker_id = "ljspeech"

last_ckpt = get_best_ckpt_from_last_run("./", new_speaker_id, duration_mins, mixing, original_speaker_id)
print(last_ckpt)

spec_model = FastPitchModel.load_from_checkpoint(last_ckpt)
spec_model.eval().to(device)

# Global variables
clients = {}
addresses = {}

HOST = '127.0.0.1'
print(HOST)
PORT = 12344
BUFSIZE = 1024
ADDRESS = (HOST, PORT)
try:
    SERVER=socket.socket(AF_INET, SOCK_STREAM)
    print("Socket creation successful")
except:
    print("Socket creation Failed")
SERVER.bind(ADDRESS)

def listen():
	""" Wait for incoming connections """
	print("Waiting for connection...")
	while True:
		client, client_address = SERVER.accept()
		print("%s:%s has connected." % client_address)
		addresses[client] = client_address
		Thread(target = call, args = (client,)).start()

def call(client):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    loop.run_until_complete(listenToClient(client))
    loop.close()

#Clean the log.txt file
with open("log.txt", "w") as f:
    f.write("")

async def listenToClient(client):
    """ Get client username """
    name = "User"
    clients[client] = name
    step = 0
    last_sentence = ""
    while True:
        msg = client.recv(BUFSIZE).decode("utf-8")         

        if msg != "" and len(msg) > 5:
            if step > 0:
                play_obj.stop()
            msg_audio = msg.replace("\n"," ")
            msg_audio = msg_audio.replace("{i}","")
            msg_audio = msg_audio.replace("{/i}",".")
            msg_audio = msg_audio.replace("~","!")
            #remove characters in {} and []
            msg_audio = re.sub(r'\{.*?\}', '', msg_audio)

            #Delete last_sentence in the msg_audio and everything at the right of it
            if last_sentence != "":
                msg_audio = msg_audio.replace(last_sentence,"\g")
                msg_audio = msg_audio.split("\g")[0]
            msg_audio_play = msg_audio
            print(msg_audio + "|" + last_sentence + "|" + msg_audio_play)
            print('\n')
            spec, audio = infer(spec_model, vocoder,msg_audio_play)
            audio = ipd.Audio(audio, rate=22050)
            play_obj = sa.play_buffer(audio.data, 1, 2, 22050)
            step += 1
            last_sentence = msg_audio
    
def sendMessage(msg, name=""):
    """ send message to all users present in
    the chat room"""
    for client in clients:
        client.send(bytes(name, "utf8") + msg)

if __name__ == "__main__":
    SERVER.listen(10)
    ACCEPT_THREAD = Thread(target=listen)
    ACCEPT_THREAD.start()
    ACCEPT_THREAD.join()
    SERVER.close()