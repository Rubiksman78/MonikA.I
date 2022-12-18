# MonikA.I.

This project aims to add new AI based features to [Monika After Story mod](https://github.com/Monika-After-Story/MonikaModDev) with the submod API.

## Installation

Run the setup with ```bash setup.sh``` that will install the requirements for the project and the requirements for the TTS module.

## Add to the game

The submod is the folder `AI_submod`. To add it to your game, you have to add it in your game folder to `game/Submods/`.

## Usage

To use it, you can launch the script `combined_server.py` that will automatically launch a server with chatbot and emotion recognitions models, it will also launch the game and initialize the client/server connection. 
There are several arguments you can use in command line:
- `--game_path` : the absolute path to your game directory like `some_path\DDLC-1.1.1-pc`
- `--chatbot_path` : the relative path to the chatbot model like `chatbot_model`
- `--use_character_ai` : if you want to use the character AI website, `True` or `False`
- `--use_chatbot` : if you want to use the chatbot, `True` or `False`
- `--use_emotion_detection` : if you want to use the emotion detection with the webcam, `True` or `False`
- `--use_audio` : if you want to use the TTS module, `True` or `False`

You have to create a json file `auth.json` with keys `USERNAME` and `PASSWORD` with your credentials for the character AI website.

