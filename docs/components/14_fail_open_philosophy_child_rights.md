# THÀNH PHẦN 14: BIỆN LUẬN TRIẾT LÝ FAIL-OPEN SAU 7 NGÀY & DANH MỤC CẤM THU THẬP

> **Tài liệu tham chiếu:** [`docs/REQUIREMENTS.md`](file:///home/cornar/Projects/OpenGuard-Kids/docs/REQUIREMENTS.md) & [`docs/DEFENSE_GUIDE.md`](file:///home/cornar/Projects/OpenGuard-Kids/docs/DEFENSE_GUIDE.md)  
> **Nguyên tắc nhân văn:** NT1 (Không bất ngờ), NT2 (Tối thiểu dữ liệu), NT6 (Khả năng phục hồi)  
> **Căn cứ pháp lý:** Luật Trẻ Em 2016 & Nghị định 13/2023/NĐ-CP về Bảo vệ Dữ liệu Cá nhân

---

## 1. Nền Tảng Công Cụ & Framework Kỹ Thuật

Thành phần này đại diện cho triết lý thiết kế và đạo đức kỹ thuật phần mềm (Software Engineering Ethics) của OpenGuard Kids:

1. **Khái Niệm An Toàn Mạng: Fail-Open vs Fail-Closed:**
   * Trong an ninh mạng công ty/doanh nghiệp: Khi tường lửa bị lỗi hoặc đứt cáp, hệ thống chọn chế độ `Fail-Closed` (Khóa cứng toàn bộ để kẻ trộm không xâm nhập được).
   * Trong ứng dụng giáo dục gia đình: Nếu phần mềm chọn `Fail-Closed`, khi gia đình mất mạng vài ngày hoặc máy chủ nhà phát triển sập, máy tính của trẻ sẽ bị khóa cứng &rarr; Trẻ không thể làm bài tập về nhà, không thể xem sách giáo khoa điện tử hay tra cứu thông tin khẩn cấp &rarr; **Phản tác dụng giáo dục**.
   * OpenGuard Kids áp dụng triết lý **Fail-Open có kiểm soát sau 7 ngày**: Ưu tiên tính liên tục của việc học tập của trẻ hơn việc kiểm soát cứng nhắc.
2. **Kỹ Thuật Giảm Thiểu Dữ Liệu Tối Đa (Data Minimization by Design):**
   * Chỉ thu thập 4 trường siêu dữ liệu (Metadata) cấp cao, hoàn toàn không chạm vào nội dung dữ liệu bên trong của người dùng.

---

## 2. Chức Năng Cốt Lõi

* **Triết Lý Fail-Open Sau 7 Ngày Mất Mạng:** Sau 7 ngày (604.800 giây) liên tục không thể kết nối tới Server quản trị, hệ thống tự động gỡ bỏ các rào cản hạn ngạch, cho phép trẻ dùng máy tính bình thường để không làm gián đoạn học tập.
* **Danh Mục 4 Nhóm Dữ Liệu Tuyệt Đối Cấm Thu Thập:** Tuyên bố và chứng minh bằng cấu trúc mã nguồn rằng phần mềm không chứa bất kỳ tính năng gián điệp (Spyware) nào.
* **Màn Hình Minh Bạch 1:1:** Cho phép trẻ em giám sát ngược lại những dữ liệu mà cha mẹ mình đang nhìn thấy.

---

## 3. Cơ Chế Vận Hành Chuyên Sâu

### 3.1. Thuật Toán Chuyển Trạng Thái Fail-Open Sau 7 Ngày
Trong vòng lặp kiểm tra của Windows Service:
```python
import time

class FailOpenPolicy:
    MAX_OFFLINE_SECONDS = 7 * 24 * 3600  # 7 ngày = 604,800 giây

    def __init__(self):
        self.last_successful_sync_mono = time.monotonic()
        self.fail_open_active = False

    def check_resilience_status(self) -> bool:
        offline_duration = time.monotonic() - self.last_successful_sync_mono
        
        # Nếu đã mất kết nối với Server quá 7 ngày:
        if offline_duration > self.MAX_OFFLINE_SECONDS:
            if not self.fail_open_active:
                self.fail_open_active = True
                # TỰ ĐỘNG MỞ QUYỀN AN TOÀN:
                # 1. Bỏ qua hạn ngạch khóa màn hình (Disable Quota Locking)
                # 2. Vẫn duy trì bộ lọc web xấu (Keep Local DNS Blacklist)
                # 3. Gửi thông báo cho trẻ: "Hệ thống đang mở quyền hỗ trợ học tập sau 7 ngày ngoại tuyến"
            return True
            
        return False
```

### 3.2. Bảng Đối Chiếu Danh Mục Cấm Thu Thập Dữ Liệu

| Hành Vi Thu Thập Thường Gặp Ở Phần Mềm Gián Điệp | Quan Điểm Thiết Kế Của OpenGuard Kids | Minh Chứng Kỹ Thuật Trong Mã Nguồn |
| :--- | :--- | :--- |
| **Ghi phím bấm (Keylogger)** | **TUYỆT ĐỐI CẤM** &bull; Vi phạm nghiêm trọng quyền riêng tư và làm lộ mật khẩu của trẻ | Tuyệt đối không sử dụng hàm `SetWindowsHookEx(WH_KEYBOARD)`. Chỉ dùng `GetLastInputInfo` để lấy tick đếm giờ. |
| **Chụp trộm màn hình (Screen Capture)** | **TUYỆT ĐỐI CẤM** &bull; Trẻ có quyền riêng tư khi vẽ tranh, làm bài tập hay trò chuyện với bạn bè | Mã nguồn không import thư viện `pyautogui`, `PIL.ImageGrab` hay hàm Win32 `BitBlt` từ Desktop DC. |
| **Bật micro / quay lén Webcam** | **TUYỆT ĐỐI CẤM** &bull; Vi phạm nghiêm trọng Điều 4 Nghị định 13/2023/NĐ-CP | Không sử dụng thư viện `cv2` (OpenCV) hay DirectShow / Media Foundation API. |
| **Đọc URL chi tiết & Lịch sử duyệt web** | **TUYỆT ĐỐI CẤM** &bull; Chỉ giám sát tên miền ở tầng DNS | Không can thiệp vào file SQLite của trình duyệt (`History.db`). Không phân tích sâu URL query hay nội dung chat. |

---

## 4. Cách Liên Kết Với Các Thành Phần Khác

1. **Với ScreenTime Tracker (Thành phần 3):** Ra lệnh tạm dừng tính năng khóa màn hình cưỡng chế khi cờ `fail_open_active == True`.
2. **Với Tray UI (Thành phần 8):** Hiển thị nhãn minh bạch "Đang hoạt động ở chế độ Fail-Open ngoại tuyến" cho trẻ yên tâm học tập.
3. **Với Parent Web Dashboard (Thành phần 12):** Thông báo cho cha mẹ khi máy tính kết nối lại sau thời gian dài mất mạng.

