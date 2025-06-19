@echo off
cd /d "%~dp0"
cd ..
"libs/python.exe" "debug scripts/test_adv_tgw.py"
