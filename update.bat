@echo off
git fetch origin
git reset --hard main
rm config.json
"libs/pythonlib/python.exe" -m pip install --force-reinstall -r requirements.txt
