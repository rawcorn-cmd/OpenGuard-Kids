# OpenGuard Kids — Hệ Thống Hỗ Trợ Quản Lý Máy Tính Trẻ Em

> **Môn học:** Mạng Máy Tính (Computer Networks) — Khoa Công nghệ Thông tin, Trường Đại học Khoa học Tự nhiên, ĐHQG-HCM (HCMUS)  
> **Hình thức:** Đồ án môn học theo nhóm (03 sinh viên) — Thời lượng 07 tuần  
> **Tôn chỉ cốt lõi:** *"Công cụ đồng hành, không phải phần mềm theo dõi lén"* (A companion tool, not spyware)  
> **Nền tảng mục tiêu:** Windows 10 / Windows 11 (x64)  
> **Ngôn ngữ & Công nghệ:** Python 3.11+ · FastAPI · SQLite (WAL mode) · SQLAlchemy · Uvicorn · dnslib · pywin32 · psutil · Argon2id · HTMX

---

## 1. Tổng Quan Dự Án & Định Vị Sản Phẩm

OpenGuard Kids giải quyết bài toán quản lý thời gian và nội dung sử dụng máy tính của trẻ em dưới góc nhìn **minh bạch và tôn trọng quyền riêng tư**, khắc phục triệt để hai nhược điểm của các phần mềm truyền thống:
1. **Khắc phục tính độc đoán/gián điệp (Anti-Spyware):** Tuyệt đối không chụp màn hình, không ghi phím (keylogger), không đọc URL chi tiết, không đọc tin nhắn/email.
2. **Khắc phục sự ngây thơ dễ bị vô hiệu hóa:** Kiến trúc phân tầng chịu lỗi, chạy Windows Service dưới quyền `NT AUTHORITY\LocalSystem` kết hợp quét mã băm nhị phân SHA-256 và DNS Proxy nội bộ.

### Sáu Nguyên Tắc Nhân Văn Bắt Buộc (NT1 – NT6)
* **NT1 (Trẻ biết mình được hỗ trợ):** Biểu tượng khay hệ thống (System Tray Icon) luôn hiển thị; thông báo chào khi khởi động; không có chế độ chạy ẩn (Fail-closed).
* **NT2 (Tối thiểu dữ liệu):** Chỉ ghi nhận 4 trường siêu dữ liệu (Metadata): `process_name`, `domain`, `duration_seconds`, `timestamp`.
* **NT3 (Trẻ có tiếng nói):** Cung cấp nút *"Xin thêm giờ"* và *"Báo chặn nhầm"* gửi trực tiếp về máy chủ phụ huynh.
* **NT4 (Chặn phải giải thích được):** Hiển thị rõ lý do và ai đặt quy định khi chặn ứng dụng/website; không giả vờ ngắt mạng.
* **NT5 (Minh bạch hai chiều):** Trẻ được xem cùng bộ báo cáo sử dụng và xem được nhật ký thay đổi luật (Audit Log) của cha mẹ.
* **NT6 (An toàn có ưu tiên tuyệt đối):** Danh sách miễn chặn vĩnh viễn: Cổng trường học, Tổng đài bảo vệ trẻ em 111, dịch vụ cứu hộ khẩn cấp; không chặn cuộc gọi khẩn cấp của Windows.

---

## 2. Kiến Trúc Kỹ Thuật (Network & System Internals)

```
   [ MÁY CỦA TRẺ - WINDOWS 10/11 x64 ]                         [ MÁY CHỦ QUẢN LÝ (SERVER) ]
 +----------------------------------------+                  +--------------------------------+
 | OGK-Agent: Session 0 (LocalSystem)     |                  | OGK-Server (FastAPI + Uvicorn) |
 |  - Screen-Time Engine (Active/Idle)    |   HTTPS (Sync)   |  - API Xác thực & Cấp Policy   |
 |  - App Controller (psutil + SHA-256)   |<---------------->|  - API Nhận Sự kiện (Metadata) |
 |  - DNS Proxy (dnslib @ 127.0.0.1:53)   |  Heartbeat (60s) |  - WebSocket Dispatcher (< 5s) |
 |  - Local SQLite WAL (Offline Cache)    |                  |  - SQLite Database (WAL Mode)  |
 +----------------------------------------+                  +----------------+---------------+
                     |                                                        |
     Local IPC       | (HTTP 127.0.0.1 + Token bí mật                         | HTTPS
     (Nội bộ máy)    |  trong %ProgramData%)                                  v
                     v                                       +--------------------------------+
 +----------------------------------------+                  | Parent Web Dashboard           |
 | OGK-Agent: Session 1 (User Desktop)    |                  | (Jinja2 + HTMX)                |
 |  - Biểu tượng khay (Taskbar Icon)      |                  |  - Quản lý lịch tuần 7x48      |
 |  - Đồng hồ đếm lùi thời gian còn lại   |                  |  - Biểu đồ thời gian dùng máy  |
 |  - Hộp thoại cảnh báo (10m, 5m, 1m)    |                  |  - Hộp thư duyệt đơn xin giờ   |
 |  - Nút 'Xin thêm giờ' & 'Báo nhầm'     |                  |  - Lịch sử kiểm toán (Audit)   |
 +----------------------------------------+                  +--------------------------------+
```

### Các Kỹ Thuật Trọng Tâm Đánh Giá (Mạng Máy Tính & Hệ Thống)
1. **Lập trình Mạng Tầng Ứng dụng & Giao vận (DNS Proxy UDP 53):**
   * Lắng nghe UDP Port 53 cục bộ bằng `dnslib`.
   * Lọc tên miền và toàn bộ subdomain wildcard ($\ge 95\%$ block rate trên bộ 50 tên miền kiểm thử; 0 lỗi chặn nhầm trên 20 tên miền giáo dục).
   * Kỹ thuật DNS CNAME Rewriting ép buộc SafeSearch trên Google/Bing (`forcesafesearch`).
   * Nhận diện và xử lý nguy cơ lách bộ lọc qua DNS-over-HTTPS (DoH).
   * Script khẩn cấp hoàn trả DNS tự động qua lệnh `netsh` (`scripts/restore_dns.bat`).
2. **Kênh Truyền Thời Gian Thực (WebSocket trên nền TCP):**
   * Đẩy lệnh khẩn cấp (*Khóa ngay, Mở khóa, Cộng 15 phút*) với độ trễ $< 5$ giây.
   * Giao tiếp định kỳ Heartbeat 60 giây và đệm sự kiện ngoại tuyến có Idempotency Key chống ghi trùng.
3. **Lập trình Hệ Thống Windows (Windows Internals):**
   * Giải quyết rào cản **Session 0 Isolation**: Tách biệt Windows Service (`LocalSystem`) và Tray UI (`User Session`).
   * Kênh giao tiếp IPC nội bộ bảo vệ bằng Bearer Token trong `%ProgramData%` phân quyền NTFS.
   * Quét tiến trình `psutil` kết hợp mã băm nhị phân SHA-256 chống đổi tên file `game.exe` $\rightarrow$ `notepad.exe`.
   * Đếm thời gian thực loại trừ giờ nhàn rỗi (`GetLastInputInfo` $> 5$ phút) và chống gian lận lùi đồng hồ hệ thống ($> 60$s rollback).

---

## 3. Cấu Trúc Thư Mục Dự Án

```text
OpenGuard-Kids/
├── docs/                               # Toàn bộ tài liệu chuẩn hóa của đồ án
│   ├── ASSIGNMENT.docx                 # Đề tài gốc của giảng viên
│   ├── REQUIREMENTS.md                 # Đặc tả yêu cầu phần mềm (SRS)
│   ├── ARCHITECTURE.md                 # Đặc tả kiến trúc kỹ thuật chi tiết
│   ├── TEST_PLAN.md                    # Ma trận và kịch bản kiểm thử toàn diện
│   ├── TEAM_PLAN.md                    # Kế hoạch phân công 3 thành viên
│   └── PROJECT_OVERVIEW.md             # Sổ tay kiến trúc & câu hỏi vấn đáp
├── audio_lessons/                      # Giáo trình bài giảng (Markdown + Audio MP3)
│   ├── hoc_phan_01.md & .mp3           # Học phần 1: Triết lý thiết kế nhân văn
│   └── hoc_phan_02.md & .mp3           # Học phần 2: Lập trình hệ thống Windows
├── src/                                # Mã nguồn ứng dụng
│   ├── common/                         # Shared schemas, DTOs, constants, security
│   ├── server/                         # FastAPI Backend API & WebSocket Hub
│   ├── agent/                          # Windows Service, Screen-Time, DNS Proxy
│   └── tray/                           # Desktop Tray UI (Session 1)
├── data/                               # Dữ liệu phân loại (200+ entries) & Test domains
├── scripts/                            # Tiện ích cứu hộ DNS (.bat), service installer
├── tests/                              # Bộ kiểm thử tự động (pytest)
├── AGENTS.md                           # Nguyên tắc phát triển của Lead Engineer
├── PROGRESS.md                         # Bảng theo dõi tiến độ đồ án
└── TODO.md                             # Danh sách công việc chi tiết
```

---

## 4. Phân Công Thành Viên Trong Nhóm 3 Sinh Viên

* **Sinh viên A (Hệ Thống Windows & Agent):** Lõi Windows Service (Session 0), Desktop Tray UI (Session 1), kênh IPC Bearer Token, bộ đếm Active/Idle Screen-time, quét mã băm SHA-256, kịch bản Demo D1.
* **Sinh viên B (Mạng, DNS Proxy & Dữ Liệu):** DNS Proxy UDP 53 (`dnslib`), SafeSearch CNAME rewriting, đối phó DoH, kịch bản khôi phục an toàn `restore_dns.bat`, bộ dữ liệu phân loại $\ge 200$ mục, bộ test suite 50 tên miền.
* **Sinh viên C (Backend Server & Dashboard):** FastAPI, Uvicorn, SQLite WAL, Argon2id Auth, WebSocket Dispatcher ($< 5$s), 90-day Auto-purge worker, Web Dashboard (HTMX) và ma trận lịch tuần 7x48.

---

## 5. Hướng Dẫn Cài Đặt Môi Trường & Chạy Thử

### Yêu Cầu Hệ Thống
* Python 3.11 hoặc mới hơn.
* Hệ điều hành Windows 10/11 x64 (đối với thành phần Agent & Tray UI thực tế trên máy trẻ).
* Môi trường phát triển và máy chủ API có thể chạy trên cả Windows, Linux và macOS.

### Cài Đặt Môi Trường Ảo (Virtual Environment)

#### 👉 Dành cho Windows PowerShell:
```powershell
# 1. Tạo môi trường ảo:
py -m venv .venv

# 2. Kích hoạt môi trường ảo:
.\.venv\Scripts\Activate.ps1

# 3. Cài đặt các gói phụ thuộc:
pip install -r requirements.txt
```

> [!NOTE] **Xử lý các lỗi thường gặp trên Windows PowerShell:**
> * **Lỗi 1 (Không nhận diện lệnh `source`):** Lệnh `source .venv/bin/activate` chỉ dùng cho Linux/macOS. Trên Windows, bạn bắt buộc phải dùng lệnh: `.\.venv\Scripts\Activate.ps1`.
> * **Lỗi 2 (PowerShell chặn chạy script - ExecutionPolicy):** Nếu thấy thông báo đỏ `...running scripts is disabled on this system...`, chạy lệnh sau một lần để cấp quyền:
>   ```powershell
>   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
>   ```
>   Sau đó gõ lại: `.\.venv\Scripts\Activate.ps1`
> * **Lỗi 3 (`python3` không tìm thấy):** Windows không có lệnh `python3`. Hãy dùng lệnh **`py`** hoặc **`python`**.

#### 🐧 Dành cho Linux / macOS:
```bash
# 1. Tạo môi trường ảo:
python3 -m venv .venv

# 2. Kích hoạt môi trường ảo:
source .venv/bin/activate

# 3. Cài đặt các gói phụ thuộc:
pip install -r requirements.txt
```

### Các Lệnh Thực Thi Hệ Thống (Turnkey Commands)

#### 🌟 1. Chạy Trình Diễn Toàn Diện Tương Tác (Live Defense Showcase):
```bash
python scripts/run_demo.py
```
*Tự động khởi động Backend Server, Agent Service, Blockpage, và mở Menu tương tác trực quan 10 kịch bản phục vụ báo cáo bảo vệ đồ án.*

#### 🚀 2. Chạy Từng Thành Phần Độc Lập:
```bash
# Chạy Parent Backend Server & Dashboard (Cổng 8000)
python -m src.server.main

# Chạy Windows Service Agent Daemon (Session 0)
python -m src.agent.main

# Chạy Desktop Tray UI Client (Session 1)
python -m src.tray.main
```

---

## 6. Chạy Kiểm Thử Tự Động (Automated Testing)

```bash
# 1. Chạy toàn bộ 53 Unit & Integration Tests:
pytest tests/ -v

# 2. Chạy kịch bản nghiệm thu đầu-cuối E2E (6 scenarios F1-F4, NT1-NT6):
python scripts/e2e_acceptance_verification.py
```

---

## 7. Liên Kết Tài Liệu Kỹ Thuật

* [docs/SYSTEM_MECHANISMS_AND_INTEGRATION.md](file:///home/cornar/Projects/OpenGuard-Kids/docs/SYSTEM_MECHANISMS_AND_INTEGRATION.md): **Tài liệu Tổng Hợp Toàn Bộ Chức Năng, Cơ Chế & Liên Kết Hệ Thống**.
* [OpenGuard_Kids_Toan_Bo_Co_Che_Thanh_Phan.pdf](file:///home/cornar/Projects/OpenGuard-Kids/OpenGuard_Kids_Toan_Bo_Co_Che_Thanh_Phan.pdf): **Báo Cáo Kỹ Thuật Đặc Tả Chuyên Sâu (PDF 12 Trang Xuất Bản)**.
* [docs/REQUIREMENTS.md](file:///home/cornar/Projects/OpenGuard-Kids/docs/REQUIREMENTS.md): Đặc tả yêu cầu phần mềm đầy đủ.
* [docs/ARCHITECTURE.md](file:///home/cornar/Projects/OpenGuard-Kids/docs/ARCHITECTURE.md): Kiến trúc hệ thống và hợp đồng IPC/API.
* [docs/FINAL_REPORT.md](file:///home/cornar/Projects/OpenGuard-Kids/docs/FINAL_REPORT.md): Báo cáo tổng kết đồ án chính thức (Section 2.3).
* [docs/DEFENSE_GUIDE.md](file:///home/cornar/Projects/OpenGuard-Kids/docs/DEFENSE_GUIDE.md): Kịch bản Demo D1 và Bộ 10 câu hỏi bảo vệ đồ án kèm mã nguồn.
* [docs/TEST_PLAN.md](file:///home/cornar/Projects/OpenGuard-Kids/docs/TEST_PLAN.md): Ma trận 51/51 kiểm thử nghiệm thu tự động (100% Passed).
* [docs/PRIVACY.md](file:///home/cornar/Projects/OpenGuard-Kids/docs/PRIVACY.md): Cam kết pháp lý bảo vệ dữ liệu trẻ em theo Nghị định 13/2023/NĐ-CP.
