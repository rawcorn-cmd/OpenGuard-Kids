import subprocess
import os
import re

PDF_PATH = "/home/cornar/Downloads/Giáo trình/Mạng máy tính/computer-networking-top-down-approach-9th.pdf"
DEST_DIR = "/home/cornar/Projects/OpenGuard-Kids/docs/network_curriculum/01_theory_notes/kurose_9th"

CHAPTERS = [
    {
        "ch": 1,
        "title": "Computer Networks and the Internet",
        "file": "chapter_1_computer_networks_and_the_internet.md",
        "start_page": 25,
        "end_page": 96,
        "openguard_link": "Tổng quan mạng, mô hình Edge-Core, độ trễ và Packet Switching liên hệ trực tiếp với mô hình tác nhân trên máy khách (Agent) và kiến trúc Localhost Socket của OpenGuard Kids."
    },
    {
        "ch": 2,
        "title": "Application Layer",
        "file": "chapter_2_application_layer.md",
        "start_page": 97,
        "end_page": 181,
        "openguard_link": "Giao thức DNS (Port 53), HTTP/1.1/2/3, CNAME record rewrite cho SafeSearch, Web Caching, và kiến trúc Client-Server / P2P — Trọng tâm đồ án OpenGuard Kids (DNS Proxy & Web Dashboard)."
    },
    {
        "ch": 3,
        "title": "Transport Layer",
        "file": "chapter_3_transport_layer.md",
        "start_page": 182,
        "end_page": 286,
        "openguard_link": "UDP Socket (DNS Proxy không trạng thái) và TCP Socket (WebSocket điều khiển realtime, HTTP REST API) cùng cơ chế kiểm soát lỗi và nghẽn."
    },
    {
        "ch": 4,
        "title": "The Network Layer - Data Plane",
        "file": "chapter_4_the_network_layer_data_plane.md",
        "start_page": 287,
        "end_page": 352,
        "openguard_link": "Định tuyến IP, Cấu trúc gói tin IPv4/IPv6, NAT, và Packet Filtering (Cơ sở xây dựng bộ lọc Windows Firewall cho OpenGuard Kids)."
    },
    {
        "ch": 5,
        "title": "The Network Layer - Control Plane",
        "file": "chapter_5_the_network_layer_control_plane.md",
        "start_page": 353,
        "end_page": 412,
        "openguard_link": "Mặt phẳng điều khiển mạng, SDN (Software-Defined Networking), giao thức ICMP (Ping chẩn đoán mạng), và cấu hình SNMP/YANG."
    },
    {
        "ch": 6,
        "title": "The Link Layer and LANs",
        "file": "chapter_6_the_link_layer_and_lans.md",
        "start_page": 413,
        "end_page": 489,
        "openguard_link": "Địa chỉ MAC vật lý, ARP protocol, Ethernet, Data Center Networking và vòng đời một truy vấn Web từ DHCP -> ARP -> DNS -> TCP -> HTTP."
    },
    {
        "ch": 7,
        "title": "Wireless and Mobile Networks",
        "file": "chapter_7_wireless_and_mobile_networks.md",
        "start_page": 490,
        "end_page": 580,
        "openguard_link": "Mạng Wi-Fi 802.11 (Wi-Fi 6), mạng di động 4G/5G, quản lý chuyển vùng (Mobility) khi thiết bị laptop của trẻ chuyển giữa các mạng Wi-Fi khác nhau."
    },
    {
        "ch": 8,
        "title": "Security in Computer Networks",
        "file": "chapter_8_security_in_computer_networks.md",
        "start_page": 581,
        "end_page": 658,
        "openguard_link": "Mật mã học, băm dữ liệu SHA-256 (kiểm tra tính toàn vẹn file thực thi), xác thực mật khẩu, TLS 1.3, DoH (DNS over HTTPS), Firewalls & IDS — Nền tảng an toàn thông tin của OpenGuard Kids."
    },
    {
        "ch": 9,
        "title": "References and Index",
        "file": "chapter_9_references_and_index.md",
        "start_page": 659,
        "end_page": 717,
        "openguard_link": "Tài liệu tham khảo học thuật chính thức và chỉ mục tra cứu từ khóa mạng máy tính."
    }
]

def clean_text_to_markdown(raw_text, ch_num, ch_title):
    # Split by pages
    pages = raw_text.split('\x0c')
    cleaned_md = []
    
    for page_idx, page in enumerate(pages):
        lines = page.splitlines()
        page_lines = []
        for line in lines:
            line_str = line.strip()
            if not line_str:
                page_lines.append("")
                continue
                
            # Filter running headers like "Chapter 1 Computer Networks and the Internet" or page numbers
            if re.match(r'^(Chapter\s+\d+|[ivxlcdm]+\s+Preface|\d+\s+Chapter|\d+\s+Table of Contents)', line_str, re.IGNORECASE):
                continue
            if re.match(r'^\d+$', line_str): # isolated page number
                continue
                
            # Format Headings
            # e.g., "1.1 What Is the Internet?" -> "## 1.1 What Is the Internet?"
            # e.g., "1.1.1 A Nuts-and-Bolts Description" -> "### 1.1.1 A Nuts-and-Bolts Description"
            # e.g., "1.1.2 A Services Description" -> "### 1.1.2 A Services Description"
            m3 = re.match(r'^(\d+\.\d+\.\d+)\s+(.+)$', line_str)
            m2 = re.match(r'^(\d+\.\d+)\s+(.+)$', line_str)
            if m3:
                page_lines.append(f"\n### {m3.group(1)} {m3.group(2)}\n")
            elif m2:
                page_lines.append(f"\n## {m2.group(1)} {m2.group(2)}\n")
            elif line_str.startswith('• '):
                page_lines.append(f"* {line_str[2:]}")
            else:
                page_lines.append(line_str)
                
        cleaned_md.append("\n".join(page_lines))
        
    return "\n\n".join(cleaned_md)

def run():
    os.makedirs(DEST_DIR, exist_ok=True)
    print(f"Bắt đầu chuyển đổi giáo trình Kurose 9th Edition sang Markdown...")
    
    for item in CHAPTERS:
        ch = item["ch"]
        title = item["title"]
        filename = item["file"]
        sp = item["start_page"]
        ep = item["end_page"]
        link = item["openguard_link"]
        out_path = os.path.join(DEST_DIR, filename)
        
        print(f"-> Đang trích xuất Chương {ch}: {title} (PDF trang {sp} - {ep})...")
        cmd = ['pdftotext', '-f', str(sp), '-l', str(ep), PDF_PATH, '-']
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode != 0:
            print(f"Lỗi khi chạy pdftotext cho chương {ch}: {res.stderr}")
            continue
            
        md_content = clean_text_to_markdown(res.stdout, ch, title)
        
        # Build Markdown Document with Header & Course Alignment
        doc = f"""# Chương {ch}: {title}
> **Giáo trình:** Computer Networking: A Top-Down Approach (9th Edition, 2026)  
> **Tác giả:** Jim Kurose, Keith Ross — Pearson Education  
> **Số trang bản gốc:** PDF trang {sp} – {ep} (Độ dài: {ep - sp + 1} trang)  

---

> [!NOTE] ỨNG DỤNG TRỰC TIẾP VÀO ĐỒ ÁN OPENGUARD KIDS
> **Mục tiêu học tập & Áp dụng thực tiễn:**  
> {link}

---

{md_content}
"""
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(doc)
            
        size_kb = os.path.getsize(out_path) / 1024
        print(f"   [V] Hoàn tất {filename} ({size_kb:.1f} KB)")
        
    # Generate README for Kurose 9th Edition
    readme_path = os.path.join(DEST_DIR, "README.md")
    readme_content = f"""# Toàn Bộ Giáo Trình Kurose & Ross: Computer Networking (9th Edition)

Tài liệu chuẩn hóa định dạng Markdown trích xuất trực tiếp từ bản in chính thức **Computer Networking: A Top-Down Approach, 9th Edition (2026)** của hai giáo sư Jim Kurose và Keith Ross.

Được số hóa phục vụ học tập môn **Mạng máy tính** và bảo vệ đồ án **OpenGuard Kids** (Hệ thống giám sát và bảo vệ máy tính trẻ em dành cho phụ huynh).

---

## Danh Mục Chi Tiết Các Chương

| Chương | Tên Chương | Nội dung học thuật | Liên hệ đồ án OpenGuard Kids | Liên kết Markdown |
| :--- | :--- | :--- | :--- | :--- |
| **01** | **Computer Networks and the Internet** | Mô hình mạng, biên (Edge), lõi (Core), Packet Switching, Trễ & Mất gói | Phân biệt mô hình Client-Server, IPC trên máy cục bộ, kiến trúc Localhost | [Chương 1](./chapter_1_computer_networks_and_the_internet.md) |
| **02** | **Application Layer** | Tầng ứng dụng: HTTP/1.1/2/3, DNS (Port 53), CNAME rewrite, Socket IPC | Thiết kế DNS Proxy chặn tên miền độc hại, Web Dashboard phụ huynh | [Chương 2](./chapter_2_application_layer.md) |
| **03** | **Transport Layer** | Tầng giao vận: UDP vs TCP, Port numbers, Sockets, RDT, Congestion Control, QUIC | Phân tích lý do DNS dùng UDP socket, WebSocket dùng TCP persistent socket | [Chương 3](./chapter_3_transport_layer.md) |
| **04** | **The Network Layer - Data Plane** | Tầng mạng (Data Plane): Định tuyến IPv4/IPv6, NAT, Packet Filtering | Quy tắc lọc IP, cấu hình tự động Windows Firewall chặn truy cập trực tiếp | [Chương 4](./chapter_4_the_network_layer_data_plane.md) |
| **05** | **The Network Layer - Control Plane** | Tầng mạng (Control Plane): Thuật toán định tuyến OSPF/BGP, SDN, ICMP, SNMP | Giám sát trạng thái mạng, ping kiểm tra kết nối Server - Agent | [Chương 5](./chapter_5_the_network_layer_control_plane.md) |
| **06** | **The Link Layer and LANs** | Tầng liên kết dữ liệu: MAC Address, ARP, Ethernet, Data Center, Chu trình duyệt Web | Tìm hiểu ARP và vòng đời gửi nhận gói tin từ tầng ứng dụng xuống card mạng | [Chương 6](./chapter_6_the_link_layer_and_lans.md) |
| **07** | **Wireless and Mobile Networks** | Mạng không dây & di động: Wi-Fi 6 (802.11ax), 4G/5G, Quản lý chuyển vùng | Xử lý sự kiện ngắt kết nối/thay đổi card mạng Wi-Fi trên laptop của trẻ | [Chương 7](./chapter_7_wireless_and_mobile_networks.md) |
| **08** | **Security in Computer Networks** | An toàn thông tin mạng: Mã hóa RSA/AES, SHA-256 hash, TLS 1.3, DoH, Firewalls | Bảo mật API token, mã băm SHA-256 chống giả mạo tiến trình, chặn lách qua DoH | [Chương 8](./chapter_8_security_in_computer_networks.md) |
| **09** | **References & Index** | Tài liệu trích dẫn và chỉ mục thuật ngữ chuyên ngành | Tra cứu định nghĩa các chuẩn RFC và khái niệm mạng máy tính | [Chỉ mục](./chapter_9_references_and_index.md) |

---

## Hướng Dẫn Sử Dụng
- Các file tài liệu Markdown trên có thể mở trực tiếp trong VS Code để đọc với tính năng tìm kiếm toàn văn (`Ctrl + F`).
- Các đề mục tiêu đề cấp 2 (`##`) và cấp 3 (`###`) đã được chuẩn hóa để sinh mục lục tự động (Outline) trong mọi trình xem Markdown.
- Mỗi chương đều có khối ghi chú `[!NOTE]` phân tích mối liên hệ cụ thể vào đồ án để phục vụ nhóm sinh viên trả lời câu hỏi phản biện của giảng viên.
"""
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(readme_content)
    print(f"[V] Đã tạo thành công Master README tại {readme_path}")

if __name__ == "__main__":
    run()
