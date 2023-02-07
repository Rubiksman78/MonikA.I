# define renpy.config.gl2 = True
# image Monika = Live2D("fullyanimatedmonika",base=.6,aliases={"open":"m01"})

# init 5 python:
#     import subprocess
#     from threading import Thread
#     import store
#     import os
#     import sys
#     import re
#     import time
#     import socket
#     from socket import AF_INET, SOCK_STREAM

#     def receiveMessage():
#         msg = client_socket.recv(BUFSIZ).decode("utf8")
#         return msg

#     def send_simple(prefix):
#         client_socket.send(bytes(prefix,encoding="utf8"))

#     def audio_file_exists(filename):
#         return os.path.isfile(filename)

#     class Slice(object):
#         def __init__(self, root, leng):
#             self.root = root # The original word
#             self.leng = leng # How many morphemes should be used as the prefix for the new portmanteau
#             self.morphemes = []
#             self.slice()

#         def slice(self):
#             ex = r'([^aeiou]*[aeiou]*)|[aeiou]*[^aeiou]*[aeiou]*'
#             root = self.root

#             # Full list of morphemes for future use
#             while root != '':
#                 end = re.match(ex, root).end()
#                 self.morphemes.append(root[0:end])
#                 root = root[end:]

#             # Check that the number given isnt more than is available
#             if len(self.morphemes) < self.leng:
#                 self.leng = len(self.morphemes)

#     HOST = '127.0.0.1'
#     PORT = 12343

#     BUFSIZ = 1024
#     ADDR = (HOST, PORT)
#     client_socket = socket.socket(AF_INET, SOCK_STREAM)

#     try:
#         client_socket.connect(ADDR)
#         connected = True
#     except:
#         connected = False

#     def get_wrapped_say(func):
#         def new_say(who, what, interact=True, *args, **kwargs):
#             speaktext = renpy.substitute(what)
#             send_simple(speaktext)

#             sentence_processed = speaktext.lower()
#             sentence_processed = re.sub(r'[^\w\s]','',sentence_processed)
#             syllabes = Slice(sentence_processed, 1).morphemes
#             _ = receiveMessage()
#             for syll in syllabes:
#                 renpy.show("Monika open")
#             func(who, what, interact=interact, *args, **kwargs)
#         return new_say

#     if connected:
#         renpy.say = get_wrapped_say(renpy.say)