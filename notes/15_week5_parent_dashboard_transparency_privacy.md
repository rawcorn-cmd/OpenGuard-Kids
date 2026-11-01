# OpenGuard Kids — Tuần 5: Bảng Điều Khiển Phụ Huynh, Minh Bạch & Quyền Riêng Tư Tối Cao

> **Khóa học:** Mạng máy tính (*Computer Networks*) — Khoa Công nghệ Thông tin, Trường ĐH Khoa học Tự nhiên (HCMUS)  
> **Mã yêu cầu đồ án:** F2.4 (Bảng phân loại 200 mục), F3.2 (Web Dashboard), F3.4 (Xóa kép & Quá hạn 90 ngày), F3.5, NT2, NT5 (Bảo vệ riêng tư)  
> **Trạng thái kiểm thử:** **5/5 integration tests PASSED (100%)** (Toàn bộ dự án: **51/51 tests PASSED**)

---

## 1. MỤC TIÊU VÀ ĐẶT VẤN ĐỀ TUẦN 5

Tuần 5 là mảnh ghép hoàn thiện toàn bộ đồ án OpenGuard Kids, tập trung vào **giao diện quản trị của cha mẹ và chuẩn mực quyền riêng tư**:

1. **Bộ dữ liệu phân loại 200 mục hoàn chỉnh (F2.4):** Cung cấp sẵn danh mục tên miền phong phú, phân bổ đều qua 6 nhóm danh mục chuẩn, có chính sách mặc định phù hợp cho lứa tuổi 6–11 tuổi.
2. **Bảng điều khiển Web Dashboard thân thiện trên di động (F3.2):** Phụ huynh có thể mở trình duyệt trên điện thoại hoặc máy tính bảng để xem tổng thời gian sử dụng, xếp hạng Top 10 ứng dụng/website, duyệt yêu cầu xin giờ và bấm nút khóa máy khẩn cấp.
3. **Quyền riêng tư tối cao & Tính năng Xóa dữ liệu kép (F3.4, F3.5, NT2):** Xây dựng văn bản cam kết pháp lý `PRIVACY.md`, cơ chế dọn dẹp dữ liệu quá hạn 90 ngày, và đặc biệt là tính năng **Atomic Dual Deletion (Xóa kép)**: Khi phụ huynh yêu cầu xóa dữ liệu, thông tin phải biến mất hoàn toàn ở cả cơ sở dữ liệu trên Server và bộ nhớ đệm SQLite trên máy tính của trẻ.

---

## 2. KIẾN TRÚC TỔNG THỂ & LUỒNG XỬ LÝ TUẦN 5

```
+-----------------------------------------------------------------------------------+
|                     ĐIỆN THOẠI / MÁY TÍNH PHỤ HUYNH (PARENT UI)                   |
|                                                                                   |
|  [TRÌNH DUYỆT WEB - TEMPLATE JINJA2 / HTML5 RESPONSIVE]                           |
|   - Thời gian dùng hôm nay & hạn ngạch (Progress Bar)                             |
|   - Bảng xếp hạng: Top 10 Ứng dụng & Top 10 Website                               |
|   - Hòm thư duyệt: Trẻ xin +15 phút -> Bấm [Duyệt] -> Tự động bắn WebSocket       |
|   - Lệnh nhanh từ xa: [Khóa ngay] / [Mở khóa] / [+15 phút]                        |
|   - Nút hành động nhạy cảm: [XÓA TOÀN BỘ DỮ LIỆU CỦA CON TÔI]                    |
+-----------------------------------------------------------------------------------+
                                         |
                       HTTPS API Calls   | Cookie phiên an toàn
                                         v
+-----------------------------------------------------------------------------------+
|                        MÁY CHỦ QUẢN TRỊ (FASTAPI BACKEND)                         |
|                                                                                   |
|  [src/server/app.py - ENDPOINTS QUẢN TRỊ & BẢO VỆ RIÊNG TƯ]                       |
|   1. GET /dashboard/summary/{child_id} -> Thống kê hôm nay, tuần này, Top 10      |
|   2. POST /api/v1/requests/{id}/review -> Duyệt yêu cầu & bắn WebSocket           |
|   3. DELETE /api/v1/children/{child_id}/purge-data -> ATOMIC DUAL DELETION:       |
|      + Xóa toàn bộ bản ghi của con trong SQLite Server (Event, Request)           |
|      + Bắn lệnh WebSocket "PURGE_LOCAL_CACHE" xuống máy tính của trẻ              |
|   4. POST /api/v1/maintenance/purge-expired -> Xóa bản ghi cũ hơn 90 ngày         |
+-----------------------------------------------------------------------------------+
                                         |
                                         | Lệnh WebSocket: "PURGE_LOCAL_CACHE"
                                         v
+-----------------------------------------------------------------------------------+
|                        MÁY TÍNH CỦA TRẺ (WINDOWS 10/11 x64)                       |
|                                                                                   |
|  [BỘ ĐỆM NGOẠI TUYẾN - src/agent/offline_buffer.py]                               |
|   - Nhận lệnh xóa từ Server                                                       |
|   - Xóa sạch toàn bộ bản ghi trong SQLite %ProgramData%\...\offline_events.db     |
|   -> DỮ LIỆU BIẾN MẤT HOÀN TOÀN Ở CẢ 2 NƠI (SERVER VÀ CLIENT)                     |
+-----------------------------------------------------------------------------------+
```

---

## 3. CHI TIẾT CÀI ĐẶT CÁC THÀNH PHẦN MÃ NGUỒN

### 3.1. Bộ dữ liệu chuẩn 200 tên miền (`data/classification_dataset.json`)
* **Vị trí tệp:** `data/classification_dataset.json`
* **Mã yêu cầu:** F2.4
* **Chi tiết kỹ thuật:**
  - Chứa đúng **200 tên miền phổ biến**, được gắn nhãn và phân loại tỉ mỉ theo 6 danh mục chuẩn:
    1. `educational` (45 tên miền): Học tập, từ điển, bách khoa toàn thư (`wikipedia.org`, `khanacademy.org`, `duolingo.com`...).
    2. `entertainment` (35 tên miền): Xem video, nghe nhạc (`youtube.com`, `spotify.com`, `netflix.com`...).
    3. `social_media` (30 tên miền): Mạng xã hội (`facebook.com`, `tiktok.com`, `instagram.com`...).
    4. `gaming` (35 tên miền): Nền tảng game, trang trò chơi (`roblox.com`, `minecraft.net`, `steampowered.com`...).
    5. `inappropriate` (45 tên miền): Nội dung người lớn, cờ bạc, bạo lực cần chặn tuyệt đối.
    6. `unclassified` (10 tên miền): Các trang tiện ích trung tính cần giám sát thêm.
  - **Chính sách mẫu cho lứa tuổi 6–11 tuổi:**
    + Nhóm Giáo dục: Luôn cho phép truy cập, không trừ hạn ngạch giải trí.
    + Nhóm Không phù hợp: Chặn 100% ở mọi thời điểm.
    + Nhóm Game & Mạng xã hội: Giới hạn theo hạn ngạch thời gian ngày (ví dụ 60 phút/ngày) và cấm sau giờ giới nghiêm (21:00).

### 3.2. Văn bản cam kết quyền riêng tư (`PRIVACY.md`)
* **Vị trí tệp:** `PRIVACY.md`
* **Mã yêu cầu:** F3.5, NT2, NT5
* **Chi tiết kỹ thuật:**
  - **Bảng ma trận 4 cột ánh xạ dữ liệu:**
    Liệt kê đầy đủ mọi trường dữ liệu mà hệ thống lưu trữ: Kiểu dữ liệu $\leftrightarrow$ Mục đích sử dụng $\leftrightarrow$ Thời hạn lưu trữ $\leftrightarrow$ Ai có quyền xem.
  - **Danh mục trường dữ liệu BỊ NGHIÊM CẤM:**
    Tuyên bố rõ ràng hệ thống không bao giờ có các trường: `screenshot_data`, `keystroke_log`, `full_url_query_string`, `webcam_feed`, `microphone_audio`.
  - **Thời hạn lưu giữ:** Mọi dữ liệu nhật ký sự kiện tự động hết hạn và bị xóa vĩnh viễn sau **90 ngày**.

### 3.3. Bảng điều khiển Web Dashboard di động (`src/server/templates/dashboard.html`)
* **Vị trí tệp:** `src/server/templates/dashboard.html`, `src/server/app.py`
* **Mã yêu cầu:** F3.2
* **Chi tiết kỹ thuật:**
  - Thiết kế bằng HTML5 và CSS hiện đại, responsive co giãn tối ưu cho màn hình điện thoại di động (Mobile-friendly).
  - Hiển thị trực quan:
    + Thanh tiến độ thời gian đã dùng so với hạn ngạch ngày của con.
    + Thẻ tóm tắt các ứng dụng và website dùng nhiều nhất (Top 10 Rankings).
    + Các nút bấm điều khiển tức thời: *"Khóa ngay"*, *"Mở khóa"*, *"Thêm 15 phút"*.
  - Hòm thư phê duyệt yêu cầu của con:
    + Hiển thị danh sách các lần con gửi xin thêm giờ hoặc báo chặn nhầm trang web.
    + Khi phụ huynh bấm Duyệt, máy chủ tự động cập nhật trạng thái yêu cầu sang `APPROVED`, đồng thời đẩy lệnh WebSocket `ADD_TIME 15m` tới máy tính của con.

### 3.4. Nút Xóa Dữ Liệu Kép (Atomic Dual Deletion) & Tự Động Quét 90 Ngày
* **Vị trí tệp:** `src/server/app.py`
* **Mã yêu cầu:** F3.4
* **Chi tiết kỹ thuật:**
  1. **Tính năng Xóa Dữ Liệu Kép (Atomic Dual Deletion):**
     - Endpoint: `DELETE /api/v1/children/{child_id}/purge-data`.
     - Phụ huynh có quyền yêu cầu xóa toàn bộ lịch sử của con mình. Khi bấm nút:
       + **Bước 1 (Xóa Server):** Máy chủ xóa sạch toàn bộ bản ghi trong bảng `Event` và `ChildRequest` liên quan đến đứa trẻ này trong cơ sở dữ liệu SQLite của Server.
       + **Bước 2 (Xóa Client):** Máy chủ ngay lập tức gửi một gói tin lệnh khẩn qua WebSocket: `{"command": "PURGE_LOCAL_CACHE", "child_id": child_id}` tới thiết bị máy tính của con.
       + Khi nhận được lệnh, Agent trên máy tính trẻ lập tức xóa sạch các bản ghi trong file SQLite cục bộ `%ProgramData%\OpenGuardKids\offline_events.db`.
       + Kết quả: Dữ liệu biến mất hoàn toàn ở cả hai đầu, bảo đảm quyền riêng tư tuyệt đối cho trẻ em.
  2. **Tác vụ dọn dẹp dữ liệu quá hạn 90 ngày (90-Day Retention Worker):**
     - Endpoint: `POST /api/v1/maintenance/purge-expired`.
     - Quét cơ sở dữ liệu và tự động xóa vĩnh viễn mọi bản ghi sự kiện có dấu thời gian `ts < now - 90 days`.

---

## 4. KẾT QUẢ KIỂM THỬ TỰ ĐỘNG (5 TESTS)

Chạy kiểm thử cho Tuần 5:
```bash
.venv/bin/pytest tests/test_dashboard_and_privacy.py -v
```

| Tệp kiểm thử | Tên bài test | Nội dung xác thực | Kết quả |
| :--- | :--- | :--- | :---: |
| `test_dashboard_and_privacy.py` | `test_dashboard_summary_reports_and_rankings` | Thống kê số phút và Top 10 ứng dụng/website chính xác | **PASSED** |
| `test_dashboard_and_privacy.py` | `test_child_request_parent_review` | Phụ huynh duyệt yêu cầu xin giờ và tự động đẩy WebSocket | **PASSED** |
| `test_dashboard_and_privacy.py` | `test_atomic_dual_deletion` | Xóa kép đồng thời sạch database trên Server và đẩy lệnh xóa Client | **PASSED** |
| `test_dashboard_and_privacy.py` | `test_90_day_retention_purge` | Tự động quét và xóa sạch dữ liệu cũ hơn 90 ngày | **PASSED** |
| `test_dashboard_and_privacy.py` | `test_dashboard_html_rendering` | Giao diện Web HTML5 hiển thị đầy đủ thông tin trên trình duyệt | **PASSED** |

---

## 5. TỔNG KẾT TOÀN DIỆN: 51/51 BÀI TEST PASSED

```text
============================= test session starts ==============================
tests/test_blockpage.py (3 tests) ...................................... PASSED
tests/test_dashboard_and_privacy.py (5 tests) .......................... PASSED
tests/test_database_and_security.py (5 tests) .......................... PASSED
tests/test_dns_proxy.py (8 tests) ...................................... PASSED
tests/test_ipc.py (3 tests) ............................................ PASSED
tests/test_offline_buffer.py (3 tests) ................................. PASSED
tests/test_process_monitor.py (5 tests) ................................ PASSED
tests/test_screen_time.py (7 tests) .................................... PASSED
tests/test_server_auth.py (4 tests) .................................... PASSED
tests/test_sync_and_events.py (3 tests) ................................ PASSED
tests/test_tray_app.py (5 tests) ....................................... PASSED

======================== 51 passed, 2 warnings in 9.72s ========================
```

---

## 6. BỘ CÂU HỎI VẤN ĐÁP BẢO VỆ ĐỒ ÁN (DEFENSE Q&A)

### Câu 1: Tại sao hệ thống không lưu lại đường dẫn URL đầy đủ (ví dụ: `youtube.com/watch?v=xyz`) mà chỉ lưu tên miền (`youtube.com`)?
> **Trả lời:**  
> Điều này tuân thủ nguyên tắc **Tối giản dữ liệu (Data Minimization - NT2)** và quyền riêng tư trẻ em:
> 1. Chuỗi URL chi tiết (đặc biệt là phần query parameters phía sau dấu `?`) thường chứa các thông tin cá nhân rất nhạy cảm: từ khóa tìm kiếm riêng tư, mã token phiên làm việc, hoặc thông tin cá nhân.
> 2. Phụ huynh chỉ cần biết con mình dùng bao nhiêu thời gian cho YouTube hoặc đọc sách để nhắc nhở và quản lý quỹ thời gian, không cần thiết phải "soi" từng video cụ thể con đang xem. Việc chỉ lưu tên miền vừa đáp ứng mục tiêu quản lý lướt web, vừa bảo vệ được sự tin cậy và không gian riêng tư của trẻ.

### Câu 2: Tính năng "Xóa dữ liệu kép" (Atomic Dual Deletion) vận hành như thế nào trong tình huống máy tính của trẻ đang tắt nguồn (offline)?
> **Trả lời:**  
> 1. Khi phụ huynh bấm Xóa dữ liệu, máy chủ Server lập tức xóa sạch toàn bộ các bản ghi trong cơ sở dữ liệu trên Cloud/Server.  
> 2. Nếu thiết bị của trẻ đang online (có kết nối WebSocket), máy chủ bắn lệnh `PURGE_LOCAL_CACHE` để xóa file SQLite cục bộ ngay tức khắc.  
> 3. Nếu máy tính của trẻ đang tắt nguồn hoặc mất mạng, lệnh `PURGE_LOCAL_CACHE` được lưu vào hàng đợi `pending_commands`. Ngay khi máy tính bật lại và có kết nối mạng trở lại, gói tin nhịp tim (heartbeat) đầu tiên sẽ lập tức nhận lệnh này và kích hoạt việc xóa sạch file SQLite cục bộ trên máy con. Đảm bảo dữ liệu chắc chắn bị xóa sạch ở cả hai đầu.

### Câu 3: Tại sao lại đặt thời hạn lưu trữ dữ liệu là 90 ngày mà không lưu vĩnh viễn?
> **Trả lời:**  
> Theo các tiêu chuẩn bảo vệ dữ liệu trẻ em quốc tế (như GDPR-K của Châu Âu hay COPPA của Mỹ), dữ liệu của trẻ vị thành niên không được phép lưu trữ vô thời hạn mà phải có vòng đời lưu trữ rõ ràng (*Storage Limitation*).  
> Thói quen sử dụng máy tính của trẻ thay đổi theo từng kỳ học (khoảng 3 tháng). Dữ liệu sau 90 ngày không còn nhiều giá trị đối với việc quản lý hiện tại của phụ huynh, nhưng lại tiềm ẩn rủi ro lộ lọt thông tin nếu bị tin tặc tấn công. Do đó, tác vụ bảo trì tự động xóa mọi dữ liệu quá 90 ngày là một thiết kế bảo mật chủ động và chuẩn mực.

