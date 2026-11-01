# -*- coding: utf-8 -*-
import random
from socket import socket, AF_INET, SOCK_DGRAM

server_socket = socket(AF_INET, SOCK_DGRAM)
server_socket.bind(('127.0.0.1', 12000))
print("[*] UDP Pinger Server san sang tai 127.0.0.1:12000 (Mo phong ty le rot goi 30%)...")

while True:
    rand = random.randint(0, 10)
    message, address = server_socket.recvfrom(1024)
    # Giả lập rớt gói tin 30% để kiểm thử UDP
    if rand < 4:
        continue
    server_socket.sendto(message.upper(), address)
