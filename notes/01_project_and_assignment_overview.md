# Chuyên Đề 01: Tổng Quan Đồ Án, Đề Bài & Triết Lý Thiết Kế

> **Môn học:** Mạng Máy Tính (Computer Networks) — Khoa CNTT, HCMUS  
> **Nguồn gốc tài liệu:** Đã được đối soát 100% khớp từng byte với file đề bài gốc của giảng viên: `MoTa_Doan_QLyViecSuDungPCCuaTre (1).docx`.

---

## 1. Bối Cảnh Môn Học & Bài Toán Thực Tế

Trong khuôn khổ môn học **Mạng máy tính**, nhóm 3 sinh viên được giao phát triển một ứng dụng kiểm soát máy tính của trẻ em mang tên **OpenGuard Kids (OGK)** chạy trên nền tảng **Windows 10/11 x64**.

### Bài toán đặt ra:
* Trẻ em hiện nay tiếp xúc với máy tính cá nhân (PC/Laptop) rất sớm để học tập, nhưng cũng đối mặt với các nguy cơ:
  * Ngồi máy tính quá nhiều giờ liên tục (ảnh hưởng thị lực, sức khỏe tâm lý).
  * Vô tình hoặc cố ý truy cập vào các trang web độc hại (cờ bạc, bạo lực, nội dung người lớn).
  * Mở các ứng dụng trò chơi (Game) trong giờ học trực tuyến.
* **Mục tiêu của OpenGuard Kids:** Cung cấp cho phụ huynh một công cụ quản lý văn minh, minh bạch, bảo vệ trẻ từ xa thông qua mạng máy tính mà không biến máy tính thành một công cụ do thám độc hại.

---

## 2. Các Nhóm Yêu Cầu Chức Năng Cốt Lõi (F1 – F5)

Dựa trên đề bài chính thức, hệ thống gồm 5 nhóm yêu cầu kỹ thuật:

| Nhóm | Tên chức năng | Chi tiết kỹ thuật theo đề bài |
| :---: | :--- | :--- |
| **F1** | **Giới hạn thời gian sử dụng (Screen-Time Management)** | • Cấu hình tổng thời gian dùng máy mỗi ngày (ví dụ: tối đa 2 giờ/ngày).<br>• Cấu hình khung giờ cấm dùng máy (ví dụ: từ 22:00 đêm đến 06:00 sáng).<br>• Đo thời gian thực tế: Tự động trừ thời gian khi trẻ không ngồi trước máy (Idle time > 5 phút).<br>• Cảnh báo trước khi hết giờ (trước 10 phút, 5 phút, 1 phút) và cho phép ân hạn (grace period). |
| **F2** | **Quản lý & Chặn ứng dụng (Application Control)** | • Giám sát danh sách các tiến trình `.exe` đang chạy.<br>• Chặn chạy các phần mềm cấm (Blacklist: Games, Tool bẻ khóa...).<br>• **Quy tắc an ninh:** Tính toán mã băm **SHA-256** của file thực thi, không tin tưởng tên file `.exe` (vì trẻ có thể đổi tên `game.exe` thành `word.exe` để lách luật). |
| **F3** | **Lọc Web & DNS (Web / DNS Content Filtering)** | • Lọc theo danh mục tên miền (Cờ bạc, Người lớn, Bạo lực, Mạng xã hội trong giờ học).<br>• Cưỡng chế bật chế độ tìm kiếm an toàn (**SafeSearch**) trên Google, Bing, YouTube bằng kỹ thuật CNAME rewriting.<br>• Phục vụ trang thông báo khi bị chặn (Blockpage HTTP Server). |
| **F4** | **Bảng điều khiển Phụ huynh (Parent Web Dashboard)** | • Xem báo cáo thời gian sử dụng máy tính, lịch sử duyệt web và các ứng dụng đã mở.<br>• Đẩy các lệnh khẩn cấp tức thì (< 5 giây): Khóa máy ngay lập tức, tắt máy, cộng thêm thời gian (Add Time). |
| **F5** | **Bảo mật, Quyền riêng tư & Cơ chế Offline** | • Mật khẩu phụ huynh mã hóa bằng chuẩn an toàn **Argon2id** (hoặc bcrypt).<br>• Toàn bộ kết nối API/WebSocket phải có Token xác thực bí mật.<br>• Cơ chế lưu đệm ngoại tuyến (Offline Buffering): Nếu máy tính mất mạng Internet, dữ liệu sự kiện vẫn được ghi an toàn vào SQLite WAL cục bộ và tự đồng bộ khi có mạng lại. |

---

## 3. Sáu Nguyên Tắc Sư Phạm & Nhân Văn Bắt Buộc (NT1 – NT6)

Đề bài HCMUS nhấn mạnh đồ án này **không chỉ là phần mềm kỹ thuật thuần túy**, mà phải tuân thủ triết lý giáo dục nhân văn:

* **NT1 (Minh bạch - Transparency):** Đứa trẻ có quyền biết máy tính đang được quản lý. Phần mềm có icon rõ ràng ở khay hệ thống (System Tray), hiển thị đồng hồ đếm ngược số phút còn lại.
* **NT2 (Tôn trọng quyền riêng tư - Privacy First):** Tuyệt đối không xâm phạm đời tư của trẻ (xem chi tiết ở Danh mục cấm bên dưới).
* **NT3 (Cảnh báo trước - Fair Warning):** Khi sắp hết giờ, phần mềm phải nhắc nhở trước 10 phút, 5 phút, 1 phút để trẻ kịp lưu bài tập đang làm dở, không được đột ngột ngắt ngang làm mất bài.
* **NT4 (Thông điệp hòa nhã - Non-Punitive Tone):** Khi trang web bị chặn, màn hình hiển thị lời giải thích nhẹ nhàng: *"Trang web này không phù hợp với thời gian học tập của bạn"*, không dùng từ ngữ xúc phạm hay dọa nạt.
* **NT5 (Giao tiếp hai chiều - Feedback Loop):** Trẻ có nút bấm "Xin thêm thời gian" (Request Extra Time) gửi thẳng về điện thoại của phụ huynh.
* **NT6 (Tự động phục hồi hệ thống - Safe Recovery):** Khi phụ huynh gỡ cài đặt hoặc tắt phần mềm, toàn bộ cấu hình mạng (DNS) phải được khôi phục nguyên trạng, không làm máy tính bị mất mạng.

---

## 4. Danh Mục Các Tính Năng Bị CẤM TUYỆT ĐỐI (Prohibited Catalog)

> [!CAUTION] CẤM KÊU GỌI HOẶC HIỆN THỰC CÁC TÍNH NĂNG SAU
> Nhóm sinh viên sẽ bị **TRỪ ĐIỂM NẶNG HOẶC ĐÁNH HỎNG** nếu cài đặt các tính năng theo kiểu phần mềm gián điệp (Spyware/Malware):
> 1. **CẤM Chụp ảnh màn hình (Screenshot capture)** bí mật khi trẻ đang dùng máy.
> 2. **CẤM Ghi lại phím gõ (Keylogger)** để ăn cắp mật khẩu hay nội dung chat của trẻ.
> 3. **CẤM Bật Camera/Microphone** từ xa để quay lén trẻ.
> 4. **CẤM Cài đặt Rootkit / Kernel Driver bí mật** can thiệp trái phép vào nhân hệ điều hành Windows.

---

## 5. Phân Chia Vai Trò Nhóm 3 Sinh Viên & Lộ Trình 6 Tuần

| Thành viên | Trách nhiệm chính | Module phụ trách |
| :--- | :--- | :--- |
| **Sinh viên A (Lead & System Engine)** | Kiến trúc hệ thống, Windows Service, Anti-Tamper | `src/agent/service.py`, `src/agent/process_watcher.py`, IPC Localhost Socket |
| **Sinh viên B (Network & Filtering)** | DNS Proxy, Windows Firewall, SafeSearch CNAME | `src/agent/dns_proxy.py`, `restore_dns.bat`, HTTP Blockpage |
| **Sinh viên C (Backend & UI Dashboard)** | Web Dashboard phụ huynh, Database SQLite WAL, Tray UI | `src/server/app.py`, `src/tray/tray_app.py`, WebSocket Dispatcher |

### Lộ trình 6 Tuần Thực Chiến:
* **Tuần 1:** Scaffolding dự án, viết script an toàn khôi phục DNS (`restore_dns.bat`), làm Technical Spikes (Service IPC, SQLite WAL).
* **Tuần 2:** Lập trình lõi DNS Proxy (`dnslib`), cơ chế đo thời gian `GetLastInputInfo`, API đăng nhập phụ huynh (Argon2id).
* **Tuần 3:** Kiểm tra mã băm SHA-256 tiến trình, WebSocket đẩy lệnh thời gian thực (< 5s), đồng bộ sự kiện ngoại tuyến.
* **Tuần 4:** Hoàn thiện giao diện khay hệ thống (Tray UI), cảnh báo 10m/5m/1m, cơ chế ân hạn $\rightarrow$ **SẴN SÀNG CHO MỐC DEMO D1**.
* **Tuần 5:** Hoàn thiện Web Dashboard phụ huynh (HTMX/FastAPI), tính năng xin thêm thời gian (NT5), kiểm thử tải 50 tên miền.
* **Tuần 6:** **ĐÓNG BĂNG MÃ NGUỒN (Strict Code Freeze)** — Không viết thêm code mới, chạy toàn bộ kịch bản kiểm thử trong `TEST_PLAN.md`, chuẩn bị slide và tài liệu để bảo vệ đồ án!

