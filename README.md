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

<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
        <ul>
        <li><a href="#features">Features</a></li>
        <li><a href="#chatbots">Chatbots</a></li>
        <li><a href="#usage-information">Usage information</a></li>
        </ul>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>


# About the project
This project aims to add new AI based features to [Monika After Story mod](https://github.com/Monika-After-Story/MonikaModDev) with the submod API.
It's using multiple AI models:
- [text-generation-webui](https://github.com/oobabooga/text-generation-webui)
- [TTS Coqui-AI](https://github.com/coqui-ai/TTS) and [Tortoise-TTS](https://github.com/152334H/tortoise-tts-fast) for Text to Speech
- [OpenAI Whisper](https://github.com/openai/whisper) with [microphone option](https://github.com/mallorbc/whisper_mic) for Speech to Text
- [Emotion detection from text model](https://huggingface.co/michellejieli/emotion_text_classifier) is also used linked with the chatbot
- NLI Classification with [deberta](https://huggingface.co/sileod/deberta-v3-base-tasksource-nli)

Check the discord [server](https://discord.gg/2RsPuaDxEn) if you have some questions or if you want to be up to date with new fixes and releases !

# Getting Started

## Prerequisites

The submod is compatible with the latest version of MAS (v0.12.15). It has been tested on Windows 10/11 with Python 3.9. A manual installation is also possible on Linux or MacOS.

## Installation

### :eight_spoked_asterisk: User version installation (Windows)

This version includes conversing with chatbots or full voicing of the game, the two modes might not be compatible so it is preferable to use them separetely.

To install the user version with executables, a tutorial is avilable [here](https://github.com/Rubiksman78/MonikA.I/wiki/Installation-tutorial-(after-2.0)) after version 2.0.

### :penguin: Python version (Linux or MacOS)

Wiki page [HERE](https://github.com/Rubiksman78/MonikA.I/wiki/Installation-Tutorial-(Linux,MacOS))

# Usage

## :fire: Features

- Speak without scripted text with Monika using any chatbots compatible with `text-generation-webui`
- Hear Monika speak with a Text to Speech module using extracts of voiced dialogues
- Talk with your own voice with Monika thanks to Speech recognition
- Let Monika control actions in the game directly from your chat with her

## :star2: Chatbots

Be sure to follow the instructions [here](../../wiki/Install-Local-Chatbots-locally) to use conversational AI models running locally.

## :warning: Usage information
 
After installation is completed, check the common information for usage on this [page](https://github.com/Rubiksman78/MonikA.I/wiki/Common-information)

# How to contribute

If you want to contribute to the project, you can check out this [page](../../wiki/How-to-contribute).
It is not necessary to know how to code and you can add dialogs or expressions. Don't hesitate to propose new things if you have more experience !

# Demonstrations

## :video_game: In Game

The features are available in a specific `AI` Talk menu in the game.
![Talk menu](images/event_mas.png)

- Click on `Let's chat together` to use the Character AI Chatbot
- Click on `Tell me about Pytorch` if you think it is superior to Tensorflow

There is also the possibility of using buttons on the main screen to directly chat. These can be disabled in the Settings Submods if you don't like them.
![Talk buttons](images/buttons_mas.png)

## 📖 Written tutorial
https://www.reddit.com/user/Sylphar/comments/1f91nsf/streamlined_new_monikai_guide/
## :cinema: Video Demonstration

https://user-images.githubusercontent.com/66365083/209359921-a4fdad5e-abbd-4550-a1fb-62d695e76c51.mp4
