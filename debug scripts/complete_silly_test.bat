@echo off
cd /d "%~dp0"
cd ..
"libs/python.exe" "debug scripts/complete_silly_test.py"
