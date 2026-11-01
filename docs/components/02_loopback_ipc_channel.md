# THÀNH PHẦN 02: KÊNH TRUYỀN NỘI BỘ LOOPBACK IPC (PORT 8765)

> **Mô-đun:** [`src/agent/ipc.py`](file:///home/cornar/Projects/OpenGuard-Kids/src/agent/ipc.py)  
> **Giao thức:** HTTP REST trên giao diện Loopback `127.0.0.1:8765`  
> **Cơ chế xác thực:** Mã bí mật `X-Agent-Token` (64 ký tự hex) bảo vệ bởi phân quyền NTFS

---

## 1. Nền Tảng Công Cụ & Framework Kỹ Thuật

Kênh truyền Loopback IPC giải quyết bài toán giao tiếp liên phiên (Cross-Session Communication) giữa **Session 0** (Dịch vụ hệ thống) và **Session 1** (Ứng dụng khay giao diện người dùng):

1. **Giao thức HTTP trên Giao diện Loopback (RFC 1122):**
   * Địa chỉ `127.0.0.1` là giao diện mạng ảo nội bộ của kernel TCP/IP stack. Các gói tin gửi đến `127.0.0.1` được kernel định tuyến trực tiếp trong bộ nhớ hệ điều hành mà không bao giờ đi qua card mạng vật lý (NIC) hay phát ra ngoài mạng LAN.
   * Sử dụng thư viện chuẩn `http.server` và `urllib.request` của Python nhằm đảm bảo tính gọn nhẹ, thời gian khởi động < 50ms, không phụ thuộc thư viện nặng.
2. **Hệ Thống Phân Quyền File NTFS (Windows Security Descriptors):**
   * Windows NT sử dụng Access Control Lists (ACL) để kiểm soát quyền đọc/ghi trên từng file.
   * File chứa mã bí mật (`config.json` hoặc `ipc_token.key`) được bảo vệ bằng quyền:
     * `NT AUTHORITY\LocalSystem`: Full Control.
     * `BUILTIN\Administrators`: Full Control.
     * `<LoggedOnUser_SID>`: Read Only.
     * **Cấm hoàn toàn:** `Everyone` và `Guests`.

---

## 2. Chức Năng Cốt Lõi

* **Bắc cầu truyền thông qua ranh giới Session 0 Isolation:** Cho phép Windows Service truyền lệnh đếm ngược, cảnh báo Toast, và trạng thái hệ thống tới Tray UI.
* **Tiếp nhận hành động của trẻ:** Nhận các tín hiệu tương tác từ khay hệ thống (Ví dụ: trẻ bấm nút *"Xin thêm 15 phút"*, *"Báo chặn nhầm"*, hoặc *"Lưu bài hoàn tất"*) để chuyển giao cho Service xử lý.
* **Cảnh báo mất kết nối dịch vụ (Red Alert Mechanism):** Phát hiện tức thì tình trạng Windows Service bị dừng bất thường hoặc bị can thiệp trái phép.

---

## 3. Cơ Chế Vận Hành Chuyên Sâu

### 3.1. Quy Trình Khởi Tạo & Bắt Tay Token Xác Thực (Handshake Flow)
1. **Windows Service khởi động:**
   * Sinh một chuỗi ngẫu nhiên cryptographically secure bằng `secrets.token_hex(32)` (chuỗi 64 ký tự hex).
   * Lưu token vào biến nhớ của `IPCServer` và ghi xuống file `%ProgramData%\OpenGuardKids\ipc.token`.
   * Gán quyền NTFS nghiêm ngặt cho file này.
2. **Tray UI khởi động:**
   * Khi khởi chạy trong phiên của trẻ, Tray UI đọc file `ipc.token`.
   * Trong mọi yêu cầu HTTP tiếp theo gửi sang Service, Tray UI bắt buộc phải đính kèm Header:
     ```http
     X-Agent-Token: 3a7f8b9c...e4d1
     ```
3. **Kiểm tra Xác thực tại IPC Server:**
   * Nếu Header thiếu hoặc giá trị token sai: Server phản hồi ngay mã `403 Forbidden` kèm payload `{"error": "Unauthorized IPC Client"}`.
   * Ngăn chặn hoàn toàn việc các tiến trình độc hại khác của các phần mềm bên thứ ba gửi lệnh giả mạo làm sai lệch giờ sử dụng.

### 3.2. Bảng Danh Mục API Loopback IPC (`127.0.0.1:8765`)

| Phương thức | Đường dẫn | Tham số Payload | Mô tả Chức năng | Phản hồi Chuẩn |
| :--- | :--- | :--- | :--- | :--- |
| `GET` | `/status` | Không | Tray UI thăm dò trạng thái hệ thống mỗi 1.0 giây | `{"state": "ACTIVE", "remaining_seconds": 2400, "daily_quota": 7200}` |
| `POST` | `/request-time` | `{"extra_minutes": 15, "reason": "Làm bài tập"}` | Trẻ bấm nút xin thêm giờ từ menu khay | `{"status": "QUEUED", "request_id": "uuid-..."}` |
| `POST` | `/report-unblock` | `{"domain": "scratch.mit.edu", "reason": "Học tập"}` | Trẻ báo cáo một trang web học tập bị chặn nhầm | `{"status": "SUBMITTED"}` |
| `POST` | `/command` | `{"action": "LOCK"}` hoặc `{"action": "UNLOCK"}` | Lệnh từ Server chuyển tiếp xuống Tray UI | `{"status": "ACK"}` |

### 3.3. Thuật Toán Báo Động Đỏ Mất Nhịp Tim (Red Alert Heartbeat)
Tray UI duy trì một luồng ngầm `HeartbeatWorker`:
```python
import time
import urllib.request
import json

class StateListener:
    def __init__(self, token: str):
        self.token = token
        self.consecutive_failures = 0
        self.alert_threshold = 15  # 15 lần lỗi liên tục (15 giây)

    def poll_service(self):
        try:
            req = urllib.request.Request("http://127.0.0.1:8765/status")
            req.add_header("X-Agent-Token", self.token)
            with urllib.request.urlopen(req, timeout=1.5) as resp:
                data = json.loads(resp.read().decode())
                self.consecutive_failures = 0
                return data
        except Exception:
            self.consecutive_failures += 1
            if self.consecutive_failures >= self.alert_threshold:
                # KÍCH HOẠT BÁO ĐỘNG ĐỎ:
                self.trigger_red_alert_ui()
```
Khi kích hoạt báo động đỏ:
* Biểu tượng Taskbar chuyển sang màu đỏ nhấp nháy.
* Hiển thị thông báo Toast khẩn cấp: *"Dịch vụ bảo vệ OpenGuard Kids đang mất kết nối! Hệ thống đang tự phục hồi..."*.

---

## 4. Cách Liên Kết Với Các Thành Phần Khác

1. **Với Windows Service (Thành phần 1):** Tiếp nhận dữ liệu thời gian thực từ `ScreenTimeTracker` và danh sách vi phạm từ `ProcessMonitor` để gửi sang Session 1.
2. **Với Tray UI (Thành phần 8):** Cung cấp API trực tiếp cho Tray UI hiển thị menu, cập nhật tooltip đếm lùi, và kích hoạt hộp thoại ân hạn 60s.

