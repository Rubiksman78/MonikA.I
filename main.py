import os
os.environ["COQUI_TOS_AGREED"] = "1"
import re
import subprocess
import torch
import yaml
import numpy as np
import time
import warnings

from playwright.sync_api import sync_playwright
from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread

from scripts.login_screen import CONFIG
from scripts.utils import HiddenPrints

# --- CONFIGURATION ---
GAME_PATH = CONFIG["GAME_PATH"]
WEBUI_PATH = CONFIG["WEBUI_PATH"]
ST_PATH = CONFIG.get("ST_PATH", "")
BACKEND_TYPE = CONFIG.get("BACKEND_TYPE", "Text-gen-webui")
USE_TTS = CONFIG["USE_TTS"]
LAUNCH_YOURSELF = CONFIG["LAUNCH_YOURSELF"]
LAUNCH_YOURSELF_WEBUI = CONFIG["LAUNCH_YOURSELF_WEBUI"]
LAUNCH_YOURSELF_ST = CONFIG.get("LAUNCH_YOURSELF_ST", False)
USE_ACTIONS = CONFIG["USE_ACTIONS"]
USE_EMOTIONS = CONFIG.get("USE_EMOTIONS", True) # Added emotion flag
TTS_MODEL = CONFIG["TTS_MODEL"]
USE_SPEECH_RECOGNITION = CONFIG["USE_SPEECH_RECOGNITION"]
VOICE_SAMPLE_COQUI = CONFIG["VOICE_SAMPLE_COQUI"]
VOICE_SAMPLE_TORTOISE = CONFIG["VOICE_SAMPLE_TORTOISE"]

warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=FutureWarning)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

uni_chr_re = re.compile(r'\\u[0-9a-fA-F]{4}')

# --- UNIFIED CLASSIFIER INITIALIZATION ---
classifier = None
if USE_ACTIONS or USE_EMOTIONS:
    try:
        from transformers import pipeline
        print("Initializing action/emotion classifier: 'tasksource/deberta-small-long-nli'...")
        # This single classifier will be used for both tasks.
        classifier = pipeline(
            "zero-shot-classification",
            model="tasksource/deberta-small-long-nli",
            device=device
        )
        #print("Classifier initialized successfully.")
    except Exception as e:
        print(f"FATAL: Failed to initialize classifier model: {e}")
        print(f"Actions and emotions disabled.")
        # Disable both features if the model fails to load.
        USE_ACTIONS = False
        USE_EMOTIONS = False
        classifier = None

# Initialize Action Classification if enabled
if USE_ACTIONS and classifier:
    #print("Action classification is enabled.")
    action_classifier = classifier
    try:
        with open("actions.yml", "r") as f:
            ACTIONS = yaml.safe_load(f)
        REVERT_ACTION_DICT = {action: key for key, action_list in ACTIONS.items() for action in action_list}
        ALL_ACTIONS = list(REVERT_ACTION_DICT.keys())
        print("Action configuration is enabled.")
    except Exception as e:
        print(f"Failed to initialize action classifier: {e}")
        USE_ACTIONS = False
else:
     print("Action classification is disabled.")

# Initialize Emotion Classification if enabled
if USE_EMOTIONS and classifier:
    emotion_classifier = classifier
    EMOTION_LABELS = ["joy", "anger", "sadness", "surprise", "disgust", "fear", "neutral", "extreme_sadness", "smug"]
    print("Emotion classification is enabled.")
else:
    print("Emotion classification is disabled.")


# --- TTS MODEL INITIALIZATION ---
with HiddenPrints():
    if USE_TTS:
        print(f"Initializing TTS model: {TTS_MODEL}...")
        from scripts.play_tts import play_TTS, initialize_xtts
        if TTS_MODEL == "Your TTS":
            from scripts.tts_api import my_TTS
            tts_model = my_TTS(model_name="tts_models/multilingual/multi-dataset/your_tts")
            sampling_rate = 16000
            voice_samples = None
            conditioning_latents = None
        elif TTS_MODEL == "XTTS":
            tts_model = initialize_xtts()
            sampling_rate = 24000
            voice_samples = None
            conditioning_latents = None
        elif TTS_MODEL == "Tortoise TTS":
            if device.type == "cuda":
                from tortoise.api_fast import TextToSpeech, MODELS_DIR
            else:
                from tortoise.api import TextToSpeech, MODELS_DIR
            from tortoise.utils.audio import load_voices
            from voicefixer import VoiceFixer
            tts_model = TextToSpeech(
                    models_dir=MODELS_DIR,
                    kv_cache=True,
                )
            voice_samples, conditioning_latents = load_voices([VOICE_SAMPLE_TORTOISE], ["tortoise_audios"])
            vfixer = VoiceFixer()
            sampling_rate = 24000
        print("TTS model initialized successfully")
    else:
        print("No TTS model selected")


# --- SPEECH RECOGNITION MODEL INITIALIZATION ---
if USE_SPEECH_RECOGNITION:
    try:
        import torch
        import speech_recognition as sr
        import whisper
        import pyaudio
        print("Initializing speech recognition...")

        english = True

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
        USE_SPEECH_RECOGNITION = False

# --- HELPER FUNCTIONS ---
def split_text_like_renpy(text):
    """
    Splits text into chunks to simulate Ren'Py dialogue boxes.
    We do this here to assign one emotion per dialogue box. Couldn't be done with Ren'py-side processing.
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

# --- BACKEND INTERACTION ---
def launch_backend():
    global WEBUI_PATH
    global ST_PATH
    if BACKEND_TYPE == "Text-gen-webui":
        WEBUI_PATH = WEBUI_PATH.replace("\\", "/")
        if not LAUNCH_YOURSELF_WEBUI:
            subprocess.Popen(WEBUI_PATH)
        else:
            print("Please launch text-generation_webui manually.")
            print("Don't forget to have a model loaded and be on the right character card")
            print("Press enter to continue.")
            input()
    else:  # SillyTavern
        st_path_normalized = ST_PATH.replace("\\", "/")
        if not LAUNCH_YOURSELF_ST:
            subprocess.Popen(st_path_normalized)
        else:
            print("Please launch SillyTavern manually.") 
            print("Make sure to have, in another ST instance, pressed the 'Auto-connect to Last Server' button in the API (plug) menu and 'Auto-load last chat' in the user parameters (man with cog) menu")
            print("Press enter to continue.")
            input()

launch_backend()

def launch(context):
    print("Launching new browser page...")
    page = context.new_page()
    
    if BACKEND_TYPE == "Text-gen-webui": #Change your TGW url here if you have a non-default one
        page.goto("http://127.0.0.1:7860")
        page.wait_for_selector("[class='svelte-1f354aw pretty_scrollbar']", timeout=60000)
        time.sleep(1)
    else:  # SillyTavern, change your URL here if you have a non-default one
        page.goto("http://127.0.0.1:8000") 
        page.wait_for_load_state("networkidle", timeout=60000)
    
    print("Page loaded successfully")
    context.storage_state(path="storage.json")
    return page

def post_message(page, message):
    if BACKEND_TYPE == "Text-gen-webui":
        if message == "QUIT":
            page.fill("[class='svelte-1f354aw pretty_scrollbar']", "I'll be right back")
        else:
            page.fill("[class='svelte-1f354aw pretty_scrollbar']", message)
        time.sleep(0.2)
        page.click('[id="Generate"]')
        page.wait_for_selector('[id="stop"]')
    else:  # SillyTavern
        if message == "QUIT":
            page.fill("#send_textarea", "I'll be right back")
        else:
            page.fill("#send_textarea", message)
        page.locator("#send_but").click()
        try:
            page.wait_for_selector(".mes_stop", state="visible", timeout=5000)
        except Exception:
            print("Warning: Stop button did not appear instantly.")


def check_generation_complete(page):
    """Check if message generation is complete in SillyTavern."""
    if BACKEND_TYPE == "Text-gen-webui":
        stop_buttons = page.locator('[id="stop"]').all()
        return not any(button.is_visible() for button in stop_buttons)
    else: # SillyTavern - should do the same, slightly more robust I think. It's what the test script does and it works.
        stop_button = page.locator(".mes_stop")
        if stop_button.is_visible():
            return False
        last_message = page.locator(".mes").last
        if last_message.get_attribute("is_user") == "true":
            return False
        if last_message.locator(".mes_text p").count() > 0:
            return True
        return False

def get_last_message(page):
    """Get the last message from the chat, handling multiple paragraphs."""
    if BACKEND_TYPE == "Text-gen-webui":
        user = page.locator('[class="message-body"]').locator("nth=-1")
        return user.inner_html()
    else:  # SillyTavern. try-except for error tracking purposes.
        try:
            paragraphs = page.locator(".mes.last_mes .mes_text p").all()
            return "\n".join(p.inner_text() for p in paragraphs)
        except Exception as e:
            print(f"Error getting message from SillyTavern: {e}")
            return ""

# --- MAIN SERVER LOGIC ---
clients = {}
addresses = {}
HOST = '127.0.0.1'
PORT = 12346
BUFSIZE = 8096
ADDRESS = (HOST, PORT)
SERVER = socket(AF_INET, SOCK_STREAM)
SERVER.bind(ADDRESS)
queued = False
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

# Launch the game
if not LAUNCH_YOURSELF:
    subprocess.Popen(GAME_PATH+'/DDLC.exe')

def listen():
    print("Waiting for connection...")
    while True:
        client, client_address = SERVER.accept()
        print("%s:%s has connected." % client_address)
        addresses[client] = client_address
        Thread(target=call, args=(client,)).start()

def call(client):
    thread = Thread(target=listenToClient, args=(client,), daemon=True)
    thread.start()

def sendMessage(msg, name=""):
    """ send message to all users present in
    the chat room"""
    for client in clients:
        client.send(bytes(name, "utf8") + msg)

def send_answer(received_msg, processed_message):
    """
    Processes actions and sends the final payload to the game.
    The processed_message contains either the raw text or the text with emotion tags.
    """
    if received_msg != "" and USE_ACTIONS and action_classifier:
        sequence_to_classify = f"The player is speaking with Monika, his virtual \
            girlfriend. Now he says: {received_msg}. What is the label of this sentence?"
        result = action_classifier(sequence_to_classify, candidate_labels=ALL_ACTIONS)
        action_to_take = result["labels"][0]
        print("Action: " + action_to_take)
        action_to_take = REVERT_ACTION_DICT[action_to_take]
    else:
        action_to_take = "none"

    # The format is: message_with_emotions/gaction_name
    msg_to_send = processed_message.encode("utf-8") + b"/g" + action_to_take.encode("utf-8")
    sendMessage(msg_to_send)


def listenToClient(client):
    """ Get client username """
    name = "User"
    clients[client] = name
    launched = False
    play_obj = None
    while True:
        try:
            received_msg = client.recv(BUFSIZE).decode("utf-8")
        except:
            print("Connection lost.")
            os._exit(0)
        received_msg = received_msg.split("/m")
        rest_msg = received_msg[1]
        received_msg = received_msg[0]
        if received_msg == "chatbot":
            if '/g' in rest_msg:
                received_msg, step = rest_msg.split("/g")
            else:
                received_msg = client.recv(BUFSIZE).decode("utf-8")
                received_msg, step = received_msg.split("/g")
            step = int(step)
            if received_msg == "begin_record":
                if USE_SPEECH_RECOGNITION:
                    with sr.Microphone(sample_rate=16000) as source:
                        sendMessage("yes".encode("utf-8"))
                        print("Listening... Speak now!")
                        audio = r.listen(source)
                        print("Processing speech...")
                        torch_audio = torch.from_numpy(
                            np.frombuffer(
                                audio.get_raw_data(),
                                np.int16
                            ).flatten().astype(np.float32) / 32768.0)
                        
                        result = audio_model.transcribe(torch_audio, language='english')
                        received_msg = result['text'].strip()
                else:
                    sendMessage("no".encode("utf-8"))
                    continue
            print("User: "+received_msg)

            if not launched:
                pw = sync_playwright().start()
                try:
                    browser = pw.firefox.launch(headless=False)
                    context = browser.new_context()
                    page = launch(context)
                except Exception as e:
                    print(f"Launch failed. Please check if {BACKEND_TYPE} is running. Error: {e}")
                    _ = client.recv(BUFSIZE).decode("utf-8")
                    sendMessage("server_error".encode("utf-8"))
                    launched = False
                    pw.stop()
                    continue
                launched = True
                _ = client.recv(BUFSIZE).decode("utf-8")
                sendMessage("server_ok".encode("utf-8"))
            try:
                post_message(page, received_msg)
            except Exception as e:
                print(f"Error while sending message. Please check if {BACKEND_TYPE} is running: {str(e)}")
                _ = client.recv(BUFSIZE).decode("utf-8")
                sendMessage("server_error".encode("utf-8"))
                launched = False
                pw.stop()
                continue
            
            while True:
                time.sleep(0.2) # Small delay to prevent busy-waiting
                try:
                    if check_generation_complete(page):
                        # --- RESPONSE PROCESSING ---
                        response_text = get_last_message(page)
                        if not response_text:
                            print("Could not retrieve a valid response.")
                            continue

                        # We process text for ren'py here now to add our emotional tags. One per dialogue box.
                        #This is the "raw text" that is sent for TTS and shown, as it's readable.
                        response_text = re.sub(r'<[^>]+>', '', response_text)
                        response_text = os.linesep.join([s for s in response_text.splitlines() if s])
                        response_text = re.sub(' +', ' ', response_text)
                        response_text = re.sub(r'&[^;]+;', '', response_text)
                        response_text = response_text.replace("END", "")
                        
                        print("-" * 50)
                        print(f"Response Received:\n{response_text}") #Remove?
                        print("-" * 50)

                        processed_message_for_game = response_text

                        # --- Process Emotions to create the game payload ---
                        if USE_EMOTIONS and classifier:
                            message_chunks = split_text_like_renpy(response_text)
                            analyzed_chunks = []
                            for chunk in message_chunks:
                                if not chunk.strip(): continue
                                classification = emotion_classifier(chunk, candidate_labels=EMOTION_LABELS)
                                detected_emotion = classification["labels"][0]
                                analyzed_chunks.append(f"{chunk}|||{detected_emotion}")

                            # This is the final string that will be sent to the game. It has emotional tags every 180 characters max.
                            final_payload = "&&&".join(analyzed_chunks)
                            processed_message_for_game = final_payload
                            
                            #print("\n--- FINAL GAME PAYLOAD (EMOTIONS) ---")
                            #print(final_payload)
                            #print("-------------------------------------\n")
                        #else:
                             #print("\n--- Emotion processing disabled. Skipping payload generation. ---\n")

                        if received_msg != "QUIT":
                            # --- TTS (uses the clean text) ---
                            if USE_TTS:
                                print("--- TTS is processing... ---")
                                play_obj = play_TTS(
                                    step,
                                    response_text,
                                    play_obj,
                                    sampling_rate,
                                    tts_model,
                                    voice_samples,
                                    conditioning_latents,
                                    TTS_MODEL,
                                    VOICE_SAMPLE_COQUI,
                                    uni_chr_re)
                            
                            # --- Send final payload to game ---
                            #print("Sent: " + processed_message_for_game)
                            send_answer(received_msg, processed_message_for_game)
                        break
                except Exception as e:
                    print(f"Error checking generation status or processing response: {e}")
                    import traceback
                    traceback.print_exc()
                    launched = False
                    pw.stop()
                    break

if __name__ == "__main__":
    SERVER.listen(5)
    ACCEPT_THREAD = Thread(target=listen)
    ACCEPT_THREAD.start()
    ACCEPT_THREAD.join()
    SERVER.close()
