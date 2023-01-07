<h1 align="center"> :computer: MonikA.I. submod </h1>

<p align="center">
  <a href="https://github.com/Rubiksman78/MonikA.I./releases/latest">
    <img alt="Latest release" src="https://img.shields.io/github/v/release/Rubiksman78/MonikA.I.">
  </a>
</p>

本项目旨在使用Submod API，为[Monika After Story mod](https://github.com/Monika-After-Story/MonikaModDev)添加新的基于AI的功能。
它使用了HuggingFace DialoGPT模型，[TTS Coqui-AI](https://github.com/coqui-ai/TTS)进行文本到语音转换，[OpenAI Whisper](https://github.com/openai/whisper) 和[microphone option](https://github.com/mallorbc/whisper_mic)进行语音到文本转换，以及[Character AI](https://character.ai/)提供更真实的回复。也使用了[emotion detection from text model](https://huggingface.co/michellejieli/emotion_text_classifier)与聊天机器人相连。
此外，还使用[HSEmotion](https://github.com/HSE-asavchenko/face-emotion-recognition)的模型（`facial_analysis.py`，`enet_b2_7.pt`，`mobilenet_7.h5`）通过网络摄像头进行情感检测。

*声明：本项目添加的功能（聊天机器人）可能不可预测，并且可能不完全符合Monika通常应该说话的方式。其目的是在无法找到谈话话题时享受自由的互动乐趣。还有许多库和模型参与其中，因此使用它们时游戏可能会变得卡顿。*

## :fire: 特点

- 通过摄像头让 Monika 看到你，并根据你的情绪做出反应
- 使用 Character AI 或 HuggingFace DialoGPT 最新的聊天机器人，与 Monika 使用交谈
- 通过文本到语音模块，听到 Monika 说话（仍在开发中）
- 通过与 Monika 交谈获得好感，你让莫妮卡放心，莫妮卡就会爱你。

![Character AI](images/image_1.png)

## ❗限制
- 本项目需要代理才能正常访问
- 无论是语音转文字还是character ai, 可能并不能很好的支持中文
> 作者的话    
> *Just be careful about the TTS model because it is completely in English and there are not a lot of well supported ones doing Chinese voice cloning. Same for character.ai, the models are in English so you would need some module doing automatic translation or directly using a chinese model.*    
> 小心使用文字转语音模型，因为它是英文模型，而且没有很多很好的支持做中文语音的模型。character.ai的模型也是英文的，所以你需要一些自动翻译的模块或者直接使用中文模型

PS: 当汉化工作基本完成后我会考虑设计自动翻译功能
## ❓安装

- 克隆存储库或下载最新版本（`source code.zip`）
- 使用您喜欢的 IDE， 转到项目文件夹
- 确保已安装 Python（3.8 或 3.9），TTS 不适用于 3.10

安装依赖库：
- 在项目文件夹内打开的终端中输入 `pip install -r requirements.txt`
（如果想安装 TTS 的开发者版本并对所做的事情有更多控制，可以输入 `bash setup.sh`）
- 不要忘记运行 `python -m playwright install` 以安装浏览器。
- 如果在安装 TTS 时遇到问题，有人为此制作了视频，请参阅[这里](https://www.youtube.com/watch?v=zRaDe08cUIk&t=743s)。
- 如果遇到故障排除或其他问题，请不要犹豫，提交issue

## :heavy_plus_sign: 添加到游戏

子模块为文件夹 `AI_submod`。要将其添加到游戏中，请将其添加到游戏文件夹的`game/Submods/`。

## :video_camera: 视频教程

[![观看视频](https://img.youtube.com/vi/EORpS-fZ10s/hqdefault.jpg)](https://youtu.be/EORpS-fZ10s)

## :loudspeaker: 使用方法

由于机器学习算法对配置要求较高，在 CPU 上的推理可能会很慢，因此建议拥有功能良好的 GPU 以获得更好的体验。

要使用它，您可以启动脚本 `combined_server.py`，该脚本将自动启动带有聊天机器人和情感识别模型的服务器，同时还会启动游戏并初始化客户端/服务器连接。

不要单独启动游戏，这会导致与主进程冲突，主进程会自动启动游戏。

在命令行中有几个参数可以使用：
- `--game_path`：到游戏目录的绝对路径，如 `some_path\DDLC-1.1.1-pc`
- `--chatbot_path`：到聊天机器人模型的相对路径，如 `chatbot_model`（实际上，由于 Character AI 网站的性能更好，库中并没有模型）
- `--use_character_ai`：是否使用 character AI 网站，输入 `True` 或 `False`
- `--use_chatbot`：如果要使用聊天机器人，输入 `True` 或 `False`
- `--use_emotion_detection`：如果要使用网络摄像头进行情感检测，输入 `True` 或 `False`
- `--use_audio`：如果要使用 TTS 模块，输入 `True` 或 `False`。注意，音频模型加载时非常慢，因此每次生成音频可能需要很长时间。
- `--emotion_time`：情感检测的摄像头检测时间（以分钟为单位）
- `--display_browser`：是否希望看到模拟的浏览器（在解决验证码时很有用）
- `--choose_character`：切换您喜欢的角色

您必须创建一个名为 `auth.json` 的 json 文件，其中包含 `USERNAME` 和 `PASSWORD` 键，并填入您的 character AI 网站凭据：
```
{
"USERNAME":"@",
"PASSWORD":"*****"
}
```

当浏览器页面启动时，您可能需要自己解决验证码，然后返回游戏，您的 id 将自动填写。

您可以通过在 `audio` 文件夹中替换 `talk_13.wav` 来更改所使用的声音。时间越长，TTS 在每生成音频所需的时间就越长。



## :video_game: 游戏内

这些特性可以在游戏中的特定“AI”谈话菜单中使用。
![Talk menu](images/image_2.png)

- 单击“一起聊天吧”使用 Character AI 聊天机器人
- 单击“看看我”在交互会话中使用面部情绪检测
- 如果认为 Pytorch 比 Tensorflow 更优秀，请单击“跟我说说Pytorch”

## :cinema: 视频演示

https://user-images.githubusercontent.com/66365083/209359921-a4fdad5e-abbd-4550-a1fb-62d695e76c51.mp4

## :microphone: 更好的声音（仅限于 Linux、MacOS 或 WSL）

Your TTS 所使用的声音是通过zero-shot学习得到的，因此并不完美，与原始声音非常接近。为了优化效果，您可以使用 [Nvidia NeMo 的 FastPitch TTS](https://github.com/NVIDIA/NeMo)。
安装过程相当困难，您可以从此 [notebook](https://github.com/NVIDIA/NeMo/blob/main/tutorials/tts/FastPitch_Finetuning.ipynb) 进行设置，并使用脚本 `combined_server_for_the_bold.py` 使用此 TTS 模型启动服务器。它还需要至少**16GB**的内存。
您可以尝试使用文件 `setup_new_tts.sh` 来帮助您安装此模型的要求。

单击 [此处](https://drive.google.com/drive/folders/1cgro9BbUJ53GFX1OizvNvmH0Cjnc7oqI?usp=sharing) 获取微调模型的第一部分（FastPitch 模型），[此处](https://drive.google.com/drive/folders/1NLNDTotB4Qyth_vLBmZMTLIg0dmIm6w0?usp=sharing) 获取语音合成器模型（HifiGAN）。

此 TTS 模型的小演示（为了方便已删除了暂停）：

https://user-images.githubusercontent.com/66365083/209716914-0ee87421-12df-4cc2-96da-9fd85f27214e.mp4
## :headphones: 声音化一切！
文件 `main_voicing.rpy` 在 `AI_submod` 中（需放在游戏子模块文件夹中）负责将实时显示的文本发送到 `voicing.py` 脚本，该脚本将从此文本播放语音。它使用的是与前面部分相同的模型，如果您想使用第一个 TTS 模型，请随意修改代码（性能不是很好，但安装较简单）。

## 故障排除

- “failed wheels for building TTS”：检查是否有 python 3.8 或 3.9，而不是 3.10 或更高
- “playwright command not found”：运行 `python -m playwright install`
- “utf8 error”：如果在 Windows 上，请确保在主脚本中使用 “\\” 而不是 “\” 写入游戏路径
- “Monika says that there is a bug somewhere”：这意味着无法访问网站，请检查是否已执行 `python -m playwright install`，并在浏览器中检查网站是否启动。您可以将 `display_browser` 设置为 `True`，以查看浏览器界面。

## :alarm_clock: 未来开发计划
- 语音到文本转换，将你的语音转换成文本，直接与 Monika 交谈 :white_check_mark:
- 更好的面部情绪检测 :white_check_mark:
- 面部识别，仅供 Monika 识别你
- 为 STT 添加在游戏中查看麦克风开始录音的功能 :white_check_mark:
- 训练新模型，用于 MEL 频谱图生成（混合 TTS...）和 Vocoders（UnivNet...）
- *欢迎提出改进或你希望看到的新 AI 功能的建议*

