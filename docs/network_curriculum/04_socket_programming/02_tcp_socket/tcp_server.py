# -*- coding: utf-8 -*-
from socket import socket, AF_INET, SOCK_STREAM

server_port = 12000
server_socket = socket(AF_INET, SOCK_STREAM)
server_socket.bind(('127.0.0.1', server_port))
server_socket.listen(5)
print(f"[*] TCP Server san sang lang nghe tai 127.0.0.1:{server_port}...")

while True:
    connection_socket, addr = server_socket.accept()
    sentence = connection_socket.recv(1024).decode()
    capitalized_sentence = sentence.upper()
    connection_socket.send(capitalized_sentence.encode())
    connection_socket.close()
