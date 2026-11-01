# THÀNH PHẦN 15: BỘ KIỂM THỬ TỰ ĐỘNG & NGHIỆM THU KỊCH BẢN DEMO D1

> **Mô-đun:** [`scripts/e2e_acceptance_verification.py`](file:///home/cornar/Projects/OpenGuard-Kids/scripts/e2e_acceptance_verification.py) & toàn bộ thư mục [`tests/`](file:///home/cornar/Projects/OpenGuard-Kids/tests/)  
> **Framework:** `pytest`, `pytest-asyncio`, `httpx`  
> **Kết quả nghiệm thu:** **51/51 Tests PASSED (100%)** trong thời gian **11.75 giây**

---

## 1. Nền Tảng Công Cụ & Framework Kỹ Thuật

Bộ kiểm thử tự động của OpenGuard Kids được thiết kế theo mô hình Kim tự tháp kiểm thử (Test Pyramid) với các tiêu chuẩn kiểm thử phần mềm chuyên nghiệp:

1. **Framework Kiểm Thử Pytest:**
   * Sử dụng các Fixture tái sử dụng của `pytest` để tự động khởi tạo và dọn dẹp cơ sở dữ liệu tạm thời (In-memory SQLite) sau mỗi ca kiểm thử.
   * Chạy kiểm thử bất đồng bộ với `anyio` và `pytest-asyncio`.
2. **Thư Viện Mô Phỏng Mạng `httpx.AsyncClient` & `fastapi.testclient.TestClient`:**
   * Kiểm thử toàn bộ các Endpoint REST API và WebSocket mà không cần phải thực sự mở port ra môi trường bên ngoài.
3. **Kịch Bản Mô Phỏng E2E Độc Lập (`e2e_acceptance_verification.py`):**
   * Tái hiện sống động các kịch bản sử dụng thực tế: lùi giờ hệ thống, đổi tên file nhị phân, mất mạng Internet, đo đạc độ trễ WebSocket.

---

## 2. Chức Năng Cốt Lõi

* **Đảm Bảo Chất Lượng Không Lỗi (Zero-Regression):** Ngăn chặn việc sửa lỗi ở thành phần này làm hỏng tính năng ở thành phần khác.
* **Chứng Minh Năng Lực Bảo Vệ Thực Tế:** Đưa ra các con số thực nghiệm khách quan để nhóm sinh viên tự tin bảo vệ đồ án trước Hội đồng chấm điểm.
* **Tự Động Hóa Kịch Bản Trình Diễn Live Demo D1:** Giúp việc demo trước ban giám khảo diễn ra trơn tru chỉ với 1 lệnh chạy duy nhất.

---

## 3. Cơ Chế Vận Hành Chuyên Sâu

### 3.1. Bảng Tổng Hợp Ma Trận 51 Bài Kiểm Thử Tự Động

| File Kiểm Thử | Số Lượng Ca | Nội Dung Kiểm Thử Chi Tiết | Kết Quả |
| :--- | :---: | :--- | :---: |
| [`test_screen_time.py`](file:///home/cornar/Projects/OpenGuard-Kids/tests/test_screen_time.py) | **7 tests** | Phân biệt Active/Idle, Hạn ngạch ngày, Lịch tuần 7x48, Bẫy lùi đồng hồ `delta_wall < -60s`, Sai số $\le \pm 30$s/h. | **7/7 PASSED** |
| [`test_process_monitor.py`](file:///home/cornar/Projects/OpenGuard-Kids/tests/test_process_monitor.py) | **5 tests** | Quét tiến trình 5s, **Băm SHA-256 phát hiện game đổi tên**, Bộ đệm RAM $O(1)$, Đóng tiến trình an toàn 2 pha. | **5/5 PASSED** |
| [`test_dns_proxy.py`](file:///home/cornar/Projects/OpenGuard-Kids/tests/test_dns_proxy.py) | **8 tests** | Phân giải UDP 53, **Bẻ hướng CNAME SafeSearch**, Chặn Wildcard `*.xxx`, **Khắc chế DoH Canary**, Whitelist 111. | **8/8 PASSED** |
| [`test_blockpage.py`](file:///home/cornar/Projects/OpenGuard-Kids/tests/test_blockpage.py) | **3 tests** | Micro-server HTTP cổng 8080, Trang web giáo dục thân thiện, Nút bấm "Báo chặn nhầm" của trẻ. | **3/3 PASSED** |
| [`test_offline_buffer.py`](file:///home/cornar/Projects/OpenGuard-Kids/tests/test_offline_buffer.py) | **3 tests** | SQLite WAL, **Loại trùng lặp Idempotency Key**, Thử lại Exponential Backoff kèm Jitter khi mất mạng. | **3/3 PASSED** |
| [`test_ipc.py`](file:///home/cornar/Projects/OpenGuard-Kids/tests/test_ipc.py) | **3 tests** | Loopback 127.0.0.1:8765, Xác thực mã bí mật `X-Agent-Token`, Chống truy cập trái phép 403 Forbidden. | **3/3 PASSED** |
| [`test_server_auth.py`](file:///home/cornar/Projects/OpenGuard-Kids/tests/test_server_auth.py) | **4 tests** | Đăng ký/Đăng nhập phụ huynh, **Mã hóa băm mật khẩu Argon2id (RFC 9106)**, Session Cookie bảo mật HttpOnly. | **4/4 PASSED** |
| [`test_database_and_security.py`](file:///home/cornar/Projects/OpenGuard-Kids/tests/test_database_and_security.py) | **5 tests** | Tạo tài khoản, **Sinh mã PIN 8 ký tự ghép đôi (TTL 10m)**, Cấp phát Device ID/Token, **Phòng chống IDOR**. | **5/5 PASSED** |
| [`test_sync_and_events.py`](file:///home/cornar/Projects/OpenGuard-Kids/tests/test_sync_and_events.py) | **3 tests** | Đồng bộ Batch HTTPS, **Kênh WebSocket lệnh khẩn cấp (Đo trễ 1.37 ms < 5s)**, Hàng đợi nhịp tim dự phòng. | **3/3 PASSED** |
| [`test_tray_app.py`](file:///home/cornar/Projects/OpenGuard-Kids/tests/test_tray_app.py) | **5 tests** | Lắng nghe StateListener 1.0s, **Chuỗi Toast 10m/5m/1m, Báo động đỏ mất service > 15s, DEMO D1**. | **5/5 PASSED** |
| [`test_dashboard_and_privacy.py`](file:///home/cornar/Projects/OpenGuard-Kids/tests/test_dashboard_and_privacy.py) | **5 tests** | Thống kê Dashboard, Hòm thư duyệt con, **Xóa Kép Atomic Dual Deletion**, Tự động dọn dẹp sau 90 ngày. | **5/5 PASSED** |
| **TỔNG CỘNG** | **51 tests** | **Toàn bộ 100% chức năng cốt lõi và tiêu chuẩn an toàn của đồ án** | **100% PASSED** |

### 3.2. Sáu Kịch Bản Trình Diễn Live Demo Nghiệm Thu
File [`scripts/e2e_acceptance_verification.py`](file:///home/cornar/Projects/OpenGuard-Kids/scripts/e2e_acceptance_verification.py) thực thi tự động 6 kịch bản chấp nhận E2E:
1. **Scenario 1:** Đổi tên file nhị phân `game_banned.exe` &rarr; `winword.exe` &rarr; Process Monitor phát hiện mã SHA-256 khớp 100% với Blacklist &rarr; Đóng thành công!
2. **Scenario 2:** Lùi giờ đồng hồ hệ thống 120 phút &rarr; Monotonic clock giữ nguyên mốc &rarr; `tamper_detected = True` &rarr; Consumed quota không bị lùi!
3. **Scenario 3 (Demo D1):** Mô phỏng chuỗi Toast cảnh báo khi còn 10 phút, 5 phút, 1 phút & Kích hoạt hộp thoại ân hạn 60 giây không làm mất bài tập.
4. **Scenario 4:** Truy vấn DNS `google.com` &rarr; Bẻ hướng CNAME `forcesafesearch.google.com` & Truy vấn `use-application-dns.net` &rarr; Trả về `NXDOMAIN` chặn DoH.
5. **Scenario 5:** Đo đạc độ trễ gửi lệnh qua WebSocket Hub &rarr; Kết quả thực tế: **1.37 ms** (Vượt xa mốc 5.000 ms).
6. **Scenario 6:** Nhấn nút "Xóa toàn bộ dữ liệu của con" &rarr; DB Server xóa sạch bản ghi đồng thời kích hoạt WebSocket xả rỗng SQLite cục bộ trên máy con.

---

## 4. Cách Liên Kết Với Các Thành Phần Khác

Bộ kiểm thử bao trùm và kiểm tra tính tương thích chéo của toàn bộ 14 thành phần còn lại trong hệ thống, là bằng chứng kỹ thuật cao nhất khẳng định sự hoàn thiện của đề tài OpenGuard Kids.

