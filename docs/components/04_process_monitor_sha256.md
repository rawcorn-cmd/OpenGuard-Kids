# THÀNH PHẦN 04: GIÁM SÁT TIẾN TRÌNH & BĂM MÃ NHỊ PHÂN SHA-256

> **Mô-đun:** [`src/agent/process_monitor.py`](file:///home/cornar/Projects/OpenGuard-Kids/src/agent/process_monitor.py)  
> **Thư viện:** `psutil`, `hashlib` (SHA-256), `ctypes` (Win32 API)  
> **Đặc tả kiểm thử:** Phát hiện 100% ứng dụng cấm bị đổi tên (Ví dụ: `game.exe` đổi thành `word.exe`)

---

## 1. Nền Tảng Công Cụ & Framework Kỹ Thuật

Process Monitor kết hợp giữa các API liệt kê tiến trình cấp thấp và hàm băm mật mã học tiêu chuẩn:

1. **Thư viện `psutil` (Process and System Utilities):**
   * Sử dụng Windows Toolhelp32 Snapshot API (`CreateToolhelp32Snapshot`, `Process32First`, `Process32Next`) để duyệt qua cây tiến trình mà không làm chậm nhân hệ điều hành.
   * Cung cấp các thông tin: PID, Process Name, Executable Path (`p.exe()`), và CPU/RAM Usage.
2. **Thuật toán Băm Mật mã học SHA-256 (RFC 6234):**
   * Thuật toán băm một chiều sinh chuỗi định danh 256-bit (64 ký tự hex) đại diện duy nhất cho nội dung byte nhị phân của file thực thi.
   * Tính chất kháng xung đột cực cao (Collision Resistance): Việc đổi tên file, di chuyển vị trí thư mục, hoặc thay đổi thuộc tính file hoàn toàn **KHÔNG THAY ĐỔI** mã băm SHA-256 của file.
3. **Cơ Chế Bộ Đệm RAM Thời Điểm Sửa Đổi (Mtime-Based RAM Cache):**
   * Đọc ổ đĩa liên tục sẽ gây nghẽn I/O (Disk Bottleneck) và hao pin laptop.
   * Tối ưu hóa bằng cấu trúc ánh xạ:
     $$\text{Cache}: \text{file\_path} \longrightarrow (\text{last\_mtime}, \text{sha256\_hash})$$
   * Nếu thời gian sửa đổi file `os.path.getmtime(path)` không đổi, hệ thống trả về ngay mã băm từ RAM với độ phức tạp thời gian $O(1)$.

---

## 2. Chức Năng Cốt Lõi

* **Quét Định Kỳ Cây Tiến Trình:** Định kỳ mỗi 5.0 giây quét toàn bộ các ứng dụng đang chạy trong phiên của người dùng.
* **Chống Thủ Thuật Đổi Tên File (Binary Renaming Anti-Bypass):** Ngăn chặn trẻ em vượt tường rào bằng cách đổi tên file game cấm (Ví dụ: đổi `gta5.exe` thành `calculator.exe`, `excel.exe`, hoặc `svchost.exe`).
* **Đóng Tiến Trình An Toàn (Graceful Termination Protocol):** Gửi tín hiệu thông báo cho tiến trình kịp lưu trạng thái trước khi cưỡng chế tắt, không gây lỗi hệ điều hành.

---

## 3. Cơ Chế Vận Hành Chuyên Sâu

### 3.1. Thuật Toán Quét & Băm Tối Ưu Hóa Bộ Nhớ RAM
```python
import os
import hashlib
import psutil
from typing import Dict, Tuple

class ProcessMonitor:
    def __init__(self, blocked_hashes: set):
        self.blocked_hashes = blocked_hashes
        self.hash_cache: Dict[str, Tuple[float, str]] = {}

    def get_file_sha256(self, file_path: str) -> str:
        try:
            current_mtime = os.path.getmtime(file_path)
            # Kiểm tra bộ đệm RAM O(1):
            if file_path in self.hash_cache:
                cached_mtime, cached_hash = self.hash_cache[file_path]
                if cached_mtime == current_mtime:
                    return cached_hash

            # Nếu chưa có trong cache hoặc file bị sửa đổi:
            sha256 = hashlib.sha256()
            with open(file_path, "rb") as f:
                # Đọc từng khối 64KB để không làm tràn RAM
                while chunk := f.read(65536):
                    sha256.update(chunk)
            
            calculated_hash = sha256.hexdigest().lower()
            self.hash_cache[file_path] = (current_mtime, calculated_hash)
            return calculated_hash
        except (PermissionError, FileNotFoundError):
            return ""
```

### 3.2. Quy Trình Hai Bước Đóng Tiến Trình Cấm (Two-Phase Termination)
Khi phát hiện tiến trình thuộc danh sách cấm:
1. **Pha 1: Yêu cầu đóng êm dịu (Graceful `SIGTERM`):**
   * Gửi tín hiệu `WM_CLOSE` hoặc gọi `proc.terminate()`.
   * Chờ tối đa 3.0 giây để ứng dụng tự giải phóng tài nguyên.
2. **Pha 2: Cưỡng chế tiêu diệt (`SIGKILL`):**
   * Nếu sau 3 giây tiến trình vẫn cố tình chạy, gọi `proc.kill()` (Tương đương hàm Win32 API `TerminateProcess(hProcess, 1)`).
3. **Pha 3: Thông báo minh bạch cho trẻ:**
   * Gửi thông báo sang Tray UI để bật Toast giải thích: *"Ứng dụng [Tên] đã bị dừng theo quy định quản lý của gia đình."* (Tuân thủ nguyên tắc NT4: Không ngắt ngầm, phải giải thích rõ ràng).

---

## 4. Cách Liên Kết Với Các Thành Phần Khác

1. **Với Windows Service (Thành phần 1):** Chạy như một worker thread độc lập trong Service để có đặc quyền đọc thông tin các tiến trình khác.
2. **Với Offline Buffer (Thành phần 7):** Tạo bản ghi sự kiện `PROCESS_BLOCKED` gồm: tên file, đường dẫn thực thi, mã băm SHA-256 và thời điểm vi phạm để ghi đệm vào SQLite.
3. **Với FastAPI Server (Thành phần 9):** Nhận danh sách đen mã băm (`blacklist_hashes`) được phụ huynh cập nhật từ Cloud Server đồng bộ về.

