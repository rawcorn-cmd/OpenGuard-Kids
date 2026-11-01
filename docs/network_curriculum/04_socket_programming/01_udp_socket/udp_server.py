# -*- coding: utf-8 -*-
"""
Chương trình Máy chủ UDP (UDP Server)
Minh họa tầng Giao vận (Transport Layer) cổng UDP 53/12000
"""
from socket import socket, AF_INET, SOCK_DGRAM

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 12000

def run_udp_server():
    # 1. Tạo socket UDP (SOCK_DGRAM) trên nền IPv4 (AF_INET)
    server_socket = socket(AF_INET, SOCK_DGRAM)
    
    # 2. Gắn (bind) socket vào địa chỉ và cổng lắng nghe
    server_socket.bind((SERVER_HOST, SERVER_PORT))
    print(f"[*] UDP Server đang lắng nghe tại {SERVER_HOST}:{SERVER_PORT}...")

    while True:
        # 3. Đón nhận gói tin từ máy khách (nhận dữ liệu và địa chỉ người gửi)
        data, client_address = server_socket.recvfrom(2048)
        message = data.decode("utf-8")
        print(f"[+] Nhận từ {client_address}: {message}")

        # 4. Xử lý và gửi phản hồi ngược lại
        response = f"SERVER_ECHO: {message.upper()}".encode("utf-8")
        server_socket.sendto(response, client_address)

if __name__ == "__main__":
    run_udp_server()
