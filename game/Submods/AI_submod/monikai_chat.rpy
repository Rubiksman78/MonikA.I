define positive = +1
define neutral = 0
define negative = -1

define polarity_strings = {
    "positive":+1,
    "neutral": 0,
    "negative":-1
}

define pose_transitions = {
    "1":["1","2","3","5"],
    "2":["1","2","5","6"],
    "3":["1","3","6","7"],
    "4":["4","6","7"],
    "5":["1","2","5"],
    "6":["2","3","4","6","7"],
    "7":["3","4","6","7"]
}
define pose_restrictions = {
    negative:["2","4","6","7"],
    neutral:["1","2","3","4","5","6","7"],
    positive:["1","3","4","5","7"]
}

define cry_tags = [ # Maybe this is counterintuitive, but NEGATIVE values of the crying level imply more intense crying sprites
    "cry",          # 50.0% chance to decrease crying level, down to -3 ("ts", streaming tears)
    "cry_weak",     # 25.0% chance to decrease crying level, down to -2 ("tu", tearing up)
    "cry_vweak",    # 12.5% chance to decrease crying level, down to -1 ("tp", pooled tears)
    "uncry",        # 50.0% chance to increase crying level, up to 0 (default for positive)
    "uncry_weak",   # 25.0% chance to increase crying level, up to 0 (default for neutral)
    "uncry_vweak",  # 12.5% chance to increase crying level, up to 0 (default for negative)
    "anticry",      # 50.0% chance to increase crying level, up to +3 (creating a buffer against crying)
    "anticry_weak", # 25.0% chance to increase crying level, up to +2 (creating a buffer against crying)
    "anticry_vweak" # 12.5% chance to increase crying level, up to +1 (creating a buffer against crying)
]
define secondary_cry_tags = [
    "cry3",         # Override crying change limit to +-3 ("ts", streaming tears)
    "cry2",         # Override crying change limit to +-2 ("tu", tearing up)
    "cry1"          # Override crying change limit to +-1 ("tp", pooled tears)
]
define blush_tags = [
    "blush_strong",     # 75% chance to increase blush
    "blush",            # 50% chance to increase blush
    "blush_weak",       # 25% chance to increase blush
    "unblush_strong",   # 75% chance to decrease blush (default for negative)
    "unblush",          # 50% chance to decrease blush (default for neutral)
    "unblush_weak"      # 25% chance to decrease blush (default for positive)
]
define blush_codes = {
    (False,False):"",
    (True,False):"bl",
    (False,True):"bs",
    (True,True):"bf"
}
define sweat_tags = [
    "sweat_strong",     # 75% chance to add sweat
    "sweat",            # 50% chance to add sweat
    "sweat_weak",       # 25% chance to add sweat
    "unsweat",          # Will remove sweat
    "unsweat_weak"      # 50% chance to remove sweat (default)
]
define sweat_codes = {
    -1:"sdl",
    0: "",
    +1:"sdr"
}

# Main chatting functions
init 5 python:
    from socket import AF_INET, socket, SOCK_STREAM
    from threading import Thread
    import select
    from time import sleep
    import random

    class monikai_emotion():
        def __init__(self, name, polarity = 0, form = "", tags = []):
            self.name = name
            if polarity in polarity_strings:
                polarity = polarity_strings[polarity]
            self.polarity = polarity
            self.form = form
            self.tags = tags
        def Is(self, attribute):
            return (attribute in self.tags) or (attribute == self.polarity)

    class monikai_emotions():
        def __init__(self):
            self.lpose = "1"
            self.crying = 0
            self.lastcry = ""
            self.blushing = [False, False]
            self.sweating = 0

            self.emotions = {}
            self.polarities = {
                -1 : [],
                0  : [],
                +1 : []}
            self.tags = {}
        def add(self, emotion):
            self.emotions[emotion.name] = emotion
            self.polarities[emotion.polarity].append(emotion.name)
            # Default tags
            if not any(x in blush_tags for x in emotion.tags):
                if emotion.Is(negative):
                    emotion.tags.append("unblush_strong")
                elif emotion.Is(neutral):
                    emotion.tags.append("unblush")
                elif emotion.Is(positive):
                    emotion.tags.append("unblush_weak")
            if not any(x in cry_tags for x in emotion.tags):
                if emotion.Is(positive):
                    emotion.tags.append("uncry_strong")
                elif emotion.Is(neutral):
                    emotion.tags.append("uncry")
                elif emotion.Is(negative):
                    emotion.tags.append("uncry_weak")
            if not any(x in sweat_tags for x in emotion.tags):
                emotion.tags.append("unsweat_weak")
            for tag in emotion.tags:
                if tag in self.tags:
                    self.tags[tag].append(emotion.name)
                else:
                    self.tags[tag] = [emotion.name]
        def pose(self, emotion):
            potential_next_poses = list( set(pose_transitions[self.lpose]) & set(pose_restrictions[ emotion.polarity ]) )
            self.lpose = random.choice(potential_next_poses)
            return self.lpose
        def blush(self, emotion):
            blushing = self.blushing
            p_blush, p_unblush = 0, 0
            
            if emotion.Is("blush_strong"):
                p_blush = 0.75
            elif emotion.Is("blush"):
                p_blush = 0.5
            elif emotion.Is("blush_weak"):
                p_blush = 0.25
            if emotion.Is("unblush_strong"):
                p_unblush = 0.75
            elif emotion.Is("unblush"):
                p_unblush = 0.5
            elif emotion.Is("unblush_weak"):
                p_unblush = 0.25

            blush0 = (blushing[0] + (random.random() < p_blush) - (random.random() < p_unblush)) > 0
            blush1 = (blushing[1] + (random.random() < p_blush**2) - (random.random() < p_unblush**2)) > 0
            blushing = blush0, blush1
            self.blushing = blushing
            return blush_codes[blushing]
        def cry(self, emotion):
            crying = self.crying
            lastcry = self.lastcry
            delta_crying = 0
            # Secondary tags that control strengths of cry changes
            crylevel = 0
            if emotion.Is("cry3"):
                crylevel = 3
            elif emotion.Is("cry2"):
                crylevel = 2
            elif emotion.Is("cry1"):
                crylevel = 1
            # The main cry tags
            surpass = crying > 0
            if emotion.Is("cry"):
                delta_crying -= (crying > -(crylevel or 3)) * (random.random() < 0.5)
            elif emotion.Is("cry_weak"):
                delta_crying -= (crying > -(crylevel or 2)) * (random.random() < 0.25)
            elif emotion.Is("cry_vweak"):
                delta_crying -= (crying > -(crylevel or 1)) * (random.random() < 0.125)
            if emotion.Is("uncry"):
                delta_crying += (crying < 1) * (random.random() < 0.5)
            elif emotion.Is("uncry_weak"):
                delta_crying += (crying < 1) * (random.random() < 0.25)
            elif emotion.Is("uncry_vweak"):
                delta_crying += (crying < 1) * (random.random() < 0.125)
            if emotion.Is("anticry"):
                R = (random.random() < 0.5)
                delta_crying += (crying < (crylevel or 3)) * R
                surpass = surpass or R
            elif emotion.Is("anticry_weak"):
                R = (random.random() < 0.25)
                delta_crying += (crying < (crylevel or 2)) * R
                surpass = surpass or R
            elif emotion.Is("anticry_vweak"):
                R = (random.random() < 0.125)
                delta_crying += (crying < (crylevel or 1)) * R
                surpass = surpass or R
            crying += delta_crying

            if crying > 0 and delta_crying > 0:
                lastcry = ""
            elif crying <= 0 and delta_crying > 0:
                lastcry = "td"
            elif crying == -1 and delta_crying <= 0:
                lastcry = "tp"
            elif crying == -2 and delta_crying <= 0:
                lastcry = "tu"
            elif crying == -3 and delta_crying <= 0:
                lastcry = "ts"
            if crying > 0 and not surpass:
                crying = 0
            self.lastcry = lastcry
            self.crying = crying
            return lastcry
        def sweat(self, emotion):
            if self.sweating == 0 and emotion.Is("sweat_strong"):
                self.sweating = random.choice([-1,+1]) * (random.random() < 0.75)
            elif self.sweating == 0 and emotion.Is("sweat"):
                self.sweating = random.choice([-1,+1]) * (random.random() < 0.5)
            elif self.sweating == 0 and emotion.Is("sweat_weak"):
                self.sweating = random.choice([-1,+1]) * (random.random() < 0.25)
            elif self.sweating != 0 and emotion.Is("unsweat"):
                self.sweating = 0
            elif self.sweating != 0 and emotion.Is("unsweat_weak"):
                self.sweating = random.choice([self.sweating, 0])
            return sweat_codes[self.sweating]
        def express(self, emote = "neutral"):
            emotion = self.emotions[emote]
            #expformat = emotion.form
            #if ":" in expformat:
            #    expformat = random.choice(expformat.split(":"))
            #expformat = expformat.split(";")
            # This bit can be done more clearly (4 lines above) or elegantly/concisely (1 line below). Uncomment only one of these.
            expformat = random.choice(emotion.form.split(":")).split(";")
            result = ""
            for element in expformat:
                if element == "*":
                    result += self.blush(emotion) + self.cry(emotion) + self.sweat(emotion)
                elif "," in element:
                    result += random.choice(element.split(","))
                else:
                    pre_result = random.choice(element)
                    if pre_result == "#":
                        pre_result = self.pose(emotion)
                    elif pre_result in ["1234567"]:
                        self.lpose = pre_result
                    result += pre_result
            return result

    # Here is where I completely changed how the code stores emotions. Instead of a bunch of disparate lists defined at the top,
    #   here, each emotion and everything about it is defined in a single line.
    # First argument of `emoter.add(monikai_emotion())` is simply the name of the emotion.
    # Second argument is either `positive`, `neutral`, or `negative`, which may either be an integer or a string or one of those variables.
    # The third argument is a string describing the possible spritecodes.
    #     Explanation of each symbol that has a special meaning:
    #         If the string contains a :colon: then colons act as separators of different permutation-formats,
    #           allowing some traits to be exclusive of each other within that emotion.
    #         ;Semicolons; in colonless strings or colon-separated substrings separate each individual feature-slot (pose, eyes, eyebrows, mouth).
    #         If a semicolon-separated substring contains a ,comma, then the substring is replaced with a random one of its comma-separated substrings.
    #           Otherwise, it is replaced with a random one of its chars.
    #           This feature was added before I made the *asterisk* stuff, so I highly recommend never using it for fear of bugs
    #         The #octothorpe# represents a random pose within the restrictions between poses, based on their mutual similarity and polarity of the emotion.
    #         The *asterisk* is a special semicolon-separated substring which acts as a substitute for my complex evaluation of blush, cry, and sweat features.
    #           It should be placed between the semicolon-separated substrings representing the eyebrows and the mouth.
    #     Repetition or duplication of the same symbol within a semicolon-separated substring can be used to adjust the probability of that particular state
    #       being used.
    # The fourth argument is a list of tags to be given to the emotion, for how blush, cry, and sweat should change when the emotion is shown.
    #   Explanations of each tag and their affects can be found in the comments by the tag lists themselves near the top of this code
    emoter = monikai_emotions()
    emoter.add(monikai_emotion( "triumphant", positive, "##3##4##7;s;f;*;abu", ["anticry"]))
    emoter.add(monikai_emotion( "smug", positive, "###1;t;f;*;abu", ["anticry_weak"]))
    emoter.add(monikai_emotion( "teasing", positive, "#;kn;s;*;abu", ["anticry_vweak"]))
    emoter.add(monikai_emotion( "outraged", negative, "#;w;f;*;cdox", ["blush_weak"]))
    emoter.add(monikai_emotion( "annoyed", negative, "#;et;f;*;cddx", ["sweat"]))
    emoter.add(monikai_emotion( "pouty", neutral, "#2;gttm;s;*;p", ["sweat"]))
    emoter.add(monikai_emotion( "ecstatic", positive, "#;s;u;*;ab:#6;f;u;*;ab", ["blush", "cry_weak", "cry3"]))
    emoter.add(monikai_emotion( "happy", positive, "##5;h;su;*;ab", ["blush", "anticry_weak"]))
    emoter.add(monikai_emotion( "passionate", positive, "##5;f;s;*;ab", ["blush_strong", "anticry"]))
    emoter.add(monikai_emotion( "flirtatious", positive, "#5;gttmtttt;u;*;abu", ["blush", "anticry_weak"]))
    emoter.add(monikai_emotion( "affectionate", positive, "###5;h;s;*;ab", ["blush_weak", "anticry_vweak"]))
    emoter.add(monikai_emotion( "revolted", negative, "#;w;k;*;cdxp", ["sweat_strong"]))
    emoter.add(monikai_emotion( "disgusted", negative, "#;f;k;*;cdxp", ["sweat"]))
    emoter.add(monikai_emotion( "displeased", negative, "#;t;ut;*;ccddt", ["sweat_weak"]))
    emoter.add(monikai_emotion( "terrified", negative, "#6;ch;k;*;cdox", ["cry", "sweat_weak"]))
    emoter.add(monikai_emotion( "afraid", negative, "##6;wh;k;*;cddx", ["cry_weak", "cry1", "sweat"]))
    emoter.add(monikai_emotion( "anxious", negative, "###6;e;u;*;cddx", ["sweat"]))
    emoter.add(monikai_emotion( "devastated", negative, "#;ed;k;*;cd", ["cry"]))
    emoter.add(monikai_emotion( "saddened", negative, "#;e;k;*;cd", ["cry_weak"]))
    emoter.add(monikai_emotion( "disappointed", negative, "#;e;k;*;ab", ["sweat_weak"]))
    emoter.add(monikai_emotion( "shocked", negative, "#;w;u;*;o", ["sweat_strong"]))
    emoter.add(monikai_emotion( "surprised", negative, "#;w;u;*;bd", ["sweat"]))
    emoter.add(monikai_emotion( "startled", negative, "#;w;u;*;cd", ["sweat_weak"]))
    #emoter.add(monikai_emotion( "neutral", negative, "#;reel;s;*;c:#;e;s;*;a"))
    emoter.add(monikai_emotion( "neutral", neutral, "#;reeleeee;s;*;aaabd"))

    default_sprite = "1esa"


    def receiveMessage():
        msg = clientSocket.recv(BUFSIZ).decode("utf8")
        return msg

    def sendMessage(prefix,step):
        full_msg = []
        last_msg = ""
        while True: # has a "break" in it, so this is not an infinite loop
            if len(full_msg) > 0:
                prefix_alt = " ("+str(len(full_msg)//2+1)+")"
            else:
                prefix_alt = ""
            my_msg = renpy.input(prefix + prefix_alt, default = last_msg)

            if my_msg.endswith("-") and len(full_msg) > 1:
                last_msg = full_msg[-2]
                full_msg.pop()
                full_msg.pop()
            else:
                last_msg = ""
                if my_msg.endswith("++"):
                    full_msg.append(my_msg[:-2])
                    full_msg.append("\n")
                elif my_msg.endswith("+"):
                    full_msg.append(my_msg[:-1])
                    full_msg.append(" ")
                else:
                    full_msg.append(my_msg)
                    break

        my_msg = "".join(full_msg)
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
        if step > 0:
            m 6wubla "Can I hear your voice again?"
            menu:
                "Yes, of course.":
                    $ sendAudio("begin_record",str(step))
                    $ step += 1
                "No, sorry I've got something to do.":
                    $ my_msg = sendAudio("QUIT",str(step))
                    $ step += 1
                    jump close_AI
                    return

        # If it is already talking
        else:
            $ sendAudio("begin_record",str(step))
            $ step += 1

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
        $ step += 1
        if my_msg in ["QUIT", "EXIT", "STOP", "END", "LEAVE"]:
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
            if step > 0:
                m 6wubla "Can I hear your voice again?"
                menu:
                    "Yes, of course.":
                        $ sendAudio("begin_record",str(step))
                        $ step += 1
                    "No, sorry I've got something to do.":
                        $ my_msg = sendAudio("QUIT",str(step))
                        $ step += 1
                        jump close_AI
                        return
            else:
                $ sendAudio("begin_record",str(step))
        else:
            $ my_msg = sendMessage("Chat with [monikaNickname]:",str(step))
            $ step += 1
            if my_msg in ["QUIT", "EXIT", "STOP", "END", "LEAVE"]:
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
    #if step == 0:
        #$ time.sleep(0.1)
        #$ send_simple("ok_ready")

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
        #elif action_to_take == "play_game":    # this occurs WAY to frequently for what it actually does
        #    call monikai_play_actions
        elif action_to_take == "be_right_back":
            call monikai_brb
            call close_AI
    return


label monika_is_talking:
    # Replace <USER> placeholder, same as before.
    $ msg = msg.replace("<USER>", player)

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

            emote = store.current_emotion
            if emote in emoter.emotions.keys():
                renpy.show("monika " + str(emoter.express(emote)))
            else:
                # Fallback to the default sprite if the emotion is somehow unknown.
                renpy.show("monika " + default_sprite)
        m "[current_sentence]"

    # After the loop finishes, return to the calling label.
    return
