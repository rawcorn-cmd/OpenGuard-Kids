# -*- coding: utf-8 -*-
from socket import socket, AF_INET, SOCK_STREAM

server_name = '127.0.0.1'
server_port = 12000

client_socket = socket(AF_INET, SOCK_STREAM)
client_socket.connect((server_name, server_port))

sentence = "hello tcp openguard kids"
client_socket.send(sentence.encode())
modified_sentence = client_socket.recv(1024).decode()
print("Phan hoi tu TCP Server:", modified_sentence)
client_socket.close()
