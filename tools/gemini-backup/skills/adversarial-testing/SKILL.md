---
name: adversarial-testing
description: Destructive and edge-case testing: rapid clicking, race conditions, corrupted payloads, boundary values, and regression validation.
---

# Adversarial Testing Skill

## Mục đích
Đóng vai trò "Kẻ tấn công/Challenger", cố tình đưa ra các tình huống ngoại lệ, dữ liệu bất thường và chuỗi thao tác dồn dập (stress) để tìm ra các lỗi tiềm ẩn mà các bài test thông thường không phát hiện được.

## Kịch bản kiểm thử phản kháng (Adversarial Scenarios)

### 1. Thao tác dồn dập (Rapid / Double Actions)
- Bấm liên tiếp nút "Tạo trang", "Xóa trang", hoặc "Lưu" nhiều lần trong mili giây.
- Đảm bảo không tạo bản ghi trùng ID và không gây deadlock giao diện.

### 2. Dữ liệu đầu vào bất thường (Malformed & Corrupt Data)
- Nhập tên sổ tay rỗng, chuỗi chỉ toàn dấu cách, ký tự đặc biệt XSS (`<script>`, `"'&`).
- Nhập tệp ncanvas có JSON bị hỏng, thiếu trường bắt buộc hoặc sai định dạng version. Hệ thống phải báo lỗi lịch sự, không crash app.

### 3. Đua tranh bất đồng bộ (Race Conditions)
- Mở tab A, chuyển sang tab B, xóa tab A trong khi tab A đang có thao tác vẽ hoặc pending autosave.
- Đổi ngôn ngữ liên tục giữa Tiếng Việt và Tiếng Anh trong khi dialog đang mở.

### 4. Kiểm tra 7 lỗi hồi quy lịch sử (7 Historical Regressions)
Mỗi bản build phải vượt qua bộ test phản kháng cho 7 lỗi:
1. Hồi sinh sổ tay đã xóa do autosave timer cũ.
2. Xóa nhầm sổ tay khi người dùng chỉ muốn xóa 1 trang.
3. Bộ đếm Sidebar bị sai lệch khi lọc môn học / yêu thích / thùng rác.
4. Rò rỉ trạng thái giữa các tab mở đồng thời (multi-tab state contamination).
5. Tooltip và nhãn bị thiếu bản dịch hoặc rơi về chuỗi mã hóa thô.
6. Ghi chú trong thùng rác lẫn vào danh sách ghi chú hoạt động.
7. Mất liên kết quan hệ khi khôi phục từ thùng rác.
