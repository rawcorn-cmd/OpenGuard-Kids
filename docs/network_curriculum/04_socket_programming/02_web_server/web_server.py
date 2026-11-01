# -*- coding: utf-8 -*-
"""
Máy chủ Web đơn giản (Single-threaded Web Server) bằng Python Socket
Minh họa Tầng Ứng dụng (HTTP) trên nền Tầng Giao vận (TCP)
"""
from socket import socket, AF_INET, SOCK_STREAM

def run_server(port=6789):
    server_socket = socket(AF_INET, SOCK_STREAM)
    server_socket.bind(('', port))
    server_socket.listen(1)
    print(f"[*] Web Server dang lang nghe tai cong http://127.0.0.1:{port}...")

    while True:
        connection_socket, addr = server_socket.accept()
        try:
            message = connection_socket.recv(1024).decode('utf-8')
            if not message:
                connection_socket.close()
                continue
            filename = message.split()[1].lstrip('/')
            
            # Đọc file được yêu cầu
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    output_data = f.read()
                header = "HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=utf-8\r\n\r\n"
                response = header + output_data
            except FileNotFoundError:
                response = "HTTP/1.1 404 Not Found\r\nContent-Type: text/html\r\n\r\n<h1>404 Not Found</h1>"
                
            connection_socket.sendall(response.encode('utf-8'))
        except Exception as e:
            print(f"Loi xu ly: {e}")
        finally:
            connection_socket.close()

if __name__ == "__main__":
    run_server()
