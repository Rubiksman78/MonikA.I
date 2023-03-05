#!/bin/bash

"libs/pythonlib/python.exe" -m pip install numpy==1.23.0
"libs/pythonlib/python.exe" -m playwright install
"libs/pythonlib/python.exe" main.py
