@echo off
git fetch origin
git reset --hard origin/main
"libs/python.exe" -m pip install -r requirements.txt
