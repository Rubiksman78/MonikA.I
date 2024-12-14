@echo off
:: Ask for the user if they want to install tortoise tts, yourTTS, playwright and if they want to use GPU
set /p installTortoiseTTS=Do you want to install Tortoise TTS? [y/n]
set /p installYourTTS=Do you want to install yourTTS and XTTS? [y/n]
set /p installPlaywright=Do you want to install local chatbot? [y/n]
set /p useActions=Do you want to use actions? [y/n]
set /p useSpeech=Do you want to use speech recognition? [y/n]
set /p useGPU=Do you want to use GPU? [y/n]
set /p cudaVersion=What is your cuda version? a for 11.8, b for 12.1, c for none [a/b/c]
:: Install requirements
@REM echo Installing requirements...
@REM "libs/python.exe" -m pip install -r requirements.txt

:: Install playwright
if /i "%installPlaywright%" EQU "y" (
    echo Installing playwright...
    "libs/python.exe" -m playwright install firefox
)
:: Install actions
if /i "%useActions%" EQU "y" (
    echo Installing transformers...
    "libs/python.exe" -m pip install transformers
)
:: Install speech recognition
if /i "%useSpeech%" EQU "y" (
    echo Installing speech recognition...
    "libs/python.exe" -m pip install OpenAI-whisper
    "libs/python.exe" -m pip install SpeechRecognition
    "libs/python.exe" -m pip install pyaudio
)

:: Install yourTTS and XTTS
if /i "%installYourTTS%" EQU "y" (
    echo Installing yourTTS and XTTS...
    "libs/python.exe" -m pip install simpleaudio-1.0.4-cp39-cp39-win_amd64.whl
    "libs/python.exe" -m pip install coqui-tss
)

:: Install tortoise tts
if /i "%installTortoiseTTS%" EQU "y" (
    echo Installing Tortoise TTS...
    "libs/python.exe" -m pip install simpleaudio-1.0.4-cp39-cp39-win_amd64.whl
    "libs/python.exe" -m pip install tortoise-tts
    "libs/python.exe" -m pip install voicefixer
)

:: Install pytorch
if /i "%useGPU%" EQU "y" (
    echo Installing pytorch...
    if /i "%cudaVersion%" EQU "a" (
        "libs/python.exe" -m pip install --force torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
        "libs/python.exe" -m pip install -U typing_extensions
    ) else if /i "%cudaVersion%" EQU "b" (
        "libs/python.exe" -m pip install --force torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
        "libs/python.exe" -m pip install -U typing_extensions
    ) else (
        echo Invalid cuda version!
    )
) else (
    echo Installing pytorch...
    "libs/python.exe" -m pip install torch torchvision torchaudio
)
