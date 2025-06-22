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
#Debug mode
DEBUG = False
def log(x)
    if DEBUG = True
        print x
        
#File config
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
# Initialize the model only if actions or emotions are enabled.
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
        print("Classifier initialized successfully.")
    except Exception as e:
        print(f"FATAL: Failed to initialize classifier model: {e}")
        # Disable both features if the model fails to load.
        USE_ACTIONS = False
        USE_EMOTIONS = False
        classifier = None

# Initialize Action Classification if enabled
if USE_ACTIONS and classifier:
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
        USE_ACTIONS = False
else:
     print("Action classification is disabled.")

# Initialize Emotion Classification if enabled
if USE_EMOTIONS and classifier:
    emotion_classifier = classifier
    EMOTION_LABELS = [
    "triumphant",
    "smug",
    "teasing",
    "outraged",
    "annoyed",
    "pouty",
    "ecstatic",
    "happy",
    "passionate",
    "flirtatious",
    "affectionate",
    "revolted",
    "disgusted",
    "displeased",
    "terrified",
    "afraid",
    "anxious",
    "devastated",
    "saddened",
    "disappointed",
    "shocked",
    "surprised",
    "startled",
    "neutral"
    ]
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
    Each sentence gets its own dialogue box. If a sentence is too long, split it
    """
    final_chunks = []
    paragraphs = [p.strip() for p in text.split('\n') if p.strip()]
    for paragraph in paragraphs:
        sentences = re.split(r'(?<=[.!?])\s+', paragraph)
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            if len(sentence) <= 180:
                final_chunks.append(sentence)
            else:
                #Sentence too long, split it.
                words = sentence.split(' ')
                temp_chunk = ""
                for word in words:
                    if len(temp_chunk) + len(word) + 1 > 180:
                        final_chunks.append(temp_chunk.strip())
                        temp_chunk = word
                    else:
                        if temp_chunk:
                            temp_chunk += " " + word
                        else:
                            temp_chunk = word
                if temp_chunk.strip():
                    final_chunks.append(temp_chunk.strip())
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
            print("Press enter to continue.")
            input()
    else:  # SillyTavern
        st_path_normalized = ST_PATH.replace("\\", "/")
        if not LAUNCH_YOURSELF_ST:
            subprocess.Popen(st_path_normalized)
        else:
            print("Please launch SillyTavern manually.")
            print("Press enter to continue.")
            input()

launch_backend()

def launch(context):
    log("[DEBUG] Launching new browser page...")
    page = context.new_page()
    
    if BACKEND_TYPE == "Text-gen-webui":
        page.goto("http://127.0.0.1:7860")
        page.wait_for_selector("[class='svelte-1f354aw pretty_scrollbar']", timeout=60000)
        time.sleep(1)
    else:  # SillyTavern
        # The URL from your test script is used here.
        page.goto("http://127.0.0.1:8000/") 
        page.wait_for_load_state("networkidle", timeout=60000)
    
    log("[DEBUG] Page loaded successfully")
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
    else: # SillyTavern - updated logic from test script
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
    else:  # SillyTavern - updated logic from test script
        try:
            last_message = page.locator(".mes").last
            paragraphs = last_message.locator(".mes_text p").all()
            return "\n".join(p.inner_text() for p in paragraphs)
        except Exception as e:
            print(f"Error getting message from SillyTavern: {e}")
            return ""

# --- MAIN SERVER LOGIC ---
clients = {}
addresses = {}
HOST = '127.0.0.1'
PORT = 12346
BUFSIZE = 1024
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
    log("[DEBUG] New listener thread started for a client.")
    name = "User"
    clients[client] = name
    launched = False
    play_obj = None

    while True:
        log("\n[DEBUG] --- Top of main loop. Waiting for new message from client. ---")
        try:
            raw_data = client.recv(BUFSIZE).decode("utf-8")
            log(f"[DEBUG] Raw data received from client: \"{raw_data}\"")
        except Exception as e:
            log(f"[DEBUG] Connection lost. Error: {e}")
            os._exit(0)

        # Splitting the initial "chatbot/m" identifier
        message_parts = raw_data.split("/m", 1)
        received_msg = message_parts[0]
        rest_msg = message_parts[1] if len(message_parts) > 1 else ""
        log(f"[DEBUG] After splitting '/m': received_msg is \"{received_msg}\", rest_msg is \"{rest_msg}\"")


        if received_msg == "chatbot":
            log("[DEBUG] 'chatbot' identifier found. Entering chatbot logic.")
            main_message_body = rest_msg
            
            # This loop ensures we get the part of the message with the user input
            log("[DEBUG] Entering loop to find the main message containing '/g'.")
            while "/g" not in main_message_body:
                log(f"[DEBUG] Current message part \"{main_message_body}\" does not contain '/g'. Waiting for next part.")
                try:
                    main_message_body = client.recv(BUFSIZE).decode("utf-8")
                    log(f"[DEBUG] Received next message part: \"{main_message_body}\"")
                except Exception as e:
                    log(f"[DEBUG] Connection lost while waiting for '/g' part. Error: {e}")
                    os._exit(0)
            
            log("[DEBUG] Found message part with '/g'. Exiting loop.")

            # Splitting the user message from the step count
            user_input, step_str = main_message_body.split("/g", 1)
            log(f"[DEBUG] After splitting '/g': user_input is \"{user_input}\", step_str is \"{step_str}\"")

            # Safely extracting the step number
            numeric_step = "".join(filter(str.isdigit, step_str))
            log(f"[DEBUG] Extracted numeric digits for step: \"{numeric_step}\"")
            
            step = int(numeric_step) if numeric_step else 0
            log(f"[DEBUG] Final step value is: {step}")

            # --- SPEECH-TO-TEXT (STT) LOGIC ---
            if user_input == "begin_record":
                log("[DEBUG] 'begin_record' command received. Initializing STT.")
                if USE_SPEECH_RECOGNITION:
                    with sr.Microphone(sample_rate=16000) as source:
                        log("[DEBUG] Sending 'yes' to client to confirm microphone is ready.")
                        sendMessage("yes".encode("utf-8"))
                        log("[DEBUG] Listening for speech...")
                        audio = r.listen(source)
                        print("Processing speech...")
                        torch_audio = torch.from_numpy(
                            np.frombuffer(
                                audio.get_raw_data(),
                                np.int16
                            ).flatten().astype(np.float32) / 32768.0)
                        
                        result = audio_model.transcribe(torch_audio, language='english')
                        user_input = result['text'].strip()
                else:
                    log("[DEBUG] STT is disabled in config. Sending 'no' to client.")
                    sendMessage("no".encode("utf-8"))
                    continue # Skip this turn if STT is disabled but was requested
            print("User: "+user_input)
            
            # This part handles the initial browser launch if needed
            if not launched:
                log("[DEBUG] Browser not launched yet. Attempting to launch.")
                pw = sync_playwright().start()
                try:
                    browser = pw.firefox.launch(headless=False)
                    context = browser.new_context()
                    page = launch(context)
                except Exception as e:
                    print(f"FATAL: Browser launch failed. Error: {e}")
                    sendMessage("server_error".encode("utf-8"))
                    launched = False
                    pw.stop()
                    continue
                launched = True
                log("[DEBUG] Browser launched successfully.")
                
                # This block now safely absorbs the optional 'ok_ready' without freezing.
                print("[DEBUG] Setting socket to non-blocking to safely absorb optional pings")
                client.setblocking(False)
                try:
                    client.recv(BUFSIZE)
                    log("[DEBUG] Absorbed an optional message.")
                except BlockingIOError:
                    log("[DEBUG] No optional message was waiting to be absorbed. Continuing normally.")
                    pass
                except Exception as e:
                    log(f"[DEBUG] An unexpected error occurred while absorbing message: {e}")
                    pass
                log("[DEBUG] Setting socket back to blocking mode for normal operation.")
                client.setblocking(True) # IMPORTANT: Return to blocking mode

            # Sending the message to the AI frontend
            try:
                log(f"Sending to AI: \"{user_input}\"")
                post_message(page, user_input)
            except Exception as e:
                log(f"[DEBUG] FATAL: Error while sending message to AI. Error: {e}")
                sendMessage("server_error".encode("utf-8"))
                launched = False
                pw.stop()
                continue
            
            # Waiting for the AI to finish generating a response
            log("[DEBUG] Waiting for AI response generation to complete...")
            while True:
                time.sleep(0.2)
                try:
                    if check_generation_complete(page):
                        log("[DEBUG] AI generation is complete.")
                        # --- RESPONSE PROCESSING ---
                        response_text = get_last_message(page)
                        log(f"[DEBUG] Raw response from AI: \"{response_text}\"")

                        if not response_text:
                            log("[DEBUG] WARNING: AI response was empty. Skipping.")
                            continue

                        # Clean up the raw text
                        response_text = re.sub(r'<[^>]+>', '', response_text)
                        response_text = os.linesep.join([s for s in response_text.splitlines() if s])
                        response_text = re.sub(' +', ' ', response_text)
                        response_text = re.sub(r'&[^;]+;', '', response_text)
                        response_text = response_text.replace("END", "")
                        log(f"[DEBUG] Cleaned response text: \"{response_text}\"")
                        
                        processed_message_for_game = response_text

                        # --- Process Emotions ---
                        if USE_EMOTIONS and classifier:
                            print(f"Processing emotions...")
                            message_chunks = split_text_like_renpy(response_text)
                            analyzed_chunks = []
                            for chunk in message_chunks:
                                if not chunk.strip(): continue
                                classification = emotion_classifier(chunk, candidate_labels=EMOTION_LABELS)
                                detected_emotion = classification["labels"][0]
                                analyzed_chunks.append(f"{chunk}|||{detected_emotion}")

                            # This is the final string that will be sent to the game
                            final_payload = "&&&".join(analyzed_chunks)
                            processed_message_for_game = final_payload
                            
                            log("[DEBUG] \n--- FINAL GAME PAYLOAD (EMOTIONS) ---")
                            print(final_payload)
                            log("-------------------------------------\n")
                        else:
                            log("\n--- Emotion processing disabled. Skipping payload generation. ---\n")
                        
                        # --- Send final payload to game ---
                        if user_input != "QUIT":
                            # --- TEXT-TO-SPEECH (TTS) LOGIC ---
                            if USE_TTS:
                                log("[DEBUG] TTS is enabled. Sending text to TTS function.")
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
                            
                            log(f"[DEBUG] Sending final payload to game.")
                            send_answer(user_input, processed_message_for_game)
                            print(f"TTS sent:" + response_text)
                        
                        # Break out of the "check_generation_complete" loop
                        break 
                except Exception as e:
                    print(f"FATAL: Error during AI response processing. Error: {e}")
                    import traceback
                    traceback.print_exc()
                    launched = False
                    pw.stop()
                    break # Break from the inner loop on error


if __name__ == "__main__":
    SERVER.listen(5)
    ACCEPT_THREAD = Thread(target=listen)
    ACCEPT_THREAD.start()
    ACCEPT_THREAD.join()
    SERVER.close()
