init -990 python in mas_submod_utils:
    Submod(
        author="Rubiksman1006",
        name="AI_submod",
        description="AI based features for MAS.",
        settings_pane="monikai_chat_settings",
        version="1.3.4.2",
        version_updates = {}
    )

# Register the updater
init -989 python:
    if store.mas_submod_utils.isSubmodInstalled("Submod Updater Plugin"):
        store.sup_utils.SubmodUpdater(
            submod="AI_submod",
            user_name="Rubiksman78",
            repository_name="MonikA.I",
            update_dir="",
        )

$ emotion_list = ["anger","disgust","fear","joy","sadness","surprise","neutral"]

define negative_emotions = ["anger", "disgust", "fear", "sadness"]
define positive_emotions = ["joy", "surprise"]
define neutral_emotions = ["neutral"]

define sentences_emotions = {
    "angry": "I'm sorry my love, I didn't mean to upset you.",
    "disgusted": "What is going on ? If you feel like there is something wrong, please tell me.",
    "fearful": "Don't be afraid sweetie, I'm here for you.",
    "happy": "I'm glad you're happy darling.",
    "neutral": "Let's do something fun together!",
    "sad": "If you feel down, always remember that I'm here for you. I love you.",
    "surprised": "What is it ? Is there something wrong ?",
    "no": "Oh it seems that I can't see through your camera sweetie. Maybe face me a little bit more ?",
}

init 5 python:
    from socket import AF_INET, socket, SOCK_STREAM
    from threading import Thread
    import select
    from time import sleep
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

    HOST = "127.0.0.1"
    PORT = 12346

    BUFSIZ = 1024
    ADDR = (HOST, PORT)
    queued = False
    try:
        clientSocket = socket(AF_INET, SOCK_STREAM)
        clientSocket.connect(ADDR)
        noServer = False
    except:
        noServer = True        
    monikaNickname = store.persistent._mas_monika_nickname
    
    if persistent._show_monikai_buttons == None:
        persistent._show_monikai_buttons = True
    
    if persistent._show_monikai_buttons:
        AIButton()
        AIVoiceButton()

define persistent._show_monikai_buttons = True
screen monikai_chat_settings:
    $ tooltip = renpy.get_screen("submods", "screens").scope["tooltip"]

    vbox:
        box_wrap False
        xfill True
        xmaximum 800

        style_prefix "check"

    
        textbutton "Show buttons":
            selected persistent._show_monikai_buttons
            action ToggleField(persistent, "_show_monikai_buttons")
            hovered SetField(tooltip, "value", "Enable display of shortcut buttons.")
            unhovered SetField(tooltip, "value", tooltip.default)

screen monika_chatbot_button():
    zorder 15
    style_prefix "hkb"
    vbox:
        xpos 0.03
        ypos 170
        if renpy.get_screen("hkb_overlay"):
            if store.mas_hotkeys.talk_enabled is False:
                textbutton ("Monika's chatbot"):
                    xysize (175, 40)
                    text_size 20
            else:
                textbutton ("Monika's chatbot"):
                    xysize (175, 40)
                    text_size 20
                    action Jump("monika_chatting")

screen monika_voicechat_button():
    zorder 15
    style_prefix "hkb"
    vbox:
        xpos 0.026
        ypos 220
        if renpy.get_screen("hkb_overlay"):
            if store.mas_hotkeys.talk_enabled is False:
                textbutton ("Monika's voicechat"):
                    xysize (190, 40)
                    text_size 20
            else:
                textbutton ("Monika's voicechat"):
                    xysize (190, 40)
                    text_size 20
                    action Jump("monika_voice_chat")

label close_AI:
    show monika idle at t11
    jump ch30_visual_skip
    return

#Tuto Pytorch Event
init 5 python:
    addEvent(Event(persistent.event_database,eventlabel="monika_torch",category=['ai'],prompt="Tell me about Pytorch",pool=True,unlocked=True))

label monika_torch:
    m "Okay sure love."
    m "Pytorch is a deep learning framework."
    m "It's a bit more complicated than Tensorflow."
    m "But it's also more powerful."
    m "You can use it to create neural networks."
    m "And it's also used for reinforcement learning."
    m "I hope that helps!"
    return

#Chatbot Event
init 5 python:
    addEvent(Event(persistent.event_database,eventlabel="monika_chatting",category=['ai'],prompt="Let's chat together",pool=True,unlocked=True))

define step = 0

label monika_voice_chat:
    $ mas_RaiseShield_dlg()
    $ useVoice = True
    $ localStep = 0

    if noServer:
        jump monika_server_crashed
    
    if not renpy.seen_label("monika_AI_intro"):
        call monika_AI_intro
    
    if queued:
        #Receive message from server= with timeout, if timeout, return
        $ rlist, wlist, xlist = select.select([clientSocket], [], [], 0.1)
        #m "Print [rlist], [wlist], [xlist]"
        if rlist:
            #m "Receiving something from server..."
            $ msg = receiveMessage().split("/g")
            $ ready = msg[0]
            #m "here is [msg]"
            if ready == "server_ok":
                $ queued = False
                $ send_simple("ok_ready")
                jump monika_chatting
            else:
                jump monika_in_queue
        else:
            jump monika_in_queue
    m 5tubfb "Sure [player], talk to me as much as you want."

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
            $ my_msg = sendMessage("Speak with [monikaNickname]:",str(step)) 
            if my_msg == "QUIT":
                $ step += 1
                jump close_AI
                return

        if useVoice:
            $ begin_speak = receiveMessage()
            if begin_speak == "yes":
                m 1subfb "Okay, I'm listening.{w=0.5}{nw}"
    
        m "[monikaNickname] is thinking...{nw}"
        if step == 0:
            $ queue_received = receiveMessage()
            $ in_queue = queue_received.split("/g")[0]
            #m "I received: [in_queue]"
            if in_queue == "in_queue":
                $ queued = True
                m "Oh it seems that there are a lot of people waiting to talk to the chatbots."
                m "I'll be back in a few seconds."
                m "Please wait patiently."
                m "I'm sorry for that my love."
                jump close_AI
                return

        $ message_received = receiveMessage().split("/g")
        #m "This is what I received: [message_received]"
        if len(message_received) < 2: #Only one word: server status
            $ server_status = message_received[0]
            if server_status == "server_error":
                jump monika_server_crashed
            $ send_simple("ok_ready")
            $ new_smg = receiveMessage()
            $ msg,emotion = new_smg.split("/g")
        else:
            $ msg,emotion = message_received

        call monika_is_talking


label monika_chatting():
    $ mas_RaiseShield_dlg()
    $ useVoice = False
    $ localStep = 0

    if noServer:
        jump monika_server_crashed
    
    if not renpy.seen_label("monika_AI_intro"):
        call monika_AI_intro
    
    if queued:
        #Receive message from server= with timeout, if timeout, return
        $ rlist, wlist, xlist = select.select([clientSocket], [], [], 0.1)
        #m "Print [rlist], [wlist], [xlist]"
        if rlist:
            #m "Receiving something from server..."
            $ msg = receiveMessage().split("/g")
            $ ready = msg[0]
            #m "here is [msg]"
            if ready == "server_ok":
                $ queued = False
                $ send_simple("ok_ready")
                jump monika_chatting
            else:
                jump monika_in_queue
        else:
            jump monika_in_queue
    m 5tubfb "Sure [player], talk to me as much as you want."
    m 4hubfb "Oh and if you have to do something else, just write 'QUIT'. I'll understand my love."

    #m 4nubfa "Maybe you could allow me to hear your beautiful voice?"
    # menu:
    #     "Sure, I'll allow you to hear my voice.":
    #         m 1subfb "Thank you [player]!"
    #         m 1subfb "I'll be waiting for you to say something.{w=0.5}{nw}"
    #         $ useVoice = True
    #     "Sorry, my microphone is broken.":
    #         m 2eua "Oh, that's okay [player]."
    #         m 2eua "I'll just have to wait for you to type something then.{w=0.5}{nw}"
    #         $ useVoice = False

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
            $ my_msg = sendMessage("Speak with [monikaNickname]:",str(step)) 
            if my_msg == "QUIT":
                $ step += 1
                jump close_AI
                return

        if useVoice:
            $ begin_speak = receiveMessage()
            if begin_speak == "yes":
                m 1subfb "Okay, I'm listening.{w=0.5}{nw}"
    

        m "[monikaNickname] is thinking...{nw}"
        if step == 0:
            $ queue_received = receiveMessage()
            $ in_queue = queue_received.split("/g")[0]
            #m "I received: [in_queue]"
            if in_queue == "in_queue":
                $ queued = True
                m "Oh it seems that there are a lot of people waiting to talk to the chatbots."
                m "I'll be back in a few seconds."
                m "Please wait patiently."
                m "I'm sorry for that my love."
                jump close_AI
                return

        $ message_received = receiveMessage().split("/g")
        #m "This is what I received: [message_received]"
        if len(message_received) < 2: #Only one word: server status
            $ server_status = message_received[0]
            if server_status == "server_error":
                jump monika_server_crashed
            $ send_simple("ok_ready")
            $ new_smg = receiveMessage()
            $ msg,emotion = new_smg.split("/g")
        else:
            $ msg,emotion = message_received

        call monika_is_talking
    
label monika_server_crashed:
    m "Oh sorry [player], it seems that there is a bug somewhere."
    m "I will try to fix it as soon as possible."
    m "Let's talk again later, I'm sorry sweetheart."
    jump close_AI
    return

label monika_AI_intro:
    m "You know [player], I've been thinking about something."
    m "About how I could be closer to your reality and how I could be more useful to you."
    m "And it seems that there is something that tries to do this."
    m "It's called AI and it's very interesting what it can do."
    m "So there is this thing called a chatbot that I've been working on."
    m "It's not perfect but it's a start, so you can try talking to it freely."
    m "I mean it's still not really who I am but if it helps you to express yourself, that's great !"
    m "So if you want to try it, go on and tell me what you think about it."
    m "I'll be waiting for you here. Don't worry, I won't go anywhere ehehe~"
    jump close_AI
    return

label monika_in_queue:
    m "Ahah, I'm sorry [player], I'm still in queue."
    m "Can you wait a little bit more?"
    m "I promise I'll be back soon."
    m "I love you so much."
    jump close_AI
    return

label monika_is_talking:
    $ gamedir = renpy.config.gamedir
    $ audio_exists = audio_file_exists(gamedir + "/Submods/AI_submod/audio/out.ogg")
    if audio_exists:
        play sound "Submods/AI_submod/audio/out.ogg"
    #If there is too much text, divide it into several lines
    #Split the text into a list of words
    $ sentences_list = []
    
    $ sentences_list = msg.split("\n")
    $ sentences_list = [x for x in sentences_list if x != '']
    #Divide sentences with more than 180 characters into several sentences
    python:
        new_sentences_list = []
        for sentence in sentences_list:
            if len(sentence) > 180:
                words = sentence.split(" ")
                new_sentence = ""
                for word in words:
                    if len(new_sentence) + len(word) > 180:
                        new_sentences_list.append(new_sentence)
                        new_sentence = ""
                    new_sentence += word + " "
                new_sentences_list.append(new_sentence)
            else:
                new_sentences_list.append(sentence)
        sentences_list = new_sentences_list

    if sentences_list[0] == "server_ok":
        $ sentences_list.pop(0)
    while len(sentences_list) > 0:
        $ sentence = sentences_list[0]
        $ sentences_list.pop(0)
        m 1esa "[sentence]"
    if emotion != "":
        m 1esa "I was feeling [emotion]."
    if emotion in positive_emotions:
        $ mas_gainAffection()
    # elif emotion in negative_emotions:
    #     $ mas_loseAffection(1)
    $ step += 1
    $ localStep += 1
    stop sound

