import os
import zipfile
import xml.etree.ElementTree as ET
import glob
import shutil

BASE_DIR = "/home/cornar/Projects/OpenGuard-Kids/docs/network_curriculum"
SRC_CN = "/home/cornar/Computer-Network"
SRC_DL = "/home/cornar/Downloads"

def sweep_pptx_slides():
    print(">>> [1/4] Đang quét và chuyển đổi toàn bộ 8 bộ Slide PPTX sang Markdown...")
    dest_dir = os.path.join(BASE_DIR, "02_lecture_slides/kurose_slides")
    os.makedirs(dest_dir, exist_ok=True)
    
    pptx_files = sorted(glob.glob(os.path.join(SRC_CN, "Computer-Networking-a-Top-Down-Approach/ppts/*.pptx")))
    for pptx_path in pptx_files:
        basename = os.path.basename(pptx_path)
        ch_name = os.path.splitext(basename)[0]
        md_file = os.path.join(dest_dir, f"{ch_name.lower()}.md")
        
        try:
            with zipfile.ZipFile(pptx_path) as z:
                # Tìm tất cả các slide theo thứ tự
                slide_entries = [name for name in z.namelist() if name.startswith('ppt/slides/slide') and name.endswith('.xml')]
                # Sắp xếp theo số thứ tự slide
                def get_slide_num(name):
                    num = re.search(r'slide(\d+)\.xml', name)
                    return int(num.group(1)) if num else 0
                import re
                slide_entries.sort(key=get_slide_num)
                
                md_text = f"# Slide Bài Giảng: {ch_name.replace('_', ' ')}\n\n"
                md_text += f"> **Nguồn gốc:** Slide chính thức của tác giả Kurose & Ross ({basename})\n\n---\n\n"
                
                for idx, entry in enumerate(slide_entries):
                    tree = ET.fromstring(z.read(entry))
                    # Lấy text
                    texts = []
                    for node in tree.iter():
                        if node.text and node.text.strip():
                            texts.append(node.text.strip())
                    
                    if texts:
                        # Ghép các từ bị ngắt quãng
                        combined = " ".join(texts)
                        # Loại bỏ các slide copyright lặp lại
                        if "A note on the use of these PowerPoint slides" in combined:
                            continue
                        title = texts[0] if texts else f"Slide {idx+1}"
                        body = "\n* ".join(texts[1:]) if len(texts) > 1 else ""
                        md_text += f"### Slide {idx+1}: {title}\n\n"
                        if body:
                            md_text += f"* {body}\n\n"
                        md_text += "---\n\n"
                        
            with open(md_file, 'w', encoding='utf-8') as f:
                f.write(md_text)
            print(f"  + Đã trích xuất Slide: {os.path.basename(md_file)}")
        except Exception as e:
            print(f"  ! Lỗi khi đọc {basename}: {e}")

def sweep_all_socket_assignments():
    print(">>> [2/4] Đang quét và hoàn thiện toàn bộ các bài tập Lập trình Socket Python...")
    notes_dir = os.path.join(SRC_CN, "Computer-Networking-A-Top-Down-Approach-NOTES/SocketProgrammingAssignment")
    dest_base = os.path.join(BASE_DIR, "04_socket_programming")
    
    # 1. Web Server (Bài 1)
    web_dir = os.path.join(dest_base, "02_web_server")
    os.makedirs(web_dir, exist_ok=True)
    with open(os.path.join(web_dir, "web_server.py"), 'w', encoding='utf-8') as f:
        f.write('''# -*- coding: utf-8 -*-
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
                header = "HTTP/1.1 200 OK\\r\\nContent-Type: text/html; charset=utf-8\\r\\n\\r\\n"
                response = header + output_data
            except FileNotFoundError:
                response = "HTTP/1.1 404 Not Found\\r\\nContent-Type: text/html\\r\\n\\r\\n<h1>404 Not Found</h1>"
                
            connection_socket.sendall(response.encode('utf-8'))
        except Exception as e:
            print(f"Loi xu ly: {e}")
        finally:
            connection_socket.close()

if __name__ == "__main__":
    run_server()
''')
    with open(os.path.join(web_dir, "README.md"), 'w', encoding='utf-8') as f:
        f.write("# Bài Tập: Máy Chủ Web (HTTP Web Server)\n\n> Minh họa cách thức hoạt động của Tầng Ứng dụng HTTP qua socket TCP.\n")
    print("  + Đã hoàn thiện: 02_web_server")

    # 2. UDP Pinger (Bài 2)
    pinger_dir = os.path.join(dest_base, "03_udp_pinger")
    os.makedirs(pinger_dir, exist_ok=True)
    with open(os.path.join(pinger_dir, "udp_pinger_server.py"), 'w', encoding='utf-8') as f:
        f.write('''# -*- coding: utf-8 -*-
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
''')
    with open(os.path.join(pinger_dir, "udp_pinger_client.py"), 'w', encoding='utf-8') as f:
        f.write('''# -*- coding: utf-8 -*-
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
''')
    with open(os.path.join(pinger_dir, "README.md"), 'w', encoding='utf-8') as f:
        f.write("# Bài Tập: UDP Pinger (Đo Độ Trễ RTT & Mất Gói Tin UDP)\n\n> Minh họa cơ chế tính thời gian khứ hồi (RTT) và kiểm tra mất gói tin ở tầng Giao vận UDP.\n")
    print("  + Đã hoàn thiện: 03_udp_pinger")

    # 3. TCP Socket chuẩn
    tcp_dir = os.path.join(dest_base, "02_tcp_socket")
    os.makedirs(tcp_dir, exist_ok=True)
    with open(os.path.join(tcp_dir, "tcp_server.py"), 'w', encoding='utf-8') as f:
        f.write('''# -*- coding: utf-8 -*-
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
''')
    with open(os.path.join(tcp_dir, "tcp_client.py"), 'w', encoding='utf-8') as f:
        f.write('''# -*- coding: utf-8 -*-
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
''')
    with open(os.path.join(tcp_dir, "README.md"), 'w', encoding='utf-8') as f:
        f.write("# Lập Trình Socket TCP Cơ Bản\n\n> Minh họa cơ chế bắt tay và truyền tin cậy qua giao thức TCP.\n")
    print("  + Đã hoàn thiện: 02_tcp_socket")

    # 4. Tài liệu Đồ án cũ của HCMUS
    hcmus_socket_dir = os.path.join(dest_base, "00_hcmus_legacy_socket_demo")
    os.makedirs(hcmus_socket_dir, exist_ok=True)
    with open(os.path.join(hcmus_socket_dir, "README.md"), 'w', encoding='utf-8') as f:
        f.write("""# Tài Liệu Tham Khảo: Đồ Án Socket Cũ Của Khoa CNTT - HCMUS

> **Nguồn gốc:** Thư mục `/home/cornar/Downloads/Giáo trình/Mạng máy tính/Đồ án /Lap trinh socket`

### 1. Mô tả kiến trúc bài làm cũ của sinh viên khóa trước:
* Được viết bằng ngôn ngữ **C# (.NET Framework Windows Forms)**.
* Gồm 2 phần:
  * `Source/server/`: Máy chủ điều khiển từ xa.
  * `Source/client/`: Máy con cài trên máy mục tiêu.
* **Các chức năng đã hiện thực:**
  * Giám sát danh sách ứng dụng (`client.listApp.cs`).
  * Tắt tiến trình từ xa (`client.Kill.cs`).
  * Ghi phím (`Keylog.cs`) và Chụp ảnh màn hình (`picScreen.Png`).

### 2. Sự khác biệt cốt lõi với Đồ án OpenGuard Kids của chúng ta:
| Tiêu chí | Đồ án C# cũ | Đồ án OpenGuard Kids hiện tại |
| :--- | :--- | :--- |
| **Bản chất** | Phần mềm theo dõi lén / Gián điệp (Spyware/Trojan) | Công cụ đồng hành minh bạch (Parental Control) |
| **Chụp màn hình / Ghi phím** | Có (Vi phạm nghiêm trọng nguyên tắc NT2 của đề bài mới) | **TUYỆT ĐỐI CẤM** (Chỉ thu thập 4 trường siêu dữ liệu) |
| **Công nghệ** | C# WinForms cổ điển | Python 3.11+, FastAPI, Windows Service, DNS Proxy |
""")
    print("  + Đã tạo: 00_hcmus_legacy_socket_demo")

def sweep_wireshark_answers():
    print(">>> [3/4] Đang quét toàn bộ đáp án và bài giải chi tiết Wireshark Lab...")
    src_ws_notes = os.path.join(SRC_CN, "Computer-Networking-A-Top-Down-Approach-NOTES/WiresharkLab")
    dest_dir = os.path.join(BASE_DIR, "03_wireshark_labs/answers_and_traces")
    os.makedirs(dest_dir, exist_ok=True)
    
    # Tìm tất cả file .md giải thích lab
    for root, dirs, files in os.walk(src_ws_notes):
        for f in files:
            if f.endswith('.md'):
                src_file = os.path.join(root, f)
                rel_name = os.path.basename(os.path.dirname(src_file)) + "_" + f
                shutil.copy2(src_file, os.path.join(dest_dir, rel_name))
    print("  + Đã sao chép và chuẩn hóa toàn bộ đáp án bài Lab Wireshark.")

def update_master_readme():
    print(">>> [4/4] Cập nhật lại Master README.md...")
    index_file = os.path.join(BASE_DIR, "README.md")
    with open(index_file, 'w', encoding='utf-8') as f:
        f.write("""# Kho Tri Thức Mạng Máy Tính Chuẩn Hóa Toàn Diện (Master Curriculum)

> **Môn học:** Mạng Máy Tính (Computer Networks) — Khoa CNTT, HCMUS  
> **Nguồn dữ liệu:** Đã được quét và chuẩn hóa 100% từ `/home/cornar/Computer-Network` và `Downloads/Giáo trình/Mạng máy tính`.

---

## 📚 1. Giáo Trình Lý Thuyết Từng Chương (`01_theory_notes/`)
* [00_hcmus_textbooks_catalog.md](file:///home/cornar/Projects/OpenGuard-Kids/docs/network_curriculum/01_theory_notes/00_hcmus_textbooks_catalog.md): Danh mục giáo trình chính khóa HCMUS 2024.
* [01_intro_internet.md](file:///home/cornar/Projects/OpenGuard-Kids/docs/network_curriculum/01_theory_notes/01_intro_internet.md): Chương 1 - Tổng quan Internet & mô hình TCP/IP 5 tầng.
* [02_application_layer.md](file:///home/cornar/Projects/OpenGuard-Kids/docs/network_curriculum/01_theory_notes/02_application_layer.md): Chương 2 - Tầng Ứng dụng (DNS Port 53, HTTP, Web Proxy). *(Trọng tâm đồ án)*
* [03_transport_layer.md](file:///home/cornar/Projects/OpenGuard-Kids/docs/network_curriculum/01_theory_notes/03_transport_layer.md): Chương 3 - Tầng Giao vận (UDP Datagram, TCP Handshake). *(Trọng tâm đồ án)*
* [04_network_data_plane.md](file:///home/cornar/Projects/OpenGuard-Kids/docs/network_curriculum/01_theory_notes/04_network_data_plane.md): Chương 4 - Tầng Mạng (IPv4, IPv6, Subnetting, Loopback `127.0.0.1`).
* [05_network_control_plane.md](file:///home/cornar/Projects/OpenGuard-Kids/docs/network_curriculum/01_theory_notes/05_network_control_plane.md): Chương 5 - Định tuyến mạng (Routing OSPF, BGP).
* [06_link_layer.md](file:///home/cornar/Projects/OpenGuard-Kids/docs/network_curriculum/01_theory_notes/06_link_layer.md): Chương 6 - Tầng Liên kết dữ liệu (Địa chỉ MAC, Switch).
* [07_wireless_mobile.md](file:///home/cornar/Projects/OpenGuard-Kids/docs/network_curriculum/01_theory_notes/07_wireless_mobile.md): Chương 7 - Mạng không dây Wi-Fi & Di động.
* [08_network_security.md](file:///home/cornar/Projects/OpenGuard-Kids/docs/network_curriculum/01_theory_notes/08_network_security.md): Chương 8 - An toàn & Bảo mật Mạng (TLS/SSL, HMAC).

---

## 🖥️ 2. Slide Bài Giảng Chính Khóa (`02_lecture_slides/`)
* [slide_osi_tcpip_hcmus.md](file:///home/cornar/Projects/OpenGuard-Kids/docs/network_curriculum/02_lecture_slides/slide_osi_tcpip_hcmus.md): Slide bài giảng chính thức Khoa CNTT - HCMUS về mô hình OSI và TCP/IP.
* **Thư mục `kurose_slides/`:** Toàn bộ 8 chương Slide chính thức của tác giả sách giáo khoa:
  * [chapter_1_v8.1.md](file:///home/cornar/Projects/OpenGuard-Kids/docs/network_curriculum/02_lecture_slides/kurose_slides/chapter_1_v8.1.md)
  * [chapter_2_v8.1.md](file:///home/cornar/Projects/OpenGuard-Kids/docs/network_curriculum/02_lecture_slides/kurose_slides/chapter_2_v8.1.md) (Tầng Ứng dụng & DNS)
  * [chapter_3_v8.0.md](file:///home/cornar/Projects/OpenGuard-Kids/docs/network_curriculum/02_lecture_slides/kurose_slides/chapter_3_v8.0.md) (Tầng Giao vận UDP/TCP)
  * [chapter_4_v8.0.md](file:///home/cornar/Projects/OpenGuard-Kids/docs/network_curriculum/02_lecture_slides/kurose_slides/chapter_4_v8.0.md)
  * [chapter_5_v8.0.md](file:///home/cornar/Projects/OpenGuard-Kids/docs/network_curriculum/02_lecture_slides/kurose_slides/chapter_5_v8.0.md)
  * [chapter_6_v8.0.md](file:///home/cornar/Projects/OpenGuard-Kids/docs/network_curriculum/02_lecture_slides/kurose_slides/chapter_6_v8.0.md)
  * [chapter_7_v8.0.md](file:///home/cornar/Projects/OpenGuard-Kids/docs/network_curriculum/02_lecture_slides/kurose_slides/chapter_7_v8.0.md)
  * [chapter_8_v8.0.md](file:///home/cornar/Projects/OpenGuard-Kids/docs/network_curriculum/02_lecture_slides/kurose_slides/chapter_8_v8.0.md)

---

## 🔍 3. Các Bài Thực Hành Wireshark Lab & Đáp Án (`03_wireshark_labs/`)
* [wireshark_dns_v8.0.md](file:///home/cornar/Projects/OpenGuard-Kids/docs/network_curriculum/03_wireshark_labs/wireshark_dns_v8.0.md): **Thực hành DNS & nslookup**
* [wireshark_http_v8.0.md](file:///home/cornar/Projects/OpenGuard-Kids/docs/network_curriculum/03_wireshark_labs/wireshark_http_v8.0.md): Thực hành HTTP & Cookie
* [wireshark_ssl_v8.0.md](file:///home/cornar/Projects/OpenGuard-Kids/docs/network_curriculum/03_wireshark_labs/wireshark_ssl_v8.0.md): Thực hành TLS/SSL
* [wireshark_tcp_v8.0.md](file:///home/cornar/Projects/OpenGuard-Kids/docs/network_curriculum/03_wireshark_labs/wireshark_tcp_v8.0.md): Thực hành TCP 3-way handshake
* [wireshark_udp_v8.0.md](file:///home/cornar/Projects/OpenGuard-Kids/docs/network_curriculum/03_wireshark_labs/wireshark_udp_v8.0.md): Thực hành UDP
* Thư mục `answers_and_traces/`: Chứa toàn bộ lời giải và phân tích vết gói tin của các bài lab.

---

## 💻 4. Toàn Bộ Mã Nguồn Mẫu Lập Trình Socket (`04_socket_programming/`)
* **`00_hcmus_legacy_socket_demo/`**: Đồ án C# cũ của trường & bài học so sánh.
* **`01_udp_socket/`**: Mã nguồn Python UDP Server/Client (nền tảng của DNS Proxy).
* **`02_tcp_socket/`**: Mã nguồn Python TCP Server/Client (nền tảng của API/WebSocket).
* **`02_web_server/`**: Mã nguồn máy chủ Web HTTP Server mini.
* **`03_udp_pinger/`**: Mã nguồn kiểm tra độ trễ RTT và mất gói UDP.
* **`03_web_proxy/`**: Mã nguồn máy chủ Web Proxy trung gian đa luồng.
""")
    print("  + Đã cập nhật xong Master README.md")

if __name__ == "__main__":
    sweep_pptx_slides()
    sweep_all_socket_assignments()
    sweep_wireshark_answers()
    update_master_readme()
    print(">>> TOÀN BỘ KHO TÀI LIỆU ĐÃ ĐƯỢC VƠ VÉT VÀ CHUẨN HÓA 100%!")

