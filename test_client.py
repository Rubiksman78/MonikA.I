emotions = ["Angry", "Disgusted", "Fearful", "Happy", "Neutral", "Sad", "Surprised"]
from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread

def receiveMessage():
    msg = client_socket.recv(BUFSIZ).decode("utf8")
    return msg

def sendMessage(prefix,step):
    my_msg = input(prefix)
    client_socket.send(bytes(my_msg + "/g" + step).encode("utf8"))
    return my_msg

HOST = "127.0.0.1"  
PORT = 12346

BUFSIZ = 1024
ADDR = (HOST, PORT)
client_socket = socket(AF_INET, SOCK_STREAM)
client_socket.connect(ADDR)

while True:
    received_emotion = receiveMessage()

    if received_emotion == "angry":
        print("You are angry")
    elif received_emotion == "disgusted":
        print("You are disgusted")
    elif received_emotion == "fearful":
        print("You are fearful")
    elif received_emotion == "happy":
        print("You are happy")
    elif received_emotion == "neutral":
        print("You are neutral")
    elif received_emotion == "sad":
        print("You are sad")
    elif received_emotion == "surprised":
        print("You are surprised")
    elif received_emotion == "confused":
        print("You are confused")
    else:
        print("I can't detect your emotion")
    