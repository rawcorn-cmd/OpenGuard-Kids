# OPENGUARD KIDS — KẾ HOẠCH NÂNG CẤP HỆ THỐNG TOÀN DIỆN (PRODUCTION UPGRADE PLAN)
## Hiện Thực Hóa Môi Trường Windows 10/11 x64: Windows Service Session 0, Desktop GUI Session 1, Bộ Script 1-Chạm & Parent Web Dashboard

---

> **Tên dự án:** OpenGuard Kids — Hệ thống Hỗ trợ Quản lý Máy tính Dành cho Phụ huynh và Trẻ em  
> **Khóa học:** Đồ án môn học Mạng máy tính (Computer Networks) — Khoa Công nghệ Thông tin, Trường Đại học Khoa học Tự nhiên, ĐHQG TP.HCM (HCMUS)  
> **Nhóm thực hiện:** 03 Sinh viên | **Thời lượng thực hiện:** 07 Tuần  
> **Nền tảng mục tiêu:** Windows 10 / Windows 11 (x64) &bull; Python 3.11+ &bull; FastAPI &bull; pywin32 &bull; SQLite WAL  
> **Văn bản căn cứ cốt lõi:** `docs/ASSIGNMENT.md`, `docs/REQUIREMENTS.md`, `docs/ARCHITECTURE.md`, `docs/DEFENSE_GUIDE.md`, `docs/TEST_PLAN.md`  
> **Hiện trạng kiểm định:** Đạt **53/53 Automated Unit Tests (100% PASS)** và **6/6 Kịch bản E2E Acceptance (100% PASS)**  
> **Mục tiêu tài liệu:** Bản đặc tả kỹ thuật và lộ trình thực thi hoàn chỉnh chuyển đổi giải pháp từ mức thử nghiệm dòng lệnh (CLI) sang sản phẩm phần mềm vận hành thực tế trên Windows 10/11 x64, bảo toàn nguyên vẹn 100% bộ kiểm thử tự động hiện có.

---

## MỤC LỤC TỔNG THỂ

1. [PHẦN 1: TỔNG QUAN NÂNG CẤP & TUÂN THỦ TRIỆT ĐỂ DOCS/ASSIGNMENT.MD](#phần-1-tổng-quan-nâng-cấp--tuân-thủ-triệt-để-docsassignmentmd)
   - 1.1 Bối cảnh Đồ án & Mục tiêu Chuyển đổi Thực tế
   - 1.2 Hiện trạng Kỹ thuật & Di sản Kiểm thử (53 Tests & 6 Kịch bản E2E)
   - 1.3 Mô hình 4 Thành phần Phân tách Bắt buộc
   - 1.4 Ma trận Tuân thủ 100% Nguyên tắc Cốt lõi (NT1–NT6, F1–F5) & Pháp lý Luật Trẻ em 2016
2. [PHẦN 2: KIẾN TRÚC KỸ THUẬT HỆ THỐNG & CƠ CHẾ PHÂN TÁCH SESSION (WINDOWS 10/11 X64)](#phần-2-kiến-trúc-kỹ-thuật-hệ-thống--cơ-chế-phân-tách-session-windows-1011-x64)
   - 2.1 Phân tích Session 0 Isolation & Rào cản Kỹ thuật WinSta0
   - 2.2 Sơ đồ Kiến trúc Khối & Sơ đồ Trình tự Giao tiếp Toàn hệ thống
   - 2.3 Kênh Loopback IPC HTTP (127.0.0.1:8765) với Token 64-Hex
   - 2.4 Cơ chế Phân quyền File Token qua NTFS ACL (icacls)
   - 2.5 Hợp đồng Thông điệp IPC (JSON Contracts) & Tự vệ Mất Kết nối (Red Alert > 15s)
3. [PHẦN 3: THIẾT KẾ CHI TIẾT NATIVE DESKTOP GUI CHO TRAY UI (SESSION 1)](#phần-3-thiết-kế-chi-tiết-native-desktop-gui-cho-tray-ui-session-1)
   - 3.1 Lựa chọn Công nghệ GUI: pystray + Pillow + tkinter (< 5MB RAM, Khởi động < 150ms)
   - 3.2 Biểu tượng Taskbar Động (Dynamic Badge) & Context Menu Chuột Phải
   - 3.3 Chuỗi Thông Báo Leo Thang Thời Gian Thực (Escalating Toasts 10m - 5m - 1m)
   - 3.4 Hộp thoại Ân Hạn 60 Giây Non-Focus-Stealing (Hỗ trợ Ctrl+S Lưu Bài)
   - 3.5 Màn hình Khóa Đồ Họa Toàn Màn Hình (Fullscreen Lock Overlay với Hotline 111 & Xin 15p)
   - 3.6 Màn hình Minh Bạch "Hôm nay em đã dùng gì" (NT5 Two-Way Transparency)
4. [PHẦN 4: THIẾT KẾ TRIỂN KHAI WINDOWS SERVICE NATIVE & DNS PROTECTION (SESSION 0)](#phần-4-thiết-kế-triển-khai-windows-service-native--dns-protection-session-0)
   - 4.1 Cấu trúc Module `src/agent/windows_service.py` bằng pywin32 ServiceFramework
   - 4.2 Vòng đời Dịch vụ & Tích hợp Service Control Manager (SCM)
   - 4.3 Cấu hình SCM Auto-Recovery Policy khi Sự cố (`sc.exe failure`)
   - 4.4 DNS Proxy UDP Port 53 & Chiến lược Khắc chế DoH 3 Lớp
   - 4.5 Cưỡng chế SafeSearch qua Ghi Đè Bản Ghi DNS CNAME
   - 4.6 Máy chủ Trang Chặn Thân Thiện Polite Blockpage (HTTP Port 8080)
5. [PHẦN 5: BỘ SCRIPT TRIỂN KHAI & GỠ BỎ 1-CHẠM (ADMINISTRATOR BATCH SCRIPTS)](#phần-5-bộ-script-triển-khai--gỡ-bỏ-1-chạm-administrator-batch-scripts)
   - 5.1 Cơ chế Tự Động Kiểm tra & Nâng Quyền UAC Administrator Chuẩn
   - 5.2 Toàn văn & Cơ chế `install_service.bat`
   - 5.3 Toàn văn & Cơ chế `enable_dns_protection.bat`
   - 5.4 Toàn văn & Cơ chế `setup_tray_startup.bat`
   - 5.5 Toàn văn & Cơ chế `uninstall_all.bat`
   - 5.6 Tích hợp Script Cứu Hộ Mạng Khẩn Cấp `restore_dns.bat`
6. [PHẦN 6: NÂNG CẤP TOÀN DIỆN PARENT WEB DASHBOARD & WEBSOCKET EMERGENCY CHANNEL](#phần-6-nâng-cấp-toàn-diện-parent-web-dashboard--websocket-emergency-channel)
   - 6.1 Kiến trúc Responsive Web: FastAPI + Jinja2 + Tailwind CSS
   - 6.2 Bố cục & Đặc tả Chi tiết 5 Tab Chức năng
   - 6.3 Kênh Lệnh Khẩn Cấp Hai Chiều WebSocket (< 5s Latency) & Fallback Queue (60s)
   - 6.4 Toàn vẹn Chính sách HMAC-SHA256 & Phiên bản Đơn điệu
7. [PHẦN 7: LỘ TRÌNH THỰC HIỆN 7 TUẦN & PHÂN CÔNG CHI TIẾT CHO 3 SINH VIÊN](#phần-7-lộ-trình-thực-hiện-7-tuần--phân-công-chi-tiết-cho-3-sinh-viên)
   - 7.1 Bảng Phân Chia Vai Trò, Trách Nhiệm & Ranh Giới Mô-đun (SV1, SV2, SV3)
   - 7.2 Ma trận Trách nhiệm RACI
   - 7.3 Kế hoạch Tiến độ Tuần W1 đến W7 & Các Cột mốc Nghiệm thu M1–M7
   - 7.4 Quy trình Phối hợp Nhóm, Git Flow & Kiểm thử Chéo
8. [PHẦN 8: KẾ HOẠCH KIỂM THỬ HỒI QUY & BẢO TOÀN 100% BỘ TEST HIỆN CÓ](#phần-8-kế-hoạch-kiểm-thử-hồi-quy--bảo-toàn-100-bộ-test-hiện-có)
   - 8.1 Nguyên lý Platform Wrapper Pattern & Zero-Regression Architecture
   - 8.2 Danh mục Chi tiết 53/53 Unit Tests & Phương án Bảo vệ
   - 8.3 Danh mục Chi tiết 6/6 Kịch bản E2E Acceptance Verification & Phương án Bảo vệ
   - 8.4 Tiêu chuẩn Nghiệm thu Kỹ thuật & Câu lệnh Kiểm định Đóng gói
   - 8.5 Ma trận Nhận diện Rủi ro & Giải pháp Phòng ngừa (Risk & Mitigation)

---

## PHẦN 1: TỔNG QUAN NÂNG CẤP & TUÂN THỦ TRIỆT ĐỂ DOCS/ASSIGNMENT.MD

### 1.1 Bối cảnh Đồ án & Mục tiêu Chuyển đổi Thực tế

Đồ án môn học Mạng máy tính (Computer Networks) tại Khoa Công nghệ Thông tin, Trường Đại học Khoa học Tự nhiên - ĐHQG TP.HCM (HCMUS) quy định nhóm thực hiện gồm đúng **03 sinh viên**, triển khai trong thời lượng **07 tuần**. Sản phẩm hướng đến đối tượng sử dụng là gia đình Việt Nam có con nhỏ trong độ tuổi tiểu học và trung học cơ sở (6–15 tuổi).

Mục tiêu của giai đoạn nâng cấp này là đưa giải pháp từ mức độ khung kiểm thử dòng lệnh (CLI prototypes) phát triển thành một hệ thống phần mềm hoàn chỉnh, sẵn sàng cài đặt và vận hành mượt mà trên nền tảng **Windows 10 / Windows 11 x64**. Toàn bộ kế hoạch bám sát 100% tài liệu gốc `docs/ASSIGNMENT.md`, tuyệt đối không thay đổi kiến trúc hoặc áp dụng các công nghệ ngoài phạm vi môn học (không dùng framework nặng nề, không biến tướng sang ứng dụng đám mây phức tạp).

### 1.2 Hiện trạng Kỹ thuật & Di sản Kiểm thử (53 Tests & 6 Kịch bản E2E)

Tính đến thời điểm hiện tại, nền tảng mã nguồn OpenGuard Kids đã xây dựng hoàn chỉnh toàn bộ logic mạng, bảo mật và quản lý thời gian cốt lõi, đạt tỷ lệ tin cậy tuyệt đối:
* **Bộ kiểm thử đơn vị & tích hợp (Unit & Integration Tests):** Đạt **53/53 tests PASSED (100%)** khi chạy `.venv/bin/pytest tests/ -v` trong thời gian 13.1 giây.
* **Kịch bản nghiệm thu toàn trình (E2E Acceptance Verification):** Đạt **6/6 scenarios PASSED (100%)** khi chạy `.venv/bin/python scripts/e2e_acceptance_verification.py`.
* **Script cứu hộ mạng gốc (`restore_dns.bat`):** Đã kiểm định cơ chế hoàn nguyên DNS về DHCP an toàn cho các giao diện Wi-Fi và Ethernet.

Nguyên tắc bất di bất dịch của Kế hoạch Nâng Cấp: **BẢO TOÀN 100% KẾT QUẢ KIỂM THỬ NÀY — KHÔNG CHẤP NHẬN BẤT KỲ MỘT LỖI HỒI QUY (ZERO REGRESSION) NÀO.**

### 1.3 Mô hình 4 Thành phần Phân tách Bắt buộc

Hệ thống được thiết kế tuân thủ nghiêm ngặt mô hình 4 thành phần phân tách theo Mục 2 `docs/ASSIGNMENT.md`:

```
   MÁY TÍNH CỦA TRẺ (Windows 10/11 x64)                MÁY CHỦ QUẢN TRỊ (LAN / VPS)
 ┌────────────────────────────────────────┐          ┌───────────────────────────────┐
 │  OGK-Agent (Python 3.11+)              │          │  OGK-Server (FastAPI+Uvicorn) │
 │  ┌──────────────────────────────────┐  │  HTTPS   │  ┌─────────────────────────┐  │
 │  │ Windows Service (Session 0)      │  │ TLS 1.2+ │  │ /auth  /enroll  /policy │  │
 │  │  - Policy Enforcer (HMAC-SHA256) │◄─┼──────────┼─►│ /events /commands       │  │
 │  │  - Screen-time Tracker (Monotonic│  │ Heartbeat│  │ /reports /audit         │  │
 │  │  - App Controller (SHA-256 Hash) │  │    60s   │  └─────────────────────────┘  │
 │  │  - Local DNS Proxy 127.0.0.1:53  │  │          │  │  SQLite (WAL Mode)      │  │
 │  │  - Blockpage Server :8080 (HTTP) │  │WebSocket │  │  SQLAlchemy 2.0         │  │
 │  │  - Offline SQLite Cache (WAL)    │  │ lenh gap │  │  (1:n:m Data Model)     │  │
 │  │  └──────────────────────────────────┘  │  (< 5s)  │  └─────────────────────────┘  │
 │                   ▲                    │          └───────────────▲───────────────┘
 │                   │ Loopback HTTP IPC  │                          │
 │                   │ 127.0.0.1:8765     │                          │ HTTPS
 │                   │ + Bearer Token     │                          │ (Mobile Responsive)
 │                   ▼                    │                          │
 │  ┌──────────────────────────────────┐  │                 ┌────────┴────────┐
 │  │ Tray UI (Session 1 User)         │  │                 │ Dashboard Phụ   │
 │  │  - Taskbar Icon & Remaining Time │  │                 │ Huynh (Web UI)  │
 │  │  - Escalating Toasts (10m,5m,1m) │  │                 │ Jinja2 + CSS/JS │
 │  │  - 60s Save-Work Grace Dialog    │  │                 │ Lich - Bao cao  │
 │  │  - Full-screen Lock Overlay      │  │                 └─────────────────┘
 │  │  - Màn hình 'Hôm nay em đã dùng' │  │
 │  └──────────────────────────────────┘  │
 └────────────────────────────────────────┘
```

1. **Windows Service (Session 0):** Chạy dưới đặc quyền `NT AUTHORITY\LocalSystem`, quản lý mọi nghiệp vụ nền (đo giờ, quét tiến trình, phân giải DNS UDP 53, máy chủ blockpage HTTP 8080, bộ đệm ngoại tuyến SQLite WAL). Tự động phục hồi qua Windows Service Control Manager (SCM).
2. **Kênh IPC Loopback:** Máy chủ HTTP nội bộ tại `127.0.0.1:8765`, bảo vệ bằng Bearer Token ngẫu nhiên 64-hex lưu tại `%ProgramData%\OpenGuardKids\ipc_secret.token` với phân quyền NTFS ACL nghiêm ngặt.
3. **Tray UI Desktop GUI (Session 1):** Khởi chạy trong phiên đồ họa người dùng của trẻ thông qua Registry Run. Cung cấp icon khay taskbar động, toast cảnh báo, hộp thoại ân hạn 60 giây và màn hình khóa bảo vệ.
4. **Parent Web Dashboard & Server:** Máy chủ FastAPI + SQLite WAL, giao diện Jinja2 kết hợp Tailwind CSS responsive trên điện thoại và máy tính, tích hợp kênh lệnh khẩn cấp WebSocket độ trễ $< 5$ giây (thực tế 0.25–0.48 ms).

### 1.4 Ma trận Tuân thủ 100% Nguyên tắc Cốt lõi (NT1–NT6, F1–F5) & Pháp lý Luật Trẻ em 2016

Sản phẩm kiên định lập trường: **"Công cụ đồng hành và giáo dục, không phải phần mềm theo dõi lén lút (Spyware)"**, tuân thủ triệt để Luật Trẻ em 2016 và Nghị định 13/2023/NĐ-CP:

| Mã | Tên Nguyên Tắc / Chức Năng | Yêu Cầu Kỹ Thuật Cốt Lõi | Cơ Chế Hiện Thực Hóa & Điểm Neo Mã Nguồn |
| :--- | :--- | :--- | :--- |
| **NT1** | Trẻ biết mình đang được hỗ trợ | Biểu tượng khay Taskbar **luôn luôn hiện hữu**. Không có chế độ chạy ẩn danh. Cơ chế Watchdog 2 chiều: Mất Tray UI $\ge 15$s kích hoạt báo động; Service mất Tray $\ge 30$s kích hoạt phòng vệ. | `src/tray/app.py`, `src/tray/state_listener.py` (`on_connection_lost`), `src/agent/service.py`, `tests/test_tray_app.py` |
| **NT2** | Tối thiểu hóa dữ liệu (Data Minimization) | Chỉ lưu 7 trường siêu dữ liệu. **CẤM TUYỆT ĐỐI:** Không lưu URL chi tiết, không keylogger, không chụp màn hình. | `src/agent/offline_buffer.py`, `src/server/models.py`, `PRIVACY.md`, `tests/test_offline_buffer.py` |
| **NT3** | Trẻ có tiếng nói (Child Agency) | Cung cấp nút *"Xin thêm 15 phút"* và *"Báo chặn nhầm"*. Phụ huynh duyệt 1-click trên Web Dashboard. | `src/tray/dialogs.py`, `src/server/app.py` (`/requests/{id}/review`), `tests/test_dashboard_and_privacy.py` |
| **NT4** | Mọi hành động phải giải thích được | Chặn web/app phải hiển thị rõ lý do và ai đặt luật. Ân hạn 60s để trẻ lưu bài tập Word/PowerPoint. | `src/agent/blockpage.py`, `src/tray/dialogs.py`, `src/agent/process_monitor.py`, `tests/test_blockpage.py` |
| **NT5** | Minh bạch hai chiều (Two-Way) | Màn hình *"Hôm nay em đã dùng gì"* hiển thị 1:1 báo cáo của cha mẹ. Xem nhật ký đổi luật (Audit Log). | `src/tray/app.py` (`get_transparency_info`), `src/server/templates/dashboard.html` (Tab 5), `tests/test_tray_app.py` |
| **NT6** | An toàn có ưu tiên tuyệt đối | Whitelist vĩnh viễn: Cổng trường học, **Tổng đài Quốc gia Bảo vệ Trẻ em 111**. Không chặn cuộc gọi khẩn cấp OS. | `src/agent/dns_proxy.py` (`PERMANENT_WHITELIST`), `src/tray/dialogs.py`, `tests/test_dns_proxy.py` |
| **F1** | Quản lý thời gian sử dụng | Hạn ngạch ngày, lịch tuần ma trận 7x48, đo giờ thực (Session 1 ủy thác `idle_seconds > 300s` chuyển `IDLE_PAUSED`), bẫy chống lùi giờ và nhảy cóc giờ hệ thống (Forward Clock Jump). | `src/agent/screen_time.py`, API `user32.GetLastInputInfo`, `tests/test_screen_time.py` |
| **F2** | Kiểm soát Ứng dụng & Web | Băm SHA-256 bắt app đổi tên, diệt app vi phạm có thông báo, DNS Proxy UDP 53, SafeSearch CNAME, chặn DoH 3 lớp. | `src/agent/process_monitor.py`, `src/agent/dns_proxy.py`, `tests/test_process_monitor.py`, `tests/test_dns_proxy.py` |
| **F3** | Báo cáo & Quyền riêng tư | Biểu đồ ngày/tuần, Top 10 app/domain, tự xóa sau 90 ngày, nút Xóa dữ liệu kép (Atomic Dual Deletion). | `src/server/app.py`, `src/agent/offline_buffer.py`, `tests/test_dashboard_and_privacy.py` |
| **F4** | Đồng bộ & Quản lý từ xa | Đồng bộ chính sách $< 60$s qua Heartbeat, kênh lệnh khẩn cấp WebSocket $< 5$s (thực tế $< 0.5$ ms), chữ ký HMAC-SHA256. | `src/server/ws_manager.py`, `src/agent/service.py`, `tests/test_sync_and_events.py` |
| **F5** | An toàn thông tin & Bảo mật | Băm mật khẩu Argon2id (RFC 9106), khóa tài khoản 15p sau 5 lần sai, Cookie HttpOnly/SameSite, chống IDOR đa tầng. | `src/server/security.py`, `src/server/auth.py`, `tests/test_database_and_security.py` |

---

## PHẦN 2: KIẾN TRÚC KỸ THUẬT HỆ THỐNG & CƠ CHẾ PHÂN TÁCH SESSION (WINDOWS 10/11 X64)

### 2.1 Phân tích Session 0 Isolation & Rào cản Kỹ thuật WinSta0

Kể từ Windows Vista và hoàn thiện trên Windows 10/11, Microsoft triển khai cơ chế **Session 0 Isolation**:
1. **Bản chất kỹ thuật:** Mọi tiến trình Windows Service chạy trong **Session 0**, không liên kết với trạm làm việc tương tác đồ họa (`WinSta0`) và màn hình làm việc tương tác (`default desktop`).
2. **Hậu quả nếu cố tình tạo GUI từ Service:** Nếu một tiến trình trong Session 0 cố tình gọi các API giao diện đồ họa (như `MessageBox`, `CreateWindow`, `Tkinter`, `PyQt`), hệ điều hành sẽ cô lập cửa sổ đó trong một desktop vô hình hoặc làm treo dịch vụ vĩnh viễn (Interactive Services Detection bị vô hiệu hóa hoàn toàn trên Windows 10/11).
3. **Ưu thế bảo mật của Session 0:** Chạy dưới tài khoản `NT AUTHORITY\LocalSystem` (SID: `S-1-5-18`), tài khoản người dùng bình thường của trẻ (Standard User) trong Session 1 không có quyền hạn kết thúc tiến trình qua Task Manager hoặc lệnh `taskkill /F /PID` (hệ điều hành báo lỗi `ERROR_ACCESS_DENIED`).
4. **Giải pháp kiến trúc:** Tách đôi hệ thống:
   - **Session 0:** Tiến trình nền `OpenGuardKidsService` chạy quyền `LocalSystem`.
   - **Session 1:** Tiến trình giao diện người dùng `OpenGuardKidsTray` chạy trong phiên đăng nhập của trẻ.
   - **Cầu nối:** Kênh Loopback IPC HTTP tại `127.0.0.1:8765` có xác thực mã bí mật.
5. **Giới hạn Hàng đợi Nhập liệu Người dùng (User Input Queue Limitation) & Ủy thác Đo Nhàn rỗi:** Do Session 0 không gắn với desktop tương tác của người dùng (`WinSta0\Default`), việc gọi trực tiếp API Win32 `user32.GetLastInputInfo` trong Session 0 sẽ chỉ đọc hàng đợi của Session 0 (luôn trả về giá trị 0 hoặc không đổi). Do đó, nhiệm vụ đọc `GetLastInputInfo` được **ủy thác hoàn toàn cho Tray UI trong Session 1**. Định kỳ mỗi 1.0 giây, Tray UI đọc thời gian không thao tác chuột/phím và gửi kèm trường `"idle_seconds"` trong gói tin nhịp tim `POST /heartbeat` về cho Service. `ScreenTimeTracker` tại Session 0 căn cứ vào số liệu này để kích hoạt trạng thái `IDLE_PAUSED` (> 300s).
6. **Bảo vệ Chống Gian Lận Nhảy Cóc Đồng Hồ Hệ Thống (Forward Clock Jump Exploit Protection):**
   - Ngoài bẫy chống chỉnh lùi giờ hệ thống (`delta_wall < -60.0s`), hệ thống bổ sung bẫy chống **nhảy cóc tiến giờ (Forward Clock Jump)**. Trẻ em có thể chỉnh đồng hồ tiến vượt qua nửa đêm (ví dụ từ 14:00 thành 00:01 hôm sau) nhằm kích hoạt sự kiện sang ngày mới để hệ thống tự động reset hạn ngạch (`consumed_seconds_today = 0`).
   - Thuật toán nhận diện: Khi phát hiện `delta_wall = wall_time_now - wall_time_last > 60.0` trong khi thời gian đơn điệu phần cứng `delta_monotonic = mono_now - mono_last <= 2.0s`:
     - Hệ thống lập tức kích hoạt cờ cảnh báo gian lận `clock_forward_jump_tamper = True`.
     - **Từ chối reset hạn ngạch:** Khóa việc reset `consumed_seconds_today = 0` qua ngưỡng nửa đêm cho đến khi có xác nhận đồng bộ thời gian từ Server hoặc phụ huynh nhập mật mã xác thực.
     - Ghi nhận sự kiện vi phạm an ninh `CLOCK_FORWARD_TAMPER` vào SQLite WAL ngoại tuyến để báo cáo lên Web Dashboard của cha mẹ.

### 2.2 Sơ đồ Luồng Tương tác Toàn Hệ thống

```
+---------------------------------------------------------------------------------------------------+
| KHUNG TƯƠNG TÁC WINDOWS 10/11 x64 (SESSION 0 <---> SESSION 1 <---> SERVER)                        |
+---------------------------------------------------------------------------------------------------+
|                                                                                                   |
| [ SESSION 0: NT AUTHORITY\LocalSystem ]                                                           |
| +-----------------------------------------------------------------------------------------------+ |
| | Windows Service (OpenGuardKidsWindowsService)                                                 | |
| |  - ScreenTimeTracker (nhận idle_seconds từ Session 1, bẫy lùi giờ & nhảy cóc giờ tiến)         | |
| |  - Tray UI Watchdog (giám sát nhịp tim Session 1; mất kết nối > 30s kích hoạt phòng vệ)       | |
| |  - ProcessMonitor (quét SHA-256 mỗi 2s, in-memory cache O(1))                                 | |
| |  - DNSProxy (lắng nghe UDP 127.0.0.1:53, bẻ CNAME SafeSearch, chặn DoH canary)               | |
| |  - LocalBlockPageServer (lắng nghe HTTP 127.0.0.1:8080)                                       | |
| |  - OfflineEventBuffer (SQLite WAL: %ProgramData%\OpenGuardKids\offline_events.db)             | |
| |  - IPCManager Server (HTTP 127.0.0.1:8765, kiểm tra Header X-OGK-Token)                      | |
| +-----------------------------------------------------------------------------------------------+ |
|         │                                                 ▲                          ▲            |
|         │ Đọc trạng thái (GET /status)                    │ Ghi file token 64-hex    │            |
|         │ Gửi heartbeat kèm idle_seconds                  │ và đặt NTFS ACL          │            |
|         │ (POST /heartbeat, POST /request)                │ với SID *S-1-5-32-545    │            |
|         ▼                                                 │                          │            |
| [ SESSION 1: INTERACTIVE USER SESSION ]                   │                          │            |
| +---------------------------------------------------------┴---------------------+    │            |
| | Tray UI Client (pystray + tkinter)                                            |    │            |
| |  - StateListener (polling mỗi 1.0s, đọc GetLastInputInfo, gửi idle_seconds)    |    │            |
| |  - Taskbar Dynamic Badge (Icon tròn 64x64 đổi màu theo số phút còn lại)       |    │            |
| |  - Toast Popups (cảnh báo 10m, 5m, 1m)                                        |    │            |
| |  - 60s Grace Window (đếm ngược 60s WS_EX_NOACTIVATE, hỗ trợ Ctrl+S lưu bài)   |    │            |
| |  - Fullscreen Lock Overlay (che kín toàn màn hình, nút Xin 15p, Hotline 111)  |    │            |
| |  - Màn hình minh bạch 'Hôm nay em đã dùng gì' (NT5, Two-Way Transparency)    |    │            |
| +-------------------------------------------------------------------------------+    │            |
|                                                                                      │            |
|                                                     HTTPS (Heartbeat 60s & REST)     │            |
|                                                     WebSocket Lệnh Khẩn (< 5s)       │            |
+──────────────────────────────────────────────────────────────────────────────────────┼────────────+
                                                                                       │
                                                                                       ▼
                                                             +--------------------------------------+
                                                             | PARENT MANAGEMENT SERVER (FastAPI)   |
                                                             |  - Auth & Security (Argon2id, IDOR)  |
                                                             |  - WebSocket Dispatcher (< 0.5 ms)   |
                                                             |  - Jinja2 Responsive Dashboard       |
                                                             |  - SQLite Database (WAL mode)        |
                                                             |  - Atomic Dual Deletion Purge Engine |
                                                             +--------------------------------------+
```

### 2.3 Kênh Loopback IPC HTTP (127.0.0.1:8765) với Token 64-Hex

* **Địa chỉ & Cổng kết nối:** `http://127.0.0.1:8765/` (Giao thức HTTP 1.1 qua ngăn xếp Loopback TCP của Windows kernel, độ trễ $< 1$ ms).
* **Mã sinh Token ngẫu nhiên:** Khi Windows Service khởi động, nó tạo ra chuỗi định danh mã hóa 64 ký tự hex ngẫu nhiên:
  ```python
  import secrets
  token = secrets.token_hex(32)  # 32 bytes entropy = 64 hex characters
  ```
* **Bảo vệ chống tấn công Timing Attack:** Khi kiểm tra Header `X-OGK-Token` gửi lên từ Tray UI, Service bắt buộc sử dụng phương thức so sánh thời gian không đổi:
  ```python
  if not secrets.compare_digest(request_token, self.valid_token):
      return Response(status_code=403, content={"error": "Forbidden: Invalid IPC Token"})
  ```

### 2.4 Cơ chế Phân quyền File Token qua NTFS ACL (icacls)

File token được lưu trữ tại đường dẫn hệ thống:  
`%ProgramData%\OpenGuardKids\ipc_secret.token` (thực tế là `C:\ProgramData\OpenGuardKids\ipc_secret.token`).

Để bảo đảm tài khoản Standard User của trẻ hoặc bất kỳ phần mềm nào không thể ghi đè hoặc chỉnh sửa token này, kịch bản cài đặt và Service áp dụng danh sách điều khiển truy cập NTFS (ACL) thông qua tiện ích chuẩn `icacls` sử dụng **Định danh Bảo mật Chuẩn (Security Identifier - SID)**:
```cmd
icacls "%ProgramData%\OpenGuardKids\ipc_secret.token" /inheritance:r /grant:r "SYSTEM":(F) /grant:r "Administrators":(F) /grant:r "*S-1-5-32-545":(R)
```
* **Tại sao bắt buộc sử dụng SID `*S-1-5-32-545` thay vì `%USERNAME%` hay tên chuỗi "Users"?**
  1. *Giải quyết bài toán tài khoản Đăng nhập Khác nhau:* Phụ huynh cài đặt phần mềm dưới quyền Quản trị viên (Administrator). Nếu chỉ cấp quyền cho `%USERNAME%`, khi trẻ em đăng nhập bằng tài khoản người dùng chuẩn (Standard User) riêng của mình, tiến trình Tray UI trong Session 1 sẽ bị nhân Windows từ chối truy cập (`Access Denied / WinError 5`) và không thể đọc token kết nối Service.
  2. *Giải quyết bài toán Đa ngôn ngữ (Windows Localization):* Trên các bản cài đặt Windows 10/11 tiếng Việt hoặc ngôn ngữ khác, nhóm người dùng "Users" bị đổi tên (ví dụ: *"Người dùng"*, *"Utilisateurs"*). Cú pháp tiền tố dấu sao `*S-1-5-32-545` yêu cầu `icacls` giải quyết trực tiếp SID tĩnh của nhóm `BUILTIN\Users`, hoạt động ổn định 100% trên mọi phiên bản ngôn ngữ Windows.
* **Ý nghĩa các tham số:**
  * `/inheritance:r`: Cắt bỏ toàn bộ quyền thừa kế không kiểm soát từ thư mục cha.
  * `/grant:r "SYSTEM":(F)`: Cấp toàn quyền (`Full Control`) cho dịch vụ hệ thống `NT AUTHORITY\LocalSystem`.
  * `/grant:r "Administrators":(F)`: Cấp toàn quyền cho nhóm Quản trị viên máy tính.
  * `/grant:r "*S-1-5-32-545":(R)`: Cấp duy nhất quyền đọc (`Read`) cho toàn bộ người dùng thông thường thuộc nhóm Users. Trẻ có thể đọc token để xác thực IPC nhưng **hoàn toàn không có quyền ghi đè, sửa đổi hoặc xóa** tệp token. Mọi cố gắng can thiệp tệp đều bị nhân Windows từ chối.

### 2.5 Hợp đồng Thông điệp IPC (JSON Contracts) & Tự vệ Mất Kết nối (Red Alert > 15s)

#### Hợp đồng 1: Thăm dò trạng thái định kỳ (`GET /status`)
* **Tần suất:** Tray UI gửi mỗi 1.0 giây một lần.
* **Header bắt buộc:** `X-OGK-Token: <64-hex-token>`
* **Response (200 OK):**
```json
{
  "status": "ACTIVE_COUNTING",
  "state": "ACTIVE_COUNTING",
  "remaining_seconds": 3540.0,
  "consumed_seconds": 1860.0,
  "daily_quota_seconds": 5400,
  "is_locked": false,
  "lock_reason": null,
  "study_mode": false,
  "timestamp": 1730448000.0,
  "policy_version": 2
}
```

#### Hợp đồng 2: Nhịp tim báo sống & Ủy thác Đo Nhàn rỗi (`POST /heartbeat`)
* **Tần suất:** Tray UI gửi định kỳ mỗi 1.0 giây (đồng bộ với chu kỳ polling trạng thái).
* **Ủy thác đo nhàn rỗi (Session 0 Idle Delegation):** Do tiến trình Windows Service chạy trong Session 0 bị cô lập khỏi trạm làm việc đồ họa (`WinSta0`), lệnh gọi Win32 API `GetLastInputInfo` trong Session 0 không thể đọc hàng đợi chuột/bàn phím tương tác của người dùng. Trách nhiệm đo nhàn rỗi được ủy thác cho Tray UI (Session 1). Tray UI gọi `user32.GetLastInputInfo`, tính toán số giây người dùng không tương tác, và gửi kèm vào trường `"idle_seconds"`. `ScreenTimeTracker` tại Session 0 sử dụng giá trị này để chuyển trạng thái sang `IDLE_PAUSED` khi `idle_seconds > 300.0s`.
* **Request Body:**
```json
{
  "client_time": 1730448002.0,
  "tray_version": "1.0.0",
  "idle_seconds": 12.5
}
```
* **Response (200 OK):**
```json
{
  "status": "OK",
  "acknowledged": true
}
```

#### Hợp đồng 3: Trẻ gửi yêu cầu xin thêm giờ (`POST /request`)
* **Quy chuẩn định danh (Canonical Schema & Backward Compatibility):** Định danh chuẩn tắc (canonical type) là `"type": "ADD_TIME"`, tuân thủ nghiêm ngặt 100% với mã nguồn `src/tray/app.py:120` (`req_type="ADD_TIME"`) và kiểm thử `tests/test_tray_app.py:142` (`assert requests_received[0]["type"] == "ADD_TIME"`). Nhằm đảm bảo tương thích ngược tuyệt đối (backward compatibility), bộ phân tích phía Service chấp nhận đồng thời cả `"MORE_TIME"` như một alias hợp lệ.
* **Request Body:**
```json
{
  "type": "ADD_TIME",
  "minutes": 15,
  "subject": "Em đang làm nốt bài tập thuyết trình môn Tin học"
}
```
* **Response (200 OK):**
```json
{
  "status": "SUCCESS",
  "message": "Yêu cầu xin thêm 15 phút đã được chuyển tiếp tới cha mẹ."
}
```

#### Hợp đồng 4: Trẻ báo cáo tên miền học tập bị chặn nhầm (`POST /request`)
* **Request Body:**
```json
{
  "type": "UNBLOCK_DOMAIN",
  "domain": "scratch.mit.edu",
  "subject": "Em cần làm bài tập lập trình Scratch theo bài tập về nhà"
}
```
* **Response (200 OK):**
```json
{
  "status": "SUCCESS",
  "message": "Đã gửi báo cáo xem xét tên miền scratch.mit.edu."
}
```

#### Cơ chế Tự Vệ Giám Sát Hai Chiều (Two-Way Watchdog Safeguard — NT1 & F5):
1. **Phía Client Tray UI (Client-Side Red Alert):**
   * Nếu Tray UI liên tiếp không thể kết nối tới Service quá **15 giây (15 chu kỳ polling thất bại)**:
     1. Trạng thái giao diện lập tức chuyển sang `CONNECTION_LOST`.
     2. Biểu tượng Taskbar đổi sang màu đỏ rực nhấp nháy kèm dấu chấm than cảnh báo.
     3. Bật cửa sổ cảnh báo khẩn cấp: *"Mất kết nối với Dịch vụ Bảo vệ OpenGuard Kids. Nếu bạn đang cố tình tắt dịch vụ, máy tính sẽ tự động chuyển sang chế độ bảo vệ an toàn."*
     4. Ngăn chặn triệt để hành vi trẻ tìm cách tắt dịch vụ ngầm để lách luật.
2. **Phía Windows Service Session 0 (Service-Side Tray Watchdog):**
   * Service lưu biến thời gian `last_tray_heartbeat_time = time.monotonic()`. Mỗi khi nhận `POST /heartbeat` thành công từ Session 1, biến này được cập nhật.
   * Nếu thời gian trôi qua $> 30$ giây không nhận được nhịp tim (quá 30 chu kỳ nhịp tim bị gián đoạn do trẻ dùng Task Manager cố tình tắt `pythonw.exe` Tray UI để né tránh màn hình khóa):
     1. Service lập tức ghi sự kiện cảnh báo vi phạm `TRAY_AGENT_TERMINATED` vào SQLite WAL ngoại tuyến để đồng bộ lên Web Dashboard của cha mẹ.
     2. Kích hoạt tư thế phòng vệ an toàn (Fallback Lock Mode): Khóa cổng mạng Internet hoặc hạn chế ứng dụng cấm.
     3. Tự động tái khởi động (relaunch) Tray UI vào phiên tương tác của trẻ (Session 1) thông qua Task Scheduler hoặc Windows API `CreateProcessAsUser` kết hợp `WTSGetActiveConsoleSessionId`.

---

## PHẦN 3: THIẾT KẾ CHI TIẾT NATIVE DESKTOP GUI CHO TRAY UI (SESSION 1)

### 3.1 Lựa chọn Công nghệ GUI: pystray + Pillow + tkinter (< 5MB RAM, Khởi động < 150ms)

Để xây dựng giao diện người dùng nhẹ nhàng, khởi động tức thì và không làm ảnh hưởng đến hiệu năng máy tính của trẻ, chúng tôi tiến hành đánh giá thực nghiệm:

| Tiêu chí Đánh giá | PyQt5 / PySide6 | pystray + Pillow + tkinter | C# / WPF Add-on |
| :--- | :--- | :--- | :--- |
| **Dung lượng bộ nhớ RAM** | 45 MB – 85 MB | **< 5 MB** (Cực nhẹ) | 60 MB – 100 MB |
| **Thời gian nạp & hiển thị** | 1.8s – 3.2s | **< 150 ms** (Tức thì) | 1.5s – 2.5s |
| **Phụ thuộc gói ngoài** | Hàng chục file DLL C++ lớn | `pystray` và `Pillow` nhỏ gọn, `tkinter` có sẵn | Cần .NET Runtime |
| **Khả năng chạy Unit Test headless** | Dễ crash trên Linux/CI nếu thiếu X11 | **Tuyệt đối an toàn** qua kiến trúc tách rời Model-View | Khó khăn trên Linux |
| **Độ ổn định trên Windows 10/11** | Tốt | **Hoàn hảo** (Native Win32 Shell NotifyIcon) | Tốt |

**Quyết định kỹ thuật:** Sử dụng bộ đôi **`pystray` + `Pillow`** cho biểu tượng khay Taskbar kết hợp với **`tkinter`** (thư viện đồ họa chuẩn đi kèm mọi bản cài đặt Python trên Windows) cho toàn bộ các cửa sổ Toast, Ân hạn, Khóa máy và Minh bạch.

* **Ủy thác Đo Nhàn Rỗi (Session 1 Input Queue Access & GetLastInputInfo):**  
  Do tiến trình Tray UI chạy trực tiếp trong Session 1 tương tác (`WinSta0\Default`), nó có quyền truy cập trực tiếp vào hàng đợi thông điệp bàn phím và chuột của người dùng. Tray UI tích hợp hàm đo thời gian nhàn rỗi chuẩn Win32 qua `ctypes`:
  ```python
  import ctypes

  class LASTINPUTINFO(ctypes.Structure):
      _fields_ = [("cbSize", ctypes.c_uint), ("dwTime", ctypes.c_uint)]

  def get_idle_seconds() -> float:
      """Đo thời gian người dùng không thao tác phím/chuột trong Session 1."""
      lii = LASTINPUTINFO()
      lii.cbSize = ctypes.sizeof(LASTINPUTINFO)
      if ctypes.windll.user32.GetLastInputInfo(ctypes.byref(lii)):
          millis = ctypes.windll.kernel32.GetTickCount() - lii.dwTime
          return max(0.0, millis / 1000.0)
      return 0.0
  ```
  Hàm này được gọi định kỳ mỗi 1.0 giây và giá trị `idle_seconds` được truyền trực tiếp vào payload của `POST /heartbeat` gửi về Windows Service Session 0.

### 3.2 Biểu tượng Taskbar Động (Dynamic Badge) & Context Menu Chuột Phải

* **Biểu tượng đồ họa vẽ trực tiếp (Dynamic Pillow Drawing):**
  Hệ thống sử dụng thư viện `Pillow` tạo ảnh `Image.new("RGBA", (64, 64))` và vẽ vòng tròn trạng thái cùng dòng chữ số phút còn lại:
  - **Trạng thái Bình thường ($> 10$ phút):** Nền xanh dương dịu mắt (`#0284c7`), số phút màu trắng (ví dụ `45m`).
  - **Trạng thái Cảnh báo ($5 - 10$ phút):** Nền màu vàng cam hổ phách (`#f59e0b`).
  - **Trạng thái Khẩn cấp ($< 5$ phút & Ân hạn):** Nền màu cam đậm rực rỡ (`#ea580c`).
  - **Trạng thái Đã Khóa hoặc Mất kết nối:** Nền màu đỏ cấm (`#dc2626`).
* **Context Menu (Khi nhấp chuột phải vào Icon):**
  1. `⏱️ Thời gian còn lại: 45 phút` *(Hiển thị trực quan trạng thái hiện tại)*.
  2. `✨ Xin cha mẹ thêm 15 phút...` *(Mở hộp thoại gửi yêu cầu)*.
  3. `🛡️ Báo cáo trang web bị chặn nhầm...` *(Mở hộp thoại báo tên miền)*.
  4. `📖 Hôm nay em đã dùng gì` *(Mở cửa sổ minh bạch NT5)*.
  5. `ℹ️ Quyền trẻ em & Hotline 111` *(Xem điều khoản bảo vệ)*.
  6. *(TUYỆT ĐỐI KHÔNG CÓ NÚT THOÁT HOẶC EXIT để đảm bảo nguyên tắc NT1)*.

### 3.3 Chuỗi Thông Báo Leo Thang Thời Gian Thực (Escalating Toasts 10m - 5m - 1m)

Chuỗi Toast thông báo xuất hiện trượt nhẹ ở góc dưới bên phải màn hình (ngay phía trên khay đồng hồ Taskbar):
1. **Toast 10 phút:**
   - *Tiêu đề:* `OpenGuard Kids — Nhắc nhở thời gian`
   - *Nội dung:* `"Bạn còn 10 phút sử dụng máy tính hôm nay. Hãy sắp xếp hoàn thành bài học nhé!"`
   - *Thời gian hiển thị:* Tự biến mất sau 6 giây.
2. **Toast 5 phút:**
   - *Tiêu đề:* `OpenGuard Kids — Sắp hết giờ!`
   - *Nội dung:* `"Chỉ còn 5 phút! Hãy chuẩn bị lưu lại tài liệu bài tập hoặc xin thêm giờ nếu cần."`
   - *Thời gian hiển thị:* Tự biến mất sau 8 giây kèm hiệu ứng nổi bật.
3. **Toast 1 phút:**
   - *Tiêu đề:* `OpenGuard Kids — CẢNH BÁO KHẨN CẤP`
   - *Nội dung:* `"Chỉ còn 1 phút! Hệ thống sẽ kích hoạt 60 giây ân hạn để bạn lưu bài tập."`
   - *Âm thanh:* Phát âm thanh cảnh báo chuẩn Windows `winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)`.

### 3.4 Hộp thoại Ân Hạn 60 Giây Non-Focus-Stealing (Hỗ trợ Ctrl+S Lưu Bài)

Đây là tính năng độc đáo mang tính nhân văn sâu sắc (NT3, NT4, F1.4):
* **Thời điểm kích hoạt:** Khi số phút còn lại rơi về đúng 0 giây hoặc bước vào giờ giới nghiêm.
* **Đặc tính kỹ thuật chuyên sâu & Giải pháp Win32 Non-Focus-Stealing:**
  - Trong Windows, nếu một cửa sổ Tkinter chỉ đơn thuần thiết lập `wm_attributes("-topmost", True)`, khi cửa sổ xuất hiện hoặc vẽ lại (map/draw), Desktop Window Manager (DWM) của hệ điều hành có xu hướng kích hoạt (`WM_ACTIVATE`) và cướp tiêu điểm phím (keyboard focus) từ ứng dụng trẻ đang soạn thảo (Word, PowerPoint, VS Code). Khi đó, phím gõ `Ctrl + S` của trẻ sẽ bị rơi vào khoảng không hoặc bị nuốt bởi hộp thoại.
  - **Giải pháp triệt để bằng Win32 Extended Style `WS_EX_NOACTIVATE`:**
    Hệ thống sử dụng `ctypes` can thiệp trực tiếp vào thuộc tính cửa sổ cấp hệ điều hành (Win32 API `SetWindowLongW`):
    ```python
    import ctypes

    GWL_EXSTYLE = -20
    WS_EX_NOACTIVATE = 0x08000000  # Ngăn chặn Windows kích hoạt và cướp focus khi hiển thị
    WS_EX_TOPMOST = 0x00000008     # Luôn hiển thị trên đỉnh màn hình để trẻ nhìn thấy đồng hồ

    # Lấy HWND của cửa sổ Tkinter và áp dụng thuộc tính mở rộng
    hwnd = ctypes.windll.user32.GetParent(root.winfo_id())
    style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
    ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style | WS_EX_NOACTIVATE | WS_EX_TOPMOST)
    ```
  - **NON-FOCUS-STEALING (KHÔNG CƯỚNG CHẾ TIÊU ĐIỂM):** Tuyệt đối không gọi `root.focus_force()` hoặc `grab_set()`. Với sự kết hợp giữa `WS_EX_TOPMOST` và `WS_EX_NOACTIVATE`, hộp thoại nổi lên trên cùng màn hình với đồng hồ đếm lùi trực quan nhưng **con trỏ chuột và tiêu điểm gõ phím vẫn nằm nguyên vẹn trong Microsoft Word hoặc PowerPoint**. Trẻ em chỉ cần bấm ngay tổ hợp phím **`Ctrl + S`** là tài liệu bài tập được lưu an toàn 100% trước khi máy tính khóa!
* **Giao diện hiển thị:**
  - Tiêu đề: **"Thời gian đã hết — 60 Giây Ân Hạn"**
  - Đồng hồ đếm lùi kỹ thuật số cỡ lớn: `59s... 58s... 57s...`
  - Thanh tiến trình đồ họa (Progress Bar) rút ngắn dần từ 100% về 0%.
  - Thông điệp: *"Bạn có 60 giây để lưu lại bài tập Word, PowerPoint trước khi máy tính tạm khóa."*
  - Hai nút tương tác:
    - `💾 Em đã lưu xong bài, Khóa ngay`: Cho phép trẻ chủ động chấp hành nội quy.
    - `✨ Xin thêm 15 phút`: Gửi yêu cầu khẩn cấp lên Dashboard của phụ huynh.

### 3.5 Màn hình Khóa Đồ Họa Toàn Màn Hình (Fullscreen Lock Overlay với Hotline 111 & Xin 15p)

* **Thời điểm kích hoạt:** Khi 60 giây ân hạn đếm về 0 hoặc khi cha mẹ bấm nút *"Khóa Ngay"* trên Web Dashboard.
* **Đặc tính kỹ thuật:**
  - Cửa sổ không viền: `root.overrideredirect(True)`.
  - Phủ kín toàn bộ độ phân giải màn hình: `root.geometry(f"{screen_width}x{screen_height}+0+0")`.
  - Luôn nằm trên đỉnh: `root.wm_attributes("-topmost", True)`.
  - Bắt giữ tiêu điểm chuột và phím (`root.grab_set()`), chặn các phím tắt đóng ứng dụng như `Alt + F4`, `Esc`.
* **Nội dung giao diện khóa (Thiết kế thẩm mỹ, giáo dục):**
  - Biểu tượng chiếc khiên và ổ khóa màu xanh thân thiện.
  - Tiêu đề nổi bật: **"Máy tính Đang Tạm Khóa"**.
  - Thông điệp: *"Hôm nay bạn đã hoàn thành tốt các nhiệm vụ. Hãy dành thời gian vận động, giúp đỡ gia đình và cho mắt nghỉ ngơi nhé!"*
  - Lý do khóa minh bạch (NT4): *"Đã dùng hết hạn mức 120 phút trong ngày"* hoặc *"Đang trong giờ giới nghiêm ban đêm (21:30 - 06:00)"*.
  - Khung thông tin cứu hộ khẩn cấp (NT6):  
    📞 **Tổng đài Quốc gia Bảo vệ Trẻ em: 111** *(Miễn phí cuộc gọi 24/7)*.
  - Nút tương tác: **"Xin Cha/Mẹ thêm 15 phút"** (Bấm để gửi thông điệp yêu cầu lên máy chủ).

### 3.6 Màn hình Minh Bạch "Hôm nay em đã dùng gì" (NT5 Two-Way Transparency)

* Cung cấp qua context menu khay taskbar.
* Thể hiện trọn vẹn dữ liệu siêu dữ liệu 1:1 tương đương bảng tổng quan của cha mẹ:
  - Tổng thời gian đã sử dụng trong ngày vs Hạn mức được phép.
  - Danh sách 5 phần mềm đã sử dụng nhiều nhất (kèm thời lượng).
  - Danh sách 5 tên miền web đã truy cập nhiều nhất.
  - Danh sách các ứng dụng hoặc trang web bị chặn (kèm lý do do cha mẹ đặt ra).
  - Cam kết quyền riêng tư: *"Hệ thống không ghi nhận phím bấm (no keylogger) và không chụp ảnh màn hình bí mật."*

---

## PHẦN 4: THIẾT KẾ TRIỂN KHAI WINDOWS SERVICE NATIVE & DNS PROTECTION (SESSION 0)

### 4.1 Cấu trúc Module `src/agent/windows_service.py` bằng pywin32 ServiceFramework

Mô-đun mới `src/agent/windows_service.py` được thiết kế theo đúng chuẩn Service của Windows NT, kế thừa từ `win32serviceutil.ServiceFramework`:

```python
"""
OpenGuard Kids — Production Windows Service Framework
Target: Windows 10/11 x64
Module: src/agent/windows_service.py
"""
import sys
import os
import logging
import winerror
import win32serviceutil
import win32service
import win32event
import servicemanager

from src.agent.service import AgentService

class OpenGuardKidsWindowsService(win32serviceutil.ServiceFramework):
    _svc_name_ = "OpenGuardKidsService"
    _svc_display_name_ = "OpenGuard Kids Parental Protection Service"
    _svc_description_ = (
        "Dịch vụ nền bảo vệ trẻ em OpenGuard Kids: Quản lý thời gian sử dụng, "
        "lọc nội dung mạng DNS UDP 53, kiểm soát phần mềm vi phạm và đồng hành an toàn."
    )
    _svc_deps_ = ["Tcpip", "Dnscache"]

    def __init__(self, args):
        super().__init__(args)
        self.stop_event = win32event.CreateEvent(None, 0, 0, None)
        
        # Đường dẫn lưu trữ dữ liệu an toàn cấp hệ thống
        program_data = os.environ.get("ProgramData", "C:\\ProgramData")
        self.data_dir = os.path.join(program_data, "OpenGuardKids")
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Khởi tạo đối tượng AgentService lõi
        # Ghi chú: ScreenTimeTracker trong AgentService nhận idle_seconds được ủy thác
        # từ Tray UI Session 1 và duy trì watchdog theo dõi nhịp tim Session 1.
        self.agent = AgentService(
            data_dir=self.data_dir,
            dns_port=53,           # Lắng nghe cổng chuẩn UDP 53 trên Windows
            blockpage_port=8080,   # Cổng phục vụ trang thông báo chặn
            ipc_port=8765,         # Cổng Loopback IPC cho Tray UI
        )

    def SvcStop(self):
        """Tiếp nhận tín hiệu dừng từ Service Control Manager (net stop)."""
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        servicemanager.LogInfoMsg("OpenGuardKidsService is stopping...")
        win32event.SetEvent(self.stop_event)
        self.agent.stop()
        self.ReportServiceStatus(win32service.SERVICE_STOPPED)

    def SvcDoRun(self):
        """Vòng lặp thực thi chính trong Session 0."""
        servicemanager.LogInfoMsg("OpenGuardKidsService is starting...")
        self.ReportServiceStatus(win32service.SERVICE_RUNNING)
        try:
            self.agent.start()
            servicemanager.LogInfoMsg("OpenGuardKidsService started successfully.")
            while self.agent.is_running:
                rc = win32event.WaitForSingleObject(self.stop_event, 1000)
                if rc == win32event.WAIT_OBJECT_0:
                    break
        except Exception as e:
            servicemanager.LogErrorMsg(f"OpenGuardKidsService encountered a fatal error: {e}")
            self.agent.stop()
            # Bắt buộc báo mã lỗi khác 0 và winerror để SCM phát hiện Service Crash và kích hoạt Recovery Actions
            self.ReportServiceStatus(
                win32service.SERVICE_STOPPED,
                win32_exit_code=winerror.ERROR_SERVICE_SPECIFIC_ERROR,
                svc_exit_code=1,
            )
            sys.exit(1)

if __name__ == "__main__":
    win32serviceutil.HandleCommandLine(OpenGuardKidsWindowsService)
```

### 4.2 Vòng đời Dịch vụ & Tích hợp Service Control Manager (SCM)

1. **Khởi động (Startup):** Khi Windows khởi động, SCM tải tiến trình Service vào Session 0 dưới quyền `LocalSystem`. Hàm `SvcDoRun()` được kích hoạt, tiến hành:
   - Khởi động bộ nhớ đệm SQLite WAL tại `%ProgramData%\OpenGuardKids\offline_events.db`.
   - Sinh mã xác thực 64-hex và ghi vào `ipc_secret.token` kèm phân quyền `icacls` với SID `*S-1-5-32-545`.
   - Khởi động máy chủ Loopback HTTP IPC tại `127.0.0.1:8765`.
   - Lắng nghe Socket UDP 53 tiếp nhận gói tin DNS.
   - Khởi động máy chủ Blockpage HTTP 8080.
   - Bật luồng theo dõi tiến trình `ProcessMonitor` và luồng đếm giờ `ScreenTimeTracker` (tiếp nhận `idle_seconds` ủy thác từ Session 1 và kiểm tra Watchdog nhịp tim > 30s).
2. **Tắt / Dừng (Stop / Shutdown):** Khi quản trị viên yêu cầu dừng hoặc khi Windows tắt máy, SCM gửi thông điệp điều khiển. Hàm `SvcStop()` kích hoạt `agent.stop()`, đóng sạch sẽ các socket, giải phóng cổng mạng, và bảo toàn toàn vẹn cơ sở dữ liệu SQLite WAL.

### 4.3 Cấu hình SCM Auto-Recovery Policy khi Sự cố (`sc.exe failure`)

Để đối phó với tình huống tiến trình dịch vụ bị lỗi ngoại lệ hoặc bị tấn công tắt tiến trình, kịch bản cài đặt tự động đăng ký chính sách phục hồi 3 nấc kết hợp cứu hộ mạng của Windows SCM:
```cmd
sc.exe failure OpenGuardKidsService reset= 86400 actions= restart/60000/restart/60000/run/60000 command= "\"%~dp0restore_dns.bat\""
```
* **Lần lỗi 1:** Tự động khởi động lại dịch vụ sau 60 giây (`restart/60000`).
* **Lần lỗi 2:** Tự động khởi động lại dịch vụ sau 60 giây (`restart/60000`).
* **Lần lỗi 3:** Tự động thực thi kịch bản cứu hộ mạng `restore_dns.bat` sau 60 giây (`run/60000 command= "\"%~dp0restore_dns.bat\""`). Cơ chế này bảo đảm nếu dịch vụ gặp sự cố nghiêm trọng không thể tự phục hồi sau 2 lần khởi động lại, SCM sẽ tự động hoàn nguyên DNS của tất cả các card mạng về DHCP, ngăn ngừa hoàn toàn nguy cơ máy tính bị cô lập mạng Internet.
* **Đặt lại bộ đếm (`reset= 86400`):** Sau 24 giờ hoạt động ổn định không xảy ra lỗi, SCM tự động đặt bộ đếm số lần crash về 0.
* **Ràng buộc mã thoát (Exit Code Binding):** Trong `SvcDoRun`, khi bắt được ngoại lệ chết người, dịch vụ bắt buộc gọi `ReportServiceStatus(..., win32_exit_code=winerror.ERROR_SERVICE_SPECIFIC_ERROR)` và `sys.exit(1)`. Việc trả về mã thoát khác 0 là điều kiện tiên quyết để nhân SCM xác định tiến trình bị lỗi bất thường và kích hoạt các hành động cứu hộ trong cấu hình failure.

### 4.4 DNS Proxy UDP Port 53 & Chiến lược Khắc chế DoH 3 Lớp

DNS Proxy cục bộ lắng nghe tại `127.0.0.1:53` UDP:
* **Chiến lược Khắc chế DNS-over-HTTPS (DoH Mitigation 3 Lớp):**
  1. *Lớp 1 — Trả về `NXDOMAIN` cho Canary Domain:* Khi nhận câu hỏi phân giải tên miền `use-application-dns.net` (RFC chuẩn), DNS Proxy lập tức trả về mã lỗi `NXDOMAIN` (RCODE 3). Cơ chế này báo hiệu cho các trình duyệt phổ biến (Google Chrome, Mozilla Firefox, Microsoft Edge) tự động vô hiệu hóa tính năng DoH tích hợp và quay về sử dụng dịch vụ DNS mặc định của hệ điều hành.
  2. *Lớp 2 — Chặn Cổng DoT & IP DoH Công cộng:* Tích hợp danh sách IP của các máy chủ DNS mã hóa nổi tiếng (`1.1.1.1`, `8.8.8.8`, `9.9.9.9`) và cổng 853 để ngăn chặn các ứng dụng lách DNS.
  3. *Lớp 3 — Cấu hình Windows Registry Policy:* Thiết lập khóa Registry chính sách vô hiệu hóa DoH trên trình duyệt qua script cài đặt.
* **Bộ quy tắc lọc tên miền:**
  - So khớp tiền tố và hậu tố wildcard: Chặn `badgame.com` sẽ tự động chặn toàn bộ `*.badgame.com`.
  - Phân loại tên miền theo 6 nhóm tuổi (Giáo dục, Giải trí, Mạng xã hội, Game, Không phù hợp, Chưa phân loại).
  - Tên miền bị chặn được trả về bản ghi A trỏ về IP máy chủ Blockpage `127.0.0.1`.
  - Tên miền hợp lệ được chuyển tiếp (forward) lên DNS gia đình Cloudflare `1.1.1.3` (tự động lọc malware) kèm DNS dự phòng Google `8.8.8.8`, lưu cache RAM với TTL 60 giây.

### 4.5 Cưỡng chế SafeSearch qua Ghi Đè Bản Ghi DNS CNAME

DNS Proxy tự động chặn các nội dung tìm kiếm độc hại ở tầng mạng lõi bằng kỹ thuật ghi đè CNAME (SafeSearch CNAME Rewriting) mà không cần can thiệp giải mã gói tin HTTPS:
* `google.com`, `www.google.com` $\to$ CNAME `forcesafesearch.google.com.`
* `bing.com`, `www.bing.com` $\to$ CNAME `strict.bing.com.`
* `youtube.com`, `www.youtube.com` $\to$ CNAME `restrict.youtube.com.`
* `duckduckgo.com` $\to$ CNAME `safe.duckduckgo.com.`

Đồng thời, DNS Proxy tự động phân giải và trả kèm địa chỉ IP của các máy chủ an toàn trong phần `Additional Records`, giúp trình duyệt kết nối trực tiếp trong chớp mắt mà không sinh thêm truy vấn vòng.

### 4.6 Máy chủ Trang Chặn Thân Thiện Polite Blockpage (HTTP Port 8080)

Khi trẻ vô tình truy cập một trang web bị cấm, trình duyệt kết nối vào máy chủ HTTP `127.0.0.1:8080`. Trang chặn được thiết kế lịch sự, văn minh (NT4):
* Tiêu đề: **"Nội dung đang được giữ an toàn theo thỏa thuận gia đình"**.
* Thông tin minh bạch: Tên website bị chặn, thuộc danh mục nào, và người đặt ra quy định (Cha/Mẹ).
* Số điện thoại hỗ trợ khẩn cấp (NT6): 📞 **Tổng đài 111**.
* Form gửi ý kiến (NT3): Trẻ có thể nhập lý do *"Con nghĩ trang này phục vụ học tập và bị chặn nhầm"* và bấm gửi; yêu cầu được chuyển thẳng vào Hòm thư duyệt đơn trên Parent Web Dashboard.

---

## PHẦN 5: BỘ SCRIPT TRIỂN KHAI & GỠ BỎ 1-CHẠM (ADMINISTRATOR BATCH SCRIPTS)

Mọi kịch bản batch trong bộ script đều được viết theo chuẩn batch chuyên nghiệp cho môi trường Windows 10/11 x64, có cơ chế tự động kiểm tra và nâng quyền Administrator (UAC Elevation).

### 5.1 Cơ chế Tự Động Kiểm tra & Nâng Quyền UAC Administrator Chuẩn

Đoạn mã mẫu dùng chung ở đầu mỗi script batch:
```bat
@echo off
setlocal EnableDelayedExpansion

:: Kiểm tra đặc quyền Administrator bằng lệnh net session
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [OpenGuard Kids] Thong bao: Script yeu cau dac quyen Administrator!
    echo Dang yeu cau nang quyen qua UAC Prompt...
    powershell -NoProfile -ExecutionPolicy Bypass -Command "Start-Process -FilePath '%~f0' -Verb RunAs"
    exit /b
)
cd /d "%~dp0"
```

### 5.2 Toàn văn & Cơ chế `install_service.bat`

```bat
@echo off
setlocal EnableDelayedExpansion

:: ============================================================================
:: OpenGuard Kids — One-Click Service Installation Script
:: Target: Windows 10/11 x64
:: File: install_service.bat
:: ============================================================================

net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [OpenGuard Kids] Yeu cau quyen Administrator de cai dat Windows Service!
    powershell -NoProfile -ExecutionPolicy Bypass -Command "Start-Process -FilePath '%~f0' -Verb RunAs"
    exit /b
)
cd /d "%~dp0"

echo ============================================================================
echo   OPENGUARD KIDS — CAI DAT WINDOWS SERVICE (SESSION 0)
echo ============================================================================

:: 1. Xac dinh trinh thong dich Python
set "PYTHON_EXE="
if exist "%~dp0.venv\Scripts\python.exe" (
    set "PYTHON_EXE=%~dp0.venv\Scripts\python.exe"
) else (
    where python >nul 2>&1
    if %errorLevel% equ 0 (
        set "PYTHON_EXE=python"
    ) else (
        echo [LOI] Khong tim thay Python 3.11+ tren he thong!
        pause
        exit /b 1
    )
)
echo [*] Su dung Python: %PYTHON_EXE%

:: 1.1 Kiem tra va dang ky pywin32 he thong (pywin32_postinstall.py -install)
echo [*] Kiem tra thu vien he thong pywin32...
"%PYTHON_EXE%" -c "import win32service" >nul 2>&1
if %errorLevel% neq 0 (
    echo [*] Dang thuc thi pywin32_postinstall.py -install de dang ky service DLL...
    if exist "%~dp0.venv\Scripts\pywin32_postinstall.py" (
        "%PYTHON_EXE%" "%~dp0.venv\Scripts\pywin32_postinstall.py" -install >nul 2>&1
    ) else (
        "%PYTHON_EXE%" -c "from pywin32_postinstall import install; install()" >nul 2>&1
    )
    "%PYTHON_EXE%" -c "import win32service" >nul 2>&1
    if %errorLevel% neq 0 (
        echo [LOI] Khong the dang ky pywin32 system DLLs! Vui long kiem tra ban quyen moi truong.
        pause
        exit /b 1
    )
)

:: 2. Tao thu muc ProgramData va phan quyen NTFS theo SID Users (*S-1-5-32-545)
set "DATA_DIR=%ProgramData%\OpenGuardKids"
if not exist "%DATA_DIR%" (
    echo [*] Tao thu muc du lieu he thong: %DATA_DIR%
    mkdir "%DATA_DIR%"
)
icacls "%DATA_DIR%" /inheritance:r /grant:r "SYSTEM":(OI)(CI)(F) /grant:r "Administrators":(OI)(CI)(F) /grant:r "*S-1-5-32-545":(OI)(CI)(RX) >nul 2>&1

:: 3. Dang ky Windows Service vao SCM bang pywin32
echo [*] Dang ky OpenGuardKidsService vao Service Control Manager (SCM)...
"%PYTHON_EXE%" "%~dp0src\agent\windows_service.py" install
if %errorLevel% neq 0 (
    echo [CANH BAO] Dang ky service co the da ton tai, thu cap nhat cau hinh...
    "%PYTHON_EXE%" "%~dp0src\agent\windows_service.py" update
)

:: 4. Thiet lap cau hinh tu phuc hoi khi crash (SCM Recovery Policy & restore_dns.bat)
echo [*] Thiet lap SCM Recovery Policy: Restart 2 lan dau, lan 3 chay restore_dns.bat...
sc.exe failure OpenGuardKidsService reset= 86400 actions= restart/60000/restart/60000/run/60000 command= "\"%~dp0restore_dns.bat\""
sc.exe config OpenGuardKidsService start= auto

:: 5. Khoi dong dich vu & Kiem tra ma loi errorlevel
echo [*] Khoi dong OpenGuardKidsService...
net start OpenGuardKidsService
if %errorLevel% neq 0 (
    echo.
    echo ============================================================================
    echo [LOI] Khong the khoi dong OpenGuardKidsService! (Ma loi: %errorLevel%)
    echo Vui long kiem tra Windows Event Viewer (Application Log) hoac log tai %DATA_DIR%.
    echo ============================================================================
    pause
    exit /b %errorLevel%
)

echo ============================================================================
echo [THANH CONG] Windows Service da duoc cai dat va khoi dong thanh cong!
echo ============================================================================
pause
```

### 5.3 Toàn văn & Cơ chế `enable_dns_protection.bat`

```bat
@echo off
setlocal EnableDelayedExpansion

:: ============================================================================
:: OpenGuard Kids — Enable DNS Protection Script (127.0.0.1:53)
:: Target: Windows 10/11 x64
:: File: enable_dns_protection.bat
:: ============================================================================

net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [OpenGuard Kids] Yeu cau quyen Administrator de cau hinh DNS!
    powershell -NoProfile -ExecutionPolicy Bypass -Command "Start-Process -FilePath '%~f0' -Verb RunAs"
    exit /b
)
cd /d "%~dp0"

echo ============================================================================
echo   OPENGUARD KIDS — KICH HOAT BAO VE DNS CUC BO (127.0.0.1:53)
echo ============================================================================

:: 0. Kiem tra tien quyet: OpenGuardKidsService bat buoc dang RUNNING
echo [*] Kiem tra trang thai OpenGuardKidsService truoc khi cau hinh DNS...
sc query OpenGuardKidsService | find "RUNNING" >nul 2>&1
if %errorLevel% neq 0 (
    echo.
    echo ============================================================================
    echo [LOI TIEN QUYET] OpenGuardKidsService chua chay hoac chua duoc cai dat!
    echo Tuyet doi khong tro DNS ve 127.0.0.1 khi service chua chay de tranh mat mang toan may.
    echo Vui long chay 'install_service.bat' truoc khi kich hoat bao ve DNS.
    echo ============================================================================
    pause
    exit /b 1
)
echo   [OK] OpenGuardKidsService dang chay on dinh tren cong 127.0.0.1:53.

:: 1. Phat hien dong cac network adapter vat ly dang ket noi mang qua PowerShell
echo [*] Phat hien dong cac network adapter dang hoat dong (PowerShell Get-NetAdapter)...
for /f "tokens=*" %%A in ('powershell -NoProfile -ExecutionPolicy Bypass -Command "Get-NetAdapter -Physical | Where-Object { $_.Status -eq 'Up' } | Select-Object -ExpandProperty Name"') do (
    echo [*] Dang thiet lap bao ve DNS cho adapter: "%%A"...
    :: Cau hinh IPv4 DNS tro ve Local DNS Proxy 127.0.0.1:53
    netsh interface ipv4 set dnsservers name="%%A" source=static address=127.0.0.1 register=none validate=no >nul 2>&1
    :: Chien luoc chong lach qua IPv6: Tro DNS IPv6 ve loopback ::1 de chan truy van ra ngoai
    netsh interface ipv6 set dnsservers name="%%A" source=static address=::1 register=none validate=no >nul 2>&1
    echo   [OK] Da kich hoat IPv4 (127.0.0.1) va bao ve IPv6 (::1) tren adapter: "%%A".
)

:: 1.1 Cau hinh du phong cho cac ten adapter tinh thong dung (Fallback static names)
for %%I in ("Wi-Fi" "Ethernet" "Ethernet 2") do (
    netsh interface ipv4 set dnsservers name=%%I source=static address=127.0.0.1 register=none validate=no >nul 2>&1
    netsh interface ipv6 set dnsservers name=%%I source=static address=::1 register=none validate=no >nul 2>&1
)

:: 2. Xoa sach bo dem DNS Resolver Windows
echo [*] Dang lam sach bo dem phan giai DNS Windows (ipconfig /flushdns)...
ipconfig /flushdns >nul 2>&1
echo   [OK] DNS Resolver Cache flushed.

echo ============================================================================
echo [THANH CONG] He thong da chuyen huong toan bo phan giai DNS qua OpenGuard Kids!
echo (Da kich hoat bao ve dong bo tren ca giao thuc IPv4 va IPv6)
echo ============================================================================
pause
```

### 5.4 Toàn văn & Cơ chế `setup_tray_startup.bat`

```bat
@echo off
setlocal EnableDelayedExpansion

:: ============================================================================
:: OpenGuard Kids — Setup Tray UI Startup Script (Session 1)
:: Target: Windows 10/11 x64
:: File: setup_tray_startup.bat
:: ============================================================================

cd /d "%~dp0"

echo ============================================================================
echo   OPENGUARD KIDS — DANG KY TRAY UI TU KHOI CHAY KHI DANG NHAP (SESSION 1)
echo ============================================================================

:: 1. Tim pythonw.exe (trinh thong dich khong hien man hinh console den)
set "PYTHONW_EXE="
if exist "%~dp0.venv\Scripts\pythonw.exe" (
    set "PYTHONW_EXE=%~dp0.venv\Scripts\pythonw.exe"
) else (
    where pythonw >nul 2>&1
    if %errorLevel% equ 0 (
        set "PYTHONW_EXE=pythonw"
    ) else (
        echo [LOI] Khong tim thay pythonw.exe!
        pause
        exit /b 1
    )
)
echo [*] Su dung Trinh thong dich: %PYTHONW_EXE%

:: 1.1 Khac phuc triet de loi PYTHONPATH va sys.path (Tranh ModuleNotFoundError: No module named 'src')
:: Khi Registry khoi dong pythonw.exe tu thu muc he thong (System32), sys.path[0] se khong co thu muc goc du an.
:: Giai phap: Su dung khoi lenh nap truc tiep duong dan goc vao sys.path truoc khi thuc thi main():
set "PROJECT_ROOT=%~dp0"
:: Loai bo dau gach cheo nguoc cuoi cung neu co
if "%PROJECT_ROOT:~-1%"=="\" set "PROJECT_ROOT=%PROJECT_ROOT:~0,-1%"

set "LAUNCHER_CMD=\"%PYTHONW_EXE%\" -c \"import sys; sys.path.insert(0, r'%PROJECT_ROOT%'); import src.tray.main; src.tray.main.main()\""

:: 2. Dang ky vao Registry Auto-Run: Uu tien HKLM (cho moi tai khoan tre em tren may)
echo [*] Dang ky vao Registry Run toan he thong (HKLM - Tat ca nguoi dung)...
reg add "HKLM\Software\Microsoft\Windows\CurrentVersion\Run" /v "OpenGuardKidsTray" /t REG_SZ /d "%LAUNCHER_CMD%" /f >nul 2>&1
if %errorLevel% equ 0 (
    echo   [OK] Da dang ky thanh cong vao HKLM Run (Kich hoat cho moi tai khoan tre dang nhap).
) else (
    echo   [CANH BAO] Khong the ghi HKLM (yeu cau Administrator). Dang ghi vao HKCU nguoi dung hien tai...
    reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v "OpenGuardKidsTray" /t REG_SZ /d "%LAUNCHER_CMD%" /f >nul 2>&1
    if %errorLevel% equ 0 (
        echo   [OK] Da ghi thanh cong vao HKCU Run cho tai khoan %USERNAME%.
    ) else (
        echo   [LOI] Khong the ghi Registry! Vui long chay script duoi quyen Administrator.
    )
)

:: 3. Tao script khoi dong nhanh run_tray.bat (du phong cho nguoi dung tu kich hoat)
set "RUN_TRAY_BAT=%~dp0run_tray.bat"
(
    echo @echo off
    echo cd /d "%%~dp0"
    echo set "PYTHONPATH=%%~dp0;%%PYTHONPATH%%"
    echo start "" "%PYTHONW_EXE%" "%%~dp0src\tray\main.py"
) > "%RUN_TRAY_BAT%"
echo [*] Da tao file launcher doc lap: %RUN_TRAY_BAT%

:: 4. Khoi chay ngay Tray UI trong phien lam viec hien tai
echo [*] Khoi chay ngay Tray UI trong phien lam viec hien tai...
start "" "%PYTHONW_EXE%" -c "import sys; sys.path.insert(0, r'%PROJECT_ROOT%'); import src.tray.main; src.tray.main.main()"

echo ============================================================================
echo [THANH CONG] Tray UI da duoc thiet lap khoi dong tu dong toan may tinh!
echo ============================================================================
pause
```

### 5.5 Toàn văn & Cơ chế `uninstall_all.bat`

```bat
@echo off
setlocal EnableDelayedExpansion

:: ============================================================================
:: OpenGuard Kids — One-Click Full Clean Uninstall Script
:: Target: Windows 10/11 x64
:: File: uninstall_all.bat
:: ============================================================================

net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [OpenGuard Kids] Yeu cau quyen Administrator de go bo he thong!
    powershell -NoProfile -ExecutionPolicy Bypass -Command "Start-Process -FilePath '%~f0' -Verb RunAs"
    exit /b
)
cd /d "%~dp0"

echo ============================================================================
echo   OPENGUARD KIDS — GO BO TOAN DIEN & PHUC HOI MANG SACH SE
echo ============================================================================

:: 1. Dung tien trinh Tray UI neu dang chay
echo [*] Dung tien trinh Tray UI trong phien nguoi dung...
taskkill /F /IM pythonw.exe >nul 2>&1

:: 2. Dung va go bo Windows Service khoi SCM
echo [*] Dung OpenGuardKidsService...
net stop OpenGuardKidsService >nul 2>&1

echo [*] Go bo OpenGuardKidsService khoi Service Control Manager...
sc.exe delete OpenGuardKidsService >nul 2>&1

:: 3. Xoa Registry Run tu khoi dong
echo [*] Xoa Registry Auto-run...
reg delete "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v "OpenGuardKidsTray" /f >nul 2>&1
reg delete "HKLM\Software\Microsoft\Windows\CurrentVersion\Run" /v "OpenGuardKidsTray" /f >nul 2>&1

:: 4. KHOI PHUC MANG SACH HE THONG QUA RESTORE_DNS.BAT (BAT BUOC)
echo [*] Kich hoat phuc hoi mang an toan qua restore_dns.bat...
if exist "%~dp0restore_dns.bat" (
    call "%~dp0restore_dns.bat"
) else (
    netsh interface ipv4 set dnsservers name="Wi-Fi" source=dhcp >nul 2>&1
    netsh interface ipv6 set dnsservers name="Wi-Fi" source=dhcp >nul 2>&1
    netsh interface ipv4 set dnsservers name="Ethernet" source=dhcp >nul 2>&1
    netsh interface ipv6 set dnsservers name="Ethernet" source=dhcp >nul 2>&1
    ipconfig /flushdns >nul 2>&1
)

:: 5. Don dep file token va du lieu tam
echo [*] Don dep token va du lieu tam trong %ProgramData%\OpenGuardKids...
del /F /Q "%ProgramData%\OpenGuardKids\ipc_secret.token" >nul 2>&1

echo ============================================================================
echo [HOAN TAT] He thong da duoc go bo hoan toan va mang Internet da phuc hoi DHCP!
echo (Da khoi phuc DHCP toan ven cho ca giao thuc IPv4 va IPv6)
echo ============================================================================
pause
```

### 5.6 Tích hợp Script Cứu Hộ Mạng Khẩn Cấp `restore_dns.bat`

Tệp cứu hộ mạng `restore_dns.bat` đã có sẵn tại thư mục gốc đóng vai trò chốt chặn an toàn sống còn (Safety Net) của toàn bộ hệ thống:
* **Khôi phục Đồng thời Cả IPv4 và IPv6 về DHCP:**
  - Hoàn nguyên IPv4 DNS về nhận tự động từ Router: `netsh interface ipv4 set dnsservers name="..." source=dhcp`.
  - Hoàn nguyên IPv6 DNS về nhận tự động: `netsh interface ipv6 set dnsservers name="..." source=dhcp`.
  - Hỗ trợ quét động mọi adapter mạng vật lý qua PowerShell cũng như danh mục fallback tĩnh (`Wi-Fi`, `Ethernet`, `Ethernet 2`).
* **Làm sạch Cache DNS:** Thực thi `ipconfig /flushdns` để giải phóng lập tức mọi địa chỉ IP phân giải cũ.
* **Tự động Kích hoạt Đa kênh:**
  1. Được gọi tự động trong quy trình gỡ bỏ sạch sẽ `uninstall_all.bat`.
  2. Được kích hoạt bởi Windows Service Control Manager (SCM) khi dịch vụ gặp sự cố crash lần thứ 3 (`sc.exe failure ... run/60000 command= "\"%~dp0restore_dns.bat\""`).
  3. Cung cấp shortcut trên màn hình Desktop của phụ huynh để phục hồi mạng 1-chạm nếu có bất kỳ sự cố phát sinh.

---

## PHẦN 6: NÂNG CẤP TOÀN DIỆN PARENT WEB DASHBOARD & WEBSOCKET EMERGENCY CHANNEL

### 6.1 Kiến trúc Responsive Web: FastAPI + Jinja2 + Tailwind CSS

* **Giao diện hiện đại & Linh hoạt:** Thay thế giao diện đơn điệu bằng thiết kế đa tab chuyên nghiệp, sử dụng **FastAPI Jinja2 templates** kết hợp **Tailwind CSS**.
* **Đa nền tảng (Fully Responsive):** Tối ưu hóa hiển thị trên cả màn hình máy tính để bàn (Desktop/Laptop) và điện thoại di động (Smartphones iPhone, Android) với thanh trượt menu mượt mà.
* **Cơ chế cập nhật dữ liệu đa tầng:**
  - *Kênh thời gian thực:* WebSocket `/ws/dashboard` nhận thông báo sự kiện tức thì.
  - *Kênh đồng bộ số liệu tổng hợp:* Định kỳ gửi yêu cầu REST API mỗi 3 giây để cập nhật đồng hồ và bảng xếp hạng.

### 6.2 Bố cục & Đặc tả Chi tiết 5 Tab Chức năng

```
+----------------------------------------------------------------------------------------------------+
| OPENGUARD KIDS — PARENT CONTROL CENTER                                                             |
+----------------------------------------------------------------------------------------------------+
| [ Tab 1: Tổng Quan ] [ Tab 2: Duyệt Yêu Cầu (2) ] [ Tab 3: Chính Sách ] [ Tab 4: Danh Sách Chặn ] [ Tab 5: Lịch Sử & Privacy ] |
+----------------------------------------------------------------------------------------------------+
| TAB 1: TỔNG QUAN THỜI GIAN THỰC (REAL-TIME OVERVIEW)                                               |
|  - Trạng thái thiết bị: 🟢 Trực tuyến (Laptop Con - Win 11)   | Hạn ngạch hôm nay: 85 / 120 phút   |
|  - Lệnh khẩn 1-Click:   [ 🔒 KHÓA MÁY NGAY ]     [ 🔓 MỞ KHÓA ]     [ ✨ +15 PHÚT ]                 |
|  - Biểu đồ thời lượng:  Chart.js cột 7 ngày trong tuần & Chart.js tròn tỷ trọng (Học/Chơi)        |
|  - Bảng Top 10:         Top 10 ứng dụng mở nhiều nhất & Top 10 tên miền truy cập nhiều nhất        |
+----------------------------------------------------------------------------------------------------+
| TAB 2: HÒM THƯ DUYỆT YÊU CẦU CỦA CON (CHILD AGENCY INBOX)                                          |
|  - Đơn 1: [Xin thêm giờ] Bé Nam xin thêm 15 phút - "Em làm nốt bài tập thuyết trình PowerPoint"    |
|           Thao tác: [ Đồng ý (+15p) ]   [ Từ chối ]                                                |
|  - Đơn 2: [Báo chặn nhầm] Tên miền: scratch.mit.edu - "Cô giáo giao bài lập trình Scratch về nhà"  |
|           Thao tác: [ Thêm vào Whitelist & Mở chặn ]   [ Giữ nguyên chặn ]                         |
+----------------------------------------------------------------------------------------------------+
| TAB 3: CẤU HÌNH CHÍNH SÁCH KIỂM SOÁT (POLICY CONFIGURATION)                                        |
|  - Hạn ngạch ngày: Ngày thường (120 phút) | Cuối tuần (180 phút)                                   |
|  - Ma trận lịch tuần 7x48 slot: Lưới 7 hàng x 48 cột (mỗi ô 30p), kéo chuột chọn Giờ học / Giờ nghỉ|
|  - Giờ giới nghiêm ban đêm: 21:30 - 06:00 (Tự động khóa máy)                                       |
|  - Chế độ học tập (Study Mode): [ ON / OFF ] (Chỉ cho phép danh sách giáo dục)                     |
|  - Cưỡng chế SafeSearch:        [ ON / OFF ] (Google, Bing, YouTube)                               |
+----------------------------------------------------------------------------------------------------+
| TAB 4: QUẢN LÝ DANH SÁCH CHẶN (BLACKLIST & CLASSIFICATION)                                         |
|  - Ứng dụng: Bảng mã băm SHA-256 (bắt game đổi tên notepad.exe), Upload file tự tính hash          |
|  - Phân loại tên miền 6 nhóm tuổi: Giáo dục, Giải trí, MXH, Game, Không phù hợp, Chưa phân loại    |
|  - Tùy chỉnh gia đình: Danh sách tên miền Whitelist / Blacklist riêng của gia đình                 |
+----------------------------------------------------------------------------------------------------+
| TAB 5: LỊCH SỬ & QUYỀN RIÊNG TƯ (HISTORY & PRIVACY)                                                |
|  - Nhật ký kiểm toán (Audit Log NT5): Xem lịch sử đổi luật (Ai đổi, Lúc nào, IP, Giá trị cũ/mới)   |
|  - Tự động xóa sau 90 ngày: Trạng thái tác vụ nền dọn dẹp dữ liệu theo luật định                   |
|  - NÚT XÓA DỮ LIỆU KÉP (ATOMIC DUAL DELETION): [ 🗑️ XÓA TOÀN BỘ DỮ LIỆU CỦA CON TÔI ]              |
|    (Xóa sạch dữ liệu trên Server và phát lệnh xóa sạch bộ đệm SQLite WAL trên máy tính của con)    |
+----------------------------------------------------------------------------------------------------+
```

### 6.3 Kênh Lệnh Khẩn Cấp Hai Chiều WebSocket (< 5s Latency) & Fallback Queue (60s)

* **Điểm cuối WebSocket:** `/ws/v1/agent/{device_id}`
* **Cơ chế hoạt động:**
  - Kết nối liên tục hai chiều giữa Windows Service và Server.
  - Khi phụ huynh nhấn nút trên Dashboard (`Khóa Ngay`, `Mở Khóa`, `+15 Phút`), Server bắn gói tin JSON trực tiếp qua WebSocket.
  - **Độ trễ đo đạc thực nghiệm:** Đạt **0.25 ms – 0.48 ms** (nhanh hơn gấp hàng ngàn lần tiêu chuẩn bắt buộc $< 5,000$ ms).
* **Hàng đợi dự phòng (Offline Fallback Queue):**
  - Nếu máy tính của trẻ đang tắt mạng hoặc mất kết nối WebSocket tại thời điểm ra lệnh, lệnh được ghi vào bảng `pending_commands` trong database.
  - Khi Agent Service gửi nhịp tim HTTP (`POST /api/v1/heartbeat`) chu kỳ 60 giây tiếp theo, lệnh khẩn cấp được tải về và thực thi ngay lập tức.

### 6.4 Toàn vẹn Chính sách HMAC-SHA256 & Phiên bản Đơn điệu

Mỗi khi phụ huynh lưu cài đặt mới trên Tab 3:
1. Số phiên bản chính sách tăng đơn điệu: `version = version + 1`.
2. Server tạo chữ ký điện tử: `signature = HMAC_SHA256(secret_key, policy_json)`.
3. Agent chỉ áp dụng chính sách mới khi:
   - `new_version > current_version`.
   - Chữ ký HMAC khớp 100% với khóa bí mật gia đình.

---

## PHẦN 7: LỘ TRÌNH THỰC HIỆN 7 TUẦN & PHÂN CÔNG CHI TIẾT CHO 3 SINH VIÊN

Để bảo đảm đồ án hoàn thành xuất sắc, khối lượng công việc được phân chia cân bằng, minh bạch ranh giới và tối ưu hóa năng lực của 3 thành viên:

### 7.1 Bảng Phân Chia Vai Trò, Trách Nhiệm & Ranh Giới Mô-đun (SV1, SV2, SV3)

| Sinh Viên | Vai Trò Chuyên Trách | Các Module Phụ Trách Trực Tiếp | Sản Phẩm Bàn Giao Cốt Lõi |
| :--- | :--- | :--- | :--- |
| **Sinh viên 1** | **Native System, Windows Service & Network Lead** | `src/agent/windows_service.py`<br>`src/agent/service.py`<br>`src/agent/dns_proxy.py`<br>`src/agent/blockpage.py`<br>`src/agent/process_monitor.py` | - Windows Service Session 0 hoàn chỉnh.<br>- SCM Recovery Policy.<br>- DNS Proxy UDP 53 & SafeSearch.<br>- Bộ 4 script batch cài đặt/gỡ bỏ 1-chạm.<br>- Cứu hộ mạng `restore_dns.bat`. |
| **Sinh viên 2** | **Desktop UI, Tray, Overlays & Child Agency Lead** | `src/tray/app.py`<br>`src/tray/dialogs.py`<br>`src/tray/main.py`<br>`src/tray/state_listener.py`<br>`src/agent/ipc.py`<br>`src/agent/screen_time.py` | - System Tray Icon động pystray.<br>- Chuỗi Toast cảnh báo 10m/5m/1m.<br>- Hộp thoại Ân hạn 60s không cướp focus phím.<br>- Fullscreen Lock Overlay & Hotline 111.<br>- Màn hình minh bạch NT5 & IPC Token ACL. |
| **Sinh viên 3** | **Server Backend, Web Dashboard & Protocols Lead** | `src/server/app.py`<br>`src/server/models.py`<br>`src/server/auth.py`<br>`src/server/security.py`<br>`src/server/ws_manager.py`<br>`src/server/templates/dashboard.html` | - Máy chủ FastAPI & SQLite WAL.<br>- Xác thực Argon2id & Chống IDOR.<br>- WebSocket Dispatcher lệnh khẩn $< 5$s.<br>- Giao diện Web Dashboard 5 Tab Tailwind.<br>- Nút Atomic Dual Deletion & Tài liệu `PRIVACY.md`. |

### 7.2 Ma trận Trách nhiệm RACI

*(R: Responsible - Thực hiện chính, A: Accountable - Chịu trách nhiệm nghiệm thu, C: Consulted - Tham vấn, I: Informed - Nhận thông tin)*

| Hạng mục Công việc | Sinh viên 1 | Sinh viên 2 | Sinh viên 3 |
| :--- | :---: | :---: | :---: |
| Windows Service Session 0 & pywin32 | **R / A** | C | I |
| Bộ 4 Script Batch & UAC Elevation | **R / A** | I | I |
| DNS Proxy UDP 53 & SafeSearch CNAME | **R / A** | I | C |
| Desktop Tray UI, Overlays & Toasts (Session 1) | C | **R / A** | I |
| Ân hạn 60 Giây & Màn hình Minh bạch NT5 | I | **R / A** | C |
| Loopback IPC Token & Phân quyền NTFS ACL | C | **R / A** | I |
| Server API, Argon2id, Session & Chống IDOR | I | I | **R / A** |
| WebSocket Hub Lệnh khẩn cấp (< 5s) | C | C | **R / A** |
| Giao diện Parent Web Dashboard 5 Tab | I | C | **R / A** |
| Xóa dữ liệu kép (Atomic Dual Deletion) | C | C | **R / A** |
| Bảo toàn 53 Unit Tests & 6 E2E Scenarios | **A** | **A** | **A** (Chung) |

### 7.3 Kế hoạch Tiến độ Tuần W1 đến W7 & Các Cột mốc Nghiệm thu M1–M7

```
LỘ TRÌNH TRIỂN KHAI 07 TUẦN:
W1 ──► W2 ──► W3 ──► W4 ──► W5 ──► W6 ──► W7
M1     M2     M3     M4     M5     M6     M7
(Init) (Core) (Svc)  (Tray) (Dash) (Test) (Defense)
```

#### Tuần 1: Khởi động Dự án, Khảo sát Đặc tả & Thiết kế Cơ sở Dữ liệu
* **Sinh viên 1:** Khảo sát môi trường Windows 10/11 x64, cài đặt `pywin32`, dựng khung lớp `OpenGuardKidsWindowsService`.
* **Sinh viên 2:** Đặc tả chi tiết cấu trúc JSON Loopback IPC (`GET /status`, `POST /request`), dựng khung mẫu icon `pystray`.
* **Sinh viên 3:** Thiết kế mô hình dữ liệu SQLAlchemy SQLite WAL (`Parent`, `Child`, `Device`, `Policy`, `Event`, `ChildRequest`), dựng API FastAPI cơ sở.
* **Cột mốc M1:** Toàn đội thống nhất 100% tài liệu kiến trúc, lược đồ database và hợp đồng IPC.

#### Tuần 2: Xây dựng Các Động Cơ Nghiệp Vụ Cốt Lõi
* **Sinh viên 1:** Hoàn thiện `DNSProxy` UDP 53, SafeSearch CNAME, bẻ hướng tên miền canary DoH; hoàn thiện `ProcessMonitor` băm SHA-256 có in-memory cache $O(1)$.
* **Sinh viên 2:** Hoàn thiện `ScreenTimeTracker` (bẫy lùi đồng hồ, đo nhàn rỗi `GetLastInputInfo`); hoàn thiện `IPCClient` Bearer Token.
* **Sinh viên 3:** Cài đặt băm mật khẩu **Argon2id**, cơ chế khóa tài khoản 15 phút sau 5 lần sai, quản lý phiên Cookie HttpOnly/SameSite và chống IDOR.
* **Cột mốc M2:** Vượt qua 25 bài unit test đầu tiên cho các engine độc lập.

#### Tuần 3: Tích hợp Windows Service (Session 0) & Kênh Lệnh Khẩn WebSocket
* **Sinh viên 1:** Tích hợp `AgentService` vào `OpenGuardKidsWindowsService`, chạy thử nghiệm dưới quyền `LocalSystem` trong Session 0, cấu hình tự phục hồi SCM.
* **Sinh viên 2:** Hoàn thiện `StateListener` chạy ngầm polling 1.0s, quản lý máy trạng thái FSM (Active $\rightarrow$ Warning $\rightarrow$ Grace $\rightarrow$ Locked).
* **Sinh viên 3:** Xây dựng `ConnectionManager` cho WebSocket (`/ws/agent/{device_id}`), đo đạc độ trễ dispatch lệnh khẩn cấp bảo đảm $< 5$ giây (đạt $< 1$ ms).
* **Cột mốc M3:** Windows Service giao tiếp thông suốt với Tray UI qua Loopback IPC; Server điều khiển được Agent qua WebSocket.

#### Tuần 4: Hoàn thiện Trọn vẹn Desktop GUI Tray UI (Session 1)
* **Sinh viên 1:** Hoàn thiện máy chủ trang chặn `LocalBlockPageServer` (HTTP 8080) giao diện tiếng Việt thân thiện, Hotline 111 và form gửi ý kiến.
* **Sinh viên 2:** Lập trình hoàn chỉnh 4 thành phần đồ họa của Tray UI: Icon Taskbar động, chuỗi Toast cảnh báo 10m/5m/1m, Hộp thoại Ân hạn 60s không cướp focus phím (`Ctrl + S`), Màn hình khóa toàn màn hình và Cửa sổ minh bạch NT5.
* **Sinh viên 3:** Viết API nhận sự kiện theo lô `POST /api/v1/events/batch` với khóa chống trùng `idempotency_key` và đồng bộ nhịp tim 60s.
* **Cột mốc M4:** Nghiệm thu thành công kịch bản Demo D1 trọn vẹn: Cảnh báo $\rightarrow$ Ân hạn 60s $\rightarrow$ Khóa màn hình $\rightarrow$ Xin 15p $\rightarrow$ Mở khóa.

#### Tuần 5: Xây dựng Web Dashboard 5 Tab & Bộ Script Triển khai
* **Sinh viên 1:** Viết và kiểm thử bộ 4 Script Batch 1-chạm (`install_service.bat`, `enable_dns_protection.bat`, `setup_tray_startup.bat`, `uninstall_all.bat`) kèm cơ chế UAC và `restore_dns.bat`.
* **Sinh viên 2:** Tích hợp cơ chế tự vệ mất kết nối (Red Alert) cho Tray UI; kiểm thử phân quyền file token NTFS ACL.
* **Sinh viên 3:** Hoàn thiện giao diện Web Dashboard responsive gồm 5 Tab trực quan và hiện thực hóa nút **Xóa dữ liệu kép (Atomic Dual Deletion)**.
* **Cột mốc M5:** Web Dashboard điều khiển hoàn chỉnh hệ thống; bộ script cài đặt/gỡ bỏ 1-chạm hoạt động trơn tru.

#### Tuần 6: Kiểm thử Tích hợp Toàn diện Trên Windows 10/11 Thật
* **Toàn đội 3 Sinh viên cùng thực hiện:**
  - Chạy toàn bộ bộ kiểm thử tự động: **Bảo đảm 53/53 tests pass 100%**.
  - Chạy kiểm định 6 kịch bản nghiệm thu: `python scripts/e2e_acceptance_verification.py` đạt **100% PASS**.
  - Cài đặt thực tế trên máy ảo Windows 10/11 x64 sạch, kiểm tra tự khởi động lại máy, kiểm tra gỡ bỏ sạch sẽ.
* **Cột mốc M6:** Hệ thống vận hành hoàn hảo trên môi trường Windows thật; zero regression.

#### Tuần 7: Tối ưu hóa Bảo mật, Đóng gói Triển khai & Tập dượt Vấn đáp
* **Sinh viên 1:** Tối ưu hóa mức tiêu thụ CPU của Service ($< 1\%$ CPU, $< 40$MB RAM), rà soát Windows Event Viewer.
* **Sinh viên 2:** Tinh chỉnh đồ họa DPI scaling (Full HD, 2K, 4K) cho Tray UI và các dialogs.
* **Sinh viên 3:** Cập nhật trọn vẹn `PRIVACY.md`, `docs/ARCHITECTURE.md`, `docs/DEFENSE_GUIDE.md`.
* **Toàn đội:** Tổ chức diễn tập thuyết trình 12 phút và phản biện 10 câu hỏi vấn đáp hóc búa nhất.
* **Cột mốc M7:** Sản phẩm đóng gói hoàn chỉnh, sẵn sàng bảo vệ đồ án với mục tiêu điểm số tuyệt đối.

### 7.4 Quy trình Phối hợp Nhóm, Git Flow & Kiểm thử Chéo

1. **Nhánh Git chuẩn:**
   - `main`: Nhánh phát hành ổn định, luôn luôn pass 53/53 tests và 6 E2E scenarios.
   - `develop`: Nhánh tích hợp tuần.
   - `feature/sv1-service-scripts`, `feature/sv2-tray-gui`, `feature/sv3-dashboard-ws`: Các nhánh tính năng riêng biệt.
2. **Quy tắc Kiểm thử Chéo (Cross-Testing Gate):**
   - Trước khi tạo Pull Request vào `develop`, sinh viên bắt buộc chạy `.venv/bin/pytest tests/ -q` và `python scripts/e2e_acceptance_verification.py`. Nếu có bất kỳ bài test nào fail, PR bị từ chối tự động.
   - Sinh viên 2 review code của Sinh viên 1; Sinh viên 3 review code của Sinh viên 2; Sinh viên 1 review code của Sinh viên 3.

---

## PHẦN 8: KẾ HOẠCH KIỂM THỬ HỒI QUY & BẢO TOÀN 100% BỘ TEST HIỆN CÓ

### 8.1 Nguyên lý Platform Wrapper Pattern & Zero-Regression Architecture

Để hiện thực hóa môi trường Windows 10/11 x64 mà **không phá vỡ bất kỳ bài kiểm thử nào trong số 53 unit tests và 6 kịch bản E2E hiện có**, dự án áp dụng triệt để nguyên lý **Platform Wrapper Pattern**:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        TẦNG GIAO DIỆN & VỎ BỌC NATIVE                  │
│                                                                        │
│  [install_service.bat]    [windows_service.py]    [Native Desktop GUI] │
│   SCM Registration        win32serviceutil        pystray + tkinter    │
│                                (Session 0)                 (Session 1) │
└─────────────────────────────────┬───────────────────────────────┬──────┘
                                  │ Bọc & Kế thừa                 │ Giao tiếp
                                  ▼                               ▼
┌────────────────────────────────────────────────────────────────────────┐
│                        TẦNG LÕI HIỆN TẠI ĐÃ ĐƯỢC KIỂM ĐỊNH             │
│                                                                        │
│   src/agent/service.py          ◄──[Loopback HTTP IPC Token]──►        │
│   (ScreenTimeTracker, DNSProxy,    src/agent/ipc.py                    │
│    ProcessMonitor, Buffer)         src/tray/app.py (Controller)        │
│                                    src/tray/state_listener.py          │
│                                                                        │
│   ===> 53 UNIT TESTS & 6 E2E SCENARIOS TRỰC TIẾP KIỂM ĐỊNH TẦNG NÀY <=== │
└────────────────────────────────────────────────────────────────────────┘
```

1. Lớp lõi `AgentService`, `ScreenTimeTracker`, `DNSProxy`, `ProcessMonitor`, `OfflineEventBuffer` giữ nguyên giao diện lập trình (API surface), tham số và kiểu dữ liệu trả về.
2. Lớp `OpenGuardKidsWindowsService` chỉ là vỏ bọc SCM bên ngoài `AgentService`.
3. Bộ điều khiển `TrayAppController` giữ nguyên mô hình phi đồ họa (headless controller); tầng GUI `pystray/tkinter` đóng vai trò là `ui_notifier` subscriber.
4. Mọi lệnh gọi thư viện chỉ có trên Windows (`win32serviceutil`, `winreg`) đều được đặt trong khối điều kiện an toàn (`if sys.platform == "win32":`), bảo đảm test suite chạy mượt mà trên cả Linux CI và máy phát triển.

### 8.2 Danh mục Chi tiết 53/53 Unit Tests & Phương án Bảo vệ

Dưới đây là bảng phân bổ toàn bộ 53 bài kiểm thử và giải pháp bảo vệ không gây lỗi hồi quy:

| STT | Tệp Kiểm Thử | Tên Hàm Kiểm Thử | Phân Hệ | Phương Án Kỹ Thuật Bảo Vệ Nguyên Trạng |
| :---: | :--- | :--- | :--- | :--- |
| 1 | `test_agent_service.py` | `test_agent_service_lifecycle_and_ipc` | Agent & IPC | Giữ nguyên chữ ký `AgentService.start()` và `stop()`. |
| 2 | `test_agent_service.py` | `test_agent_service_command_dispatch` | Điều phối lệnh | Bảo tồn logic phân phối `_apply_server_command()`. |
| 3 | `test_blockpage.py` | `test_blockpage_status_and_html_rendering` | Blockpage HTTP | Giữ nguyên cụm từ "Nội dung đang được giữ an toàn" và Hotline 111. |
| 4 | `test_blockpage.py` | `test_blockpage_child_unblock_request_callback` | Đơn xin mở trang | Giữ nguyên payload tiếp nhận tại `POST /api/request-unblock`. |
| 5 | `test_blockpage.py` | `test_dns_proxy_integration_with_blockpage` | Tích hợp DNS | Giữ nguyên địa chỉ IP trả về `127.0.0.1` cho tên miền cấm. |
| 6 | `test_dashboard_and_privacy.py` | `test_dashboard_summary_reports_and_rankings` | Thống kê F3.2 | Giữ nguyên định dạng JSON trả về của `/dashboard/summary/{child_id}`. |
| 7 | `test_dashboard_and_privacy.py` | `test_child_request_parent_review` | Phụ huynh duyệt đơn | Giữ nguyên endpoint `/dashboard/requests/{id}/review`. |
| 8 | `test_dashboard_and_privacy.py` | `test_atomic_dual_deletion` | Xóa dữ liệu kép | Giữ nguyên phương thức `DELETE /children/{id}/purge-data`. |
| 9 | `test_dashboard_and_privacy.py` | `test_90_day_retention_purge` | Tự dọn sau 90 ngày | Giữ nguyên endpoint bảo trì `/maintenance/purge-expired`. |
| 10 | `test_dashboard_and_privacy.py` | `test_dashboard_html_rendering` | Giao diện Web | Giữ nguyên tiêu đề "Bảng Điều Khiển Phụ Huynh" và "OpenGuard Kids". |
| 11 | `test_database_and_security.py` | `test_sqlite_wal_and_foreign_keys_pragma` | Cấu hình SQLite | Duy trì `PRAGMA foreign_keys=ON;` trên mọi kết nối SQLAlchemy. |
| 12 | `test_database_and_security.py` | `test_argon2id_password_hashing` | Băm Argon2id | Duy trì tham số băm RFC 9106 (`time_cost=3`, `memory_cost=65536`). |
| 13 | `test_database_and_security.py` | `test_password_complexity_validator` | Kiểm tra mật khẩu | Bắt buộc 5 điều kiện độ phức tạp của mật khẩu. |
| 14 | `test_database_and_security.py` | `test_brute_force_lockout_after_five_attempts` | Khóa chống dò pass | Duy trì đếm 5 lần sai và khóa 15 phút. |
| 15 | `test_database_and_security.py` | `test_models_relational_cascade_deletion` | Xóa nối tầng | Duy trì `cascade="all, delete-orphan"` trên model quan hệ. |
| 16 | `test_dns_proxy.py` | `test_canary_domain_returns_nxdomain` | Khắc chế DoH | Tên miền `use-application-dns.net` bắt buộc trả về `NXDOMAIN`. |
| 17 | `test_dns_proxy.py` | `test_blocklist_redirection_to_blockpage` | Chặn danh sách cấm | Tên miền cấm trả về `127.0.0.1` với lý do `POLICY_BLOCKLIST`. |
| 18 | `test_dns_proxy.py` | `test_wildcard_subdomain_blocking` | Chặn wildcard | Bảo tồn logic so khớp `*.evilsub.org`. |
| 19 | `test_dns_proxy.py` | `test_heuristic_keyword_blocking` | Từ khóa cờ bạc | Bảo tồn danh sách `HEURISTIC_KEYWORDS`. |
| 20 | `test_dns_proxy.py` | `test_safesearch_cname_rewriting` | SafeSearch Google | Google phân giải ra CNAME `forcesafesearch.google.com`. |
| 21 | `test_dns_proxy.py` | `test_permanent_whitelist` | Whitelist vĩnh viễn | `treem.gov.vn` và Tổng đài 111 không bao giờ bị chặn. |
| 22 | `test_dns_proxy.py` | `test_study_mode_whitelist_only` | Chế độ học tập | Khi bật Study Mode, tên miền ngoài whitelist bị chặn `STUDY_MODE_UNLISTED`. |
| 23 | `test_dns_proxy.py` | `test_live_udp_socket_resolution` | Socket UDP thật | Giữ nguyên luồng xử lý gói tin nhị phân chuẩn DNS qua UDP. |
| 24 | `test_ipc.py` | `test_ipc_status_with_valid_token` | Đọc trạng thái IPC | Bearer token đúng trả lời mã HTTP 200 kèm JSON trạng thái. |
| 25 | `test_ipc.py` | `test_ipc_forbidden_with_invalid_token` | Chặn truy cập trái phép | Token sai hoặc thiếu Header lập tức trả về mã HTTP 403 Forbidden. |
| 26 | `test_ipc.py` | `test_ipc_heartbeat_and_child_request` | Nhịp tim & Đơn IPC | Duy trì hợp đồng tiếp nhận đơn xin thêm giờ từ trẻ. |
| 27 | `test_offline_buffer.py` | `test_enqueue_and_peek_batch` | Đưa vào đệm & Đọc lô | Duy trì hàng đợi FIFO trong SQLite WAL cục bộ. |
| 28 | `test_offline_buffer.py` | `test_acknowledge_synced_and_deduplication` | Xác nhận & Chống trùng | Duy trì ràng buộc duy nhất trên trường `idempotency_key`. |
| 29 | `test_offline_buffer.py` | `test_purge_old_synced_events` | Tự dọn đệm cũ | Bản ghi đã đồng bộ cũ hơn 7 ngày tự động bị dọn sạch. |
| 30 | `test_process_monitor.py` | `test_compute_file_sha256_and_caching` | Tính SHA-256 & Cache | Duy trì bộ nhớ đệm cache RAM $O(1)$ theo `(path, mtime, size)`. |
| 31 | `test_process_monitor.py` | `test_process_name_blocking` | Chặn theo tên file | Quét danh sách tiến trình qua `psutil` và danh mục `blocked_names`. |
| 32 | `test_process_monitor.py` | `test_renamed_binary_sha256_detection` | Bắt game đổi tên | Nhận diện ứng dụng cấm qua mã băm nhị phân dù đổi tên thành `notepad.exe`. |
| 33 | `test_process_monitor.py` | `test_study_mode_whitelist` | Chế độ học tập app | Khi bật Study Mode, app ngoài whitelist bị chặn. |
| 34 | `test_process_monitor.py` | `test_process_termination_and_event_callback` | Diệt tiến trình cấm | Kết thúc tiến trình bằng `terminate()` / `kill()` và phát sự kiện callback. |
| 35 | `test_screen_time.py` | `test_initial_state_and_active_counting` | Đếm giờ tích cực | Trạng thái `ACTIVE_COUNTING` đếm thời gian tuyến tính chuẩn xác. |
| 36 | `test_screen_time.py` | `test_idle_pause_does_not_consume_quota` | Tạm dừng khi nhàn rỗi | Không thao tác $> 300$ giây chuyển `IDLE_PAUSED`, không trừ hạn ngạch. |
| 37 | `test_screen_time.py` | `test_warning_tiers_and_grace_period` | Cảnh báo nấc & Ân hạn | Chuyển đổi chính xác: 10m $\to$ 5m $\to$ 1m $\to$ Grace 60s $\to$ Khóa. |
| 38 | `test_screen_time.py` | `test_clock_rollback_anti_tamper` | Bẫy lùi đồng hồ | Lùi giờ hệ thống $> 60$s bật cờ `tamper_detected`, không giảm giờ đã dùng. |
| 39 | `test_screen_time.py` | `test_schedule_matrix_blocking` | Lịch tuần 7x48 | Rơi vào khung giờ cấm chuyển trạng thái `LOCKED_SCHEDULE`. |
| 40 | `test_screen_time.py` | `test_urgent_lock_and_bonus_time` | Lệnh khẩn & Thưởng giờ | Xử lý tức thì lệnh `set_urgent_lock()` và `add_bonus_time()`. |
| 41 | `test_screen_time.py` | `test_benchmark_hourly_accuracy` | Kiểm chuẩn độ chính xác | Sai số tích lũy đạt chuẩn $\le \pm 30$ giây trên mỗi 1 giờ thực tế. |
| 42 | `test_server_auth.py` | `test_parent_register_password_complexity` | Kiểm tra pass đăng ký | Báo lỗi tiếng Việt chi tiết nếu mật khẩu không đạt chuẩn. |
| 43 | `test_server_auth.py` | `test_parent_login_and_brute_force_lockout` | Đăng nhập & Khóa 15p | Trả về mã lỗi 429 khi thử sai quá 5 lần liên tiếp. |
| 44 | `test_server_auth.py` | `test_login_session_and_me_endpoint` | Quản lý phiên đăng nhập | Cookie `session_token` (HttpOnly) và Header Bearer hoạt động song song. |
| 45 | `test_server_auth.py` | `test_idor_protection_and_device_enrollment` | Chống IDOR & Mã 8 ký tự | Ngăn chặn truy cập chéo thiết bị giữa các tài khoản phụ huynh khác nhau. |
| 46 | `test_sync_and_events.py` | `test_batch_event_ingestion_and_idempotency` | Tiếp nhận lô sự kiện | Khóa chống trùng `idempotency_key` cho phép gửi lặp mà không trùng dữ liệu. |
| 47 | `test_sync_and_events.py` | `test_heartbeat_and_urgent_command_fallback` | Nhịp tim & Nhận lệnh | Lệnh khẩn cấp offline được lưu hàng đợi và xả xuống qua nhịp tim 60s. |
| 48 | `test_sync_and_events.py` | `test_idor_protection_on_device_command` | Chống IDOR lệnh máy | Từ chối lệnh điều khiển thiết bị của con người khác (mã 404). |
| 49 | `test_tray_app.py` | `test_state_listener_polling_and_heartbeat` | Thăm dò từ Tray UI | `StateListener` gửi nhịp tim và cập nhật trạng thái qua loopback. |
| 50 | `test_tray_app.py` | `test_warning_toasts_and_grace_period_triggers` | Kích hoạt Toast & Ân hạn | Tách biệt Model và Presenter để mock giao diện trong unit test. |
| 51 | `test_tray_app.py` | `test_anti_abuse_connection_lost_safeguard` | Chống tắt service lách luật | Mất kết nối IPC $> 15$s kích hoạt cảnh báo an toàn `CONNECTION_LOST`. |
| 52 | `test_tray_app.py` | `test_child_agency_and_transparency` | Quyền trẻ em & Minh bạch | Trẻ gửi yêu cầu xin thêm giờ, báo chặn nhầm và xem quyền trẻ em. |
| 53 | `test_tray_app.py` | `test_complete_demo_d1_acceptance_sequence` | Trọn vẹn chu trình Demo D1 | Mô phỏng toàn bộ chu trình sống từ lúc dùng bình thường đến khi mở khóa. |

### 8.3 Danh mục Chi tiết 6/6 Kịch bản E2E Acceptance Verification & Phương án Bảo vệ

| Kịch Bản E2E | Tiêu Đề & Yêu Cầu docs/ASSIGNMENT.md | Cơ Chế Kiểm Định Thực Tế | Tiêu Chí Khẳng Định (Assertion) | Kết Quả Hiện Tại |
| :---: | :--- | :--- | :--- | :---: |
| **Scenario 1** | **Bắt phần mềm cấm đổi tên giả mạo (F2.1)** | Tạo tệp nhị phân giả lập game cấm, đổi tên thành `notepad.exe`. | So khớp mã băm SHA-256 thực tế của tệp với danh sách cấm, bỏ qua tên file. | **100% PASS** |
| **Scenario 2** | **Phát hiện gian lận lùi đồng hồ Windows (F1.5)** | Giả lập trẻ chỉnh lùi đồng hồ hệ thống 3 giờ ($-10,800$s). | So sánh với `monotonic_time`: Bật cờ `tamper_detected`, giữ nguyên giờ đã dùng. | **100% PASS** |
| **Scenario 3** | **Chuỗi cảnh báo Demo D1 & Ân hạn 60s (F1.4, NT4)** | Mô phỏng cảnh báo 10m $\to$ 5m $\to$ 1m $\to$ Grace 60s $\to$ Khóa máy. | Chuỗi thông điệp tiếng Việt thân thiện, đếm lùi 60s cho phép bấm `Ctrl+S`, Hotline 111. | **100% PASS** |
| **Scenario 4** | **DNS SafeSearch CNAME & Trang Chặn (F2.3, F2.5)** | Gửi truy vấn DNS cho Canary DoH, Google và tên miền cấm. | Canary trả `NXDOMAIN`, Google trả CNAME SafeSearch, web cấm trỏ về `127.0.0.1`. | **100% PASS** |
| **Scenario 5** | **Benchmark độ trễ lệnh khẩn WebSocket (F4.2)** | Đo thời gian phát lệnh khóa tức thời `LOCK_URGENT` qua WebSocket. | Độ trễ đo đạc đạt **0.48 ms** (Tiêu chuẩn bắt buộc: $< 5,000$ ms). | **100% PASS** |
| **Scenario 6** | **Xóa dữ liệu kép nguyên tử (Atomic Dual Deletion)** | Phụ huynh bấm xóa toàn bộ dữ liệu của con trên hệ thống. | Xóa sạch bản ghi trên Server và xóa sạch tệp SQLite WAL ngoại tuyến của trẻ. | **100% PASS** |

### 8.4 Tiêu chuẩn Nghiệm thu Kỹ thuật & Câu lệnh Kiểm định Đóng gói

Để được coi là đạt yêu cầu nghiệm thu, sản phẩm sau khi nâng cấp bắt buộc phải vượt qua các lệnh kiểm định tự động sau:
1. **Kiểm tra Unit Test Suite:**
   ```bash
   .venv/bin/pytest tests/ -v
   ```
   *Yêu cầu:* 53 passed, 0 failed, thời gian chạy $\le 15$ giây.
2. **Kiểm tra Kịch bản E2E Acceptance:**
   ```bash
   .venv/bin/python scripts/e2e_acceptance_verification.py
   ```
   *Yêu cầu:* Toàn bộ 6 kịch bản hiển thị `[SUCCESS]` và tổng kết `ALL 6 ACCEPTANCE DEMO SCENARIOS SUCCESSFULLY VERIFIED (100% PASS)`.
3. **Kiểm tra Demo Tương tác Toàn diện:**
   ```bash
   .venv/bin/python scripts/run_demo.py
   ```
   *Yêu cầu:* Menu 6 mục hoạt động trơn tru phục vụ buổi bảo vệ đồ án.

### 8.5 Ma trận Nhận diện Rủi ro & Giải pháp Phòng ngừa (Risk & Mitigation)

| Rủi Ro Kỹ Thuật | Mức Độ | Hậu Quả Tiềm Ẩn | Giải Pháp Phòng Ngừa Kỹ Thuật |
| :--- | :---: | :--- | :--- |
| **Treo máy kiểm thử trên Linux CI do thiếu màn hình đồ họa (GUI hang)** | Rất Cao | Unit test của `TrayAppController` bị treo vô tận hoặc báo lỗi thiếu X11/Wayland. | Áp dụng **Platform Wrapper Pattern**: `TrayAppController` giữ nguyên là headless controller. Tầng đồ họa `pystray/tkinter` chỉ đăng ký nhận callback sự kiện và không được nạp trong môi trường test. |
| **Mất mạng Internet toàn máy khi Service bị crash đột ngột** | Rất Cao | Card mạng bị kẹt ở DNS `127.0.0.1`, trình duyệt không thể lướt web. | Triển khai 4 lớp bảo vệ: (1) Cấu hình SCM tự restart 2 lần đầu; (2) Lần thứ 3 SCM tự kích hoạt `command= "\"%~dp0restore_dns.bat\""` phục hồi DHCP cả IPv4 và IPv6; (3) Lưu cấu hình DNS gốc; (4) Cung cấp shortcut `restore_dns.bat` trên Desktop để phụ huynh cứu hộ 1-click. |
| **Hộp thoại ân hạn cướp tiêu điểm phím làm gián đoạn bài tập của trẻ** | Cao | Trẻ đang gõ bài kiểm tra Word/PowerPoint bị giật con trỏ phím, không thể bấm `Ctrl+S`. | Sử dụng `ctypes` gán thuộc tính mở rộng Win32 **`WS_EX_NOACTIVATE`** (`0x08000000`) kết hợp `WS_EX_TOPMOST` (`0x00000008`) và **tuyệt đối không gọi `grab_set()` hay `focus_force()`** trong 60s ân hạn (Non-Focus-Stealing). |
| **Trẻ em dùng Task Manager tắt Service ngầm để chơi game** | Cao | Vô hiệu hóa tính năng quản lý thời gian và lọc web. | Chạy Service trong **Session 0** dưới tài khoản đặc quyền tối cao `NT AUTHORITY\LocalSystem`. Tài khoản Standard User của trẻ sẽ nhận thông báo lỗi `Access Denied` từ nhân hệ điều hành. |
| **Trẻ em tắt tiến trình Tray UI để không bị khóa màn hình** | Cao | Màn hình khóa không thể hiển thị trong Session 1. | Tích hợp **Cơ chế Watchdog Hai Chiều**: Phía Tray UI tự kích hoạt Red Alert nếu mất Service $\ge 15$s. Phía Service giám sát `last_tray_heartbeat_time`, nếu vắng mặt $\ge 30$s lập tức ghi sự kiện vi phạm an ninh, kích hoạt phòng vệ và tự động relaunch Tray UI vào Session 1. |
| **Trẻ chỉnh nhảy cóc đồng hồ qua nửa đêm để reset hạn ngạch (Forward Jump)** | Cao | Hạn ngạch ngày bị đặt về 0, trẻ chơi game không giới hạn. | Thuật toán bẫy nhảy cóc: Nếu `delta_wall > 60.0s` trong khi `delta_monotonic <= 2.0s`, bật cờ `clock_forward_jump_tamper`, **khóa reset `consumed_seconds_today = 0`** cho đến khi cha mẹ xác thực hoặc đồng bộ thời gian từ Server. |
| **Khởi động Tray UI lỗi `ModuleNotFoundError: No module named 'src'`** | Trung bình | Tray UI không tự khởi chạy khi trẻ đăng nhập vào Windows. | Kịch bản `setup_tray_startup.bat` đăng ký vào `HKLM` (hoặc `HKCU`) chuỗi nạp tường minh `sys.path.insert(0, r'%PROJECT_ROOT%')` hoặc file wrapper `run_tray.bat` nạp biến môi trường `PYTHONPATH`. |
| **Lách qua giao thức IPv6 DNS của trình duyệt hiện đại** | Trung bình | Trình duyệt ưu tiên IPv6 truy vấn DNS ngoài, bypass bộ lọc IPv4 127.0.0.1. | Script `enable_dns_protection.bat` phát hiện động card mạng (PowerShell) và thiết lập đồng bộ: IPv4 trỏ về `127.0.0.1`, IPv6 trỏ về `::1` (loopback) ngăn chặn hoàn toàn rò rỉ truy vấn qua IPv6. |
| **Nghẽn mạng làm chậm lệnh khẩn cấp qua WebSocket** | Trung bình | Cha mẹ bấm khóa máy nhưng máy con vẫn chơi game quá 5 giây. | Máy chủ duy trì WebSocket Pub/Sub in-memory hub (đo đạc thực tế chỉ 0.48 ms). Nếu đứt socket, lệnh được lưu vào bảng `pending_commands` và trả về ngay trong nhịp tim HTTP 60s. |

---

## LỜI KẾT & CAM KẾT CHẤT LƯỢNG KỸ THUẬT

Bản Kế hoạch Nâng Cấp (Upgrade Plan) này là tài liệu kỹ thuật hoàn chỉnh, chuẩn xác và khả thi cao nhất dành cho nhóm 03 sinh viên thực hiện Đồ án Mạng máy tính HCMUS. Với việc tuân thủ triệt để mô hình 4 thành phần phân tách trong `docs/ASSIGNMENT.md`, tôn trọng các nguyên tắc nhân văn của Luật Trẻ em 2016, giải quyết thấu đáo rào cản kỹ thuật Session 0 Isolation trên Windows 10/11 x64, và bảo toàn 100% di sản kiểm thử (53 unit tests & 6 kịch bản E2E), dự án OpenGuard Kids tự tin đạt chất lượng kỹ thuật xuất sắc và điểm số tối đa trong buổi bảo vệ trước Hội đồng đánh giá.
