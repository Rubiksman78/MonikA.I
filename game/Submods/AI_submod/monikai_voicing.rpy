init 5 python in mas_voice:
    import os
    import socket
    from socket import AF_INET, SOCK_STREAM

    renpy.music.register_channel("mvoice", mixer= "sfx", loop=False)

    def receiveMessage():
        msg = client_socket.recv(BUFSIZ).decode("utf8")
        return msg

    def send_simple(prefix):
        client_socket.send(bytes(prefix).encode("utf8"))

    def audio_file_exists(filename):
        return os.path.isfile(filename)

    HOST = '127.0.0.1'
    PORT = 12344 #Be sure to have a different port for voicing, no conflict with chat

    BUFSIZ = 1024
    ADDR = (HOST, PORT)
    client_socket = socket.socket(AF_INET, SOCK_STREAM)

    try:
        client_socket.connect(ADDR)
        connected = True
    except:
        connected = False

    def get_wrapped_say(func):
        def new_say(who, what, interact=True, *args, **kwargs):
            speaktext = renpy.substitute(what)
            send_simple(speaktext)
            func(who, what, interact=interact, *args, **kwargs)
        return new_say

    if connected:
        renpy.say = get_wrapped_say(renpy.say)
