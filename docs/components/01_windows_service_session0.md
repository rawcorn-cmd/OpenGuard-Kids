# THÀNH PHẦN 01: DỊCH VỤ NỀN WINDOWS SERVICE (SESSION 0)

> **Mô-đun:** `src/agent/` &bull; Thư viện: `pywin32` (`win32serviceutil`, `win32service`, `win32event`)  
> **Đặc quyền thực thi:** `NT AUTHORITY\LocalSystem` &bull; **Môi trường chạy:** Windows Session 0 (Non-interactive)

---

## 1. Nền Tảng Công Cụ & Framework Kỹ Thuật

Thành phần Windows Service của OpenGuard Kids được xây dựng trên các nền tảng hệ thống cấp thấp của Windows NT:

1. **Windows Service Control Manager (SCM):**
   * SCM là một tiến trình hệ thống đặc quyền (`services.exe`) chịu trách nhiệm nạp, khởi động, giám sát, dừng và cấu hình chính sách phục hồi cho các dịch vụ nền của Windows.
   * Dịch vụ tương tác với SCM qua giao thức chuẩn RPC (Remote Procedure Call) và Windows Service API.
2. **Thư viện `pywin32` (`win32serviceutil`, `win32service`):**
   * Là thư viện cầu nối (wrapper) C-Python cung cấp quyền truy cập trực tiếp vào Win32 API.
   * Lớp cơ sở kế thừa `win32serviceutil.ServiceFramework` cung cấp hai phương thức bắt buộc:
     * `SvcDoRun()`: Vòng lặp luồng chính (Main Service Thread).
     * `SvcStop()`: Tiếp nhận tín hiệu `SERVICE_CONTROL_STOP` từ SCM.
3. **Mô hình Cách ly Session 0 (Session 0 Isolation Architecture):**
   * Được Microsoft áp dụng từ Windows Vista nhằm triệt tiêu hoàn toàn kỹ thuật tấn công **Shatter Attack** (kẻ tấn công gửi thông điệp cửa sổ `WM_COMMAND` chứa mã độc từ phiên người dùng bình thường tới các tiến trình dịch vụ đặc quyền hệ thống).
   * Tại Session 0, không có bất kỳ Desktop subsystem đồ họa hay tiến trình hiển thị (Windows Explorer / Taskbar) nào được phép chạy. Điều này bảo vệ an toàn tuyệt đối cho các tiến trình lõi.

---

## 2. Chức Năng Cốt Lõi

* **Trọng tài Giám sát Tối cao:** Đóng vai trò hạt nhân của toàn bộ hệ thống OpenGuard Kids trên máy tính của trẻ.
* **Quản trị Vòng đời Các Tiến Trình Con:** Khởi tạo, theo dõi và phục hồi các thành phần: DNS Proxy UDP 53, Process Monitor, Screen-Time Tracker, Loopback IPC Server và Offline Buffer.
* **Chống Ép Tắt Ứng Dụng (Anti-Kill Mechanism):** Ngăn chặn người dùng trẻ em tìm cách tắt phần mềm qua Task Manager, dòng lệnh `taskkill` hay các công cụ can thiệp tiến trình bên thứ ba.

---

## 3. Cơ Chế Vận Hành Chuyên Sâu

### 3.1. Cơ chế Chống Tắt Ứng Dụng (Anti-Kill via DACL & LocalSystem)
* Khi trẻ đăng nhập vào Windows với quyền **Standard User** (không có đặc quyền Administrator), trẻ sở hữu Token người dùng có SID thông thường (ví dụ: `S-1-5-21-...-1001`).
* Windows Service chạy dưới danh nghĩa tiến trình hệ thống `NT AUTHORITY\LocalSystem` (SID: `S-1-5-18`).
* Bảng điều khiển truy cập tùy ý (Discretionary Access Control List - DACL) gắn trên Process Handle của dịch vụ chỉ cấp cờ `PROCESS_TERMINATE (0x0001)` và `PROCESS_SUSPEND_RESUME (0x0800)` cho `LocalSystem` và `Administrators`.
* Khi trẻ mở Task Manager hoặc gõ lệnh:
  ```cmd
  taskkill /F /PID <service_pid>
  ```
  Nhân Windows Security Subsystem (LSASS & Kernel) sẽ chặn đứng lệnh và trả về mã lỗi:
  ```
  ERROR_ACCESS_DENIED (Code 5: Access is denied)
  ```

### 3.2. Cơ chế Tự Động Phục Hồi qua SCM (Auto-Recovery Policy)
Dịch vụ được đăng ký với SCM với cấu hình hành động phục hồi sự cố (`SC_ACTION_RESTART`):
* **Lần gặp sự cố 1 (First Failure):** Khởi động lại dịch vụ sau 60 giây.
* **Lần gặp sự cố 2 (Second Failure):** Khởi động lại dịch vụ sau 60 giây.
* **Lần gặp sự cố kế tiếp (Subsequent Failures):** Tiếp tục khởi động lại dịch vụ sau 60 giây.
* Chu kỳ đếm lại thời gian reset lỗi: 86400 giây (24 giờ).

### 3.3. Vòng Lặp Vận Hành (Main Service Loop)
```python
import win32serviceutil
import win32service
import win32event

class OpenGuardService(win32serviceutil.ServiceFramework):
    _svc_name_ = "OpenGuardKidsService"
    _svc_display_name_ = "OpenGuard Kids Parental Protection Service"
    _svc_description_ = "Dịch vụ giám sát thời gian và nội dung máy tính trẻ em"

    def __init__(self, args):
        super().__init__(args)
        self.stop_event = win32event.CreateEvent(None, 0, 0, None)
        self.is_running = True

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.stop_event)
        self.is_running = False

    def SvcDoRun(self):
        # Khởi chạy các worker luồng con:
        # 1. Start DNS Proxy UDP 53
        # 2. Start ScreenTime Tracker & Process Monitor
        # 3. Start Loopback IPC Server (127.0.0.1:8765)
        # 4. Connect WebSocket Hub to Backend Server
        while self.is_running:
            # Chờ tín hiệu dừng từ SCM với timeout 1000ms
            rc = win32event.WaitForSingleObject(self.stop_event, 1000)
            if rc == win32event.WAIT_OBJECT_0:
                break
```

---

## 4. Cách Liên Kết Với Các Thành Phần Khác

1. **Với Tray UI (Session 1):** Khởi chạy tiến trình `OpenGuardTray.exe` vào Session 1 của trẻ bằng Windows API `CreateProcessAsUser` (thông qua nạp Token người dùng từ hàm `WTSQueryUserToken`).
2. **Với Loopback IPC Server (Thành phần 2):** Khởi tạo máy chủ HTTP nội bộ để tiếp nhận lệnh và truyền trạng thái qua lại với Tray UI.
3. **Với SQLite Offline Buffer (Thành phần 7):** Quản lý kết nối ghi đệm và điều phối luồng đồng bộ dữ liệu sự kiện lên Cloud Server.

