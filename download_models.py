import torch
import torch

import speech_recognition as sr
import whisper

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

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