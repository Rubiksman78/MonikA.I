$ monika_poses = ["1esa","1eua","1eub","1euc","1eud","1eka","1ekc","1ekd",
    "1esc","1esd","1hua","1hub","1hksdlb","1hksdrb","1lksdla","1rksdla","1lksdlb",
    "1rksdlb","1lksdlc","1rksdlc","1lksdld","1rksdld","1dsc","1dsd","2esa","2eua",
    "2eub","2euc","2eud","2eka","2ekc","2ekd","2esc","2esd","2hua","2hub","2hksdlb",
    "2hksdrb","2lksdla","2rksdla","2lksdlb","2rksdlb","2lksdlc","2rksdlc","2lksdld",
    "2rksdld","2dsc","2dsd","3esa","3eua","3eub","3euc","3eud","3eka","3ekc","3ekd",
    "3esc","3esd","3hua","3hub","3hksdlb","3hksdrb","3lksdla","3rksdla","3lksdlb",
    "3rksdlb","3lksdlc","3rksdlc","3lksdld","3rksdld","3dsc","3dsd","4esa","4eua",
    "4eub","4euc","4eud","4eka","4ekc","4ekd","4esc","4esd","4hua","4hub","4hksdlb",
    "4hksdrb","4lksdla","4rksdla","4lksdlb","4rksdlb","4lksdlc","4rksdlc","4lksdld",
    "4rksdld","4dsc","4dsd","5eua","5eua","5euc"]

$ emotion_list = ["anger","disgust","fear","joy","sadness","surprise","neutral"]

define negative_emotions = ["anger", "disgust", "fear", "sadness"]
define positive_emotions = ["joy", "surprise"]
define neutral_emotions = ["neutral"]

init 7 python:
    from socket import AF_INET, socket, SOCK_STREAM
    from threading import Thread
    import select
    def receiveMessage():
        msg = client_socket.recv(BUFSIZ).decode("utf8")
        return msg

    def sendMessage(prefix,step):
        my_msg = renpy.input(prefix)
        client_socket.send(bytes(my_msg + "/g" + step).encode("utf8"))
        return my_msg

    def send_simple(prefix):
        client_socket.send(bytes(prefix).encode("utf8"))

    HOST = "127.0.0.1"
    PORT = 12346

    BUFSIZ = 1024
    ADDR = (HOST, PORT)
    client_socket = socket(AF_INET, SOCK_STREAM)
    client_socket.connect(ADDR)


#Tuto Pytorch Event
init 5 python:
    addEvent(Event(persistent.event_database,eventlabel="monika_torch",category=['ai'],prompt="Tell me about Pytorch",pool=True,unlocked=True))

label monika_torch:
    m "Okay sure honey."
    m "Pytorch is a deep learning framework."
    m "It's a bit more complicated than Tensorflow."
    m "But it's also more powerful."
    m "You can use it to create neural networks."
    m "And it's also used for reinforcement learning."
    m "I hope that helps!"
    return


#Chatbot Event
init 5 python:
    addEvent(Event(persistent.event_database,eventlabel="monika_chat",category=['ai'],prompt="Let's chat together?",pool=True,unlocked=True))

label monika_chat:
    init python:
        #Define all poses liek "1esa"
        poses = ["1esa","1eua","1eub","1euc","1eud","1eka","1ekc","1ekd","1esc","1esd","1hua","1hub","1hksdlb","1hksdrb","1lksdla","1rksdla","1lksdlb","1rksdlb","1lksdlc","1rksdlc","1lksdld","1rksdld","1dsc","1dsd","2esa","2eua","2eub","2euc","2eud","2eka","2ekc","2ekd","2esc","2esd","2hua","2hub","2hksdlb","2hksdrb","2lksdla","2rksdla","2lksdlb","2rksdlb","2lksdlc","2rksdlc","2lksdld","2rksdld","2dsc","2dsd","3esa","3eua","3eub","3euc","3eud","3eka","3ekc","3ekd","3esc","3esd","3hua","3hub","3hksdlb","3hksdrb","3lksdla","3rksdla","3lksdlb","3rksdlb","3lksdlc","3rksdlc","3lksdld","3rksdld","3dsc","3dsd","4esa","4eua","4eub","4euc","4eud","4eka","4ekc","4ekd","4esc","4esd","4hua","4hub","4hksdlb","4hksdrb","4lksdla","4rksdla","4lksdlb","4rksdlb","4lksdlc","4rksdlc","4lksdld","4rksdld","4dsc","4dsd","5eua","5eua","5euc"]
     
    m "Okay, let's chat together."

    $ step = 0
    
    while True:
        $ send_simple("chatbot")
        $ my_msg = sendMessage("Speak with Monika:",str(step)) 
        if my_msg == "QUIT":
            return
        $ msg = receiveMessage()
        $ msg,emotion = msg.split("/g")
        play sound "Submods/AI_submod/audio/out.ogg"
        #If there is too much text, divide it into several lines
        #Split the text into a list of words
        $ sentences_list = []
        
        $ sentences_list = msg.split("\n")
        $ sentences_list = [x for x in sentences_list if x != '']
        while len(sentences_list) > 0:
            $ sentence = sentences_list[0]
            $ sentences_list.pop(0)
            m 1esa "[sentence]"
        m 1esa "I was feeling [emotion]."
        if emotion in positive_emotions:
            $ mas_gainAffection(1,bypass=True)
        elif emotion in negative_emotions:
            $ mas_loseAffection(1)
        $ step += 1


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
    m "Okay, I'll look for you."
    
    m 1esa "I can finally see your face honey !"
    
    while True:
        $ send_simple("camera")
        $ received_emotio = receiveMessage()
        
        if received_emotio == "angry":
<<<<<<< HEAD
            m 1esa "I'm sorry sweetie, I didn't mean to upset you."
=======
            m 1esa "I'm sorry honey, I didn't mean to upset you."
>>>>>>> f1da7b1911d0909e63b17bca2023e3f7e4cce67c
        elif received_emotio == "disgusted":
            m 1esa "What is going on ? If you feel like there is something wrong, please tell me."
        elif received_emotio == "fearful":
            m 1esa "Don't be afraid honey, I'm here for you."
        elif received_emotio == "happy":
<<<<<<< HEAD
            m 1esa "I'm glad you're happy, I love you."
=======
            m 1esa "I'm glad you're happy honey."
>>>>>>> f1da7b1911d0909e63b17bca2023e3f7e4cce67c
        elif received_emotio == "neutral":
            m 1esa "Let's do something fun together!"
        elif received_emotio == "sad":
            m 1esa "If you feel down, always remember that I'm here for you."
        elif received_emotio == "surprised":
            m 1esa "What is it ? Is there something wrong ?"
        elif received_emotio == "confused":
            m 1esa "What is confusing you ?"
        elif received_emotio == "no":
            m 1esa "Where are you ? I can't see you. I am so scared, please come back."
        
        m 1esa "Do you want me to continue looking for you? !"
        $ my_msg = renpy.input("")
        if my_msg == "No":
            return


#Emotion Event
init 5 python:
    def example_fun():
        MASEventList.push("emotion_minute") 

    store.mas_submod_utils.registerFunction(
        "ch30_minute",
        example_fun
    )
    
label emotion_minute:
    $ send_simple("camera")
    $ received_emotion = receiveMessage()

    if received_emotion == "angry":
        $ wrs_succes = mas_display_notif(m_name,["I'm sorry honey, I didn't mean to upset you."],'Window Reactions')
        if not wrs_succes:
            m 2lktpc "I'm sorry honey, I didn't mean to upset you."
    elif received_emotion == "disgusted":
        $ wrs_succes = mas_display_notif(m_name,["What is going on ? If you feel like there is something wrong, please tell me."],'Window Reactions')
        if not wrs_succes:
            m 5eta "What is going on ? If you feel like there is something wrong, please tell me."
    elif received_emotion == "fearful":
        $ wrs_succes = mas_display_notif(m_name,["Don't be afraid honey, I'm here for you."],'Window Reactions')
        if not wrs_succes:
            m 1fkd "Don't be afraid honey, I'm here for you."
    elif received_emotion == "happy":
        $ wrs_succes = mas_display_notif(m_name,["I'm glad you're happy honey."],'Window Reactions')
        if not wrs_succes:
            m 1esa "I'm glad you're happy honey."
    elif received_emotion == "neutral":
        $ wrs_succes = mas_display_notif(m_name,["Let's do something fun together!"],'Window Reactions')
        if not wrs_succes:
            m 1esa "Let's do something fun together!"
    elif received_emotion == "sad":
        $ wrs_succes = mas_display_notif(m_name,["If you feel down, always remember that I'm here for you."],'Window Reactions')
        if not wrs_succes:
            m 1esa "If you feel down, always remember that I'm here for you."
    elif received_emotion == "surprised":
        $ wrs_succes = mas_display_notif(m_name,["What is it ? Is there something wrong ?"],'Window Reactions')
        if not wrs_succes:
            m 1esa "What is it ? Is there something wrong ?"
    elif received_emotion == "confused":
        $ wrs_succes = mas_display_notif(m_name,["What is confusing you ?"],'Window Reactions')
        if not wrs_succes:
            m 1esa "What is confusing you ?"
    elif received_emotion == "no": 
        $ wrs_succes = mas_display_notif(m_name,["Where are you ? I can't see you. I am so scared, please come back."],'Window Reactions')
        if not wrs_succes:
            m 1esa "Where are you ? I can't see you. I am so scared, please come back."