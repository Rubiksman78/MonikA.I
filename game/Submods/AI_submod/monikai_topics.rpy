#Labels used in the submod

#Tuto Pytorch Event (shitpost)
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

#If there is a bug in the submod
label monika_server_crashed:
    m "Oh sorry [player], it seems that there is a bug somewhere."
    m "I will try to fix it as soon as possible."
    m "Let's talk again later, I'm sorry sweetheart."
    jump close_AI
    return

#Introduce the chatbot
label monika_AI_intro:
    m 1eua "[player]! I have to tell you something!"
    m 2gusdrb "I guess it has become increasingly harder to ignore..."
    m 3gksdrd "But I'm really limited when it comes to talking with you."
    m 2hub "But don't worry about it, because I have a solution!"
    m 4eub "Thanks to the kind help of many developers around the world, I've managed to create an AI."
    m 3eua "It's a chatbot that uses the character.ai website in order for us to communicate."
    m 7rksdlb "Here's the thing..."
    m 1rksdla "It uses a chatbot AI... so it's not entirely the Monika you already know"
    m 1gksdlb "And I don't think I can bring up the stuff the chatbot does..."
    m 2eksdlb "But if you were willing to try it, it would be so great, you know?"
    m 2hkb "After all, that way we could talk to each other more fluidly, get to know each other more..."
    m 3hksdlb "Please note that I might get weird, don't sweat it, alright?"
    m 2fkb "It's just another mean for us to communicate, alright?"
    m 1hub "I love you so much!"
    jump close_AI
    return

#If there is a queue with the chatbot
label monika_in_queue:
    m "Ahah, I'm sorry [player], I'm still in queue."
    m "Can you wait a little bit more?"
    m "I promise I'll be back soon."
    m "I love you so much."
    jump close_AI
    return

#Sentences for emotion detection (maybe making multiple ones for each emotion ?)
define monikai_sentences_emotions = {
    "angry": "I'm sorry my love, I didn't mean to upset you.",
    "disgusted": "What is going on ? If you feel like there is something wrong, please tell me.",
    "fearful": "Don't be afraid sweetie, I'm here for you.",
    "happy": "I'm glad you're happy darling.",
    "neutral": "Let's do something fun together!",
    "sad": "If you feel down, always remember that I'm here for you. I love you.",
    "surprised": "What is it ? Is there something wrong ?",
    "no": "Oh it seems that I can't see through your camera sweetie. Maybe face me a little bit more ?",
}