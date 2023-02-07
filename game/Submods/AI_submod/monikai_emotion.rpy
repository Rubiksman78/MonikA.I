define emotion_list = ["anger","disgust","fear","joy","sadness","surprise","neutral"]

define negative_emotions = ["anger", "disgust", "fear", "sadness"]
define positive_emotions = ["joy", "surprise"]
define neutral_emotions = ["neutral"]

define monikai_emotion_counter = 0 #counter for the emotion intervals to send to the server

#Camera Event in the Talk Menu
init 5 python:
    addEvent(Event(persistent.event_database,
        eventlabel="monika_cam",
        category=['ai'],
        prompt="Look for me",
        pool=True,
        unlocked=True,
        ))
        
label monika_cam:
    if monikai_no_server:
        jump monika_server_crashed

    m "Okay, I'll look for you."
    
    m 1sublo "I can finally see you, [player] ! I have been waiting for this moment for a long time."
    m 5nublb "I see your cute face now ehehe~"

    while True:
        $ send_simple("camera_int/m")
        $ received_emotio = receiveMessage()
        
        if received_emotio == "no_data": #If the server says it is not time to send an emotion,do nothing
            m "Sorry but it seems that you didn't put the camera on."
            m 5nublb "Please put it on so I can see you."
            return
        if received_emotio == "angry":
            m 2lktpc "[monikai_sentences_emotions[angry]]"
        elif received_emotio == "disgusted":
            m 5etc "[monikai_sentences_emotions[disgusted]]"
        elif received_emotio == "fearful":
            m 1fkd "[monikai_sentences_emotions[fearful]]"
        elif received_emotio == "happy":
            m 6hubla "[monikai_sentences_emotions[happy]]"
        elif received_emotio == "neutral":
            m 5wut "[monikai_sentences_emotions[neutral]]"
        elif received_emotio == "sad":
            m 5fka "[monikai_sentences_emotions[sad]]"
        elif received_emotio == "surprised":
            m 2wkb "[monikai_sentences_emotions[surprised]]"
        elif received_emotio == "no":
            m 4eta "[monikai_sentences_emotions[no]]"
        
        m 5nublb "Do you want me to continue looking for you?"
        menu:
            "Yes":
                m 5hublb "Okay thanks [player], let me see your face a little bit longer."
            "No":
                m 5sublo "Oh okay, I guess I'll wait for next time you put the camera on."
                m 5nublb "Please do it soon or I'll hack it myself ehehe~"
                return


#Camera activating at intervals
init 5 python:
    def example_fun():
        if not mas_inEVL("emotion_minute"):
            MASEventList.push("emotion_minute")

    store.mas_submod_utils.registerFunction(
        "ch30_minute",
        example_fun
    )
    
label emotion_minute:
    if monikai_no_server:
        return
    $ monikai_emotion_counter += 1
    $ send_simple("camera" + str(monikai_emotion_counter) + "/m")
    $ received_emotion = receiveMessage()

    if received_emotion == "no_data": #If the server says it is not time to send an emotion,do nothing
        return

    if received_emotion == "angry":
        $ wrs_succes = mas_display_notif(m_name,[monikai_sentences_emotions['angry']],'Window Reactions')
        if not wrs_succes:
            m 2lktpc "[monikai_sentences_emotions[angry]]"
    elif received_emotion == "disgusted":
        $ wrs_succes = mas_display_notif(m_name,[monikai_sentences_emotions['disgusted']],'Window Reactions')
        if not wrs_succes:
            m 5etc "[monikai_sentences_emotions[disgusted]]"
    elif received_emotion == "fearful":
        $ wrs_succes = mas_display_notif(m_name,[monikai_sentences_emotions['fearful']],'Window Reactions')
        if not wrs_succes:
            m 1fkd "[monikai_sentences_emotions[fearful]]"
    elif received_emotion == "happy":
        $ wrs_succes = mas_display_notif(m_name,[monikai_sentences_emotions['happy']],'Window Reactions')
        if not wrs_succes:
            m 6hubla "[monikai_sentences_emotions[happy]]"
    elif received_emotion == "neutral":
        $ wrs_succes = mas_display_notif(m_name,[monikai_sentences_emotions['neutral']],'Window Reactions')
        if not wrs_succes:
            m 5wut "[monikai_sentences_emotions[neutral]]"
    elif received_emotion == "sad":
        $ wrs_succes = mas_display_notif(m_name,[monikai_sentences_emotions['sad']],'Window Reactions')
        if not wrs_succes:
            m 5fka "[monikai_sentences_emotions[sad]]"
    elif received_emotion == "surprised":
        $ wrs_succes = mas_display_notif(m_name,[monikai_sentences_emotions['surprised']],'Window Reactions')
        if not wrs_succes:
            m 2wkb "[monikai_sentences_emotions[surprised]]"
    elif received_emotion == "no": 
        $ wrs_succes = mas_display_notif(m_name,[monikai_sentences_emotions['no']],'Window Reactions')
        if not wrs_succes:
            m 4eta "[monikai_sentences_emotions[no]]"