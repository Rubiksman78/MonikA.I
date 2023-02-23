label monikai_play_actions: 
    #m 1eka "What would you like to do?"
    call mas_pick_a_game
    return 

label monikai_goodbye: 
    return "quit"

label monikai_greetings:
    return

label monikai_go_somewhere: 
    if mas_isMoniEnamored(higher=True):
        call monika_change_background
    else:
        m 1eua "Oh no it seems that I can't go anywhere for now."
        m 1eka "I'm sorry, [player]."
    return

label monikai_change_clothes: 
    #m 1eka "What would you like to change into?"
    call monika_clothes_select
    return

label monikai_be_right_back:
    return "idle"

label monikai_be_right_back_callback:
    m 1eka "You're back, [player]!"
    m 1eka "I missed you."
    jump monika_chatting_text

label monikai_brb:
    hide screen mas_background_timed_jump
    $ _history_list.pop()
    $ persistent._mas_idle_data["monikai_be_right_back"] = True
    $ mas_setupIdleMode("monikai_be_right_back", "monikai_be_right_back_callback")
    return

label monikai_ask_kiss:
    if mas_shouldKiss:
        call monika_kissing_motion_short
    else:
        m 1eka "Well with a second thought, I don't think I'm ready for that yet."
        m 1eka "I'm sorry, [player], maybe when we'll be more advanced in our relationship."
    return 

label monikai_normal_chat:
    return

label monikai_change_weather: 
    if mas_isMoniAff(higher=True):
        call monika_change_weather
    else:
        m 1eka "I'm sorry, [player], but I can't change the weather for now."
    return

label monikai_compliment: 
    #m 1eka "Thank you, [player]."
    $ mas_gainAffection()
    return