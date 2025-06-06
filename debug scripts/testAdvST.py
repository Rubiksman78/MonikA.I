import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

os.environ["COQUI_TOS_AGREED"] = "1"

import time
import warnings
import torch
import yaml
import re
import numpy as np
from playwright.sync_api import sync_playwright

warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=FutureWarning)


uni_chr_re = re.compile(r'\\u[0-9a-fA-F]{4}')
# Configuration
CONFIG = {
    "USE_TTS": True,
    "USE_ACTIONS": True,
    "USE_SPEECH_RECOGNITION": True,
    "TTS_MODEL": "XTTS",  # Options: "Your TTS", "XTTS", "Tortoise TTS"
    "VOICE_SAMPLE_COQUI": "MonikaTest.wav",  # Only needed for XTTS
    "VOICE_SAMPLE_TORTOISE": "monika_voice"  # Only needed for Tortoise
}

# Initialize device
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

# Initialize Action Classification if enabled
if CONFIG["USE_ACTIONS"]:
    try:
        from transformers import pipeline
        print("Initializing action classifier...")
        
        # Load actions from YAML
        with open("actions.yml", "r") as f:
            ACTIONS = yaml.safe_load(f)
        
        REVERT_ACTION_DICT = {}
        for key in ACTIONS:
            for action in ACTIONS[key]:
                REVERT_ACTION_DICT[action] = key
        ALL_ACTIONS = []
        for key in ACTIONS:
            ALL_ACTIONS += ACTIONS[key]
        
        action_classifier = pipeline(
            "zero-shot-classification",
            model="sileod/deberta-v3-base-tasksource-nli"
        )
        print("Action classifier initialized successfully")
    except Exception as e:
        print(f"Failed to initialize action classifier: {e}")
        CONFIG["USE_ACTIONS"] = False

# Initialize TTS if enabled
if CONFIG["USE_TTS"]:
    try:
        from scripts.play_tts import play_TTS, initialize_xtts
        print(f"Initializing TTS model: {CONFIG['TTS_MODEL']}...")
        
        if CONFIG["TTS_MODEL"] == "Your TTS":
            from scripts.tts_api import my_TTS
            tts_model = my_TTS(model_name="tts_models/multilingual/multi-dataset/your_tts")
            sampling_rate = 16000
            voice_samples = None
            conditioning_latents = None
        elif CONFIG["TTS_MODEL"] == "XTTS":
            tts_model = initialize_xtts()
            sampling_rate = 24000
            voice_samples = None
            conditioning_latents = None
        elif CONFIG["TTS_MODEL"] == "Tortoise TTS":
            if device.type == "cuda":
                from tortoise.api_fast import TextToSpeech, MODELS_DIR
            else:
                from tortoise.api import TextToSpeech, MODELS_DIR
            from tortoise.utils.audio import load_voices
            from voicefixer import VoiceFixer
            tts_model = TextToSpeech(models_dir=MODELS_DIR, kv_cache=True)
            voice_samples, conditioning_latents = load_voices(
                [CONFIG["VOICE_SAMPLE_TORTOISE"]], 
                ["tortoise_audios"]
            )
            vfixer = VoiceFixer()
            sampling_rate = 24000
        
        print("TTS model initialized successfully")
    except Exception as e:
        print(f"Failed to initialize TTS model: {e}")
        CONFIG["USE_TTS"] = False

# Initialize Speech Recognition if enabled
if CONFIG["USE_SPEECH_RECOGNITION"]:
    try:
        import speech_recognition as sr
        import whisper
        print("Initializing speech recognition...")
        
        def init_stt(model="base", english=True, energy=300, pause=0.8, dynamic_energy=False):
            if model != "large" and english:
                model = model + ".en"
            audio_model = whisper.load_model(model)
            r = sr.Recognizer()
            r.energy_threshold = energy
            r.pause_threshold = pause
            r.dynamic_energy_threshold = dynamic_energy
            return r, audio_model

        r, audio_model = init_stt()
        print("Speech recognition initialized successfully")
    except Exception as e:
        print(f"Failed to initialize speech recognition: {e}")
        CONFIG["USE_SPEECH_RECOGNITION"] = False

def get_speech_input():
    """Record and transcribe speech input"""
    if not CONFIG["USE_SPEECH_RECOGNITION"]:
        print("Enter your message (or press Enter without text to send empty input):")
        text_input = input().strip()
        return text_input
    try:
        with sr.Microphone(sample_rate=16000) as source:
            print("Listening... Speak now!")
            audio = r.listen(source)
            print("Processing speech...")
            
            torch_audio = torch.from_numpy(
                np.frombuffer(
                    audio.get_raw_data(),
                    np.int16
                ).flatten().astype(np.float32) / 32768.0
            )
            
            result = audio_model.transcribe(torch_audio, language='english')
            transcribed_text = result['text'].strip()
            print(f"Transcribed: {transcribed_text}")
            return transcribed_text
    except Exception as e:
        print(f"Speech recognition failed: {e}")
        return "test"  # Fallback on error

def process_with_actions(message):
    """Process message through action classifier if enabled"""
    if not CONFIG["USE_ACTIONS"]:
        return "none"
        
    try:
        sequence = f"The player is speaking with Monika, his virtual girlfriend. Now he says: {message}. What is the label of this sentence?"
        result = action_classifier(sequence, ALL_ACTIONS)
        action = result['labels'][0]
        return REVERT_ACTION_DICT[action]
    except Exception as e:
        print(f"Action classification failed: {e}")
        return "none"

def play_tts_response(message, step=0):
    """Play TTS for the response if enabled"""
    if not CONFIG["USE_TTS"]:
        return
        
    try:
        play_obj = play_TTS(
            step,
            message,
            None,
            sampling_rate,
            tts_model,
            voice_samples,
            conditioning_latents,
            CONFIG["TTS_MODEL"],
            CONFIG.get("VOICE_SAMPLE_COQUI"),
            uni_chr_re
        )
        # Wait for audio to finish
        time.sleep(len(message.split()) * 0.3)  # Rough estimate of speech duration
    except Exception as e:
        print(f"TTS playback failed: {e}")
        print("Full error context:", e.__class__.__name__)
        import traceback
        traceback.print_exc()

def check_generation_complete(page):
    """Check if message generation is complete"""
    # First check if the stop button is still visible
    stop_button = page.locator(".mes_stop")
    if stop_button.is_visible():
        print("Generation still in progress...")
        return False
        
    # Then verify we're looking at the last message
    last_message = page.locator(".mes").last
    if not last_message.is_visible():
        print("Waiting for message to appear...")
        return False
        
    # Make sure it's not a user message by checking the is_user attribute
    if last_message.get_attribute("is_user") == "true":
        print("Last message is from user, waiting for response...")
        return False
        
    # Check if the message has content
    message_text = last_message.locator(".mes_text p")
    has_content = message_text.count() > 0
    if has_content:
        print("Response received!")
    return has_content

def get_last_message(page):
    """Get the last message from the chat"""
    try:
        # Get the last message that isn't from the user
        last_message = page.locator(".mes").last
        # Get all paragraph elements from the message
        paragraphs = last_message.locator(".mes_text p").all()
        # Combine all paragraphs with newlines between them
        return "\n".join(p.inner_text() for p in paragraphs)
    except Exception as e:
        print(f"Error getting message from SillyTavern: {e}")
        return ""

def main():
    print("Starting enhanced test script...")
    
    with sync_playwright() as p:
        print("Launching browser...")
        browser = p.firefox.launch(headless=False)
        page = browser.new_page()
        
        print("Navigating to SillyTavern...")
        page.goto("http://127.0.0.1:8000/")
        
        print("Waiting for chat interface...")
        page.wait_for_load_state("networkidle")
        
        print("Press Enter to record your voice message or to begin writing your text message (or type 'quit' to exit)...")
        while True:
            user_input = input()
            if user_input.lower() == 'quit':
                break
                
            # Get speech input
            message = get_speech_input()
            if not message:
                continue
                
            # Send message
            print(f"Sending message: {message}")
            if message == "empty":
                page.fill("#send_textarea", "")
            else:
                page.fill("#send_textarea", message)
            page.locator("#send_but").click()       # New, more reliable method
            page.wait_for_selector(".mes_stop", state="visible") #so that it doesn't see the generate button before it is clicked
            print("Stop button seen !")
            
            # Wait for generation to complete
            print("Waiting for generation to complete...")
            while not check_generation_complete(page):
                time.sleep(0.1)  # Small delay to prevent CPU overuse
            
            # Get the response
            response = get_last_message(page)
            print(f"Response received: {response}")
            
            # Process actions
            action = process_with_actions(message)
            print(f"Detected action: {action}")
            
            # Play TTS
            play_tts_response(response)
        
        print("Closing browser...")
        browser.close()

if __name__ == "__main__":
    main()
