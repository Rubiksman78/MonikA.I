@echo off
py -m venv venv
"venv/Scripts/python.exe" -m pip install -r requirements.txt
git clone https://github.com/coqui-ai/TTS
cd TTS
"../venv/Scripts/python.exe" -m pip install -e .
cd ..
git clone https://github.com/152334H/tortoise-tts-fast
cd tortoise-tts-fast
"../venv/Scripts/python.exe" -m pip install -e .
cd ..
cp -r bitsandbytes venv/Lib/site-packages