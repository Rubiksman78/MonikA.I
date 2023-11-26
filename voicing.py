from socket import AF_INET, SOCK_STREAM
import socket
from threading import Thread
import torch
import IPython.display as ipd
import simpleaudio as sa
import re
import asyncio
from scripts.tts_api import my_TTS
import os
import sys


class HiddenPrints:
    def __enter__(self):
        self._original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout.close()
        sys.stdout = self._original_stdout


device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

with HiddenPrints():
    model = my_TTS(model_name="tts_models/multilingual/multi-dataset/your_tts")

# Global variables
clients = {}
addresses = {}

HOST = '127.0.0.1'
print(HOST)
PORT = 12344
BUFSIZE = 1024
ADDRESS = (HOST, PORT)
try:
    SERVER = socket.socket(AF_INET, SOCK_STREAM)
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
        Thread(target=call, args=(client,)).start()


def call(client):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    loop.run_until_complete(listenToClient(client))
    loop.close()


async def listenToClient(client):
    """ Get client username """
    name = "User"
    clients[client] = name
    step = 0
    last_sentence = ""
    while True:
        try:
            msg = client.recv(BUFSIZE).decode("utf-8")
        except:
            print("Connection lost")
            os._exit(0)
        if msg != "" and msg != "..." and "{fast}" not in msg and "{/fast}" not in msg:
            if step > 0:
                play_obj.stop()
            msg_audio = msg.replace("\n", " ")
            msg_audio = msg_audio.replace("{i}", "")
            msg_audio = msg_audio.replace("{/i}", ".")
            msg_audio = msg_audio.replace("~", "!")
            msg_audio = re.sub(r'\{.*?\}', '', msg_audio)

            if last_sentence != "":
                msg_audio = msg_audio.replace(last_sentence, "\g")
                msg_audio = msg_audio.split("\g")[0]
            msg_audio_play = msg_audio
            # print(msg + "|" + last_sentence + "|" + msg_audio_play)
            with HiddenPrints():
                audio = model.tts(text=msg_audio_play, speaker_wav='coquiai_audios/talk_13.wav', language='en')
            audio = ipd.Audio(audio, rate=16000)
            play_obj = sa.play_buffer(audio.data, 1, 2, 16000)
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
