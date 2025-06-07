define emotion_list = [
    "anger",
    "disgust",
    "fear",
    "joy",
    "sadness",
    "surprise",
    "neutral"
]

define negative_emotions = ["anger", "disgust", "fear", "sadness"]
define positive_emotions = ["joy", "surprise"]
define neutral_emotions = ["neutral"]

# Main chatting functions
init 5 python:
    from socket import AF_INET, socket, SOCK_STREAM
    from threading import Thread
    import select
    from time import sleep
    import random

    # NEW: Dictionary to map emotions from the AI to MAS sprite codes.
    # The keys MUST match the EMOTION_LABELS from main.py
    emotion_sprite_map = {
        "joy": "4sub",          # User specified sprite code
        "sadness": "6dsc",        # User specified sprite code
        "anger": "4esd",        # Default from plan
        "surprise": "1esa",       # Default from plan
        "disgust": "4esd",       # Default from plan
        "fear": "2esc",         # Default from plan
        "neutral": "1esc"        # Default from plan
    }
    # A default sprite to use if an unknown emotion is received
    default_sprite = "1esa"


    def receiveMessage():
        msg = clientSocket.recv(BUFSIZ).decode("utf8")
        return msg

    def sendMessage(prefix,step):
        my_msg = renpy.input(prefix)
        clientSocket.send(bytes(my_msg + "/g" + step).encode("utf8"))
        return my_msg

    def sendAudio(prefix,step):
        clientSocket.send(bytes(prefix + "/g" + step).encode("utf8"))

    def send_simple(prefix):
        clientSocket.send(bytes(prefix).encode("utf8"))

    def audio_file_exists(filename):
        return os.path.isfile(filename)

    def AIButton():
        if not AIVisible():
            config.overlay_screens.append("monika_chatbot_button")

    def AIVisible():
        return "monika_chatbot_button" in config.overlay_screens

    def AIVoiceButton():
        if not AIVoiceVisible():
            config.overlay_screens.append("monika_voicechat_button")

    def AIVoiceVisible():
        return "monika_voicechat_button" in config.overlay_screens

    def mas_get_player_nickname(
        capitalize=False,
        exclude_names=[],
        _default=None,
        regex_replace_with_nullstr=None
    ):
        if _default is None:
            _default = player

        if mas_isMoniHappy(lower=True) or not persistent._mas_player_nicknames:
            return _default

        nickname_pool = persistent._mas_player_nicknames + [player]

        if exclude_names:
            nickname_pool = [
                nickname
                for nickname in nickname_pool
                if nickname not in exclude_names
            ]

            if not nickname_pool:
                return _default

        selected_nickname = random.choice(nickname_pool)

        if regex_replace_with_nullstr is not None:
            selected_nickname = re.sub(
                regex_replace_with_nullstr,
                "",
                selected_nickname
            )

        if capitalize:
            selected_nickname = selected_nickname.capitalize()
        return selected_nickname

    HOST = "127.0.0.1"
    PORT = 12346
    BUFSIZ = 8096
    ADDR = (HOST, PORT)

    try:
        clientSocket = socket(AF_INET, SOCK_STREAM)
        clientSocket.connect(ADDR)
        monikai_no_server = False
    except:
        monikai_no_server = True
    monikaNickname = store.persistent._mas_monika_nickname

    if persistent._show_monikai_buttons == None:
        persistent._show_monikai_buttons = True

    if persistent._use_monikai_actions == None:
        persistent._use_monikai_actions = True

    if persistent._show_monikai_buttons:
        AIButton()
        AIVoiceButton()

define step = 0

# Label for voice chat from the button in the main screen
label monika_voice_chat:
    $ mas_RaiseShield_dlg()
    $ useVoice = True
    $ localStep = 0

    # If the game was launched without the python script
    if monikai_no_server:
        jump monika_server_crashed

    # If the player has never talked to the chatbot, show the intro
    if not renpy.seen_label("monika_AI_intro"):
        call monika_AI_intro

    if step == 0:
        m 5tubfb "Sure [player], talk to me as much as you want."

    while True:
        $ send_simple("chatbot/m")
        # Continue to speak or not
        if localStep > 0:
            m 6wubla "Can I hear your voice again?"
            menu:
                "Yes, of course.":
                    $ sendAudio("begin_record",str(step))
                "No, sorry I've got something to do.":
                    $ my_msg = sendAudio("QUIT",str(step))
                    jump close_AI
                    return

        # If it is already talking
        else:
            $ sendAudio("begin_record",str(step))

        # If the server activates microphone, start recording
        $ begin_speak = receiveMessage()
        if begin_speak == "yes":
            m 1subfb "Okay, I'm listening.{w=0.5}{nw}"
        elif begin_speak == "no":
            m "Oh, it seems you forgot to activate the speech recognition.{w=0.5}{nw}"
            jump close_AI
        call monikai_get_actions

# Label for text chat from the button in the main screen
label monika_chatting_text:
    $ mas_RaiseShield_dlg()
    $ useVoice = False
    $ localStep = 0

    if monikai_no_server:
        jump monika_server_crashed

    if not renpy.seen_label("monika_AI_intro"):
        call monika_AI_intro

    if step == 0:
        m 5tubfb "Sure [player], talk to me as much as you want."
        m 4hubfb "Oh and if you have to do something else, just write 'QUIT'. I'll understand my love."

    while True:
        $ send_simple("chatbot/m")
        $ my_msg = sendMessage("Chat with [monikaNickname]:",str(step))
        if my_msg == "QUIT":
            $ step += 1
            jump close_AI
            return

        call monikai_get_actions


# Chatbot Event
init 5 python:
    addEvent(Event(
        persistent.event_database,
        eventlabel="monika_chatting",
        category=['ai'],
        prompt="Let's chat together",
        pool=True,
        unlocked=True
    ))

label monika_chatting():
    $ localStep = 0

    if monikai_no_server:
        jump monika_server_crashed

    if not renpy.seen_label("monika_AI_intro"):
        call monika_AI_intro

    if step == 0:
        m 5tubfb "Sure [player], talk to me as much as you want."
        m 4hubfb "Oh and if you have to do something else, just write 'QUIT'. I'll understand my love."

    m 4nubfa "Maybe you could allow me to hear your beautiful voice?"
    #Choose to use voice or not
    menu:
        "Sure, I'll allow you to hear my voice.":
            m 1subfb "Thank you [player]!"
            m 1subfb "I'll be waiting for you to say something.{w=0.5}{nw}"
            $ useVoice = True
        "Sorry, my microphone is broken.":
            m 2eua "Oh, that's okay [player]."
            m 2eua "I'll just have to wait for you to type something then.{w=0.5}{nw}"
            $ useVoice = False

    while True:
        $ send_simple("chatbot/m")
        if useVoice:
            if localStep > 0:
                m 6wubla "Can I hear your voice again?"
                menu:
                    "Yes, of course.":
                        $ sendAudio("begin_record",str(step))
                    "No, sorry I've got something to do.":
                        $ my_msg = sendAudio("QUIT",str(step))
                        jump close_AI
                        return
            else:
                $ sendAudio("begin_record",str(step))
        else:
            $ my_msg = sendMessage("Chat with [monikaNickname]:",str(step))
            if my_msg == "QUIT":
                $ step += 1
                jump close_AI
                return

        if useVoice:
            $ begin_speak = receiveMessage()
            if begin_speak == "yes":
                m 1subfb "Okay, I'm listening.{w=0.5}{nw}"
            elif begin_speak == "no":
                m "Oh, it seems you forgot to activate the speech recognition.{w=0.5}{nw}"
                jump close_AI
                return
        call monikai_get_actions

# Common label to receive messages from the chatbot and get the actions
label monikai_get_actions:
    m 1rsc "[monikaNickname] is thinking...{nw}"

    # If this is the first message, tell the server we're ready for the response.
    if step == 0:
        $ send_simple("ok_ready")

    # 1. Receive the message from the server.
    $ message_received = receiveMessage()

    # 2. Check for a server error message first.
    if message_received == "server_error":
        jump monika_server_crashed

    # 3. Split the message into the main payload (msg) and the action.
    $ message_parts = message_received.split("/g")
    $ msg = message_parts[0]
    # Provide a fallback for action_to_take if it's missing
    $ action_to_take = message_parts[1] if len(message_parts) > 1 else "normal_chat"

    # 4. Call the label that handles displaying the dialogue.
    call monika_is_talking

    # 5. Handle the action part of the message.
    if persistent._use_monikai_actions:
        if action_to_take == "compliment":
            call monikai_compliment
        elif action_to_take == "change_clothes":
            call monikai_change_clothes
        elif action_to_take == "change_weather":
            call monikai_change_weather
        elif action_to_take == "go_somewhere":
            call monikai_go_somewhere
        elif action_to_take == "greetings":
            call monikai_greetings
        elif action_to_take == "goodbye":
            $ MASEventList.push("monikai_goodbye")
            call close_AI
        elif action_to_take == "ask_kiss":
            call monikai_ask_kiss
        elif action_to_take == "normal_chat":
            call monikai_normal_chat
        elif action_to_take == "play_game":
            call monikai_play_actions
        elif action_to_take == "be_right_back":
            call monikai_brb
            call close_AI
    return


label monika_is_talking:
    # Replace <USER> placeholder, same as before.
    $ player_nickname_ai = mas_get_player_nickname()
    $ msg = msg.replace("<USER>", player_nickname_ai)

    # Split the payload into a list of dialogues to show.
    $ chunk_pairs = msg.split('&&&')

    # Use a Ren'Py-level 'while' loop to iterate through the dialogues.
    # This is the safest way to loop in old versions of Ren'Py.
    while chunk_pairs:
        python:
            # Take the first dialogue chunk from the list for this iteration.
            current_pair = chunk_pairs.pop(0)

            # Split the chunk into the sentence and its emotion.
            pair_parts = current_pair.split('|||')
            store.current_sentence = pair_parts[0]

            # Store the emotion, with "neutral" as a safe fallback.
            if len(pair_parts) > 1:
                store.current_emotion = pair_parts[1]
            else:
                store.current_emotion = "neutral"

        # This is the "big elif tower" you know works, using the variables
        # we prepared in the python block above. This is 100% safe.
        if store.current_emotion == "joy":
            m 4sub "[current_sentence]"
        elif store.current_emotion == "sadness":
            m 6dsc "[current_sentence]"
        elif store.current_emotion == "anger":
            m 4esd "[current_sentence]"
        elif store.current_emotion == "surprise":
            m 1esa "[current_sentence]"
        elif store.current_emotion == "disgust":
            m 4esd "[current_sentence]"
        elif store.current_emotion == "fear":
            m 2esc "[current_sentence]"
        elif store.current_emotion == "neutral":
            m 1esc "[current_sentence]"
        else:
            # Fallback to the default sprite if the emotion is somehow unknown.
            m 1esa "[current_sentence]"

    # After the loop finishes, return to the calling label.
    return
