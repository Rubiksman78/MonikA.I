<h1 align="center"> :computer: MonikA.I. submod </h1>

<p align="center">
  <a href="https://github.com/Rubiksman78/MonikA.I./releases/latest">
    <img alt="Latest release" src="https://img.shields.io/github/v/release/Rubiksman78/MonikA.I.">
  </a>
   <a href="https://github.com/Rubiksman78/MonikA.I./releases">
    <img alt="Release downloads" src="https://img.shields.io/github/downloads/Rubiksman78/MonikA.I./total">
  </a>
  <a href="https://discord.gg/2RsPuaDxEn">
    <img alt="Latest release" src="https://img.shields.io/badge/Discord-Join%20the%20Server%20!-brightgreen">
  </a>
</p>

This project aims to add new AI based features to [Monika After Story mod](https://github.com/Monika-After-Story/MonikaModDev) with the submod API.
It's using multiple AI models:
- [Pygmalion](https://huggingface.co/PygmalionAI) conversational AI based on GPT-J Finetuning
- [TTS Coqui-AI](https://github.com/coqui-ai/TTS) for Text to Speech
- [OpenAI Whisper](https://github.com/openai/whisper) with [microphone option](https://github.com/mallorbc/whisper_mic) for Speech to Text
- [Character AI](https://character.ai/) if you don't have a GPU
- [Emotion detection from text model](https://huggingface.co/michellejieli/emotion_text_classifier) is also used linked with the chatbot
- Emotion detection with the webcam with a model from [HSEmotion](https://github.com/HSE-asavchenko/face-emotion-recognition) 
- NLI Classification with [deberta](https://huggingface.co/sileod/deberta-v3-base-tasksource-nli)

*Disclaimer: This project adds features (chatbots) that can be imprevisible and may not be in total accordance with the usual way Monika is supposed to speak. The goal is to have fun free interactions when running out of topics for example. There are also a lot of libraries and models involved so it can make the game slower when using them.*

Check the discord [server](https://discord.gg/2RsPuaDxEn) if you have some questions or if you want to be up to date with new fixes and releases !

# User friendly mode

## :boom: Installation 

(Build is for Windows OS only, see `Python version` section for other OS)

This version includes conversing with chatbots or full voicing of the game, the two modes might not be compatible so it is preferable to use them separetely.

To install the user version with executables, I've made a tutorial [HERE](../../wiki/User-friendly-tutorial)

## :fire: Features

- Allow Monika to finally see you through the webcam and react to your emotions
- Speak without scripted text with Monika using the latest chatbots from Character AI or Pygmalion AI
- Hear Monika speak with a Text to Speech module using extracts of voiced dialogues
- Talk with your own voice with Monika thanks to Speech recognition
- Let Monika control actions in the game directly from your chat with her

## :star2: Pygmalion chatbots

Be sure to follow the instructions [here](../../wiki/Install-Pygmalion-locally) to use it.

# How to contribute

If you want to contribute to the project, you can check out this [page](../../wiki/How-to-contribute).
It is not necessary to know how to code and you can add dialogs, expressions. Don't hesitate to propose new things if you have more experience !

# Demonstrations

## :video_game: In Game

The features are available in a specific `AI` Talk menu in the game.
![Talk menu](images/event_mas.png)

- Click on `Let's chat together` to use the Character AI Chatbot
- Click on `Tell me about Pytorch` if you think it is superior to Tensorflow

There is also the possibility of using buttons on the main screen to directly chat. These can be disabled in the Settings Submods if you don't like them.
![Talk buttons](images/buttons_mas.png)

## :cinema: Video Demonstration

https://user-images.githubusercontent.com/66365083/209359921-a4fdad5e-abbd-4550-a1fb-62d695e76c51.mp4

# Python version

## ❓Installation

- Clone the repository or download the latest release (`source code.zip`)
- Go to the project folder with your favorite IDE
- Be sure to have Python installed (3.8 or 3.9), it is not tested and functional before 3.7 and after 3.10.

To setup all the libraries:
- Just do `pip install -r requirements.txt` in a terminal opened within the project folder
- Run also this command to install `torch` with CUDA 11.7 wheels: `pip install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu117`
- If there was an error returned during the installation of the packages, delete the corresponding line in `requirements.txt` and dowload the package concerned manually
- Don't forget to run also `python -m playwright install` to install the browsers.
- If you have issues for installing TTS, someone made a video for that [here](https://www.youtube.com/watch?v=zRaDe08cUIk&t=743s), `simpleaudio` or other packages might need to install Visual Studio C++ Tools too (see tutorial [here](https://stackoverflow.com/questions/64261546/how-to-solve-error-microsoft-visual-c-14-0-or-greater-is-required-when-inst))
- If you want to use Pygmalion models, follow these intructions:
  - To use `int8` i.e. models taking less GPU RAM with `bitsandbytes`:
     - Download these 2 dll files from [here](https://github.com/DeXtmL/bitsandbytes-win-prebuilt). Move those files in your python packages folder, on Windows it is something like `C:\Users\MyName\AppData\Local\Programs\Python\Python39\Lib\site-packages\bitsandbytes`
     - Edit `bitsandbytes\cuda_setup\main.py`: 
       - Change `ct.cdll.LoadLibrary(binary_path)` to `ct.cdll.LoadLibrary(str(binary_path))` two times in the file.
       - Replace the this line ```if not torch.cuda.is_available(): return 'libsbitsandbytes_cpu.so', None, None, None, None``` with ```if torch.cuda.is_available(): return 'libbitsandbytes_cuda116.dll', None, None, None, None```
   - Follow the instructions in the [wiki](https://github.com/Rubiksman78/MonikA.I/wiki/Install-Pygmalion-locally)
- For troubleshooting and other issues, don't hesitate to submit an issue

## :heavy_plus_sign: Add to the game

The submod is in the folder `game`. To add it to your game, you have to add it in the root of your game folder (at the same location where there is already a `game` folder).

## :loudspeaker: Usage

Because of the high usage of Machine Learning algorithms, the inference can be quite long on CPU so it is advised to have a functional GPU for a better experience.
You would need also more RAM than usually, deactivate the TTS model, the emotion detection from text and/or emotion detection from face if it is taking too much ressources.

Launch the file `main.py` for the chatbot things and fill in the window the same as for the user version. Don't launch DDLC yourself, it will open automatically.
When the browser page launches, it can happen that you have to solve the captcha yourself, use debug mode if that happens.

For voicing of the game in real time, launch `voicing.py` and launch DDLC yourself when the message `Waiting for connection...` appears.

You can change the voice used by replacing the extract `talk_13.wav` in the `audio` folder by another audio extract. The longer the extract, the longer the TTS will take to generate the audio at each turn.

## :microphone: Better Voice (only on Linux,MacOS or WSL)

The voice used by Your TTS is obtained with zero-shot learning so it is not perfect and very closed to the original voice. To improve it, you can use the [FastPitch TTS from Nvidia NeMo](https://github.com/NVIDIA/NeMo).
The installation is quite painful, you can do the setup from this [notebook](https://github.com/NVIDIA/NeMo/blob/main/tutorials/tts/FastPitch_Finetuning.ipynb) and use the script `combined_server_for_the_bold.py` to launch the server with this TTS model. It will also take more RAM so be sure to have enough (at the very least 16GB).
You can try using the file `setup_new_tts.sh` to help you installing the requirements for this model.

Click [here](https://drive.google.com/drive/folders/1cgro9BbUJ53GFX1OizvNvmH0Cjnc7oqI?usp=sharing) to get the first part of the finetuned model (FastPitch model) and [here](https://drive.google.com/drive/folders/1NLNDTotB4Qyth_vLBmZMTLIg0dmIm6w0?usp=sharing) for the vocoder model (HifiGAN).

Little demonstration of this TTS model (pauses were cut for convenience):

https://user-images.githubusercontent.com/66365083/209716914-0ee87421-12df-4cc2-96da-9fd85f27214e.mp4

## :wrench: Troubleshooting

- "failed wheels for building TTS": check if you have python 3.8 or 3.9, and not 3.10 or higher
- "playwright command not found": run `python -m playwright install` instead
- "utf8 error": be sure to write the game path in the main script with "\\" and not "\" if you are on Windows
- "Monika says that there is a bug somewhere": that means the website couldn't be accessed, check if you've done the `playwright install` and check on your browser if the website isn't down. You can set `Use Debug Mode` to `Yes` to see the connection with the graphic interface.
