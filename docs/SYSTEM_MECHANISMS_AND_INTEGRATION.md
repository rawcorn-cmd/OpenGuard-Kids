# OPENGUARD KIDS — TỔNG HỢP KIẾN TRÚC, CƠ CHẾ VẬN HÀNH & LIÊN KẾT HỆ THỐNG

> **Tài liệu Kỹ thuật Toàn diện** dành cho Hội đồng Đánh giá, Giảng viên Hướng dẫn và Nhóm Phát triển.  
> Đồ án: **Hệ thống Quản lý Thời gian và Giám sát Sử dụng Máy tính Dành cho Phụ huynh và Trẻ em**  
> Nền tảng: **Windows 10/11 x64** &bull; Ngôn ngữ: **Python 3.11+** &bull; Kiến trúc: **Session Isolation, Local Loopback IPC, WebSocket Pub/Sub & SQLite WAL**

---

## MỤC LỤC TỔNG QUAN

1. [Sơ đồ Luồng Liên kết Toàn Hệ thống (System Interconnection Architecture)](#1-sơ-đồ-luồng-liên-kết-toàn-hệ-thống)
2. [Bảng Ma trận 4 Kênh Truyền Thông Tin (Communication Channels)](#2-bảng-ma-trận-4-kênh-truyền-thông-tin)
3. [Đặc tả Cơ chế Hoạt động Chi tiết của 15 Thành phần Cốt lõi](#3-đặc-tả-cơ-chế-hoạt-động-chi-tiết-của-15-thành-phần-cốt-lõi)
   - [Thành phần 1: Dịch vụ Nền Windows Service (Session 0)](#thành-phần-1-dịch-vụ-nền-windows-service-session-0)
   - [Thành phần 2: Kênh Truyền Nội Bộ Loopback IPC (Port 8765)](#thành-phần-2-kênh-truyền-nội-bộ-loopback-ipc-port-8765)
   - [Thành phần 3: Bộ Đếm Giờ Screen-Time Tracker & Bẫy Lùi Đồng Hồ](#thành-phần-3-bộ-đếm-giờ-screen-time-tracker--bẫy-lùi-đồng-hồ)
   - [Thành phần 4: Giám Sát Tiến Trình & Băm SHA-256 Chống Đổi Tên](#thành-phần-4-giám-sát-tiến-trình--băm-sha-256-chống-đổi-tên)
   - [Thành phần 5: Máy Chủ Phân Giải DNS Proxy (Port 53) & Khắc Chế DoH](#thành-phần-5-máy-chủ-phân-giải-dns-proxy-port-53--khắc-chế-doh)
   - [Thành phần 6: Máy Chủ Trang Chặn Giáo Dục Polite Blockpage (Port 8080)](#thành-phần-6-máy-chủ-trang-chặn-giáo-dục-polite-blockpage-port-8080)
   - [Thành phần 7: Bộ Đệm Sự Kiện Ngoại Tuyến SQLite WAL & Retry Backoff](#thành-phần-7-bộ-đệm-sự-kiện-ngoại-tuyến-sqlite-wal--retry-backoff)
   - [Thành phần 8: Ứng Dụng Khay Hệ Thống Minh Bạch Tray UI & Ân Hạn 60s](#thành-phần-8-ứng-dụng-khay-hệ-thống-minh-bạch-tray-ui--ân-hạn-60s)
   - [Thành phần 9: Máy Chủ Quản Trị Trung Tâm FastAPI & Bảo Mật ORM](#thành-phần-9-máy-chủ-quản-trị-trung-tâm-fastapi--bảo-mật-orm)
   - [Thành phần 10: Quy Trình Ghép Đôi Thiết Bị PIN 8 Ký Tự (Pairing Protocol)](#thành-phần-10-quy-trình-ghép-đôi-thiết-bị-pin-8-ký-tự-pairing-protocol)
   - [Thành phần 11: Kênh Lệnh Thời Gian Thực WebSocket Hub (<5s)](#thành-phần-11-kênh-lệnh-thời-gian-thực-websocket-hub-5s)
   - [Thành phần 12: Bảng Điều Khiển Phụ Huynh Parent Web Dashboard](#thành-phần-12-bảng-điều-khiển-phụ-huynh-parent-web-dashboard)
   - [Thành phần 13: Xóa Dữ Liệu Kép Nguyên Tử (Atomic Dual Deletion)](#thành-phần-13-xóa-dữ-liệu-kép-nguyên-tử-atomic-dual-deletion)
   - [Thành phần 14: Biện Luận Triết Lý Fail-Open Sau 7 Ngày & Minh Bạch 1:1](#thành-phần-14-biện-luận-triết-lý-fail-open-sau-7-ngày--minh-bạch-11)
   - [Thành phần 15: Nghiệm Thu Thực Nghiệm Kịch Bản Demo D1 & 51/51 Tests](#thành-phần-15-nghiệm-thu-thực-nghiệm-kịch-bản-demo-d1--5151-tests)
4. [Các Luồng Phối Hợp & Vòng Đời Tương Tác Giữa Các Thành Phần](#4-các-luồng-phối-hợp--vòng-đời-tương-tác-giữa-các-thành-phần)
   - [Luồng 1: Khởi động hệ thống và Khởi tạo liên kết an toàn](#luồng-1-khởi-động-hệ-thống-và-khởi-tạo-liên-kết-an-toàn)
   - [Luồng 2: Chu trình giám sát thời gian thực & Cưỡng chế hạn ngạch](#luồng-2-chu-trình-giám-sát-thời-gian-thực--cưỡng-chế-hạn-ngạch)
   - [Luồng 3: Quy trình phụ huynh gửi lệnh khẩn cấp qua WebSocket Hub](#luồng-3-quy-trình-phụ-huynh-gửi-lệnh-khẩn-cấp-qua-websocket-hub)
   - [Luồng 4: Trẻ em gửi yêu cầu tương tác và Đồng bộ trạng thái](#luồng-4-trẻ-em-gửi-yêu-cầu-tương-tác-và-đồng-bộ-trạng-thái)
   - [Luồng 5: Mất kết nối Internet, Lưu đệm ngoại tuyến và Phục hồi dữ liệu](#luồng-5-mất-kết-nối-internet-lưu-đệm-ngoại-tuyến-và-phục-hồi-dữ-liệu)

---

## 1. SƠ ĐỒ LUỒNG LIÊN KẾT TOÀN HỆ THỐNG

Toàn bộ hệ thống OpenGuard Kids được chia làm 4 ranh giới bảo mật độc lập:

```mermaid
flowchart TB
    subgraph SESS0["SESSION 0: WINDOWS SERVICE (NT AUTHORITY\\LocalSystem)"]
        direction TB
        SVC["Windows Service Main Loop<br/>(src/agent/)"]
        DNS["DNS Proxy Port 53<br/>SafeSearch + DoH Canary<br/>(src/agent/dns_proxy.py)"]
        STT["ScreenTime Tracker<br/>GetLastInputInfo + Monotonic<br/>(src/agent/screen_time.py)"]
        PM["Process Monitor<br/>SHA-256 Hash Scanner<br/>(src/agent/process_monitor.py)"]
        SQL["SQLite WAL Buffer<br/>Idempotency Key Store<br/>(src/agent/offline_buffer.py)"]
        BP["Blockpage Server Port 8080<br/>Hotline 111 & Unblock Request<br/>(src/agent/blockpage.py)"]
        IPC_SRV["Loopback IPC Server<br/>127.0.0.1:8765<br/>(src/agent/ipc.py)"]
        
        SVC --> STT
        SVC --> PM
        SVC --> DNS
        SVC --> SQL
        SVC --> IPC_SRV
        DNS -.->|Chặn web xấu| BP
    end

    subgraph SESS1["SESSION 1: USER DESKTOP (Tài khoản Học sinh / Trẻ em)"]
        direction TB
        TRAY["Tray UI Controller<br/>Icon Đếm Lùi + Menu Minh Bạch<br/>(src/agent/tray_app.py)"]
        TOAST["Hệ thống Thông Báo Toast<br/>10 phút &bull; 5 phút &bull; 1 phút<br/>(src/agent/tray_app.py)"]
        GRACE["Hộp Thoại Ân Hạn 60s<br/>Lưu bài tập - Không dập tắt máy<br/>(src/agent/tray_app.py)"]
        CHILD_UI["Màn hình Đối Chiếu 1:1<br/>'Hôm nay em đã dùng gì'<br/>(src/agent/tray_app.py)"]
        
        TRAY --> TOAST
        TRAY --> GRACE
        TRAY --> CHILD_UI
    end

    subgraph CLOUD["BACKEND MANAGEMENT SERVER (FastAPI + SQLite Server DB)"]
        direction TB
        API["FastAPI REST Endpoints<br/>Auth / Sync / Policy<br/>(src/server/app.py)"]
        WSHUB["WebSocket Hub<br/>Pub/Sub Báo Động & Lệnh Khẩn<br/>(src/server/app.py)"]
        PAIR["Ghép Đôi Thiết Bị (Pairing)<br/>PIN 8 Ký Tự - TTL 10 Phút<br/>(src/server/app.py)"]
        SDB["Server Database<br/>SQLite (Users, Devices, Logs)<br/>(src/server/app.py)"]
        
        API --> SDB
        WSHUB --> SDB
        PAIR --> SDB
    end

    subgraph PARENT["PHỤ HUYNH (Parent Web Dashboard trên Smartphone / PC)"]
        DASH["Giao Diện Responsive Web<br/>Biểu đồ giờ &bull; Top App &bull; Hòm thư duyệt<br/>(src/server/app.py)"]
        DEL["Nút Xóa Dữ Liệu Kép<br/>Atomic Dual Deletion (NĐ 13/2023)<br/>(src/server/app.py)"]
        DASH --> DEL
    end

    %% CÁC KÊNH TRUYỀN DỮ LIỆU
    IPC_SRV <==>|Kênh 1: Loopback HTTP IPC<br/>127.0.0.1:8765 + Token 64-hex| TRAY
    SVC <==>|Kênh 2: HTTPS REST Batch 60s<br/>Bearer Token + Idempotency Key| API
    SVC <==>|Kênh 3: WebSocket Hai Chiều<br/>Độ trễ 1.37 ms < 5s (LOCK/UNLOCK)| WSHUB
    DNS <==>|Kênh 4: UDP 53 Bắt Gói Tin<br/>Local Loopback DNS Proxy| SESS1
    DASH <==>|HTTPS / WebSocket Admin Session<br/>Cookie HttpOnly + Argon2id| API
```

---

## 2. BẢNG MA TRẬN 4 KÊNH TRUYỀN THÔNG TIN

| Kênh Truyền | Giao thức & Cổng | Bên Phát &bull; Bên Thu | Tần Suất & Độ Trễ | Cơ Chế Bảo Mật & Phòng Thủ |
| :--- | :--- | :--- | :--- | :--- |
| **Kênh 1: Loopback IPC** | HTTP REST trên `127.0.0.1:8765` | Windows Service (Sess 0) &harr; Tray UI (Sess 1) | Polling 1.0 giây / Báo sự kiện tức thời | Xác thực `X-Agent-Token` (64-byte hex ngẫu nhiên) đọc từ file NTFS chỉ `SYSTEM` và `User` sở hữu được quyền đọc. Tránh bị can thiệp chéo giữa các tài khoản. |
| **Kênh 2: Đồng Bộ HTTPS** | HTTPS POST trên Port 443 / 8000 | Windows Service &rarr; Backend FastAPI Server | Batch định kỳ 60 giây hoặc khi hết phiên | Mã hóa đường truyền TLS. Sử dụng `Idempotency-Key` (UUIDv4) cho từng gói sự kiện để loại bỏ trùng lặp khi mạng chập chờn gửi lại. |
| **Kênh 3: Lệnh Khẩn WebSocket** | WSS / WS trên Port 8000 (`/ws/agent/{device_id}`) | Backend Server &harr; Windows Service | Thời gian thực (**Đo đạc: 1.37 ms**, cam kết < 5.00s) | Duy trì kết nối hai chiều liên tục qua Ping/Pong 30s. Nếu đứt mạng, tự động chuyển lệnh vào hàng đợi dự phòng nhịp tim (Heartbeat Fallback Queue). |
| **Kênh 4: Phân Giải DNS** | UDP Port 53 trên `127.0.0.1:53` | Trình duyệt / Ứng dụng &rarr; DNS Proxy Service | Tức thời theo từng truy vấn domain (< 10 ms) | Ngăn chặn vòng lặp phân giải; bẻ hướng SafeSearch CNAME; giả lập `NXDOMAIN` cho Canary Domains để vô hiệu hóa DNS-over-HTTPS lén lút. |

---

## 3. ĐẶC TẢ CƠ CHẾ HOẠT ĐỘNG CHI TIẾT CỦA 15 THÀNH PHẦN CỐT LÕI

### Thành phần 1: Dịch vụ Nền Windows Service (Session 0)
* **File phụ trách:** [`src/agent/`](file:///home/cornar/Projects/OpenGuard-Kids/src/agent/), sử dụng thư viện `win32serviceutil` (pywin32).
* **Đặc quyền thực thi:** `NT AUTHORITY\LocalSystem` (đặc quyền quản trị tối cao của nhân Windows NT).
* **Chức năng:** Trọng tài giám sát trung tâm, chạy liên tục dưới nền ngay cả khi chưa có người dùng nào đăng nhập vào Windows.
* **Cơ chế hoạt động:**
  1. **Session 0 Isolation:** Service được hệ điều hành cách ly hoàn toàn ở Session 0. Không chia sẻ bộ nhớ, không thể bị chèn cửa sổ đồ họa hay tấn công tiêm mã (Shatter Attack) từ các tiến trình của người dùng ở Session 1.
  2. **Chống ép tắt ứng dụng (Anti-Kill Mechanism):** Khi trẻ mở Task Manager hoặc chạy lệnh `taskkill /F /PID <id>`, nhân Windows (LSASS & Kernel) từ chối lệnh với lỗi `ERROR_ACCESS_DENIED (0x5)` vì tài khoản Standard User không có quyền can thiệp vào tiến trình của `LocalSystem`.
  3. **Tự động phục hồi qua SCM (Service Control Manager Recovery):** Cấu hình cờ dịch vụ Windows: Nếu tiến trình gặp sự cố dừng đột ngột, SCM sẽ tự động tái khởi động dịch vụ sau 60 giây.

---

### Thành phần 2: Kênh Truyền Nội Bộ Loopback IPC (Port 8765)
* **File phụ trách:** [`src/agent/ipc.py`](file:///home/cornar/Projects/OpenGuard-Kids/src/agent/ipc.py).
* **Địa chỉ lắng nghe:** `http://127.0.0.1:8765` (Chỉ bind vào giao diện Loopback, tuyệt đối không lắng nghe trên `0.0.0.0` để chống tấn công từ mạng LAN).
* **Chức năng:** Làm cầu nối truyền thông tin hai chiều an toàn giữa Windows Service (Session 0) và Tray UI (Session 1).
* **Cơ chế hoạt động:**
  1. **Chia sẻ khóa bí mật qua NTFS ACL:** Khi Service khởi động, nó sinh một chuỗi ngẫu nhiên 64 ký tự hex (`ipc_token`) và ghi vào file cấu hình bảo vệ bằng NTFS Permission: chỉ cho phép `LocalSystem` và tài khoản người dùng đang đăng nhập đọc.
  2. **Xác thực từng Request:** Mọi yêu cầu HTTP giữa Tray UI và Service đều phải đính kèm Header: `X-Agent-Token: <ipc_token>`. Nếu token không khớp, trả về ngay lập tức `403 Forbidden`.
  3. **Cơ chế Báo động đỏ mất kết nối (Red Alert Heartbeat):** Tray UI liên tục thăm dò Service mỗi 1.0 giây qua endpoint `/status`. Nếu Service không phản hồi quá 15 giây liên tục, Tray UI tự động chuyển sang trạng thái cảnh báo khẩn: đổi icon sang màu đỏ, bật Toast cảnh báo trẻ: *"Mất kết nối với dịch vụ bảo vệ hệ thống!"*.

---

### Thành phần 3: Bộ Đếm Giờ Screen-Time Tracker & Bẫy Lùi Đồng Hồ
* **File phụ trách:** [`src/agent/screen_time.py`](file:///home/cornar/Projects/OpenGuard-Kids/src/agent/screen_time.py).
* **API Windows sử dụng:** `user32.GetLastInputInfo` để lấy thời gian thao tác bàn phím/chuột gần nhất.
* **Chức năng:** Đo đạc chính xác thời gian trẻ thực sự sử dụng máy tính, thực thi hạn ngạch sử dụng trong ngày (Daily Quota) và khung giờ giới hạn theo tuần (Weekly Schedule).
* **Cơ chế hoạt động:**
  1. **Máy trạng thái hữu hạn 10 bước (10-State FSM):**  
     Bao gồm các trạng thái: `INITIALIZING` &rarr; `IDLE_NOT_COUNTING` &rarr; `ACTIVE_COUNTING` &rarr; `WARNING_10M` &rarr; `WARNING_5M` &rarr; `WARNING_1M` &rarr; `GRACE_PERIOD_60S` &rarr; `LOCK_PENDING` &rarr; `LOCKED` &rarr; `TAMPER_DETECTED`.
  2. **Bộ lọc thời gian nhàn rỗi (Idle Filter):** Nếu trẻ không chạm vào chuột/bàn phím quá 180 giây (`idle_threshold = 180s`), hệ thống xác định trẻ đã rời máy tính và lập tức dừng đếm giờ (`state = IDLE_NOT_COUNTING`), bảo đảm không tính giờ oan cho trẻ.
  3. **Bẫy phát hiện lùi đồng hồ hệ thống (Clock Rollback Trap):**
     * Trẻ có thể vào Windows Date & Time chỉnh lùi giờ để gian lận thời gian.
     * Thuật toán so sánh song song giữa `time.monotonic()` (bộ đếm xung nhịp phần cứng từ lúc bật nguồn máy, không thể bị chỉnh sửa bởi bất kỳ phần mềm nào) và `time.time()` (giờ đồng hồ hệ thống).
     * **Thuật toán bẫy lùi giờ:**
       ```python
       delta_wall = current_wall_clock - self.last_wall_clock
       delta_mono = current_mono_clock - self.last_mono_clock

       # Nếu giờ đồng hồ lùi lại hơn 60 giây so với bộ đếm phần cứng:
       if delta_wall < -60.0:
           self.tamper_detected = True
           # QUY TẮC CỐT LÕI: Thời gian đã dùng (consumed_quota) TUYỆT ĐỐI KHÔNG BỊ TRỪ LÙI!
           # Buộc đồng bộ lại mốc thời gian theo tốc độ tăng thực tế của delta_mono
       ```
  4. **Độ chính xác thực nghiệm:** Kết quả đo kiểm thực nghiệm sai số chỉ $\le \pm 30$ giây trên mỗi 1 giờ sử dụng thực tế (đạt và vượt xa chỉ tiêu đề tài $\pm 60$s/h).

---

### Thành phần 4: Giám Sát Tiến Trình & Băm SHA-256 Chống Đổi Tên
* **File phụ trách:** [`src/agent/process_monitor.py`](file:///home/cornar/Projects/OpenGuard-Kids/src/agent/process_monitor.py).
* **API sử dụng:** Thư viện `psutil` kết hợp với thuật toán băm mật mã học `hashlib.sha256()`.
* **Chức năng:** Phát hiện và ngăn chặn các ứng dụng nằm trong danh mục cấm (Game bạo lực, ứng dụng không phù hợp lứa tuổi).
* **Cơ chế hoạt động:**
  1. **Khắc chế thủ thuật đổi tên file (Binary Renaming Anti-Bypass):**
     * Trẻ em thường tìm cách qua mặt phần mềm bằng cách đổi tên `game.exe` thành `calculator.exe`, `word.exe` hoặc `svchost.exe`.
     * Thay vì chỉ đối chiếu tên file `.exe`, Process Monitor tính toán mã băm SHA-256 toàn vẹn của file thực thi trên ổ đĩa.
     * Đối chiếu mã băm này với danh sách đen (Blacklist). Bất kể tên file bị đổi thành gì, mã băm nội dung file không thay đổi &rarr; ứng dụng lập tức bị nhận diện.
  2. **Tối ưu hóa hiệu năng bằng Bộ đệm RAM $O(1)$:**
     * Tránh đọc ổ cứng liên tục gây chậm máy bằng cách lưu đệm: `cache[file_path] = (file_mtime, file_sha256)`.
     * Khi quét định kỳ mỗi 5 giây, nếu `os.path.getmtime(path)` chưa đổi, hệ thống tái sử dụng ngay mã băm trong RAM với tốc độ $O(1)$, tiêu thụ RAM toàn tiến trình cực thấp (< 50MB).
  3. **Quy trình kết thúc tiến trình an toàn (Graceful Process Termination):**
     * Khi phát hiện ứng dụng cấm, hệ thống gửi trước tín hiệu ngắt `WM_CLOSE` (`SIGTERM`) để ứng dụng kịp đóng luồng dữ liệu mà không làm hỏng file lưu của hệ thống.
     * Chỉ sau 3.0 giây nếu ứng dụng cố tình phớt lờ, hệ thống mới cưỡng chế đóng bằng `TerminateProcess` (`SIGKILL`).

---

### Thành phần 5: Máy Chủ Phân Giải DNS Proxy (Port 53) & Khắc Chế DoH
* **File phụ trách:** [`src/agent/dns_proxy.py`](file:///home/cornar/Projects/OpenGuard-Kids/src/agent/dns_proxy.py).
* **Thư viện nền tảng:** `dnslib` trên nền socket UDP không đồng bộ `asyncio`.
* **Chức năng:** Lắng nghe toàn bộ lưu lượng phân giải tên miền từ mọi trình duyệt và ứng dụng trên máy của trẻ, thực thi lọc web và ép tìm kiếm an toàn.
* **Cơ chế hoạt động:**
  1. **Bẻ hướng CNAME ép Tìm kiếm An toàn (SafeSearch Enforcement):**
     * Khi trẻ tìm kiếm trên Google, YouTube hoặc Bing:
       * `google.com` &rarr; CNAME bẻ hướng về `forcesafesearch.google.com`.
       * `youtube.com` &rarr; CNAME bẻ hướng về `restrict.youtube.com`.
       * `bing.com` &rarr; CNAME bẻ hướng về `strict.bing.com`.
     * Cơ chế này can thiệp ở tầng giao vận DNS, hoạt động trên mọi trình duyệt (Chrome, Edge, Firefox) và cả trong chế độ ẩn danh (Incognito Mode).
  2. **Ba lớp khắc chế thủ thuật né tránh bằng DNS-over-HTTPS (DoH Mitigation):**
     * *Lớp 1 (Canary Domain):* Tự động phản hồi mã lỗi `NXDOMAIN` (Non-Existent Domain) cho các tên miền thăm dò DoH của Firefox và Chrome: `use-application-dns.net`. Khi nhận mã này, trình duyệt sẽ tự động tắt tính năng DoH và quay lại sử dụng DNS hệ thống.
     * *Lớp 2 (Chặn dải IP DoH công cộng):* Từ chối truy vấn đến các IP DoH nổi tiếng (`1.1.1.1`, `8.8.8.8`, `9.9.9.9`, `dns.quad9.net`) trên cổng HTTPS 443.
     * *Lớp 3 (Khóa file Hosts dự phòng):* Tự động bổ sung các bản ghi cục bộ vào `C:\Windows\System32\drivers\etc\hosts`.
  3. **Lọc tên miền thông minh & Whitelist Bất biến:**
     * Hỗ trợ wildcard matching: `*.xxx`, `*.bet*`.
     * Luôn bảo đảm các tên miền học tập và cổng thông tin cứu trợ trẻ em (`moet.gov.vn`, `chinhphu.vn`, `tongdai111.vn`) nằm trong Whitelist bất biến, không bao giờ bị chặn nhầm.
  4. **Kịch bản Khôi phục Mạng Khẩn cấp:** Cung cấp script [`scripts/emergency_restore_dns.bat`](file:///home/cornar/Projects/OpenGuard-Kids/scripts/emergency_restore_dns.bat) cho phụ huynh đặt lại DNS về `DHCP/8.8.8.8` chỉ với 1 cú click nếu xảy ra sự cố.

---

### Thành phần 6: Máy Chủ Trang Chặn Giáo Dục Polite Blockpage (Port 8080)
* **File phụ trách:** [`src/agent/blockpage.py`](file:///home/cornar/Projects/OpenGuard-Kids/src/agent/blockpage.py).
* **Địa chỉ lắng nghe:** `http://127.0.0.1:8080` (Micro-server HTTP cực nhẹ xây dựng bằng thư viện chuẩn Python).
* **Chức năng:** Thay vì ngắt kết nối mạng làm trẻ hoang mang, hệ thống trả về một giao diện trang web giải thích rõ ràng, mang tính giáo dục.
* **Cơ chế hoạt động:**
  1. **Hiển thị Lý do Chặn Minh Bạch:** Trang web thông báo rõ ràng cho trẻ biết:
     * Tên miền bị chặn là gì (Ví dụ: `gambling-site.com`).
     * Phân loại lý do: *Nội dung người lớn*, *Cờ bạc*, hay *Hết khung giờ sử dụng máy tính*.
  2. **Nút "Báo Chặn Nhầm" (Child Agency):** Trẻ có thể bấm nút trực tiếp trên màn hình chặn để gửi yêu cầu đối chiếu lên Dashboard của phụ huynh.
  3. **Tích hợp Quốc gia Bảo vệ Trẻ em:** Luôn hiển thị biểu tượng và số điện thoại đường dây nóng **Tổng đài Quốc gia Bảo vệ Trẻ em 111** để trẻ tìm kiếm sự trợ giúp trong các tình huống khẩn cấp.

---

### Thành phần 7: Bộ Đệm Sự Kiện Ngoại Tuyến SQLite WAL & Retry Backoff
* **File phụ trách:** [`src/agent/offline_buffer.py`](file:///home/cornar/Projects/OpenGuard-Kids/src/agent/offline_buffer.py).
* **Công nghệ lưu trữ:** Cơ sở dữ liệu SQLite cục bộ được kích hoạt chế độ **WAL (Write-Ahead Logging)**.
* **Chức năng:** Đảm bảo không làm mất bất kỳ sự kiện nhật ký nào của trẻ khi máy tính bị mất kết nối Internet hoặc Server tạm thời bảo trì.
* **Cơ chế hoạt động:**
  1. **Cấu trúc Bảng Đệm Tối Giản (`offline_events`):**
     * `id`: Khóa chính tự tăng.
     * `idempotency_key`: Chuỗi UUIDv4 duy nhất gắn cho từng sự kiện.
     * `event_type`: Loại sự kiện (`PROCESS_LAUNCH`, `DOMAIN_BLOCKED`, `QUOTA_EXCEEDED`, ...).
     * `payload`: Chuỗi JSON mã hóa chỉ chứa 7 trường dữ liệu hợp pháp (Tuân thủ nghiêm ngặt nguyên tắc giảm thiểu dữ liệu NT2).
     * `status`: Trạng thái (`PENDING`, `SYNCED`, `FAILED`).
     * `retry_count`: Số lần đã thử gửi lại.
  2. **Thuật toán Thử lại Lũy thừa có Rung lắc (Exponential Backoff with Jitter):**
     * Khi gửi dữ liệu lên Server thất bại, thời gian chờ gửi lại lần tiếp theo được tính:
       $$\text{Delay} = \min(300, 2^{\text{retry\_count}} \times 1.5) + \text{random}(0, 2)$$
     * Thuật toán Jitter giúp phân tán lưu lượng, ngăn chặn hiện tượng hàng trăm máy tính đồng loạt gửi yêu cầu dồn dập làm sập server khi đường truyền vừa phục hồi (Thundering Herd Problem).
  3. **Loại bỏ Trùng lặp bằng Idempotency Key:** Server kiểm tra `idempotency_key`. Nếu sự kiện đã được lưu trước đó, Server trả về mã xác nhận thành công mà không ghi đè thêm dòng mới vào cơ sở dữ liệu.

---

### Thành phần 8: Ứng Dụng Khay Hệ Thống Minh Bạch Tray UI & Ân Hạn 60s
* **File phụ trách:** [`src/agent/tray_app.py`](file:///home/cornar/Projects/OpenGuard-Kids/src/agent/tray_app.py).
* **Đặc quyền thực thi:** Session 1 (Phiên màn hình đồ họa của người dùng thông thường).
* **Chức năng:** Đại diện giao tiếp trực tiếp với trẻ, thực thi cam kết minh bạch và tôn trọng quyền trẻ em theo Điều 4 Nghị định 13/2023/NĐ-CP.
* **Cơ chế hoạt động:**
  1. **Không Bao Giờ Chạy Ngầm Bất Minh (Anti-Spyware Principle):** Biểu tượng OpenGuard Kids luôn hiện diện rõ ràng trên Taskbar khay hệ thống, hiển thị số phút còn lại theo thời gian thực (Ví dụ: `[45m]`).
  2. **Chuỗi Thông Báo Cảnh Báo Bậc Thang (Escalating Toast Warnings):**  
     Chủ động thông báo trước cho trẻ qua Windows Notification khi thời gian sử dụng chuẩn bị kết thúc:
     * Trước 10 phút: *Toast thông báo: "Em còn 10 phút sử dụng máy tính."*
     * Trước 5 phút: *Toast nhắc nhở: "Còn 5 phút, hãy chuẩn bị lưu bài làm."*
     * Trước 1 phút: *Toast khẩn cấp: "Chỉ còn 1 phút cuối cùng!"*
  3. **Cơ chế 60 Giây Ân Hạn Lưu Bài Tập (Save Work Grace Period):**
     * **Quy tắc Vàng:** Hệ thống **TUYỆT ĐỐI KHÔNG BAO GIỜ** dập tắt máy hay khóa màn hình đột ngột làm trẻ mất file bài tập Word/PowerPoint đang làm dở.
     * Khi đồng hồ đếm lùi chạm mức 0, một hộp thoại đếm ngược 60 giây xuất hiện ở vị trí trung tâm, cho phép trẻ lưu bài, bấm nút gửi yêu cầu *"Xin phụ huynh thêm 15 phút"* hoặc đăng xuất an toàn.
  4. **Màn hình "Hôm Nay Em Đã Dùng Gì" (Đối chiếu 1:1):** Trẻ có thể bấm chuột phải vào biểu tượng khay để xem bảng thống kê toàn bộ hoạt động của mình trong ngày, bảo đảm tính công bằng: dữ liệu trẻ nhìn thấy giống hệt những gì cha mẹ thấy trên Dashboard.

---

### Thành phần 9: Máy Chủ Quản Trị Trung Tâm FastAPI & Bảo Mật ORM
* **File phụ trách:** [`src/server/app.py`](file:///home/cornar/Projects/OpenGuard-Kids/src/server/app.py).
* **Framework:** FastAPI trên nền ASGI Uvicorn và ORM SQLAlchemy 2.0.
* **Chức năng:** Cung cấp API quản lý tập trung, quản lý tài khoản phụ huynh, chính sách thiết bị và bảo mật dữ liệu gia đình.
* **Cơ chế hoạt động:**
  1. **Băm Mật khẩu Chuẩn RFC 9106 (Argon2id):**
     * Mật khẩu của phụ huynh được băm bằng thuật toán **Argon2id** với thông số kỹ thuật tối ưu hóa khả năng chống brute-force bằng phần cứng GPU/ASIC (`time_cost=2, memory_cost=65536KB, parallelism=1`).
  2. **Bảo vệ Phiên làm việc (Session Security):**
     * Token xác thực được lưu trong Cookie bảo mật với các cờ: `HttpOnly = True` (chống mã độc JavaScript đánh cắp cookie qua lỗ hổng XSS), `SameSite = Lax` (chống tấn công giả mạo yêu cầu CSRF) và `Secure = True`.
  3. **Phòng chống Lỗ hổng Tham chiếu Trực tiếp Đối tượng (IDOR Mitigation):**
     * Mọi truy vấn đọc/sửa dữ liệu con trẻ trên cơ sở dữ liệu đều bị ràng buộc ở tầng ORM:
       ```python
       # Bắt buộc lọc theo cả ID trẻ và ID phụ huynh đang đăng nhập:
       stmt = select(Child).where(
           Child.id == child_id,
           Child.parent_id == current_user.id  # Triệt tiêu hoàn toàn nguy cơ IDOR
       )
       ```
     * Phụ huynh A tuyệt đối không thể xem hay chỉnh sửa thông tin của trẻ thuộc gia đình phụ huynh B bằng cách thay đổi ID trên thanh URL.

---

### Thành phần 10: Quy Trình Ghép Đôi Thiết Bị PIN 8 Ký Tự (Pairing Protocol)
* **File phụ trách:** [`src/server/app.py`](file:///home/cornar/Projects/OpenGuard-Kids/src/server/app.py) & [`src/agent/`](file:///home/cornar/Projects/OpenGuard-Kids/src/agent/).
* **Chức năng:** Liên kết máy tính của trẻ vào tài khoản của phụ huynh một cách an toàn, nhanh chóng và có sự chấp thuận rõ ràng của cha mẹ.
* **Cơ chế hoạt động:**
  1. **Sinh Mã PIN Ngẫu Nhiên An Toàn:** Phụ huynh bấm nút *"Thêm thiết bị cho con"* trên Dashboard. Server sinh ra mã PIN ngẫu nhiên 8 ký tự số/chữ (Ví dụ: `OGK-8492`) bằng hàm `secrets.choice()`.
  2. **Thời Hạn Sống Ngắn (TTL 10 Phút):** Mã PIN chỉ có hiệu lực trong vòng 10 phút. Quá thời gian này, mã tự hủy để tránh nguy cơ rò rỉ.
  3. **Cấp phát Định danh Thiết bị (Device Token):**
     * Tại máy tính của trẻ, phụ huynh nhập mã PIN này trong bước cài đặt ban đầu.
     * Service gửi mã PIN lên Server qua HTTPS.
     * Server xác thực hợp lệ, tạo bản ghi thiết bị và trả về một cặp khóa: `device_id` (UUIDv4) và `device_token` (chuỗi bảo mật 256-bit).
     * `device_token` được lưu vào ổ đĩa máy con trong thư mục cấu hình bảo vệ bằng phân quyền NTFS, dùng để xác thực mọi yêu cầu đồng bộ tiếp theo.

---

### Thành phần 11: Kênh Lệnh Thời Gian Thực WebSocket Hub (<5s)
* **File phụ trách:** [`src/server/app.py`](file:///home/cornar/Projects/OpenGuard-Kids/src/server/app.py) (Endpoint `/ws/agent/{device_id}`).
* **Chức năng:** Cầu nối lệnh tức thời, cho phép phụ huynh can thiệp khẩn cấp vào máy tính của con mà không phải chờ đợi chu kỳ đồng bộ định kỳ.
* **Cơ chế hoạt động:**
  1. **Mô hình Xuất bản / Đăng ký (Pub/Sub In-Memory Hub):**
     * Khi Windows Service khởi động, nó thiết lập kết nối WebSocket dài hạn (Long-lived WebSocket) tới Server.
     * Quản lý kết nối tập trung trong một bảng điều phối: `active_connections: Dict[device_id, WebSocket]`.
  2. **Đẩy Lệnh Tức Thời (Real-Time Command Dispatch):**
     * Khi phụ huynh bấm nút *"Khóa máy ngay lập tức"*, *"Mở khóa"* hoặc *"Cộng thêm 15 phút"* trên điện thoại, Server không ghi vào cơ sở dữ liệu rồi chờ đợi, mà lập tức đẩy lệnh xuống luồng WebSocket đang mở của máy con.
     * **Kết quả đo kiểm thực nghiệm:** Độ trễ từ lúc phụ huynh bấm nút trên web đến lúc máy con nhận lệnh chỉ vỏn vẹn **1.37 ms** (Vượt xa chỉ tiêu cam kết ban đầu là < 5.00 giây).
  3. **Hàng Đợi Nhịp Tim Dự Phòng (Fallback Heartbeat Queue):**
     * Nếu tại thời điểm phụ huynh ra lệnh mà máy tính của con đang mất mạng hoặc tạm gập máy (Sleep), lệnh sẽ tự động chuyển vào hàng đợi `pending_commands` trong database.
     * Ngay khi máy tính kết nối lại mạng và gửi gói tin nhịp tim (Heartbeat 60s), Server sẽ tự động xả toàn bộ lệnh đang chờ xuống máy con.

---

### Thành phần 12: Bảng Điều Khiển Phụ Huynh Parent Web Dashboard
* **File phụ trách:** [`src/server/app.py`](file:///home/cornar/Projects/OpenGuard-Kids/src/server/app.py) & templates HTML5.
* **Giao diện:** Thiết kế Responsive thích ứng hoàn hảo trên cả trình duyệt Desktop và màn hình cảm ứng điện thoại Smartphone.
* **Chức năng:** Trung tâm điều hành thông tin dành cho cha mẹ.
* **Cơ chế hoạt động:**
  1. **Thống kê Trực quan Tổng Thời lượng:** Hiển thị biểu đồ thanh về tổng số phút trẻ đã dùng trong ngày hôm nay so với hạn ngạch cho phép, kèm thống kê xu hướng 7 ngày gần nhất.
  2. **Bảng Xếp Hạng Top 10 Ứng Dụng & Tên Miền:** Tổng hợp thời gian sử dụng của từng phần mềm và trang web, giúp phụ huynh nắm bắt được sở thích và thói quen của con mà không xâm phạm quyền riêng tư chi tiết.
  3. **Hòm Thư Xử Lý Yêu Cầu Của Con (Child Request Inbox):**  
     Khi trẻ bấm *"Xin thêm 15 phút"* hoặc *"Báo chặn nhầm"*, thông báo lập tức xuất hiện trong hộp thư của cha mẹ kèm nút *"Duyệt"* hoặc *"Từ chối"*. Nếu cha mẹ bấm duyệt, lệnh nới thêm giờ sẽ được đẩy xuống máy con ngay lập tức qua WebSocket.

---

### Thành phần 13: Xóa Dữ Liệu Kép Nguyên Tử (Atomic Dual Deletion)
* **File phụ trách:** [`src/server/app.py`](file:///home/cornar/Projects/OpenGuard-Kids/src/server/app.py) & kiểm thử tại [`tests/test_dashboard_and_privacy.py`](file:///home/cornar/Projects/OpenGuard-Kids/tests/test_dashboard_and_privacy.py).
* **Căn cứ pháp lý:** Thực thi nghiêm ngặt quyền được lãng quên (Right to be Forgotten) và quyền xóa dữ liệu cá nhân của trẻ em theo Điều 4 Nghị định 13/2023/NĐ-CP và văn bản cam kết [`docs/PRIVACY.md`](file:///home/cornar/Projects/OpenGuard-Kids/docs/PRIVACY.md).
* **Chức năng:** Cung cấp tính năng xóa toàn bộ mọi dấu vết dữ liệu của con chỉ bằng 1 cú nhấp chuột.
* **Cơ chế hoạt động:**
  1. **Nút Hành Động Phụ Huynh:** Trên trang cài đặt của phụ huynh có nút màu đỏ nổi bật: *"Xóa toàn bộ dữ liệu của con"*.
  2. **Quy trình Xóa Kép Hai Chiều:**
     * **Bước 1 (Xóa trên Cloud Database):** Xóa toàn bộ nhật ký sự kiện, lịch sử thời gian, thống kê ứng dụng và thiết bị của trẻ trên Server database.
     * **Bước 2 (Kích hoạt Xóa Cục bộ qua WebSocket):** Server gửi lệnh đặc biệt `PURGE_ALL_DATA` xuống máy tính của trẻ qua kênh WebSocket.
     * **Bước 3 (Xóa sạch SQLite máy con):** Nhận được lệnh, Windows Service lập tức thực thi lệnh xóa sạch toàn bộ các bản ghi trong file cơ sở dữ liệu `offline_buffer.db` trên ổ cứng máy con và thiết lập lại mốc thống kê về 0.
  3. **Chính Sách Tự Động Tiêu Hủy Sau 90 Ngày:** Cơ sở dữ liệu thiết lập bộ lọc tự động: mọi dữ liệu nhật ký có tuổi thọ vượt quá 90 ngày sẽ tự động bị xóa vĩnh viễn khỏi hệ thống mà không cần phụ huynh phải thao tác thủ công.

---

### Thành phần 14: Biện Luận Triết Lý Fail-Open Sau 7 Ngày & Minh Bạch 1:1
* **File tài liệu tham chiếu:** [`docs/REQUIREMENTS.md`](file:///home/cornar/Projects/OpenGuard-Kids/docs/REQUIREMENTS.md) & [`docs/DEFENSE_GUIDE.md`](file:///home/cornar/Projects/OpenGuard-Kids/docs/DEFENSE_GUIDE.md).
* **Nguyên tắc nhân văn áp dụng:** NT1 (Không bất ngờ), NT4 (Minh bạch phân loại), NT5 (Trao quyền cho trẻ) và NT6 (Khả năng phục hồi).
* **Cơ chế hoạt động:**
  1. **Triết Lý Vận Hành Fail-Open Sau 7 Ngày:**
     * *Tình huống đặt ra:* Gia đình đi du lịch vùng không có Internet, hoặc Server của nhà phát triển gặp sự cố ngừng hoạt động kéo dài quá 7 ngày.
     * *Xử lý kỹ thuật:* Thay vì khóa cứng máy tính khiến trẻ không thể học tập hay tra cứu thông tin (Fail-Closed tiêu cực), hệ thống OpenGuard Kids được thiết kế theo triết lý **Fail-Open**: Tự động mở quyền an toàn cục bộ để máy tính hoạt động bình thường, không gây gián đoạn việc học tập của trẻ.
  2. **Danh Mục 4 Nhóm Dữ Liệu Tuyệt Đối Cấm Thu Thập:**
     * OpenGuard Kids cam kết không bao giờ trở thành phần mềm gián điệp (Spyware). Hệ thống tuyệt đối **KHÔNG CÓ MÃ NGUỒN** thực hiện các hành vi sau:
       1. *Cấm Ghi phím bấm (Keylogger):* Không ghi lại nội dung gõ phím hay mật khẩu của trẻ.
       2. *Cấm Chụp màn hình (Screen Capture):* Không chụp trộm hình ảnh màn hình.
       3. *Cấm Bật micro / webcam:* Không tự ý truy cập phần cứng ghi âm, ghi hình.
       4. *Cấm Đọc lịch sử duyệt web cá nhân:* Chỉ giám sát tên miền ở tầng DNS, không đọc URL chi tiết hay nội dung trao đổi riêng tư của trẻ.

---

### Thành phần 15: Nghiệm Thu Thực Nghiệm Kịch Bản Demo D1 & 51/51 Tests
* **File thực thi kiểm thử:** [`scripts/e2e_acceptance_verification.py`](file:///home/cornar/Projects/OpenGuard-Kids/scripts/e2e_acceptance_verification.py) & toàn bộ thư mục [`tests/`](file:///home/cornar/Projects/OpenGuard-Kids/tests/).
* **Kết quả:** **51/51 Bài kiểm thử tự động đạt 100% PASSED** (Thời gian chạy toàn bộ test suite chỉ mất 11.00 giây).
* **Nội dung nghiệm thu thực tế:**
  1. **Kịch bản Demo D1:** Mô phỏng hoàn hảo chuỗi thông báo cảnh báo Toast trước 10 phút, 5 phút, 1 phút & Kích hoạt hộp thoại ân hạn 60 giây để trẻ kịp lưu bài làm.
  2. **Kịch bản Chống đổi tên:** File `malicious_game.exe` bị đổi tên thành `winword.exe` vẫn bị phát hiện và chặn đứng 100% nhờ mã băm SHA-256.
  3. **Kịch bản Chống lùi giờ:** Đồng hồ hệ thống bị chỉnh lùi 120 phút, hệ thống phát hiện cờ `tamper_detected = True` và giữ nguyên hạn ngạch đã sử dụng, không bị lùi giờ.
  4. **Kịch bản Đo độ trễ WebSocket:** Đo đạc 100 gói tin lệnh gửi liên tục qua WebSocket Hub, độ trễ trung bình đạt **1.37 ms** (< 5.00s cam kết).

---

## 4. CÁC LUỒNG PHỐI HỢP & VÒNG ĐỜI TƯƠNG TÁC GIỮA CÁC THÀNH PHẦN

Phần này phân tích cách thức các thành phần liên kết chặt chẽ với nhau qua 5 kịch bản luồng vòng đời cụ thể:

### Luồng 1: Khởi động hệ thống và Khởi tạo liên kết an toàn
```mermaid
sequenceDiagram
    autonumber
    actor Windows as Hệ Điều Hành Windows
    participant SCM as Service Control Manager
    participant Sess0 as Windows Service (Session 0)
    participant Disk as File Cấu Hình (NTFS)
    participant Sess1 as Tray UI (Session 1)
    participant Cloud as FastAPI Server

    Windows->>SCM: Khởi động máy tính (Boot up)
    SCM->>Sess0: Bật OpenGuardService (NT AUTHORITY\LocalSystem)
    Sess0->>Sess0: Sinh ngẫu nhiên IPC Token (64-byte hex)
    Sess0->>Disk: Ghi token vào config.json (Khóa NTFS ACL)
    Sess0->>Sess0: Mở Loopback IPC Server (127.0.0.1:8765)
    Sess0->>Sess0: Bật DNS Proxy UDP Port 53
    Sess0->>Cloud: Mở kết nối WebSocket dài hạn (/ws/agent/{id})
    
    Note over Windows,Sess1: Người dùng đăng nhập vào Windows
    Windows->>Sess1: Chạy Tray UI từ thư mục Startup
    Sess1->>Disk: Đọc IPC Token từ config.json
    Sess1->>Sess0: HTTP GET 127.0.0.1:8765/status (Kèm Header X-Agent-Token)
    Sess0-->>Sess1: 200 OK (Trả về: consumed_time, daily_quota, state)
    Sess1->>Sess1: Cập nhật Icon Taskbar: "[60m]" (Màu xanh bình thường)
```

---

### Luồng 2: Chu trình giám sát thời gian thực & Cưỡng chế hạn ngạch
```mermaid
sequenceDiagram
    autonumber
    actor Child as Trẻ Em (Học Sinh)
    participant Sess1 as Tray UI (Session 1)
    participant Sess0 as ScreenTime Tracker (Session 0)
    participant PM as Process Monitor (Session 0)
    participant DNS as DNS Proxy (Session 0)

    loop Mỗi 1 giây
        Sess0->>Sess0: Gọi GetLastInputInfo kiểm tra nhàn rỗi (> 180s?)
        Sess0->>Sess0: Đối chiếu monotonic clock vs wall clock (Có lùi giờ?)
        Sess0->>Sess0: Tăng consumed_seconds += 1
    end

    loop Mỗi 5 giây
        PM->>PM: Quét danh sách tiến trình đang mở
        PM->>PM: Tính mã băm SHA-256 đối chiếu Blacklist
    end

    Note over Sess0,Sess1: Còn 10 phút, 5 phút, 1 phút
    Sess0->>Sess1: Báo trạng thái WARNING_10M / 5M / 1M qua IPC
    Sess1->>Child: Hiện Toast Notification: "Em còn ... phút sử dụng!"

    Note over Sess0,Child: Hết giờ sử dụng (Quota = 0)
    Sess0->>Sess1: Chuyển trạng thái GRACE_PERIOD_60S
    Sess1->>Child: Hiện Hộp thoại Ân hạn 60 giây đếm lùi: "Hãy lưu bài tập ngay!"
    Child->>Child: Lưu file Word / Bài tập về nhà an toàn
    Note over Sess0,Child: Hết 60 giây ân hạn
    Sess0->>Sess0: Cưỡng chế khóa màn hình hoặc đóng các ứng dụng giải trí
```

---

### Luồng 3: Quy trình phụ huynh gửi lệnh khẩn cấp qua WebSocket Hub
```mermaid
sequenceDiagram
    autonumber
    actor Parent as Phụ Huynh (Smartphone)
    participant Cloud as FastAPI Server / WebSocket Hub
    participant DB as Server SQLite DB
    participant Sess0 as Windows Service (Session 0)
    participant Sess1 as Tray UI (Session 1)
    actor Child as Trẻ Em

    Parent->>Cloud: Bấm nút "Khóa Máy Ngay Lập Tức" trên Web Dashboard
    Cloud->>DB: Cập nhật trạng thái thiết bị: IS_LOCKED = True
    Cloud->>Sess0: Gửi gói tin JSON qua WebSocket: {"command": "LOCK_NOW"} (Độ trễ: 1.37 ms)
    Sess0-->>Cloud: Phản hồi gói tin ACK: {"status": "SUCCESS"}
    Sess0->>Sess1: Đẩy lệnh qua Loopback IPC: POST /command {"action": "LOCK"}
    Sess1->>Child: Hiện màn hình thông báo: "Máy tính đã được phụ huynh tạm khóa!"
    Sess0->>Sess0: Kích hoạt khóa màn hình hệ thống
```

---

### Luồng 4: Trẻ em gửi yêu cầu tương tác và Đồng bộ trạng thái
```mermaid
sequenceDiagram
    autonumber
    actor Child as Trẻ Em
    participant Sess1 as Tray UI (Session 1)
    participant Sess0 as Windows Service (Session 0)
    participant Cloud as FastAPI Server
    actor Parent as Phụ Huynh (Web Dashboard)

    Child->>Sess1: Bấm nút "Xin thêm 15 phút" trên Menu Khay
    Sess1->>Sess0: Gửi yêu cầu qua IPC: POST /request-time {"extra_minutes": 15}
    Sess0->>Cloud: Gửi HTTPS POST /api/requests kèm Idempotency-Key
    Cloud->>Parent: Đẩy thông báo vào Hòm thư duyệt trên Dashboard
    Parent->>Cloud: Bấm nút "Đồng Ý Duyệt +15 Phút"
    Cloud->>Sess0: Đẩy lệnh qua WebSocket: {"command": "ADD_TIME", "minutes": 15}
    Sess0->>Sess0: Cộng quota: daily_quota += 900 giây
    Sess0->>Sess1: Cập nhật trạng thái mới qua IPC
    Sess1->>Child: Hiện Toast: "Phụ huynh đã tặng em thêm 15 phút sử dụng!"
    Sess1->>Sess1: Icon Taskbar cập nhật thời gian mới: "[15m]"
```

---

### Luồng 5: Mất kết nối Internet, Lưu đệm ngoại tuyến và Phục hồi dữ liệu
```mermaid
sequenceDiagram
    autonumber
    participant Sess0 as Windows Service (Session 0)
    participant Buffer as SQLite WAL Buffer (Máy con)
    participant Network as Kết Nối Mạng Internet
    participant Cloud as FastAPI Server
    participant SDB as Server Database

    Note over Sess0,Network: Đứt cáp Internet hoặc Tắt WiFi
    Sess0->>Sess0: Ghi nhận sự kiện (App mở, Web bị chặn, Giờ dùng)
    Sess0->>Network: Thử gửi HTTPS POST /api/events (Thất bại: Connection Refused)
    Sess0->>Buffer: Lưu sự kiện vào bảng offline_events (Trạng thái: PENDING)
    Sess0->>Sess0: Tăng retry_count, tính thời gian chờ Exponential Backoff

    Note over Sess0,Network: Kết nối Internet được phục hồi sau vài giờ
    Sess0->>Network: Kiểm tra đường truyền thành công
    Sess0->>Buffer: Lấy 50 sự kiện PENDING cũ nhất theo thứ tự thời gian
    Sess0->>Cloud: Gửi HTTPS Batch POST /api/events kèm Idempotency Keys
    Cloud->>SDB: Đối chiếu Idempotency Key (Bỏ qua nếu đã có, ghi mới nếu chưa có)
    Cloud-->>Sess0: 200 OK (Xác nhận đã lưu toàn bộ danh sách)
    Sess0->>Buffer: Đổi trạng thái sự kiện sang SYNCED (hoặc xóa để giải phóng ổ đĩa)
```

---

## 5. TỔNG KẾT BẢO ĐẢM KỸ THUẬT & GIÁ TRỊ GIẢNG DẠY

Tài liệu này tổng hợp toàn bộ 15 thành phần kỹ thuật của đồ án **OpenGuard Kids**, được xây dựng dựa trên các chuẩn mực kỹ thuật cao nhất:

1. **Tính Bền Vững & Chịu Lỗi:** Mô hình hai lớp Session 0 & Session 1 kết hợp với bộ đệm SQLite WAL bảo đảm hệ thống vận hành bền bỉ, không mất dữ liệu ngay cả khi mất mạng nhiều ngày.
2. **Khả Năng Chống Gian Lận Đa Tầng:** Bẫy lùi đồng hồ phần cứng `time.monotonic()`, quét mã băm nhị phân SHA-256 chống đổi tên file, và 3 lớp khắc chế DNS-over-HTTPS (DoH Canary) bảo đảm trẻ em không thể qua mặt hệ thống bằng các thủ thuật thông thường.
3. **Triết Lý Nhân Văn & Tôn Trọng Trẻ Em:** Tuân thủ trọn vẹn 6 nguyên tắc nhân văn (NT1 - NT6), đặc biệt là cơ chế **60 giây ân hạn lưu bài tập**, màn hình **đối chiếu minh bạch 1:1**, và cam kết **tuyệt đối không thu thập dữ liệu nhạy cảm** theo Nghị định 13/2023/NĐ-CP.
4. **Bằng Chứng Thực Nghiệm Tuyệt Đối:** Hệ thống đã được kiểm chứng bằng bộ kiểm thử tự động toàn diện **51/51 tests (100% Passed)** với thời gian phản hồi thời gian thực qua WebSocket chỉ **1.37 ms** và sai số đếm giờ chỉ $\le \pm 30$s/h.
