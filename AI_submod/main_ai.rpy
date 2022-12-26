init -990 python in mas_submod_utils:
    Submod(
        author="Rubiksman1006",
        name="AI_submod",
        description="AI based features for MAS.",
        version="1.1.1",
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
        msg = client_socket.recv(BUFSIZ).decode("utf8")
        return msg

    def sendMessage(prefix,step):
        my_msg = renpy.input(prefix)
        client_socket.send(bytes(my_msg + "/g" + step).encode("utf8"))
        return my_msg

    def sendAudio(prefix,step):
        client_socket.send(bytes(prefix + "/g" + step).encode("utf8"))

    def send_simple(prefix):
        client_socket.send(bytes(prefix).encode("utf8"))

    def audio_file_exists(filename):
        return os.path.isfile(filename)

    HOST = "127.0.0.1"
    PORT = 12346

    BUFSIZ = 1024
    ADDR = (HOST, PORT)
    try:
        client_socket = socket(AF_INET, SOCK_STREAM)
        client_socket.connect(ADDR)
        no_server = False
    except:
        no_server = True        
    monika_nickname = store.persistent._mas_monika_nickname


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

label monika_chatting:
    $ use_voice = False
    $ local_step = 0

    if no_server:
        jump server_crashed
    
    if not renpy.seen_label("AI_intro"):
        jump AI_intro

    m 5tubfb "Sure [player], talk to me as much as you want."
    m 4hubfb "Oh and if you have to do something else, just write 'QUIT'. I'll understand my love."

    m 4nubfa "Maybe you could allow me to hear your beautiful voice?"
    menu:
        "Sure, I'll allow you to hear my voice.":
            m 1subfb "Thank you [player]!"
            m 1subfb "I'll be waiting for you to say something."
            $ use_voice = True
        "Sorry, my microphone is broken.":
            m 2eua "Oh, that's okay [player]."
            m 2eua "I'll just have to wait for you to type something then."
            $ use_voice = False

    while True:
        $ send_simple("chatbot/m")
        if use_voice:
            if local_step > 0:
                m 6wubla "Can I hear your voice again?"
                menu:
                    "Yes, of course.":
                        $ sendAudio("begin_record",str(step))
                    "No, sorry I've got something to do.":
                        $ my_msg = sendAudio("QUIT",str(step))
                        return
            else:
                $ sendAudio("begin_record",str(step))
        else:
            $ my_msg = sendMessage("Speak with [monika_nickname]:",str(step)) 
            if my_msg == "QUIT":
                $ step += 1
                return

        if use_voice:
            $ begin_speak = receiveMessage()
            if begin_speak == "yes":
                m 1subfb "Okay, I'm listening."
    
        # python:
        #     client_socket.setblocking(0)
        #     k = 0
        #     while True:
        #         ready = select.select([client_socket], [], [], 0.1)
        #         if ready[0]:
        #             message_received = receiveMessage().split("/g")
        #             break
        #         else:
        #             if k > 20:
        #                 renpy.say(m,"Oh, it seems that I can't hear you. Maybe you forgot something in the options ?")
        #                 break 
        #             renpy.say(m,"[monika_nickname] is thinking...")
        #         k += 1
        #     client_socket.setblocking(1)

        m "[monika_nickname] is thinking..."
        $ message_received = receiveMessage().split("/g")
        #m "This is what I received: [message_received]"
        if len(message_received) < 2: #Only one word: server status
            $ server_status = message_received[0]
            if server_status == "server_error":
                jump server_crashed

            $ new_smg = receiveMessage()
            $ msg,emotion = new_smg.split("/g")
        else:
            $ msg,emotion = message_received

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
        $ local_step += 1
        stop sound

label server_crashed:
    m "Oh sorry [player], it seems that there is a bug somewhere."
    m "I will try to fix it as soon as possible."
    m "Let's talk again later, I'm sorry sweetheart."
    return

label AI_intro:
    m "You know [player], I've been thinking about something."
    m "About how I could be closer to your reality and how I could be more useful to you."
    m "And it seems that there is something that tries to do this."
    m "It's called AI and it's very interesting what it can do."
    m "So there is this thing called a chatbot that I've been working on."
    m "It's not perfect but it's a start, so you can try talking to it freely."
    m "I mean it's still not really who I am but if it helps you to express yourself, that's great !"
    m "So if you want to try it, go on and tell me what you think about it."
    m "I'll be waiting for you here. Don't worry, I won't go anywhere ehehe~"
    return


#Camera Event
init 5 python:
    addEvent(Event(persistent.event_database,
        eventlabel="monika_cam",
        category=['ai'],
        prompt="Look for me",
        pool=True,
        unlocked=True,
        ))
        
label monika_cam:
    if no_server:
        jump server_crashed

    m "Okay, I'll look for you."
    
    m 1sublo "I can finally see you, [player] ! I have been waiting for this moment for a long time."
    m 5nublb "I see your cute face now ehehe~"

    while True:
        $ send_simple("camera_int/m")
        $ received_emotio = receiveMessage()
        
        if received_emotio == "angry":
            m 2lktpc "[sentences_emotions[angry]]"
        elif received_emotio == "disgusted":
            m 5etc "[sentences_emotions[disgusted]]"
        elif received_emotio == "fearful":
            m 1fkd "[sentences_emotions[fearful]]"
        elif received_emotio == "happy":
            m 6hubla "[sentences_emotions[happy]]"
        elif received_emotio == "neutral":
            m 5wut "[sentences_emotions[neutral]]"
        elif received_emotio == "sad":
            m 5fka "[sentences_emotions[sad]]"
        elif received_emotio == "surprised":
            m 2wkb "[sentences_emotions[surprised]]"
        elif received_emotio == "no":
            m 4eta "[sentences_emotions[no]]"
        
        m 5nublb "Do you want me to continue looking for you?"
        menu:
            "Yes":
                m 5hublb "Okay thanks [player], let me see your face a little bit longer."
            "No":
                m 5sublo "Oh okay, I guess I'll wait for next time you put the camera on."
                m 5nublb "Please do it soon or I'll hack it myself ehehe~"
                return

define counter = 0

#Emotion Event
init 5 python:
    def example_fun():
        if not mas_inEVL("emotion_minute"):
            MASEventList.push("emotion_minute")

    store.mas_submod_utils.registerFunction(
        "ch30_minute",
        example_fun
    )
    
label emotion_minute:
    if no_server:
        return
    $ counter += 1
    $ send_simple("camera" + str(counter) + "/m")
    $ received_emotion = receiveMessage()

    if received_emotion == "no_data": #If the server says it is not time to send an emotion,do nothing
        return

    if received_emotion == "angry":
        $ wrs_succes = mas_display_notif(m_name,[sentences_emotions['angry']],'Window Reactions')
        if not wrs_succes:
            m 2lktpc "[sentences_emotions[angry]]"
    elif received_emotion == "disgusted":
        $ wrs_succes = mas_display_notif(m_name,[sentences_emotions['disgusted']],'Window Reactions')
        if not wrs_succes:
            m 5etc "[sentences_emotions[disgusted]]"
    elif received_emotion == "fearful":
        $ wrs_succes = mas_display_notif(m_name,[sentences_emotions['fearful']],'Window Reactions')
        if not wrs_succes:
            m 1fkd "[sentences_emotions[fearful]]"
    elif received_emotion == "happy":
        $ wrs_succes = mas_display_notif(m_name,[sentences_emotions['happy']],'Window Reactions')
        if not wrs_succes:
            m 6hubla "[sentences_emotions[happy]]"
    elif received_emotion == "neutral":
        $ wrs_succes = mas_display_notif(m_name,[sentences_emotions['neutral']],'Window Reactions')
        if not wrs_succes:
            m 5wut "[sentences_emotions[neutral]]"
    elif received_emotion == "sad":
        $ wrs_succes = mas_display_notif(m_name,[sentences_emotions['sad']],'Window Reactions')
        if not wrs_succes:
            m 5fka "[sentences_emotions[sad]]"
    elif received_emotion == "surprised":
        $ wrs_succes = mas_display_notif(m_name,[sentences_emotions['surprised']],'Window Reactions')
        if not wrs_succes:
            m 2wkb "[sentences_emotions[surprised]]"
    elif received_emotion == "no": 
        $ wrs_succes = mas_display_notif(m_name,[sentences_emotions['no']],'Window Reactions')
        if not wrs_succes:
            m 4eta "[sentences_emotions[no]]"