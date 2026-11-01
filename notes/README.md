# Toàn Bộ Ghi Chú Học Tập & Thực Chiến Đồ Án (OpenGuard Kids)

> **Môn học:** Mạng Máy Tính (*Computer Networks*) — Khoa CNTT, Trường ĐH Khoa học Tự nhiên (HCMUS)  
> **Đồ án:** OpenGuard Kids — Hệ thống Giám sát & Quản lý Máy tính Trẻ em  
> **Tổng hợp từ:** Toàn bộ quá trình giảng dạy, đối thoại kiến trúc và hiện thực hóa thực chiến mã nguồn.

---

## 📌 BẢN ĐỒ CẤU TRÚC TÀI LIỆU (SYLLABUS & PRACTICAL INDEX)

Hệ thống tài liệu được phân chia thành **2 phần rõ rệt**:
1. **Phần I (Chuyên đề 01 – 10): Lý thuyết Nền tảng Mạng máy tính & Hệ điều hành chuyên sâu** bám sát giáo trình chuẩn quốc tế *Computer Networking: A Top-Down Approach (Kurose & Ross)* và Windows Internals.
2. **Phần II (Chuyên đề 11 – 15): Sổ tay Thực chiến Từng tuần (Week 1 $\rightarrow$ Week 5)** ghi chú chi tiết từng dòng code, bài test và bộ câu hỏi vấn đáp bảo vệ đồ án của từng tuần riêng biệt.

---

### PHẦN I: LÝ THUYẾT NỀN TẢNG MẠNG & HỆ ĐIỀU HÀNH CHUYÊN SÂU

| Chuyên đề | Tên tài liệu ghi chú | Nội dung kiến thức cốt lõi |
| :---: | :--- | :--- |
| **01** | [01_project_and_assignment_overview.md](./01_project_and_assignment_overview.md) | Tổng quan đồ án Mạng máy tính, phân tích đề bài gốc, nguyên tắc sư phạm NT1–NT6, danh mục cấm (Prohibited Catalog), lộ trình 6 tuần. |
| **02** | [02_windows_internals_and_anti_tamper.md](./02_windows_internals_and_anti_tamper.md) | Kiến trúc Windows Internals, User/Kernel Space, Session 0 Isolation, cơ chế IPC an toàn qua Localhost Socket, băm SHA-256 tiến trình, đo screen-time `GetLastInputInfo`. |
| **03** | [03_network_addressing_ports_and_sockets.md](./03_network_addressing_ports_and_sockets.md) | Bản chất địa chỉ mạng, Port 16-bit, Socket API, 2-tuple (UDP) vs 4-tuple (TCP), tại sao 1 card mạng mở được hàng trăm tab Chrome, địa chỉ Loopback `127.0.0.1` trong RAM. |
| **04** | [04_dns_deep_dive_traditional_vs_doh.md](./04_dns_deep_dive_traditional_vs_doh.md) | Giao thức DNS truyền thống (Port 53 UDP), sự ra đời của DoH (DNS over HTTPS), nghịch lý DoH với phần mềm phụ huynh, **chiến lược phòng thủ 3 lớp chặn DoH (Registry Policy, Canary Domain `use-application-dns.net`, Firewall Fallback)**, giải pháp kiến trúc "Secure Local Resolver". |
| **05** | [05_tcpip_vs_osi_and_application_layer.md](./05_tcpip_vs_osi_and_application_layer.md) | Đối chiếu 7 tầng OSI vs 5 tầng TCP/IP, phân tích Facebook hoạt động trên các tầng, bản chất Tầng Ứng dụng (App software $\neq$ App protocol), Encapsulation & Decapsulation. |
| **06** | [06_ip_vs_mac_routing_and_forwarding.md](./06_ip_vs_mac_routing_and_forwarding.md) | IP (Toàn trình End-to-End) vs MAC (Từng chặng Hop-by-Hop), tại sao gói tin ra khỏi máy mang MAC Router nhà, giao thức ARP, cách máy tính tìm đường (Subnet Mask) & Router tìm đường (BGP/OSPF/Longest Prefix Match). |
| **07** | [07_network_devices_rules_and_layer_boundaries.md](./07_network_devices_rules_and_layer_boundaries.md) | Quy tắc vàng: "Thiết bị ở Tầng N chỉ bóc gói tin lên tới Tầng N", phân cấp Hub/Switch/Router/Proxy, 3 lý do Router trung gian không bóc lên Tầng 4/5 (Tốc độ ASIC, Bảo mật TLS 1.3, Nguyên lý End-to-End). |
| **08** | [08_openguard_kids_domain_lifecycle_walkthrough.md](./08_openguard_kids_domain_lifecycle_walkthrough.md) | Tường thuật chi tiết từng mili-giây hành trình một tên miền khi nhập vào Chrome trên máy cài OpenGuard Kids: Web cấm $\rightarrow$ Blockpage, Web hợp lệ $\rightarrow$ Upstream DoH sạch, CNAME SafeSearch, và **Kịch bản 4: Xử lý tên miền lạ/chưa rõ an toàn (Regex Heuristic, Cloudflare 1.1.1.3 AI, Whitelist giờ học + nút xin phép NT5)**. |
| **09** | [09_transport_layer_tcp_udp_deep_dive.md](./09_transport_layer_tcp_udp_deep_dive.md) | **Tầng Giao vận chuyên sâu:** Khái niệm RTT (Round Trip Time), cấu trúc gói tin UDP Datagram (8B) vs TCP Segment (20B), Bắt tay 3 bước (tại sao không phải 2 bước), cơ chế RDT (Seq & Cumulative Ack), Fast Retransmit (3 Dup ACKs), Kiểm soát Luồng (`rwnd`) vs Kiểm soát Nghẽn (`cwnd`, Slow Start, AIMD), Đóng kết nối 4 bước & trạng thái `TIME_WAIT`. |
| **10** | [10_router_internals_dns_proxy_and_packet_redirection.md](./10_router_internals_dns_proxy_and_packet_redirection.md) | **Cơ chế Router, 9Router AI & Bản chất DNS Proxy:** Cấu trúc phần cứng Router (Data/Control Plane, chip TCAM, Crossbar fabric, HOL blocking), công nghệ 9Router AI Gateway, giải mã Port 53 (Server cố định vs Client tạm thời), bí quyết bẻ gãy vòng lặp vô tận (Loopback resolution) và đường đi vật lý qua Card mạng Wi-Fi. |

---

### PHẦN II: SỔ TAY THỰC CHIẾN TỪNG TUẦN (WEEK-BY-WEEK PRACTICAL NOTES)

| Tuần | Tên tài liệu ghi chú | Trọng tâm kỹ thuật & Mã yêu cầu | Tệp mã nguồn (`src/`) & Kiểm thử (`tests/`) |
| :---: | :--- | :--- | :--- |
| **11** | [11_week1_scaffolding_and_technical_spikes.md](./11_week1_scaffolding_and_technical_spikes.md) | **Tuần 1: Khung sườn & 3 Spike Rủi ro cao**<br>• Cứu hộ mạng `restore_dns.bat`<br>• DNS Proxy UDP 53, Canary DoH, CNAME SafeSearch<br>• SQLite WAL mode & Băm mật khẩu Argon2id (RFC 9106)<br>• Loopback IPC 8765 với Token 64-hex | `agent/dns_proxy.py`<br>`server/database.py`<br>`server/security.py`<br>`agent/ipc.py`<br>*(16 bài test)* |
| **12** | [12_week2_local_engines_and_auth_foundations.md](./12_week2_local_engines_and_auth_foundations.md) | **Tuần 2: Động cơ Đếm giờ & Auth API**<br>• Máy trạng thái 10 bước FSM (`ACTIVE` $\leftrightarrow$ `IDLE`)<br>• Bẫy lùi đồng hồ hệ thống (`monotonic` vs `time`)<br>• Đo sai số 1 giờ $\le \pm 30$s (F1.3)<br>• Máy chủ HTTP 8080 Blockpage giáo dục & Hotline 111<br>• Đăng ký/đăng nhập Cookie phiên, Mã PIN 8 ký tự | `agent/screen_time.py`<br>`agent/blockpage.py`<br>`server/app.py`<br>`server/auth.py`<br>`server/schemas.py`<br>*(14 bài test)* |
| **13** | [13_week3_process_enforcement_and_event_sync.md](./13_week3_process_enforcement_and_event_sync.md) | **Tuần 3: Giám sát Tiến trình & WebSocket Khẩn**<br>• Quét `psutil`, băm nhị phân SHA-256 ứng dụng<br>• Bắt bài chiêu trò đổi tên `game.exe` $\rightarrow$ `notepad.exe`<br>• Bộ nhớ đệm RAM Hash Caching $O(1)$ không tốn đĩa<br>• Bộ đệm SQLite ngoại tuyến chuẩn 7 trường NT2 & Idempotency<br>• WebSocket Hub truyền lệnh khẩn $< 5$s & Heartbeat fallback | `agent/process_monitor.py`<br>`agent/offline_buffer.py`<br>`server/ws_manager.py`<br>`data/test_domains.json`<br>*(11 bài test)* |
| **14** | [14_week4_desktop_tray_ui_and_demo_d1.md](./14_week4_desktop_tray_ui_and_demo_d1.md) | **Tuần 4: Giao diện Tray UI & Nghiệm thu Demo D1**<br>• Tray Controller chạy ở Session 1 (User desktop)<br>• StateListener polling 1.0s, Báo động đỏ mất kết nối $>15$s<br>• Chuỗi Toast 10m/5m/1m & Hộp thoại Ân hạn 60s lưu bài<br>• Màn hình khóa lịch sự, Hotline 111, Nút xin 15 phút<br>• Mô phỏng hoàn chỉnh 6 bước nghiệm thu Demo D1 | `tray/state_listener.py`<br>`tray/dialogs.py`<br>`tray/app.py`<br>*(5 bài test)* |
| **15** | [15_week5_parent_dashboard_transparency_privacy.md](./15_week5_parent_dashboard_transparency_privacy.md) | **Tuần 5: Web Dashboard & Quyền Riêng tư Tối cao**<br>• Bảng phân loại 200 tên miền 6 nhóm & Policy 6-11 tuổi<br>• Văn bản pháp lý cam kết quyền riêng tư `PRIVACY.md`<br>• Giao diện Web HTML5 di động cho cha mẹ<br>• **Atomic Dual Deletion (Xóa kép):** Xóa sạch đồng thời Database Server và SQLite máy con qua WebSocket<br>• Worker dọn dẹp dữ liệu quá hạn 90 ngày | `server/templates/dashboard.html`<br>`data/classification_dataset.json`<br>`PRIVACY.md`<br>`server/app.py`<br>*(5 bài test)* |
| **16** | [16_week6_code_freeze_hardening_and_defense.md](./16_week6_code_freeze_hardening_and_defense.md) | **Tuần 6: Đóng Băng Mã Nguồn, Tôi Luyện & Bảo Vệ Đồ Án**<br>• Strict Code Freeze (Zero new features)<br>• Tự động hóa 6 kịch bản Demo: `e2e_acceptance_verification.py`<br>• Báo cáo kỹ thuật Mục 2.3 Vòng đời & Giao thức: `FINAL_REPORT.md`<br>• Cẩm nang vấn đáp Top 10 câu hỏi hóc búa: `DEFENSE_GUIDE.md`<br>• Nghiệm thu 51/51 bài test passed (100%) | `scripts/e2e_acceptance_verification.py`<br>`docs/FINAL_REPORT.md`<br>`docs/DEFENSE_GUIDE.md`<br>`docs/TEST_PLAN.md`<br>*(51/51 tests verified)* |

---

## 🎯 Mục Tiêu Sử Dụng Bộ Ghi Chú Này
1. **Ôn thi và Nắm chắc môn Mạng máy tính:** Toàn bộ kiến thức bám sát 100% giáo trình chuẩn quốc tế **Computer Networking: A Top-Down Approach (9th Edition, Kurose & Ross)** và slide bài giảng chính khóa của HCMUS.
2. **Vũ khí phản biện bảo vệ đồ án:** Từng khái niệm lý thuyết đều được chỉ rõ: *"Nó nằm ở dòng code nào / module nào trong OpenGuard Kids?"*, giúp nhóm sinh viên tự tin trả lời bất kỳ câu hỏi hóc búa nào từ hội đồng chấm thi.
3. **Tra cứu nhanh trong quá trình phát triển:** Từng tuần có một tài liệu độc lập, đầy đủ kiến trúc, mã nguồn, ca kiểm thử và câu hỏi vấn đáp trực tiếp.
