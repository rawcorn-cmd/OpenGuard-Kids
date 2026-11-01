# Toàn Bộ Giáo Trình Kurose & Ross: Computer Networking (9th Edition)

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
