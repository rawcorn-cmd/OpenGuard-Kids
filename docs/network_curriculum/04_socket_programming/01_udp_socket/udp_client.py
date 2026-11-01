# -*- coding: utf-8 -*-
"""
Chương trình Máy khách UDP (UDP Client)
"""
from socket import socket, AF_INET, SOCK_DGRAM

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 12000

def run_udp_client():
    client_socket = socket(AF_INET, SOCK_DGRAM)
    msg = "xin chao openguard kids"
    print(f"[*] Gửi tin nhắn UDP: '{msg}' tới {SERVER_HOST}:{SERVER_PORT}")
    client_socket.sendto(msg.encode("utf-8"), (SERVER_HOST, SERVER_PORT))

    data, _ = client_socket.recvfrom(2048)
    print(f"[+] Nhận phản hồi: {data.decode('utf-8')}")
    client_socket.close()

if __name__ == "__main__":
    run_udp_client()
