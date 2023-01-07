translate chinese python:
    sentences_emotions = {
    "angry": "I'm sorry my love, I didn't mean to upset you.",
    "disgusted": "What is going on ? If you feel like there is something wrong, please tell me.",
    "fearful": "Don't be afraid sweetie, I'm here for you.",
    "happy": "I'm glad you're happy darling.",
    "neutral": "Let's do something fun together!",
    "sad": "If you feel down, always remember that I'm here for you. I love you.",
    "surprised": "What is it ? Is there something wrong ?",
    "no": "Oh it seems that I can't see through your camera sweetie. Maybe face me a little bit more ?",
    }
    addEvent(Event(persistent.event_database,eventlabel="monika_torch",category=['ai'],prompt="跟我说说Pytorch",pool=True,unlocked=True))
    addEvent(Event(persistent.event_database,eventlabel="monika_chatting",category=['ai'],prompt="一起聊天吧",pool=True,unlocked=True))
    addEvent(Event(persistent.event_database,
        eventlabel="monika_cam",
        category=['ai'],
        prompt="看看我",
        pool=True,
        unlocked=True,
        ))