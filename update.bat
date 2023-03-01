@echo off
git fetch origin
git reset --hard origin
"libs/pythonlib/python.exe" -m pip install --force-reinstall -r requirements.txt
