# OpenGuard Kids — Chính Sách Quyền Riêng Tư & Bảng Ánh Xạ Dữ Liệu (PRIVACY.md)

> **Mã yêu cầu:** F3.5 (Đặc tả chức năng Mục 3) & NT2 (Triết lý thiết kế tối thiểu dữ liệu).  
> **Nguyên tắc cốt lõi:** *"Công cụ đồng hành, không phải phần mềm theo dõi lén"*. Tuyệt đối không thu thập nội dung nhạy cảm, không có chế độ chạy ngầm bí mật, cam kết xóa kép đồng thời (Atomic Dual Deletion) sau 90 ngày.

---

## 1. Bảng Ánh Xạ Dữ Liệu Thu Thập (Data Mapping Table)

Mọi trường dữ liệu được lưu trữ trong hệ thống OpenGuard Kids bắt buộc phải có mục đích rõ ràng, thời hạn lưu trữ và đối tượng được xem. Trường nào không giải thích được mục đích đều bị loại bỏ khỏi lược đồ cơ sở dữ liệu:

| Tên trường dữ liệu | Kiểu dữ liệu | Mục đích kỹ thuật | Thời hạn lưu trữ | Quyền xem (Visibility) |
| :--- | :--- | :--- | :--- | :--- |
| **`ts`** | Số thực (Unix Timestamp) | Xác định mốc thời gian diễn ra hoạt động để tổng hợp biểu đồ ngày/tuần. | Tối đa 90 ngày (Tự động xóa) | Phụ huynh, Trẻ em |
| **`device_id`** | Chuỗi (UUIDv4) | Định danh máy tính Windows của trẻ trong gia đình để áp dụng đúng chính sách. | Theo vòng đời thiết bị | Phụ huynh, Quản trị viên |
| **`child_id`** | Chuỗi (UUIDv4) | Liên kết thiết bị với hồ sơ độ tuổi của trẻ. | Đến khi xóa hồ sơ trẻ | Phụ huynh, Quản trị viên |
| **`type`** | Chuỗi liệt kê (`enum`) | Phân loại sự kiện: `blocked_domain`, `process_blocked`, `screen_time`, `quota_warning`, `locked`, `unlock_request`. | Tối đa 90 ngày | Phụ huynh, Trẻ em |
| **`subject`** | Chuỗi (Tên tiến trình / Tên miền) | Tên tệp ứng dụng (ví dụ: `zoom.exe`, `game.exe`) hoặc tên miền cấp hai (ví dụ: `hcmus.edu.vn`). **Tuyệt đối không lưu URL đầy đủ.** | Tối đa 90 ngày | Phụ huynh, Trẻ em |
| **`duration_sec`** | Số nguyên (Giây) | Thời lượng sử dụng thực tế của phiên làm việc để trừ vào hạn ngạch ngày. | Tối đa 90 ngày | Phụ huynh, Trẻ em |
| **`idempotency_key`** | Chuỗi (Hash hex) | Khóa chống trùng lặp sự kiện khi đồng bộ ngoại tuyến từ Agent lên Server. | Tối đa 90 ngày | Hệ thống (Nội bộ) |

---

## 2. Danh Mục Các Trường Dữ Liệu BỊ CẤM TUYỆT ĐỐI (Strictly Prohibited)

Tuân thủ nghiêm ngặt **DANH MỤC CẤM** của đề bài và Nghị định 13/2023/NĐ-CP về bảo vệ dữ liệu cá nhân, OpenGuard Kids cam kết **KHÔNG BAO GIỜ** thiết kế, thu thập hoặc lưu trữ các dữ liệu sau:

| Loại dữ liệu bị cấm | Lý do loại trừ | Cơ chế ngăn chặn kỹ thuật |
| :--- | :--- | :--- |
| **Ảnh chụp màn hình (Screenshots / Screen Recording)** | Xâm phạm nghiêm trọng quyền riêng tư thị giác của trẻ khi học tập và sinh hoạt. | Không tích hợp bất kỳ hàm chụp màn hình `BitBlt` hay GDI nào trong mã nguồn. |
| **Bản ghi phím bấm (Keylogger)** | Nguy cơ làm lộ mật khẩu, tài khoản trường học và nội dung trò chuyện của trẻ. | Không sử dụng Windows Hook `WH_KEYBOARD_LL`. Chỉ dùng `user32.GetLastInputInfo` để lấy mốc thời gian rảnh rỗi. |
| **URL chi tiết & Tham số tìm kiếm (Full URLs & Query Strings)** | URL có thể chứa từ khóa tìm kiếm riêng tư hoặc token xác thực phiên web. | DNS Proxy chỉ phân giải ở tầng tên miền (Domain Name), hoàn toàn không can thiệp vào tầng HTTP path/query. |
| **Nội dung email, tin nhắn, tài liệu cá nhân** | Xâm phạm bí mật đời tư được pháp luật bảo vệ. | Không quét ổ đĩa, không đọc tệp tài liệu của trẻ. Chỉ băm SHA-256 tệp thực thi nhị phân (`.exe`). |
| **Dữ liệu chia sẻ bên thứ ba** | Đảm bảo an toàn thông tin gia đình. | Hệ thống hoạt động độc lập (Self-hosted / LAN / Local VPS), không gửi dữ liệu ra bất kỳ cloud bên thứ 3 nào. |

---

## 3. Chính Sách Tự Động Xóa Dữ Liệu & Nút Xóa Kép (Atomic Dual Deletion)

1. **Thời hạn lưu trữ 90 ngày (90-Day Auto Purge):**
   - Định kỳ mỗi đêm, tác vụ tự động trên Server sẽ quét và xóa toàn bộ các bản ghi `events` có mốc thời gian `ts < now - 90 days`.
2. **Nút "Xóa toàn bộ dữ liệu của con tôi" (Atomic Dual Deletion - F3.4):**
   - Khi phụ huynh nhấn nút này trên Web Dashboard:
     - Server xóa sạch toàn bộ lịch sử hoạt động, sự kiện và yêu cầu của trẻ trong cơ sở dữ liệu trung tâm.
     - Đồng thời, Server gửi lệnh qua WebSocket tới Windows Agent để xóa sạch tệp SQLite ngoại tuyến tại `%ProgramData%\OpenGuardKids\offline_events.db`.
     - Đảm bảo dữ liệu biến mất hoàn toàn trên cả máy chủ lẫn máy tính của trẻ.

