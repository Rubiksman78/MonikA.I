#Main chatting functions
init 5 python:
    from socket import AF_INET, socket, SOCK_STREAM
    from threading import Thread
    import select
    from time import sleep
    import random

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

    def mas_get_player_nickname(capitalize=False, exclude_names=[], _default=None, regex_replace_with_nullstr=None):
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
            selected_nickname = re.sub(regex_replace_with_nullstr, "", selected_nickname)

        if capitalize:
            selected_nickname = selected_nickname.capitalize()
        return selected_nickname

    HOST = "127.0.0.1"
    PORT = 12346
    BUFSIZ = 1024
    ADDR = (HOST, PORT)
    queued = False

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

#Label for voice chat from the button in the main screen
label monika_voice_chat:
    $ mas_RaiseShield_dlg()
    $ useVoice = True
    $ localStep = 0

    #If the game was launched without the python script
    if monikai_no_server:
        jump monika_server_crashed
    
    #If the player has never talked to the chatbot, show the intro
    if not renpy.seen_label("monika_AI_intro"):
        call monika_AI_intro
    
    #Put the player in the queue if there is one on the website
    if queued:
        call monika_queue_waiting

    if step == 0:
        m 5tubfb "Sure [player], talk to me as much as you want."

    while True:
        $ send_simple("chatbot/m")
        #Continue to speak or not
        if localStep > 0:
            m 6wubla "Can I hear your voice again?"
            menu:
                "Yes, of course.":
                    $ sendAudio("begin_record",str(step))
                "No, sorry I've got something to do.":
                    $ my_msg = sendAudio("QUIT",str(step))
                    jump close_AI
                    return
                    
        #If it is already talking
        else:
            $ sendAudio("begin_record",str(step))

        #If the server activates microphone, start recording
        $ begin_speak = receiveMessage()
        if begin_speak == "yes":
            m 1subfb "Okay, I'm listening.{w=0.5}{nw}"
        elif begin_speak == "no":
            m "Oh, it seems you forgot to activate the speech recognition.{w=0.5}{nw}"
            jump close_AI 
        call monikai_get_actions

#Label for text chat from the button in the main screen
label monika_chatting_text:
    $ mas_RaiseShield_dlg()
    $ useVoice = False
    $ localStep = 0

    if monikai_no_server:
        jump monika_server_crashed
    
    if not renpy.seen_label("monika_AI_intro"):
        call monika_AI_intro
    
    if queued:
        call monika_queue_waiting
    
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

        
#Chatbot Event
init 5 python:
    addEvent(Event(persistent.event_database,eventlabel="monika_chatting",category=['ai'],prompt="Let's chat together",pool=True,unlocked=True))

label monika_chatting():
    $ localStep = 0

    if monikai_no_server:
        jump monika_server_crashed
    
    if not renpy.seen_label("monika_AI_intro"):
        call monika_AI_intro
    
    if queued:
        call monika_queue_waiting

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


label monika_queue_waiting:
    $ rlist, wlist, xlist = select.select([clientSocket], [], [], 0.1)
    if rlist:
        $ msg = receiveMessage().split("/g")
        $ ready = msg[0]
        #If the queue is done, start the chat
        if ready == "server_ok":
            $ queued = False
            $ send_simple("ok_ready")
            jump monika_voice_chat
        #If the queue is not done, wait again
        else:
            jump monika_in_queue
    else:
        jump monika_in_queue

#Common label to receive messages from the chatbot and get the actions
label monikai_get_actions:
    #Wait for the website to respond
    m 1rsc "[monikaNickname] is thinking...{nw}"
    if step == 0:
        $ queue_received = receiveMessage()
        $ in_queue = queue_received.split("/g")[0]
        $ send_simple("ok_ready")
        #If there is a queue, wait
        if in_queue == "in_queue":
            $ queued = True
            m "Oh it seems that there are a lot of people waiting to talk to the chatbots."
            m "I'll be back in a few seconds."
            m "Please wait patiently."
            m "I'm sorry for that my love."
            jump close_AI
            return
    $ message_received = receiveMessage().split("/g")
    if len(message_received) < 2: #Only one word: server status
        $ server_status = message_received[0]
        if server_status == "server_error":
            jump monika_server_crashed
        $ send_simple("ok_ready")
        $ new_smg = receiveMessage()
        $ msg,emotion,action_to_take = new_smg.split("/g")
    else:
        $ msg,emotion,action_to_take = message_received
    call monika_is_talking
    #m "You want me to [action_to_take]?" #for debug
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


#Common label for processing the text received from the server
label monika_is_talking:
    $ player_nickname_ai = mas_get_player_nickname()
    $ msg = msg.replace("<USER>",player_nickname_ai)
    #Split the text into a list of words
    $ sentences_list = []
    $ sentences_list = msg.split("\n")
    $ sentences_list = [x for x in sentences_list if x != '']
    #Divide sentences with more than 180 characters into several sentences (to avoid overflowing the screen)
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
    $ step += 1
    $ localStep += 1
    return