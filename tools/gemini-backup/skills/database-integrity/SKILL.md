---
name: database-integrity
description: Rigorous verification of SQLite schemas, migrations, foreign key constraints, autosave isolation, soft-delete vs hard-delete.
---

# Database Integrity Skill

## Mục đích
Đảm bảo tính toàn vẹn tuyệt đối của cơ sở dữ liệu SQLite, ngăn chặn mất mát dữ liệu của người dùng, cô lập các thao tác tự động lưu (autosave), và loại bỏ bản ghi mồ côi (orphaned records).

## Các tiêu chuẩn kiểm tra bắt buộc

### 1. Ràng buộc Khóa Ngoại (Foreign Keys)
- SQLite mặc định tắt foreign keys! Mọi kết nối phải chạy `PRAGMA foreign_keys = ON;`.
- Khi xóa một Sổ tay (`Note`), tất cả các trang (`Page`) thuộc sổ tay đó phải được xóa tự động thông qua `ON DELETE CASCADE`. Không chấp nhận có trang mồ côi tồn tại trong bảng `pages`.

### 2. Ngăn ngừa Hồi sinh Dữ liệu do Autosave (Autosave Race Condition)
- Khi một sổ tay hoặc trang bị xóa:
  - Phải hủy toàn bộ timer `debounce` hoặc hàng đợi lưu ngầm (`cancelPendingAutosaves`).
  - Đảm bảo nếu một thao tác lưu đến sau thao tác xóa, hệ thống phải kiểm tra xem bản ghi cha còn tồn tại hay không trước khi ghi đè lại vào DB.

### 3. Di chuyển Schema (Schema Migrations)
- Kiểm tra quá trình nâng cấp từ phiên bản cũ (v1) lên phiên bản mới không làm mất mát dữ liệu hiện có.
- Cột mới (như `order_index`, `objects_json`, `is_custom_title`) phải có giá trị mặc định hợp lệ.

### 4. Kiểm định Định kỳ
- Chạy `PRAGMA foreign_key_check;` để đảm bảo 0 lỗi vi phạm.
- Chạy `PRAGMA integrity_check;` để đảm bảo file B-Tree không bị phân mảnh hoặc lỗi index.
