---
name: tauri-desktop-testing
description: Techniques and procedures for testing Tauri 2 desktop applications on Linux, IPC commands, single-instance socket handling, and native dialogs.
---

# Tauri Desktop Testing Skill

## Mục đích
Đặc tả phương pháp kiểm thử cho ứng dụng desktop Tauri 2 trên Linux Mint (WebKit2GTK, Wayland/X11), cầu nối IPC Rust-JS, và cơ chế tích hợp desktop.

## Các khía cạnh kiểm thử bắt buộc

### 1. IPC Commands & Error Handling
- Kiểm tra toàn bộ invoke commands (`get_cli_open_file`, `read_ncanvas_file`, `write_ncanvas_file`, `open_ncanvas_dialog`, `save_ncanvas_dialog`).
- Đảm bảo khi thao tác file thất bại (thiếu quyền, đường dẫn không tồn tại), Rust backend trả về `Err(String)` rõ ràng chứ không làm ứng dụng sập (panic).

### 2. Atomic File Persistence (`.ncanvas`)
- Ghi tệp phải áp dụng mẫu atomic: ghi ra file tạm `.tmp.<pid>` -> `sync_all()` -> `fs::rename()`.
- Kiểm thử unit test Rust trực tiếp xác minh dữ liệu không bị hỏng nếu quá trình ghi bị ngắt quãng.

### 3. Single-Instance & Socket IPC
- Kiểm tra socket Unix domain socket:
  - Khi mở phiên bản thứ hai, lệnh `OPEN:<path>` hoặc `FOCUS:` phải được truyền tới tiến trình chính.
  - Tiến trình thứ hai phải tự thoát ngay lập tức với mã 0.
  - Cửa sổ tiến trình chính phải được unminimize, show và set focus.

### 4. Linux Desktop Integration
- File desktop shortcut: `/usr/share/applications/notecanvas.desktop` hoặc `~/.local/share/applications/notecanvas.desktop`.
- MIME type association: `application/x-notecanvas` cho đuôi `.ncanvas`.
- File icon: `notecanvas.png` trong hicolor theme.
