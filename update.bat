@echo off
git fetch main
git reset --hard main
"libs/pythonlib/python.exe" -m pip install --force-reinstall -r requirements.txt
