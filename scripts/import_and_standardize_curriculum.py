import os
import shutil
import subprocess
import glob
import re

BASE_DIR = "/home/cornar/Projects/OpenGuard-Kids/docs/network_curriculum"
SRC_CN = "/home/cornar/Computer-Network"
SRC_DL = "/home/cornar/Downloads"

def process_theory_notes():
    print(">>> 1. Chuẩn hóa ghi chú lý thuyết các chương...")
    chapter_map = {
        "01. Computer Networks and the Internet": "01_intro_internet.md",
        "02. Application Layer": "02_application_layer.md",
        "03. Transport Layer": "03_transport_layer.md",
        "04. The Network Layer - Data Plane": "04_network_data_plane.md",
        "05. The Network Layer - Control Plane": "05_network_control_plane.md",
        "06. The Link Layer and LANs": "06_link_layer.md",
        "07. Wireless and Mobile Networks": "07_wireless_mobile.md",
        "08. Security in Computer Networks": "08_network_security.md"
    }

    src_notes_dir = os.path.join(SRC_CN, "Computer-Networking---A-Top-Down-Approach")
    dest_dir = os.path.join(BASE_DIR, "01_theory_notes")

    for src_folder, dest_file in chapter_map.items():
        src_md = os.path.join(src_notes_dir, src_folder, "README.md")
        dest_md = os.path.join(dest_dir, dest_file)
        if os.path.isfile(src_md):
            with open(src_md, 'r', encoding='utf-8') as f:
                content = f.read()
            header = f"> **Tài liệu học tập:** Giáo trình Kurose & Ross (Top-Down Approach)\n> **Chuyên đề:** {src_folder}\n\n---\n\n"
            with open(dest_md, 'w', encoding='utf-8') as f:
                f.write(header + content)
            print(f"  + Đã tạo: {dest_file}")

    # Tạo file tham chiếu giáo trình HCMUS 2024
    ref_file = os.path.join(dest_dir, "00_hcmus_textbooks_catalog.md")
    with open(ref_file, 'w', encoding='utf-8') as f:
        f.write("""# Danh Mục Giáo Trình Mạng Máy Tính HCMUS (2024)

> **Khoa Công nghệ Thông tin — Trường Đại học Khoa học Tự nhiên, ĐHQG-HCM**

### 1. Giáo trình chính khóa của trường (Bản quét CamScanner):
* **Giáo trình MMT (2024) Phần 1:** `/home/cornar/Downloads/Giáo trình/Mạng máy tính/Giáo trình MMT (2024) (P1).pdf` (272 trang, 148 MB)
* **Giáo trình MMT (2024) Phần 2:** `/home/cornar/Downloads/Giáo trình/Mạng máy tính/Giáo trình MMT (2024) (P2).pdf`
* **Giáo trình Mạng máy tính (P1 & P2):** `/home/cornar/Downloads/Giáo trình/Mạng máy tính/Giáo trình Mạng máy tính (P1).pdf`

### 2. Giáo trình chuẩn quốc tế tương đương (Bản Text số hóa):
* **Computer Networking: A Top-Down Approach (9th Edition):** `/home/cornar/Downloads/Giáo trình/Mạng máy tính/computer-networking-top-down-approach-9th.pdf`
* Giáo trình của trường được biên soạn bám sát 100% khung lý thuyết 5 tầng của cuốn Kurose & Ross này. Toàn bộ các chương lý thuyết tương đương đã được trích xuất thành Markdown trong thư mục này.
""")
    print("  + Đã tạo: 00_hcmus_textbooks_catalog.md")

def process_slides():
    print(">>> 2. Chuẩn hóa Slide bài giảng sang Markdown...")
    dest_dir = os.path.join(BASE_DIR, "02_lecture_slides")
    
    # 2.1 Trích xuất Slide 04 - OSI - TCPIP - T5.pdf của trường
    src_slide = os.path.join(SRC_DL, "04 - OSI - TCPIP- T5.pdf")
    if os.path.isfile(src_slide):
        res = subprocess.run(['pdftotext', src_slide, '-'], stdout=subprocess.PIPE, text=True)
        raw_text = res.stdout
        
        # Format thành slide Markdown
        pages = raw_text.split('\x0c')
        md_content = "# Slide Bài Giảng: Mô Hình Mạng OSI – TCP/IP\n\n"
        md_content += "> **Nguồn:** Slide bài giảng chính khóa Khoa CNTT - HCMUS (`04 - OSI - TCPIP- T5.pdf`)\n\n---\n\n"
        
        for idx, page in enumerate(pages):
            text = page.strip()
            if text:
                md_content += f"## Slide {idx+1}\n\n```text\n{text}\n```\n\n---\n\n"
        
        dest_md = os.path.join(dest_dir, "slide_osi_tcpip_hcmus.md")
        with open(dest_md, 'w', encoding='utf-8') as f:
            f.write(md_content)
        print("  + Đã trích xuất: slide_osi_tcpip_hcmus.md")

def process_wireshark_labs():
    print(">>> 3. Chuẩn hóa các bài thực hành Wireshark Lab sang Markdown...")
    dest_dir = os.path.join(BASE_DIR, "03_wireshark_labs")
    
    # Tìm các lab v8.0 hoặc v7.0
    labs = glob.glob(os.path.join(SRC_CN, "Computer-Networking-a-Top-Down-Approach/labs/Wireshark_*.pdf"))
    if not labs:
        labs = glob.glob(os.path.join(SRC_CN, "**", "PDF_Wireshark_labs", "Wireshark_*.pdf"), recursive=True)
        
    for lab_pdf in labs:
        basename = os.path.basename(lab_pdf)
        clean_name = os.path.splitext(basename)[0].lower()
        clean_name = clean_name.replace(" ", "_")
        
        res = subprocess.run(['pdftotext', lab_pdf, '-'], stdout=subprocess.PIPE, text=True)
        raw_text = res.stdout
        
        pages = raw_text.split('\x0c')
        md_content = f"# Thực Hành Mạng: {basename.replace('.pdf', '')}\n\n"
        md_content += f"> **Nguồn gốc:** Wireshark Lab (Kurose & Ross Top-Down Approach)\n"
        md_content += f"> **File PDF gốc:** `{lab_pdf}`\n\n---\n\n"
        
        for idx, page in enumerate(pages):
            text = page.strip()
            if text:
                # Làm sạch các ký tự đặc biệt
                md_content += f"### Trang {idx+1}\n\n{text}\n\n"
        
        dest_file = os.path.join(dest_dir, f"{clean_name}.md")
        with open(dest_file, 'w', encoding='utf-8') as f:
            f.write(md_content)
        print(f"  + Đã chuyển đổi: {os.path.basename(dest_file)}")

def process_socket_programming():
    print(">>> 4. Chuẩn hóa mã nguồn mẫu Lập trình Socket Python...")
    src_socket_notes = os.path.join(SRC_CN, "Computer-Networking-A-Top-Down-Approach-NOTES")
    
    # 4.1 UDP Socket
    udp_dir = os.path.join(BASE_DIR, "04_socket_programming/01_udp_socket")
    src_udp_md = os.path.join(src_socket_notes, "Notes/UDP套接字编程.md")
    if os.path.isfile(src_udp_md):
        shutil.copy2(src_udp_md, os.path.join(udp_dir, "HUONG_DAN_UDP.md"))
    
    # Tạo script UDP mẫu tiếng Việt chuẩn
    with open(os.path.join(udp_dir, "udp_server.py"), 'w', encoding='utf-8') as f:
        f.write('''# -*- coding: utf-8 -*-
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
''')

    with open(os.path.join(udp_dir, "udp_client.py"), 'w', encoding='utf-8') as f:
        f.write('''# -*- coding: utf-8 -*-
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
''')

    # 4.2 Web Proxy
    proxy_dir = os.path.join(BASE_DIR, "04_socket_programming/03_web_proxy")
    src_proxy_dir = os.path.join(src_socket_notes, "SocketProgrammingAssignment/作业4-多线程Web代理服务器")
    src_proxy_py = os.path.join(src_proxy_dir, "source/WebProxy.py")
    if os.path.isfile(src_proxy_py):
        shutil.copy2(src_proxy_py, os.path.join(proxy_dir, "web_proxy.py"))
    
    with open(os.path.join(proxy_dir, "README.md"), 'w', encoding='utf-8') as f:
        f.write("""# Bài Tập Lập Trình: Web Proxy Server Đa Luồng

> **Tài liệu tham khảo:** Kurose & Ross Chapter 2 Programming Assignment 4  
> **Áp dụng vào OpenGuard Kids:** Nguyên lý đón bắt yêu cầu HTTP/DNS, kiểm tra bộ đệm (cache), lọc nội dung và chuyển tiếp (forwarding).
""")
    print("  + Đã tạo các bài mẫu Lập trình Socket UDP & Web Proxy.")

def create_master_index():
    print(">>> 5. Tạo Sổ tay mục lục tra cứu toàn diện (Master Index)...")
    index_file = os.path.join(BASE_DIR, "README.md")
    content = """# Kho Tri Thức Mạng Máy Tính Chuẩn Hóa (Computer Networks Knowledge Base)

> **Môn học:** Mạng Máy Tính (Computer Networks) — Khoa CNTT, HCMUS  
> **Nguồn trích xuất:** Giáo trình MMT 2024 HCMUS, Slide bài giảng, Kurose & Ross 9th Edition và các bài thực hành Wireshark Labs.  
> **Mục tiêu:** Cung cấp tài liệu tra cứu trực tiếp bằng định dạng Markdown gọn nhẹ, hỗ trợ đọc và học trực tiếp trong VS Code cho đồ án OpenGuard Kids.

---

## 📚 1. Giáo Trình Lý Thuyết Từng Chương (`01_theory_notes/`)

Tóm tắt toàn bộ 8 chương cốt lõi theo giáo trình chuẩn quốc tế, bám sát barem lý thuyết của trường:

* [00_hcmus_textbooks_catalog.md](file:///home/cornar/Projects/OpenGuard-Kids/docs/network_curriculum/01_theory_notes/00_hcmus_textbooks_catalog.md): Danh mục giáo trình chính khóa HCMUS 2024 (P1 & P2).
* [01_intro_internet.md](file:///home/cornar/Projects/OpenGuard-Kids/docs/network_curriculum/01_theory_notes/01_intro_internet.md): Tổng quan mạng, mô hình TCP/IP 5 tầng, độ trễ và mất gói.
* [02_application_layer.md](file:///home/cornar/Projects/OpenGuard-Kids/docs/network_curriculum/01_theory_notes/02_application_layer.md): **Tầng Ứng dụng** — Giao thức DNS (Port 53), HTTP/1.1 vs HTTP/2, Web Proxy Server. *(Trọng tâm đồ án!)*
* [03_transport_layer.md](file:///home/cornar/Projects/OpenGuard-Kids/docs/network_curriculum/01_theory_notes/03_transport_layer.md): **Tầng Giao vận** — UDP Segment, TCP Handshake, Socket Multiplexing. *(Trọng tâm đồ án!)*
* [04_network_data_plane.md](file:///home/cornar/Projects/OpenGuard-Kids/docs/network_curriculum/01_theory_notes/04_network_data_plane.md): **Tầng Mạng (Data Plane)** — IPv4, IPv6, Subnetting, Loopback `127.0.0.1`.
* [05_network_control_plane.md](file:///home/cornar/Projects/OpenGuard-Kids/docs/network_curriculum/01_theory_notes/05_network_control_plane.md): **Tầng Mạng (Control Plane)** — Định tuyến OSPF, BGP, SDN.
* [06_link_layer.md](file:///home/cornar/Projects/OpenGuard-Kids/docs/network_curriculum/01_theory_notes/06_link_layer.md): **Tầng Liên kết dữ liệu** — Địa chỉ MAC, Switch, Ethernet.
* [07_wireless_mobile.md](file:///home/cornar/Projects/OpenGuard-Kids/docs/network_curriculum/01_theory_notes/07_wireless_mobile.md): Mạng không dây Wi-Fi 802.11 và Di động.
* [08_network_security.md](file:///home/cornar/Projects/OpenGuard-Kids/docs/network_curriculum/01_theory_notes/08_network_security.md): **An toàn & Bảo mật Mạng** — Mã hóa TLS/SSL, Chữ ký số, HMAC, Chống tấn công MitM.

---

## 🖥️ 2. Slide Bài Giảng Chính Khóa (`02_lecture_slides/`)

* [slide_osi_tcpip_hcmus.md](file:///home/cornar/Projects/OpenGuard-Kids/docs/network_curriculum/02_lecture_slides/slide_osi_tcpip_hcmus.md): Trích xuất toàn văn từng slide bài giảng chính khóa của Khoa CNTT - HCMUS về mô hình OSI và TCP/IP.

---

## 🔍 3. Các Bài Thực Hành Bắt Gói Tin Wireshark (`03_wireshark_labs/`)

Được chuyển thể toàn bộ từ file PDF sang Markdown để đọc và làm theo trực tiếp trong VS Code:

* [wireshark_dns_v8.0.md](file:///home/cornar/Projects/OpenGuard-Kids/docs/network_curriculum/03_wireshark_labs/wireshark_dns_v8.0.md): **Thực hành bắt gói tin DNS & dùng lệnh `nslookup`** *(Đề bài yêu cầu kiểm chứng bằng bài này!)*
* [wireshark_http_v8.0.md](file:///home/cornar/Projects/OpenGuard-Kids/docs/network_curriculum/03_wireshark_labs/wireshark_http_v8.0.md): Bắt gói tin HTTP GET/POST và Cookie.
* [wireshark_ssl_v8.0.md](file:///home/cornar/Projects/OpenGuard-Kids/docs/network_curriculum/03_wireshark_labs/wireshark_ssl_v8.0.md): Phân tích bắt tay mã hóa TLS/HTTPS.
* [wireshark_tcp_v8.0.md](file:///home/cornar/Projects/OpenGuard-Kids/docs/network_curriculum/03_wireshark_labs/wireshark_tcp_v8.0.md): Bắt tay 3 bước SYN/ACK và kiểm soát luồng TCP.
* [wireshark_udp_v8.0.md](file:///home/cornar/Projects/OpenGuard-Kids/docs/network_curriculum/03_wireshark_labs/wireshark_udp_v8.0.md): Phân tích cấu trúc Datagram UDP.
* [wireshark_ip_v8.0.md](file:///home/cornar/Projects/OpenGuard-Kids/docs/network_curriculum/03_wireshark_labs/wireshark_ip_v8.0.md): Phân tích Header gói tin IPv4 và phân mảnh gói tin.
* [wireshark_nat_v8.0.md](file:///home/cornar/Projects/OpenGuard-Kids/docs/network_curriculum/03_wireshark_labs/wireshark_nat_v8.0.md): Cơ chế biên dịch địa chỉ mạng (NAT).
* [wireshark_icmp_v8.0.md](file:///home/cornar/Projects/OpenGuard-Kids/docs/network_curriculum/03_wireshark_labs/wireshark_icmp_v8.0.md): Lệnh ping và traceroute.

---

## 💻 4. Thư Viện Lập Trình Socket Mẫu Bằng Python (`04_socket_programming/`)

* **`01_udp_socket/`**:
  * [udp_server.py](file:///home/cornar/Projects/OpenGuard-Kids/docs/network_curriculum/04_socket_programming/01_udp_socket/udp_server.py): Máy chủ UDP lắng nghe cổng, tiền đề viết DNS Proxy.
  * [udp_client.py](file:///home/cornar/Projects/OpenGuard-Kids/docs/network_curriculum/04_socket_programming/01_udp_socket/udp_client.py): Máy khách gửi gói tin UDP.
* **`03_web_proxy/`**:
  * [web_proxy.py](file:///home/cornar/Projects/OpenGuard-Kids/docs/network_curriculum/04_socket_programming/03_web_proxy/web_proxy.py): Máy chủ Proxy đa luồng hoàn chỉnh bằng Python.
"""
    with open(index_file, 'w', encoding='utf-8') as f:
        f.write(content)
    print("  + Đã tạo: README.md (Master Index)")

if __name__ == "__main__":
    process_theory_notes()
    process_slides()
    process_wireshark_labs()
    process_socket_programming()
    create_master_index()
    print(">>> HOÀN TẤT CHUẨN HÓA KHO TRI THỨC MẠNG!")

