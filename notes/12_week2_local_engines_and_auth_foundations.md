# OpenGuard Kids — Tuần 2: Động Cơ Thời Gian, Trang Chặn Giáo Dục & API Xác Thực

> **Khóa học:** Mạng máy tính (*Computer Networks*) — Khoa Công nghệ Thông tin, Trường ĐH Khoa học Tự nhiên (HCMUS)  
> **Mã yêu cầu đồ án:** F1.1 – F1.5 (Bộ đếm giờ, chống gian lận), F2.2, F2.5 (Trang chặn thân thiện), F4.1, F5 (API & Bảo mật)  
> **Trạng thái kiểm thử:** **14/14 unit tests PASSED (100%)** (Lũy kế: 30/30 passed)

---

## 1. MỤC TIÊU VÀ ĐẶT VẤN ĐỀ TUẦN 2

Tuần 2 tập trung vào việc biến các khung sườn kỹ thuật ở Tuần 1 thành **các động cơ nghiệp vụ chạy thực tế trên máy tính**:

1. **Bộ đếm thời gian thông minh (Screen-Time Engine):** Phải phân biệt chính xác khi nào trẻ đang dùng máy và khi nào trẻ đi vắng (treo máy) để không trừ giờ oan; đồng thời phải chống được các chiêu trò gian lận chỉnh giờ hệ thống.
2. **Trang chặn mang tính giáo dục (Polite Blockpage):** Khi trẻ truy cập trang web cấm, không được hiển thị màn hình lỗi mạng khô khan gây ức chế, mà phải giải thích lý do, đưa số Tổng đài 111 và cho phép trẻ gửi yêu cầu phản hồi mở trang web.
3. **API Xác thực & Ghép đôi an toàn:** Cho phép phụ huynh đăng ký tài khoản, đăng nhập qua cookie an toàn, và ghép đôi thiết bị của con thông qua mã PIN 8 ký tự có thời hạn sống (TTL).

---

## 2. KIẾN TRÚC HỆ THỐNG TUẦN 2

```
+-----------------------------------------------------------------------------------+
|                        MÁY TÍNH CỦA TRẺ (WINDOWS 10/11 x64)                       |
|                                                                                   |
|  [ĐỘNG CƠ ĐẾM GIỜ MÀN HÌNH - src/agent/screen_time.py]                            |
|   +----------------------------------------------------------------------------+  |
|   | 10-State Finite State Machine (FSM):                                       |  |
|   | ACTIVE_COUNTING <---> IDLE_PAUSED (user32.GetLastInputInfo > 300s)         |  |
|   |         |                                                                  |  |
|   |         v                                                                  |  |
|   | WARNING_10M -> WARNING_5M -> WARNING_1M -> GRACE_PERIOD_60S -> LOCKED_QUOTA|  |
|   |                                                                            |  |
|   | Bẫy lùi đồng hồ: So sánh time.time() & time.monotonic() (Delta < -60s)    |  |
|   | Sai số thực nghiệm: Delta <= +-30s / giờ hoạt động                        |  |
|   +----------------------------------------------------------------------------+  |
|                                                                                   |
|  [MÁY CHỦ HTTP BLOCKPAGE GIÁO DỤC - src/agent/blockpage.py]                       |
|   +----------------------------------------------------------------------------+  |
|   | Cổng HTTP 127.0.0.1:8080                                                   |  |
|   | - Nhận request khi DNS chuyển hướng trang cấm                              |  |
|   | - Hiển thị lý do: "Trang web thuộc danh mục hạn chế theo thỏa thuận"       |  |
|   | - Số điện thoại cứu trợ trẻ em: Tổng đài 111                              |  |
|   | - Form gửi phản hồi: "Báo chặn nhầm / Xin mở trang web này"                |  |
|   +----------------------------------------------------------------------------+  |
+-----------------------------------------------------------------------------------+
                                       |
                   HTTPS API Calls     | Cookie: session_token (HttpOnly, SameSite)
                                       v
+-----------------------------------------------------------------------------------+
|                        MÁY CHỦ QUẢN TRỊ (FASTAPI BACKEND)                         |
|                                                                                   |
|  [HỆ THỐNG XÁC THỰC & GHÉP ĐÔI - src/server/app.py, auth.py, schemas.py]          |
|   - POST /api/v1/auth/register : Kiểm tra độ phức tạp mật khẩu                 |  |
|   - POST /api/v1/auth/login    : Khóa 15p sau 5 lần sai, cấp Cookie phiên      |  |
|   - POST /api/v1/devices/enroll: Ghép đôi bằng PIN 8 ký tự (TTL 10 phút)       |  |
|   - Ngăn chặn IDOR: Ép Child.parent_id == current_parent.id trong mọi query    |  |
+-----------------------------------------------------------------------------------+
```

---

## 3. CHI TIẾT CÀI ĐẶT CÁC THÀNH PHẦN MÃ NGUỒN

### 3.1. Động cơ tính giờ & Máy trạng thái 10 bước (`src/agent/screen_time.py`)
* **Vị trí tệp:** `src/agent/screen_time.py`
* **Mã yêu cầu:** F1.1, F1.2, F1.3, F1.4, F1.5
* **Chi tiết kỹ thuật:**
  1. **Máy trạng thái hữu hạn (10-State FSM):**
     Hệ thống quản lý trạng thái phiên dùng máy qua các trạng thái chuẩn:
     - `ACTIVE_COUNTING`: Đang sử dụng và tính giờ bình thường.
     - `IDLE_PAUSED`: Trẻ không thao tác chuột/phím $> 5$ phút ($300$ giây), tạm dừng trừ giờ.
     - `WARNING_10M`, `WARNING_5M`, `WARNING_1M`: Các mốc cảnh báo thời gian sắp hết.
     - `GRACE_PERIOD_60S`: 60 giây ân hạn cho phép trẻ lưu bài học trước khi khóa máy.
     - `LOCKED_QUOTA`: Hết hạn ngạch thời gian trong ngày.
     - `LOCKED_SCHEDULE`: Nằm trong khung giờ giới nghiêm (ví dụ 22:00 – 06:00).
     - `LOCKED_URGENT`: Bị khóa khẩn cấp bởi phụ huynh từ xa.
     - `UNLOCKED_OVERRIDE`: Được mở khóa tạm thời / cộng thêm giờ.
  2. **Phát hiện nhàn rỗi (Idle Detection):**
     - Gọi hàm Windows API `user32.GetLastInputInfo()` để lấy thời điểm thao tác cuối cùng của người dùng.
     - Nếu `idle_duration >= 300` giây $\rightarrow$ Tự động chuyển sang `IDLE_PAUSED`, đồng hồ dừng đếm.
     - Ngay khi có cử động chuột hoặc bấm phím, trạng thái tự động khôi phục về `ACTIVE_COUNTING`.
  3. **Cơ chế chống lùi đồng hồ hệ thống (Clock Rollback Detection):**
     - Đứa trẻ có thể vào Windows Settings để chỉnh lùi đồng hồ từ 20:00 về 18:00 nhằm "hack" thêm giờ.
     - Giải pháp kỹ thuật: Hệ thống duy trì song song hai nguồn thời gian:
       + Thời gian đồng hồ thực tế: `time.time()`
       + Đồng hồ phần cứng đơn điệu: `time.monotonic()` (tương đương `GetTickCount64` trên Windows, đếm liên tục từ lúc bật máy và không thể bị chỉnh sửa bởi bất kỳ phần mềm nào).
     - Trong mỗi chu kỳ đếm, nếu phát hiện `delta_time = current_wall_clock - last_wall_clock < -60` giây:
       + Phát hiện hành vi gian lận chỉnh giờ.
       + **Tuyệt đối không giảm số phút đã sử dụng**.
       + Kích hoạt cờ cảnh báo `clock_tamper_detected` và ghi nhật ký kiểm toán.
  4. **Đo đạc độ chính xác (Hourly Accuracy Benchmark):**
     - Kiểm nghiệm thực tế chạy trong 1 giờ ($3600$ giây): sai số thời gian ghi nhận tích lũy nằm trong khoảng $\le \pm 30$ giây (đạt chuẩn F1.3).

### 3.2. Máy chủ HTTP Blockpage cổng 8080 (`src/agent/blockpage.py`)
* **Vị trí tệp:** `src/agent/blockpage.py`
* **Mã yêu cầu:** F2.2, F2.5, NT3, NT4
* **Chi tiết kỹ thuật:**
  1. **Khởi tạo máy chủ HTTP Loopback:**
     - Chạy trên cổng nội bộ `127.0.0.1:8080`.
     - Nhận các yêu cầu HTTP khi DNS Proxy phân giải các tên miền cấm về `127.0.0.1`.
  2. **Giao diện trang chặn thân thiện:**
     - Sử dụng HTML5/CSS hiện đại, ngôn từ lịch sự, mang tính giải thích lý do thay vì trừng phạt.
     - Hiển thị rõ: *"Trang web này nằm trong danh mục hạn chế theo thỏa thuận sử dụng máy tính của gia đình."*
     - Công khai số điện thoại **Tổng đài Quốc gia Bảo vệ Trẻ em: 111** để hỗ trợ khi trẻ gặp nguy cơ trên không gian mạng.
  3. **Hộp thoại phản hồi và xin mở trang (Child Agency):**
     - Cung cấp form nhập liệu: Lý do cần truy cập (học tập, làm bài tập nhóm...).
     - Khi trẻ bấm gửi, dữ liệu được ghi nhận vào hàng đợi để chuyển tiếp lên Server cho phụ huynh duyệt.

### 3.3. API Xác thực Phụ huynh & Ghép đôi Thiết bị
* **Vị trí tệp:** `src/server/app.py`, `src/server/auth.py`, `src/server/schemas.py`
* **Mã yêu cầu:** F4.1, F5
* **Chi tiết kỹ thuật:**
  1. **Quản lý phiên với Cookie an toàn:**
     - Sử dụng cookie `session_token` với cờ bảo mật:
       + `HttpOnly`: Ngăn chặn JavaScript đọc cookie, miễn nhiễm với tấn công XSS.
       + `SameSite=Lax`: Ngăn chặn gửi cookie qua các yêu cầu chéo trang, chống tấn công CSRF.
     - Thời hạn phiên: 12 giờ.
  2. **Ghép đôi thiết bị bằng mã PIN 8 ký tự:**
     - Mã PIN gồm 8 ký tự ngẫu nhiên lấy từ tập ký tự dễ đọc: `ABCDEFGHJKLMNPQRSTUVWXYZ23456789` (loại bỏ `O, 0, I, 1` để người dùng không bị nhầm lẫn khi nhập).
     - Thời gian sống (TTL) của mã PIN: đúng 10 phút. Quá 10 phút mã sẽ tự hủy và phải tạo mã mới.
  3. **Phòng chống lỗ hổng phân quyền IDOR (Insecure Direct Object References):**
     - Khi một phụ huynh gọi API truy vấn thông tin một đứa trẻ hoặc thiết bị (`/api/v1/children/{child_id}`), Server không chỉ truy vấn theo `child_id` mà luôn kèm điều kiện bắt buộc:
       `WHERE Child.id == child_id AND Child.parent_id == current_parent.id`.
     - Phụ huynh A tuyệt đối không thể xem hay chỉnh sửa thông tin của con phụ huynh B dù có đoán được ID.

---

## 4. KẾT QUẢ KIỂM THỬ TỰ ĐỘNG (14 TESTS)

Chạy kiểm thử cho Tuần 2:
```bash
.venv/bin/pytest tests/test_screen_time.py tests/test_blockpage.py tests/test_server_auth.py -v
```

| Tệp kiểm thử | Tên bài test | Nội dung xác thực | Kết quả |
| :--- | :--- | :--- | :---: |
| `test_screen_time.py` | `test_initial_state_and_active_counting` | Khởi tạo FSM và đếm thời gian khi hoạt động | **PASSED** |
| `test_screen_time.py` | `test_idle_pause_does_not_consume_quota` | Nhàn rỗi $> 5$ phút tự dừng trừ giờ | **PASSED** |
| `test_screen_time.py` | `test_warning_tiers_and_grace_period` | Kích hoạt cảnh báo 10p, 5p, 1p và ân hạn 60s | **PASSED** |
| `test_screen_time.py` | `test_clock_rollback_anti_tamper` | Phát hiện lùi giờ hệ thống, giữ nguyên hạn ngạch đã dùng | **PASSED** |
| `test_screen_time.py` | `test_schedule_matrix_blocking` | Khóa máy chính xác theo khung giờ giới nghiêm ban đêm | **PASSED** |
| `test_screen_time.py` | `test_urgent_lock_and_bonus_time` | Tiếp nhận lệnh khóa khẩn cấp và cộng thêm giờ | **PASSED** |
| `test_screen_time.py` | `test_benchmark_hourly_accuracy` | Sai số tích lũy sau 1 giờ chạy $\le \pm 30$ giây | **PASSED** |
| `test_blockpage.py` | `test_blockpage_status_and_html_rendering` | Máy chủ cổng 8080 trả về HTML giao diện giáo dục | **PASSED** |
| `test_blockpage.py` | `test_blockpage_child_unblock_request_callback` | Tiếp nhận yêu cầu xin mở trang web từ form của trẻ | **PASSED** |
| `test_blockpage.py` | `test_dns_proxy_integration_with_blockpage` | Tích hợp giữa DNS Proxy và Blockpage cổng 8080 | **PASSED** |
| `test_server_auth.py` | `test_parent_register_password_complexity` | Kiểm tra bắt buộc độ phức tạp mật khẩu khi đăng ký | **PASSED** |
| `test_server_auth.py` | `test_parent_login_and_brute_force_lockout` | Khóa tài khoản sau 5 lần đăng nhập thất bại | **PASSED** |
| `test_server_auth.py` | `test_login_session_and_me_endpoint` | Đăng nhập thành công trả về Cookie phiên và đọc `/me` | **PASSED** |
| `test_server_auth.py` | `test_idor_protection_and_device_enrollment` | Chống IDOR và ghép đôi thiết bị bằng mã PIN 8 ký tự | **PASSED** |

---

## 5. BỘ CÂU HỎI VẤN ĐÁP BẢO VỆ ĐỒ ÁN (DEFENSE Q&A)

### Câu 1: Tại sao phải sử dụng `time.monotonic()` thay vì chỉ dùng `time.time()` để đếm giờ?
> **Trả lời:**  
> `time.time()` lấy thời gian từ đồng hồ hệ thống (Wall-clock time). Giá trị này có thể bị thay đổi bất cứ lúc nào khi người dùng chỉnh giờ trong Windows Control Panel hoặc khi giao thức đồng bộ mạng NTP cập nhật. Nếu chỉ dựa vào `time.time()`, đứa trẻ có thể lùi giờ máy tính để có thêm thời gian sử dụng vô tận.  
> Trong khi đó, `time.monotonic()` (tương đương `GetTickCount64` trên Windows) là bộ đếm phần cứng đo nhịp xung clock của CPU từ lúc khởi động máy tính, luôn tăng tịnh tiến đều đặn và không có bất kỳ API nào có thể chỉnh lùi được. Nhờ so sánh song song hai đồng hồ này, hệ thống vừa biết chính xác thời gian thực trong ngày, vừa phát hiện tức thì mọi hành vi gian lận chỉnh giờ.

### Câu 2: Thuật toán phát hiện nhàn rỗi (Idle Detection) hoạt động như thế nào và tại sao lại đặt ngưỡng 5 phút?
> **Trả lời:**  
> Hệ thống gọi hàm Windows API `user32.GetLastInputInfo()` để lấy thời điểm (tính bằng mili-giây) mà người dùng chạm vào chuột hoặc gõ bàn phím lần cuối. Lấy thời điểm hiện tại trừ đi mốc này sẽ ra số giây không thao tác (`idle_seconds`).  
> Ngưỡng **5 phút ($300$ giây)** được lựa chọn theo nguyên tắc nhân văn (NT4): Nếu trẻ chỉ dừng lại 1–2 phút để đọc tài liệu hoặc suy nghĩ giải bài tập thì máy vẫn đếm giờ học; nhưng nếu trẻ rời khỏi bàn để đi ăn cơm, đi ngủ mà quên tắt máy tính, hệ thống tự động tạm dừng đếm để trẻ không bị mất oan thời gian chơi của mình.

### Câu 3: Lỗ hổng IDOR là gì và làm sao mã nguồn của nhóm bảo vệ được dữ liệu của phụ huynh?
> **Trả lời:**  
> IDOR (*Insecure Direct Object Reference*) là lỗ hổng xảy ra khi hệ thống nhận một định danh từ phía người dùng (ví dụ: `GET /api/v1/children/5`) và truy vấn trực tiếp vào database mà không kiểm tra xem người dùng đó có quyền sở hữu đối tượng số 5 hay không. Tin tặc có thể thay số 5 thành số 6 để xem trộm thông tin con của người khác.  
> Trong OpenGuard Kids, mọi câu truy vấn ORM trong `src/server/app.py` đều được kiểm tra kép:
> `db.query(Child).filter(Child.id == child_id, Child.parent_id == current_parent.id).first()`.
> Nếu phụ huynh không phải chủ sở hữu hợp pháp của bản ghi đó, hệ thống lập tức trả về lỗi `404 Not Found` hoặc `403 Forbidden`.

