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

# --- CONFIGURATION ---
# Set booleans here to enable or disable features during testing.
CONFIG = {
    "USE_TTS": True,
    "USE_ACTIONS": True,
    "USE_EMOTIONS": True, # <-- New flag to control emotion processing
    "USE_SPEECH_RECOGNITION": False,
    "TTS_MODEL": "XTTS",
    "VOICE_SAMPLE_COQUI": "Monika2.wav",
    "VOICE_SAMPLE_TORTOISE": "monika_voice"
}

# --- INITIALIZATION ---
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

# --- UNIFIED CLASSIFIER INITIALIZATION ---
# Initialize the model only if actions or emotions are enabled.
if CONFIG["USE_ACTIONS"] or CONFIG["USE_EMOTIONS"]:
    try:
        from transformers import pipeline
        print("Initializing action/emotion classifier: 'tasksource/deberta-small-long-nli'...")
        # This single classifier will be used for both tasks.
        classifier = pipeline(
            "zero-shot-classification",
            model="tasksource/deberta-small-long-nli",
            device=device
        )
        print("Classifier initialized successfully.")
    except Exception as e:
        print(f"FATAL: Failed to initialize classifier model: {e}")
        # Disable both features if the model fails to load.
        CONFIG["USE_ACTIONS"] = False
        CONFIG["USE_EMOTIONS"] = False
        classifier = None
else:
    classifier = None

# Initialize Action Classification if enabled
if CONFIG["USE_ACTIONS"] and classifier:
    print("Action classification is enabled.")
    action_classifier = classifier
    try:
        with open("actions.yml", "r") as f:
            ACTIONS = yaml.safe_load(f)
        REVERT_ACTION_DICT = {action: key for key, action_list in ACTIONS.items() for action in action_list}
        ALL_ACTIONS = list(REVERT_ACTION_DICT.keys())
        print("Action configuration loaded.")
    except Exception as e:
        print(f"Failed to initialize action classifier: {e}")
        CONFIG["USE_ACTIONS"] = False
else:
     print("Action classification is disabled.")

# Initialize Emotion Classification if enabled
if CONFIG["USE_EMOTIONS"] and classifier:
    emotion_classifier = classifier
    EMOTION_LABELS = ["joy", "anger", "sadness", "surprise", "disgust", "fear", "neutral"]
    print("Emotion classification is enabled.")
else:
    print("Emotion classification is disabled.")


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

def split_text_like_renpy(text):
    """
    Splits text into chunks to simulate Ren'Py dialogue boxes.
    This is essential for assigning emotions to the correct dialogue lines.
    """
    sentences_list = [s.strip() for s in text.split('\n') if s.strip()]
    final_chunks = []
    for sentence in sentences_list:
        if len(sentence) > 180:
            words = sentence.split(' ')
            current_chunk = ""
            for word in words:
                if len(current_chunk) + len(word) + 1 > 180:
                    final_chunks.append(current_chunk.strip())
                    current_chunk = word + " "
                else:
                    current_chunk += word + " "
            if current_chunk.strip():
                final_chunks.append(current_chunk.strip())
        else:
            final_chunks.append(sentence)
    return final_chunks

def process_with_actions(message):
    """Process message through action classifier if enabled"""
    if not CONFIG["USE_ACTIONS"] or not classifier:
        return "none"
    try:
        sequence = f"The player is speaking with Monika, his virtual girlfriend. Now he says: {message}. What is the label of this sentence?"
        result = action_classifier(sequence, candidate_labels=ALL_ACTIONS)
        action = result['labels'][0]
        return REVERT_ACTION_DICT[action]
    except Exception as e:
        print(f"Action classification failed: {e}")
        return "none"

def play_tts_response(message, step=0):
    """Plays TTS for the raw response if enabled."""
    if not CONFIG["USE_TTS"]:
        return
    print(f"--- Sending to TTS: '{message}' ---")
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


# (SillyTavern interaction functions like check_generation_complete and get_last_message remain the same)
def check_generation_complete(page):
    """Check if message generation is complete in SillyTavern."""
    stop_button = page.locator(".mes_stop")
    if stop_button.is_visible():
        print("Generation still in progress (stop button is visible)...")
        return False
    last_message = page.locator(".mes").last
    if last_message.get_attribute("is_user") == "true":
        print("Waiting for character response...")
        return False
    if last_message.locator(".mes_text p").count() > 0:
        print("Character response received.")
        return True
    return False

def get_last_message(page):
    """Get the last message from the chat, handling multiple paragraphs."""
    try:
        last_message = page.locator(".mes").last
        paragraphs = last_message.locator(".mes_text p").all()
        return "\n".join(p.inner_text() for p in paragraphs)
    except Exception as e:
        print(f"Error getting message from SillyTavern: {e}")
        return ""

# --- MAIN TEST FUNCTION ---
def main():
    print("Starting integrated test script for MonikAI...")
    with sync_playwright() as p:
        browser = p.firefox.launch(headless=False)
        page = browser.new_page()
        page.goto("http://127.0.0.1:8000/") # Your SillyTavern URL
        page.wait_for_load_state("networkidle", timeout=60000)

        while True:
            message = get_speech_input()
            if message.lower() == 'quit':
                break
            if not message:
                continue

            print(f"Sending message: '{message}'")
            page.fill("#send_textarea", message)
            page.locator("#send_but").click()

            try:
                page.wait_for_selector(".mes_stop", state="visible", timeout=5000)
            except Exception:
                print("Warning: Stop button did not appear instantly.")

            print("Waiting for generation to finish...")
            timeout_seconds = 60
            start_time = time.time()
            while not check_generation_complete(page):
                if time.time() - start_time > timeout_seconds:
                    print("Error: Timed out waiting for response.")
                    break
                time.sleep(0.2)

            # --- RESPONSE PROCESSING ---
            response_text = get_last_message(page)
            if not response_text:
                print("Could not retrieve a valid response.")
                continue

            print("-" * 50)
            print(f"Raw Response Received:\n{response_text}")
            print("-" * 50)


            # 1. Process Actions
            action = process_with_actions(message)
            print(f"Detected Action: {action}")

            # 2. Process Emotions and create the game payload
            if CONFIG["USE_EMOTIONS"] and classifier:
                message_chunks = split_text_like_renpy(response_text)
                analyzed_chunks = []
                for chunk in message_chunks:
                    if not chunk.strip(): continue
                    classification = emotion_classifier(chunk, candidate_labels=EMOTION_LABELS)
                    detected_emotion = classification["labels"][0]
                    analyzed_chunks.append(f"{chunk}|||{detected_emotion}")

                # This is the final string that would be sent to the game
                final_payload = "&&&".join(analyzed_chunks)
                
                print("\n--- FINAL GAME PAYLOAD (EMOTIONS) ---")
                print(final_payload)
                print("-------------------------------------\n")
            else:
                 print("\n--- Emotion processing disabled. Skipping payload generation. ---\n")
            
            # 3. TTS (uses the clean, raw text)
            play_tts_response(response_text)


        print("Closing browser...")
        browser.close()

if __name__ == "__main__":
    main()
