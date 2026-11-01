# -*- coding: utf-8 -*-
import time
from socket import socket, AF_INET, SOCK_DGRAM

client_socket = socket(AF_INET, SOCK_DGRAM)
client_socket.settimeout(1.0) # Timeout 1 giay

for seq in range(1, 11):
    start = time.time()
    msg = f"Ping {seq} {start}"
    try:
        client_socket.sendto(msg.encode(), ('127.0.0.1', 12000))
        data, _ = client_socket.recvfrom(1024)
        rtt = time.time() - start
        print(f"Tra loi tu server: {data.decode()} - RTT: {rtt*1000:.2f} ms")
    except Exception:
        print(f"Goi tin {seq}: Yeu cau bi Timeout (Goi bi rot tren kenh UDP)")
client_socket.close()
