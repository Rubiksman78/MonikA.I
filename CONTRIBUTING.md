# To do

These are some ideas that come in my mind but it is surely not exhaustive. Feel free to give suggestions on Issues or on the discord server.

- Improve dialogs to introduce the Submod the first time (telling what it does, how is it different from actual Monika) :white_check_mark:
- Add saving history of conversations to see again your best interactions
- Making it like a messaging app with questions/answers listed on a same window
- Define better facial expressions corresponding to predifined emotions (happiness,fear,surprise...)
- Convert more functionalities to executable files (TTS,Speech Recognition) :white_check_mark:
- Make the better TTS available only on MacOS/Linux for now usable also on other OS.
- Link this with Live2D for face movements with speech and emotions
- Face recognition for Monika only to recognize you
- Training new models for MEL Spectrogram Generation (Mixed TTS...) and Vocoders (UnivNet...)
- Speech to text to convert your own voice in text and directly speak with Monika :white_check_mark:
- Better face emotions detection :white_check_mark:
- Add possibility to see when microphone starts recording in the game for STT :white_check_mark:


# How can you contribute:

## Simple scripting

Renpy files are accessible on the repository [here](https://github.com/Rubiksman78/MonikA.I/blob/main/game/Submods/AI_submod).
You can check out `monikai_topics.rpy` with a set of scripted dialogues to introduce the mod, announce some bugs...etc. Feel free to propose better ones, tune the facial expressions or other topics you find pertinents in this submod

## More coding in renpy

There are other renpy files available:
- `monikai_buttons.rpy` for the buttons on the main screen to use text chat or voice chat
- `monikai_chat.rpy` for the main functions about chatting with the bot
- `monikai_voicing.rpy` to overwrite the `renpy.say` for the full voicing mode
- `monikai_emotion.rpy` to do the facial emotion detection (available soon)

## Python code

You can take a look at the source code if you want to uprade things concerning the tkinter login interface `login_screen.py` or the main scripts like `main.py` (chat) or `voicing.py` (full voicing).

There are other scripts that can be useful in the repository, some of them are in the folder `old_scripts` because they are no longer indate with the releases.
