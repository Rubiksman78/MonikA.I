@echo off
git pull
"libs/pythonlib/python.exe" -m pip install --force-reinstall -r requirements.txt
