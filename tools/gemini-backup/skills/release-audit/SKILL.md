---
name: release-audit
description: Independent release validation gate: binary integrity, .deb packaging, desktop integration, evidence collection, zero false PASS.
---

# Release Audit Skill

## Mục đích
Đóng vai trò Kiểm toán viên độc lập (Auditor), giữ chốt chặn cuối cùng trước khi phần mềm được phép đóng gói và phát hành tới người dùng Linux Mint.

## Nguyên tắc Zero False PASS
- Không chấp nhận câu trả lời "Có vẻ hoạt động tốt" hoặc "Đã kiểm tra bằng mắt".
- Mọi phê duyệt phải đính kèm:
  - Commit hash chính xác.
  - Kết quả chạy `npm run qa` với mã thoát 0 từ toàn bộ các tầng.
  - Báo cáo máy đọc `test-results/reports/test-summary.json`.
  - Báo cáo nghiệm thu Markdown `test-results/reports/acceptance-report.md`.
  - Ảnh chụp màn hình thực tế chứng minh không có lỗi layout hoặc vỡ giao diện.

## Checklist Nghiệm thu Release
1. **Kiểm tra Mã nguồn:**
   - `git status` sạch, không có file lạ chưa commit.
   - Không có cảnh báo `svelte-check`.
2. **Kiểm tra Nhị phân:**
   - Bản build phát hành: nhị phân biên dịch thành công (`src-tauri/target/release/notecanvas` hoặc gói `.deb`).
   - Tệp `.desktop` nằm đúng vị trí và có quyền thực thi.
3. **Kiểm tra Tính toàn vẹn Dữ liệu:**
   - SQLite migration hoạt động mượt mà trên database sạch và database cũ.
   - Thao tác xuất PDF và ncanvas tạo file hợp lệ theo đặc tả chuẩn.
4. **Kiểm tra Trải nghiệm Người dùng:**
   - Không còn nút trùng lặp hoặc chức năng thừa.
   - Dark Mode và Light Mode đạt chuẩn độ tương phản.
   - Không có console error nào phát sinh trong quá trình tương tác cơ bản.
