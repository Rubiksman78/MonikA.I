@echo off
git fetch origin/main
git reset --hard origin/main
"libs/pythonlib/python.exe" -m pip install --force-reinstall -r requirements.txt
