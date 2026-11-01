# Học Phần 2: Lập Trình Hệ Thống Windows & Cơ Chế Session 0 Isolation

> **Môn học:** Mạng Máy Tính (Computer Networks) — Khoa CNTT, HCMUS  
> **Chuyên đề:** Windows Internals, Process Monitoring, Screen-Time Tracking & Anti-Tamper  
> **Tài liệu kỹ thuật liên quan:** [docs/ARCHITECTURE.md](file:///home/cornar/Projects/OpenGuard-Kids/docs/ARCHITECTURE.md) (Mục 1 & Mục 3)  
> **File âm thanh bài giảng:** [audio_lessons/hoc_phan_02.mp3](file:///home/cornar/Projects/OpenGuard-Kids/audio_lessons/hoc_phan_02.mp3)

---

## 1. Bài Toán Bảo Vệ Tiến Trình: Session 0 vs Session 1

### 1.1 Điểm yếu của phần mềm giám sát thông thường
Nếu bạn chỉ viết một chương trình Python bình thường (ví dụ: file `agent.exe` có giao diện cửa sổ) chạy trong phiên đăng nhập của người dùng:
* Trẻ chỉ cần mở **Task Manager** (`Ctrl + Shift + Esc`), tìm tiến trình của bạn và nhấn **End Task**.
* Ngay lập tức toàn bộ hệ thống bị vô hiệu hóa, không còn đồng hồ đếm giờ và không còn bộ lọc ứng dụng nào hoạt động.

### 1.2 Giải pháp: Chạy dưới dạng Windows Service (Session 0)
Để ngăn chặn việc này, logic lõi của OpenGuard Kids bắt buộc phải được triển khai dưới dạng một **Windows Service** chính thống:
* **Tài khoản vận hành:** Chạy dưới tài khoản đặc quyền tối cao của hệ điều hành: `NT AUTHORITY\LocalSystem`.
* **Cơ chế tự phục hồi (Service Recovery):** Được đăng ký với **Service Control Manager (SCM)** của Windows. Nếu tiến trình bị cố tình tắt hoặc gặp sự cố bất ngờ, Windows SCM sẽ tự động khởi động lại dịch vụ ngay lập tức.
* **Đặc quyền mở cổng mạng:** Quyền `LocalSystem` cho phép dịch vụ mở và lắng nghe trực tiếp trên cổng mạng đặc quyền **UDP Port 53** (DNS Proxy).

```
 +-------------------------------------------------------------------------+
 | HỆ ĐIỀU HÀNH WINDOWS 10 / 11                                            |
 |                                                                         |
 |  [ SESSION 0: Không có màn hình giao diện (Non-Interactive) ]           |
 |  +-------------------------------------------------------------------+  |
 |  | OGK Service (Quyền NT AUTHORITY\LocalSystem)                      |  |
 |  |  - Giám sát & Chặn tiến trình (psutil + SHA-256)                  |  |
 |  |  - Đếm giờ dùng máy & Chống gian lận (GetLastInputInfo)           |  |
 |  |  - DNS Proxy lọc tên miền (UDP Port 53)                           |  |
 |  +---------------------------------+---------------------------------+  |
 |                                    |                                    |
 |                   Kênh IPC nội bộ  | Loopback HTTP (127.0.0.1)          |
 |                   (Được bảo vệ)    | Bearer Token trong %ProgramData%   |
 |                                    v                                    |
 |  [ SESSION 1: Phiên làm việc của trẻ (Interactive User Session) ]       |
 |  +-------------------------------------------------------------------+  |
 |  | OGK Tray UI (Quyền User thông thường)                             |  |
 |  |  - Biểu tượng thanh tác vụ (Taskbar Tray Icon)                    |  |
 |  |  - Đồng hồ đếm lùi thời gian còn lại                              |  |
 |  |  - Hộp thoại cảnh báo (10 phút, 5 phút, 1 phút)                   |  |
 |  |  - Nút tương tác: "Xin thêm giờ" & "Báo chặn nhầm"                |  |
 |  +-------------------------------------------------------------------+  |
 +-------------------------------------------------------------------------+
```

### 1.3 Rào cản Session 0 Isolation & Sự ra đời của Tray UI
Một câu hỏi lớn đặt ra: **Tại sao Service không tự vẽ giao diện và hiện icon khay luôn cho tiện?**
* **Lịch sử Windows:** Trước Windows Vista (thời Windows XP), một service có thể đánh dấu tùy chọn *"Allow service to interact with desktop"*. Tuy nhiên, điều này mở ra lỗ hổng bảo mật cực kỳ nguy hiểm có tên **Shatter Attack** (ứng dụng độc hại quyền thấp có thể gửi message vào cửa sổ của service để chiếm quyền Administrator).
* **Quy chuẩn Session 0 Isolation:** Từ Windows Vista, Windows 7, 10 đến 11, Microsoft đã **cô lập hoàn toàn Session 0**. Mọi tiến trình chạy trong Session 0 hoàn toàn không có desktop và **không thể hiển thị bất kỳ cửa sổ hay icon khay nào lên màn hình của người dùng**.
* **Giải pháp hai tiến trình:**
  1. Tiến trình thứ nhất: **OGK Service** nằm trong Session 0 làm nhiệm vụ thực thi chính sách (không có giao diện).
  2. Tiến trình thứ hai: **OGK Tray UI** chạy trong Session 1 (phiên desktop của trẻ) làm nhiệm vụ hiển thị giao diện và tương tác.

---

## 2. Kênh Giao Tiếp Nội Bộ IPC (Inter-Process Communication)

Giữa Session 0 và Session 1 cần một cầu nối để trao đổi thông tin (ví dụ: Tray UI hỏi Service xem con còn bao nhiêu phút, hoặc khi con bấm nút *"Xin thêm giờ"* thì gửi lệnh vào Service).

### So sánh Named Pipe và Loopback HTTP
* **Named Pipe:** Cơ chế giao tiếp truyền thống của Windows. Tuy nhiên việc thiết lập phân quyền bảo mật (DACL) giữa Session 0 và các Session người dùng tương đối phức tạp và dễ phát sinh lỗi phân quyền.
* **Loopback HTTP (Lựa chọn tối ưu):**
  * Service mở một web server nội bộ lắng nghe tại `http://127.0.0.1:<port>` sử dụng `asyncio`.
  * **Cơ chế bảo mật bằng Token bí mật:** Để tránh việc một tiến trình độc hại khác của trẻ tự gửi request HTTP giả mạo lệnh, khi Service khởi động, nó tự sinh một chuỗi ngẫu nhiên 32 bytes (Bearer Token) và ghi vào file:
    `%ProgramData%\OpenGuardKids\ipc_secret.token`
  * File này được thiết lập quyền truy cập NTFS bảo mật (chỉ tài khoản `SYSTEM` và `Administrators` mới có quyền đọc/ghi). Khi Tray UI khởi động, nó đọc token này và gắn vào header mỗi khi gửi request:
    `Authorization: Bearer <ipc_secret_token>`

---

## 3. Giám Sát Tiến Trình & Kháng Gian Lận Đổi Tên File

### 3.1 Vấn đề đổi tên file (Rename Bypass Attack)
Trẻ em rất nhanh trí: Nếu hệ thống chỉ chặn danh sách theo tên file `game.exe`, trẻ chỉ cần đổi tên file thực thi thành `calc.exe` hoặc `notepad.exe` là vượt qua mặt các phần mềm kiểm soát thông thường.

### 3.2 Giải pháp kỹ thuật: Quét mã băm nhị phân SHA-256
Sử dụng thư viện `psutil` để quét định kỳ danh sách tiến trình đang hoạt động:
1. Lấy đường dẫn file thực thi từ tiến trình: `proc.exe()`.
2. Kiểm tra tên file với danh sách chặn nhanh: `proc.name().lower()`.
3. Nếu tên file đáng ngờ hoặc nằm trong danh mục ứng dụng cần quét sâu: Tiến hành đọc các khối nhị phân đầu tiên của file và tính toán mã băm **SHA-256**.
4. So sánh mã băm SHA-256 với cơ sở dữ liệu các ứng dụng bị hạn chế.
5. Nếu phát hiện vi phạm: Gửi tín hiệu dừng tiến trình `proc.terminate()` (hoặc `proc.kill()` nếu không phản hồi), đồng thời gửi sự kiện `blocked_app` lên hệ thống kèm lý do chặn rõ ràng theo nguyên tắc **NT4**.

---

## 4. Bộ Đếm Thời Gian Màn Hình & Chống Gian Lận Lùi Giờ

### 4.1 Phân biệt Thời gian hoạt động (Active Time) và Thời gian nhàn rỗi (Idle Time)
Nếu trẻ bật máy tính rồi rời khỏi phòng đi đá bóng 2 tiếng, hệ thống có nên trừ hết thời gian dùng máy của trẻ không?
* Câu trả lời là **KHÔNG**. Trừ giờ như vậy là bất công và vi phạm triết lý đồng hành.
* **Kỹ thuật nhận biết máy nhàn rỗi (Idle Detection):**
  * Sử dụng hàm Win32 API: **`GetLastInputInfo`** thông qua thư viện `pywin32`.
  * Hàm này trả về dấu thời gian của lần cuối cùng người dùng gõ một phím hoặc di chuyển chuột.
  * Lấy `tick_count_hien_tai - tick_count_lan_nhap_cuoi`.
  * Nếu thời gian trôi qua **vượt quá 5 phút (300 giây)**: Hệ thống xác định trẻ đã rời máy, lập tức **tạm dừng bộ đếm thời gian** cho đến khi có thao tác người dùng quay trở lại.

### 4.2 Nhận diện màn hình khóa (Lock Screen Detection)
* Khi trẻ chủ động khóa màn hình (`Windows + L`) hoặc máy tính rơi vào trạng thái ngủ (Sleep):
* Service đăng ký theo dõi thông báo phiên qua hàm **`WTSRegisterSessionNotification`**.
* Khi nhận sự kiện khóa màn hình `WTS_SESSION_LOCK`, bộ đếm giờ tự động đóng băng (freeze).

### 4.3 Phòng chống gian lận lùi đồng hồ hệ thống (Clock Rollback Attack)
Một chiêu trò phổ biến khác: Trẻ vào phần cài đặt *Date & Time* của Windows, tắt chế độ tự động đồng bộ giờ Internet và chỉnh lùi giờ từ 21:00 về 19:00 để được chơi tiếp.

* **Thuật toán Anti-Tamper của OpenGuard Kids:**
  * Bộ đếm thời gian lưu lại mốc thời gian của vòng lặp kiểm tra trước đó (`last_check_timestamp`).
  * Ở mỗi chu kỳ đếm (ví dụ mỗi giây): Lấy thời gian hiện tại `current_timestamp`.
  * So sánh: Nếu `current_timestamp < last_check_timestamp - 60` (tức là đồng hồ hệ thống bị lùi ngược hơn 60 giây):
    1. Lập tức kích hoạt cờ cảnh báo gian lận (`tamper_flag = True`).
    2. Không cộng thêm bất kỳ hạn ngạch thời gian nào.
    3. Đẩy sự kiện cảnh báo `clock_tampering_detected` về máy chủ phụ huynh.

---

## 5. Bảng Tóm Tắt Kỹ Thuật Dành Cho Sinh Viên A (Lead Windows Agent)

| Thành phần | Công nghệ / API sử dụng | Trách nhiệm chính |
| :--- | :--- | :--- |
| **Windows Service** | `pywin32` (`win32serviceutil`), `SCM` | Duy trì quyền `LocalSystem`, tự khởi động lại khi crash, quản lý vòng đời Agent. |
| **Kênh IPC** | `asyncio.start_server`, HTTP 127.0.0.1 | Trao đổi dữ liệu an toàn giữa Session 0 và Session 1 qua Bearer Token bí mật. |
| **Bộ đếm thời gian** | `GetLastInputInfo`, `WTSRegisterSessionNotification` | Đếm chính xác thời gian thực, tạm dừng khi Idle $> 5$ phút hoặc khóa máy. |
| **Chống lùi giờ** | Thuật toán so sánh Delta thời gian đơn điệu | Phát hiện bước nhảy lùi đồng hồ $> 60$ giây, ngăn chặn gian lận giờ. |
| **Giám sát ứng dụng** | `psutil`, `hashlib.sha256` | Quét tiến trình, đối chiếu mã băm SHA-256 chống đổi tên file, tắt app vi phạm. |

