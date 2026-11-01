# OpenGuard Kids — Tuần 4: Giao Diện Tray UI Desktop & Nghiệm Thu Sống Còn Demo D1

> **Khóa học:** Mạng máy tính (*Computer Networks*) — Khoa Công nghệ Thông tin, Trường ĐH Khoa học Tự nhiên (HCMUS)  
> **Mã yêu cầu đồ án:** F1.4 (Cảnh báo & 60s ân hạn), NT1, NT4, NT5 (Minh bạch & Trao quyền cho trẻ), F5 (Anti-abuse)  
> **Trạng thái kiểm thử:** **5/5 integration tests PASSED (100%)** (Lũy kế: 46/46 passed)

---

## 1. MỤC TIÊU VÀ ĐẶT VẤN ĐỀ TUẦN 4

Tuần 4 là bước chuyển mình từ các dịch vụ chạy ngầm sang **giao diện người dùng thực tế trên Desktop (Session 1)**:

1. **Tuân thủ triệt để nguyên tắc Không phần mềm theo dõi lén (NT1, NT5):** Ứng dụng phải luôn hiện diện trên thanh tác vụ (Taskbar Tray), hiển thị rõ ràng cho đứa trẻ biết còn bao nhiêu phút, chính sách nào đang áp dụng. Tuyệt đối không được ẩn mình.
2. **Cơ chế bảo vệ chống chạy lén khi mất liên lạc (Anti-abuse safeguard):** Nếu kẻ gian tìm cách ngắt kênh liên lạc giữa Tray UI và Service để lén lút theo dõi mà trẻ không biết, Tray UI phải lập tức phát hiện trong vòng 15 giây và hiển thị cảnh báo đỏ toàn màn hình.
3. **Chuỗi cảnh báo nhân văn & 60 giây ân hạn (Save work grace period):** Không bao giờ khóa máy đột ngột làm mất bài tập dở dang của trẻ. Phải có chuỗi cảnh báo tăng dần (10p $\rightarrow$ 5p $\rightarrow$ 1p) và 60 giây đếm ngược để trẻ kịp bấm Save tài liệu.
4. **Nghiệm thu toàn diện kịch bản DEMO D1:** Bài kiểm tra sống còn của dự án mô phỏng toàn bộ hành trình trải nghiệm người dùng từ cảnh báo đến khóa máy và mở khóa từ xa.

---

## 2. KIẾN TRÚC GIAO TIẾP TRAY UI & DỊCH VỤ HỆ THỐNG

```
+-----------------------------------------------------------------------------------+
|                        MÁY TÍNH CỦA TRẺ (WINDOWS 10/11 x64)                       |
|                                                                                   |
|  [SESSION 0: WINDOWS SERVICE]              [SESSION 1: TRAY UI (USER DESKTOP)]    |
|   +--------------------------+              +-----------------------------------+  |
|   | ScreenTimeEngine (FSM)   |              | TrayController (src/tray/app.py)  |  |
|   | Loopback IPC Server      |              | - Icon khay hệ thống (Taskbar)   |  |
|   | (127.0.0.1:8765)         |              | - Trạng thái minh bạch (NT1, NT5) |  |
|   +------------+-------------+              +-----------------+-----------------+  |
|                ^                                              |                    |
|                |                                              v                    |
|                |    Loopback HTTP Polling (1.0s) & Heartbeat  |                    |
|                |    Header: X-OGK-Token: <64-hex secret>      |                    |
|                +----------------------------------------------+                    |
|                                                               |                    |
|                                                               v                    |
|                                             +-----------------------------------+  |
|                                             | StateListener (state_listener.py) |  |
|                                             | - Polling chu kỳ 1.0s             |  |
|                                             | - Mất kết nối > 15s -> BÁO ĐỘNG ĐỎ|  |
|                                             +-----------------+-----------------+  |
|                                                               |                    |
|                                                               v                    |
|                                             +-----------------------------------+  |
|                                             | Dialogs Hub (src/tray/dialogs.py) |  |
|                                             | 1. Toast 10m / 5m / 1m (F1.4)     |  |
|                                             | 2. Hộp thoại ân hạn 60s lưu bài   |  |
|                                             | 3. Màn hình khóa (Lock Overlay)   |  |
|                                             | 4. Form xin 15p & Báo chặn nhầm   |  |
|                                             | 5. Màn hình minh bạch (NT5)       |  |
|                                             +-----------------------------------+  |
+-----------------------------------------------------------------------------------+
```

---

## 3. CHI TIẾT CÀI ĐẶT CÁC THÀNH PHẦN MÃ NGUỒN

### 3.1. Luồng lắng nghe trạng thái StateListener (`src/tray/state_listener.py`)
* **Vị trí tệp:** `src/tray/state_listener.py`
* **Mã yêu cầu:** NT1, F5 (Anti-abuse)
* **Chi tiết kỹ thuật:**
  1. **Thăm dò liên tục (Periodic Polling):**
     - Luồng nền chạy định kỳ mỗi **1.0 giây**, gửi yêu cầu HTTP `GET /status` qua cổng nội bộ `127.0.0.1:8765` kèm mã xác thực Token.
     - Cứ mỗi 10 giây gửi kèm gói tin nhịp tim `POST /heartbeat`.
  2. **Bảo vệ chống chạy lén (Connection Lost Safeguard):**
     - Đề bài nghiêm cấm phần mềm chạy ngầm theo dõi người dùng mà không có giao diện (NT1).
     - Nếu tiến trình Service bị lỗi, bị crash, hoặc bị một bên thứ ba ngắt kết nối quá **15 giây** (`time.time() - last_seen > 15`):
       + `StateListener` lập tức chuyển sang trạng thái báo động `LOST_CONNECTION`.
       + Kích hoạt cảnh báo nổi bật trên màn hình thông báo cho trẻ biết phần mềm đang mất liên lạc với hệ thống giám sát. Tuyệt đối không cho phép phần mềm rơi vào trạng thái "giám sát ẩn".

### 3.2. Chuỗi cảnh báo nhân văn & Hộp thoại Ân hạn 60s (`src/tray/dialogs.py`)
* **Vị trí tệp:** `src/tray/dialogs.py`
* **Mã yêu cầu:** F1.4, NT4
* **Chi tiết kỹ thuật:**
  1. **Chuỗi cảnh báo thông minh tăng dần:**
     - **Mốc còn 10 phút:** Hiển thị thông báo Toast xanh dương nhắc nhở trẻ sắp hết phiên dùng máy để trẻ chuẩn bị hoàn thành công việc.
     - **Mốc còn 5 phút:** Hiển thị thông báo Toast màu vàng nhắc nhở lưu các tệp bài tập.
     - **Mốc còn 1 phút:** Hiển thị thông báo Toast màu cam/đỏ khẩn cấp.
  2. **Hộp thoại ân hạn 60 giây (Save Work Grace Period):**
     - Khi đồng hồ chạm mốc 0 phút, hệ thống **không khóa máy ngay lập tức**.
     - Một hộp thoại đếm ngược 60 giây xuất hiện ở góc màn hình: *"Đã hết giờ dùng máy hôm nay! Em có 60 giây để bấm Save lưu lại bài tập Word, PowerPoint trước khi màn hình khóa."*
     - Hết 60 giây, hệ thống mới kích hoạt màn hình khóa toàn diện (`LOCKED_QUOTA`).
  3. **Màn hình khóa lịch sự (Lock Overlay):**
     - Màn hình khóa có tông màu dịu mắt, giải thích nguyên nhân rõ ràng (hết hạn ngạch hoặc đến giờ giới nghiêm ban đêm).
     - Luôn có số điện thoại **Tổng đài 111** để trẻ có thể gọi cứu trợ khi cần.
     - Cung cấp hai nút bấm tương tác: *"Xin cha mẹ thêm 15 phút"* và *"Báo chặn nhầm trang web"*.

### 3.3. Trao quyền cho trẻ (Child Agency) & Màn hình minh bạch (`src/tray/app.py`)
* **Vị trí tệp:** `src/tray/app.py`
* **Mã yêu cầu:** NT4, NT5
* **Chi tiết kỹ thuật:**
  1. **Tôn trọng quyền làm chủ của trẻ:**
     - Nút *"Xin thêm 15 phút"*: Trẻ nhập lý do (ví dụ: "Em cần thêm giờ nộp bài tập môn Lý") $\rightarrow$ Yêu cầu được chuyển thẳng lên hòm thư Web Dashboard của phụ huynh.
     - Khi phụ huynh bấm Đồng ý, thời gian được tự động cộng và màn hình tự mở khóa.
  2. **Màn hình minh bạch dữ liệu (Transparency Dialog - NT5):**
     - Bất kỳ lúc nào, đứa trẻ có thể bấm chuột phải vào icon trên thanh Taskbar và chọn *"Hôm nay em đã dùng gì?"*.
     - Màn hình hiển thị trung thực:
       + Số phút đã dùng hôm nay / Tổng hạn ngạch ngày.
       + Khung giờ giới nghiêm ban đêm (ví dụ: 22:00 – 06:00).
       + **Bốn cam kết bảo vệ quyền riêng tư:** (1) Không bao giờ chụp ảnh màn hình; (2) Không lưu mật khẩu/phím gõ; (3) Không đọc trộm tin nhắn riêng tư; (4) Không lưu toàn bộ lịch sử lướt web.

---

## 4. KỊCH BẢN NGHIỆM THU DEMO D1 (TOÀN DIỆN 6 BƯỚC)

Kịch bản Demo D1 trong đề bài kiểm tra xem hệ thống có vận hành mượt mà từ đầu đến cuối phiên sử dụng hay không:

```
[BƯỚC 1: ĐANG DÙNG]
Trẻ dùng máy bình thường, icon Taskbar đếm ngược thời gian.
        |
        v
[BƯỚC 2: CẢNH BÁO TĂNG DẦN]
Thời gian cạn dần -> Toast 10 phút -> Toast 5 phút -> Toast 1 phút.
        |
        v
[BƯỚC 3: ÂN HẠN 60 GIÂY]
Chạm mốc 0 phút -> Kích hoạt đếm ngược 60s cho trẻ bấm Lưu bài (Save work).
        |
        v
[BƯỚC 4: KHÓA MÁY LỊCH SỰ]
Hết 60s -> Hiện màn hình khóa kèm số Tổng đài 111 và nút xin thêm giờ.
        |
        v
[BƯỚC 5: TRẺ XIN THÊM GIỜ]
Trẻ bấm "Xin thêm 15 phút" kèm lý do -> Server tiếp nhận yêu cầu.
        |
        v
[BƯỚC 6: PHỤ HUYNH DUYỆT -> MỞ KHÓA TỨC THỜI]
Phụ huynh bấm Duyệt -> WebSocket bắn lệnh UNLOCK -> Màn hình trẻ tự động mở khóa!
```

Toàn bộ quy trình 6 bước này được tự động hóa và xác thực trọn vẹn trong bài kiểm thử `test_complete_demo_d1_acceptance_sequence`.

---

## 5. KẾT QUẢ KIỂM THỬ TỰ ĐỘNG (5 TESTS)

Chạy kiểm thử cho Tuần 4:
```bash
.venv/bin/pytest tests/test_tray_app.py -v
```

| Tệp kiểm thử | Tên bài test | Nội dung xác thực | Kết quả |
| :--- | :--- | :--- | :---: |
| `test_tray_app.py` | `test_state_listener_polling_and_heartbeat` | Polling 1.0s và gửi nhịp tim định kỳ qua loopback IPC | **PASSED** |
| `test_tray_app.py` | `test_warning_toasts_and_grace_period_triggers` | Kích hoạt đúng thời điểm cảnh báo 10p, 5p, 1p và ân hạn 60s | **PASSED** |
| `test_tray_app.py` | `test_anti_abuse_connection_lost_safeguard` | Báo động đỏ khi mất liên lạc với Service $> 15$ giây | **PASSED** |
| `test_tray_app.py` | `test_child_agency_and_transparency` | Màn hình minh bạch NT5 và form gửi yêu cầu xin thêm 15 phút | **PASSED** |
| `test_tray_app.py` | `test_complete_demo_d1_acceptance_sequence` | Mô phỏng trọn vẹn 6 bước của kịch bản nghiệm thu sống còn Demo D1 | **PASSED** |

---

## 6. BỘ CÂU HỎI VẤN ĐÁP BẢO VỆ ĐỒ ÁN (DEFENSE Q&A)

### Câu 1: Tại sao không khóa máy ngay khi hết giờ mà phải cho thêm 60 giây ân hạn?
> **Trả lời:**  
> Khóa máy đột ngột khi hết giờ là cách làm mang tính áp đặt và phản giáo dục. Nếu đứa trẻ đang làm dở bài văn trên Word hoặc đang vẽ đồ án PowerPoint, việc khóa máy đột ngột sẽ khiến bài làm bị mất toàn bộ nội dung chưa kịp lưu, gây bức xúc và tâm lý ức chế cho trẻ.  
> Thời gian **60 giây ân hạn (Grace Period)** tuân thủ triệt để nguyên tắc **NT4 (Tôn trọng và đồng hành)**, cho phép trẻ kịp bấm tổ hợp phím `Ctrl + S` để lưu giữ thành quả học tập trước khi máy tính bước vào trạng thái nghỉ ngơi.

### Câu 2: Cơ chế chống chạy lén (Anti-abuse connection lost safeguard) giải quyết rủi ro bảo mật gì?
> **Trả lời:**  
> Đề bài quy định nghiêm ngặt nguyên tắc **NT1 (Minh bạch)**: Đây là công cụ đồng hành giữa cha mẹ và con cái, tuyệt đối không phải phần mềm gián điệp chạy lén.  
> Nếu một người cố tình tắt tiến trình Tray UI hoặc can thiệp chặn gói tin loopback để đứa trẻ không biết máy tính đang bị kiểm soát, Service và Tray UI sẽ phát hiện mất nhịp tim quá 15 giây. Khi đó, hệ thống lập tức kích hoạt trạng thái `LOST_CONNECTION`, hiện thông báo cảnh báo đỏ trên màn hình, từ chối chạy âm thầm trong bóng tối.

### Câu 3: Khi đứa trẻ gửi yêu cầu "Xin thêm 15 phút", luồng dữ liệu đi qua những đâu để tới được điện thoại cha mẹ?
> **Trả lời:**  
> 1. Trẻ bấm *"Xin thêm 15 phút"* trên giao diện Tray UI (Session 1).  
> 2. Tray UI gửi yêu cầu qua Loopback IPC HTTP `127.0.0.1:8765` tới Service (Session 0).  
> 3. Service gọi API máy chủ `POST /api/v1/requests` qua HTTPS kèm theo lý do trẻ nhập.  
> 4. Server lưu vào bảng `ChildRequest` và cập nhật tức thời lên Web Dashboard của phụ huynh.  
> 5. Phụ huynh mở điện thoại, xem lý do và bấm *"Đồng ý"*. Server đẩy gói tin qua kết nối WebSocket `ADD_TIME 15m` về máy con, máy con lập tức cộng thêm 15 phút vào bộ đếm và tự động giải phóng màn hình khóa.

