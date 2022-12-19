<h1 align="center"> :computer: MonikA.I. submod </h1>

<p align="center">
  <a href="https://github.com/Rubiksman78/MonikA.I./releases/latest">
    <img alt="Latest release" src="https://img.shields.io/github/v/release/Rubiksman78/MonikA.I.">
  </a>
  <a href="https://github.com/Rubiksman78/MonikA.I./releases">
    <img alt="Release downloads" src="https://img.shields.io/github/downloads/Rubiksman78/MonikA.I./total">
  </a>
</p>

This project aims to add new AI based features to [Monika After Story mod](https://github.com/Monika-After-Story/MonikaModDev) with the submod API.
It's using HuggingFace DialoGPT models, [TTS Coqui-AI](https://github.com/coqui-ai/TTS) for Text to Speech and [Character AI](https://character.ai/) for more realistic responses. An [emotion detection from text model](https://huggingface.co/michellejieli/emotion_text_classifier) is also used linked with the chatbot.
There is also emotion detection with the webcam with a model from [HSEmotion](https://github.com/HSE-asavchenko/face-emotion-recognition).


## :fire: Features

- Allow Monika to finally see you through the webcam and react to your emotions
- Speak without scripted text with Monika using the latest chatbots from Character AI or HuggingFace DialoGPT
- Hear Monika speak with a Text to Speech module using extracts of voiced dialogues (still in development)
- Gain affection points by talking with Monika, the more you make her feel positive emotions, the more she will love you (with respect to the daily cap). Be careful, she can also feel negative emotions and lose affection points.

![Character AI](images/image_1.png)
## ❓Installation

Run the setup with ```bash setup.sh``` that will install the requirements for the project and the requirements for the TTS module.

## :heavy_plus_sign: Add to the game

The submod is the folder `AI_submod`. To add it to your game, you have to add it in your game folder to `game/Submods/`.

## :loudspeaker: Usage

To use it, you can launch the script `combined_server.py` that will automatically launch a server with chatbot and emotion recognitions models, it will also launch the game and initialize the client/server connection. 

Don't launch the game independently, it will cause conflicts with the process that will automatically launch the game in the main.

There are several arguments you can use in command line:
- `--game_path` : the absolute path to your game directory like `some_path\DDLC-1.1.1-pc`
- `--chatbot_path` : the relative path to the chatbot model like `chatbot_model` (There is actually no model in the repository because of the better performances of the Character AI website)
- `--use_character_ai` : if you want to use the character AI website, `True` or `False`
- `--use_chatbot` : if you want to use the chatbot, `True` or `False`
- `--use_emotion_detection` : if you want to use the emotion detection with the webcam, `True` or `False`
- `--use_audio` : if you want to use the TTS module, `True` or `False`. Warning, the audio model is quite long to load, so it can take a while before the sound plays.

You have to create a json file `auth.json` with keys `USERNAME` and `PASSWORD` with your credentials for the character AI website

You can change the voice used by replacing the extract `talk_13.wav` in the `audio` folder by another audio extract. The longer the extract, the longer the TTS will take to generate the audio at each turn.

When the browser page launches, you now have to solve the captcha yourself and then go back to the game.

The features are available in a specific `AI` Talk menu in the game.
![Talk menu](images/image_2.png)

## :alarm_clock: To develop
- Convert `playwright` browser simulator to python `requests` for faster run and no parasite window
- Speech to text to convert your own voice in text and directly speak with Monika
- Better face emotions detection for changes in weather, postures...etc
- Face recognition for Monika only to recognize you
