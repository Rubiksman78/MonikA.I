#!/bin/bash

pip install -r requirements.txt
git clone https://github.com/coqui-ai/TTS
cd TTS
pip install -e .
cd ..