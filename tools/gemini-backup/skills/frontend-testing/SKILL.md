---
name: frontend-testing
description: Guidelines, patterns, and best practices for testing Svelte 5 runes, stores, DOM interactions, and CSS layouts.
---

# Frontend Testing Skill

## Mục đích
Cung cấp hướng dẫn và mẫu chuẩn để kiểm thử giao diện frontend xây dựng bằng Svelte 5, TypeScript, và CSS hiện đại.

## Quy tắc kiểm thử Svelte 5
1. **Rune State Reactivity:**
   - Trong Svelte 5, các biến `$state` cần được kiểm tra trong môi trường hỗ trợ (file `.svelte.ts` hoặc thông qua component test harness).
   - Đảm bảo các side effect của `$derived` và `$effect` được kích hoạt đầy đủ trước khi assert.
2. **Tránh kiểm tra Implementation Details:**
   - Không assert vào tên biến private hoặc phương thức nội bộ nếu không cần thiết.
   - Tập trung assert vào:
     - Giá trị trả về của Store / State.
     - Trạng thái DOM hiển thị (text, attribute, disabled, aria-*).
     - Sự kiện phát ra (CustomEvent, click, input, keydown).
3. **Môi trường Vitest Polyfills:**
   - Đảm bảo các API trình duyệt thiếu vắng trong Node (như `localStorage`, `matchMedia`, `ResizeObserver`) được polyfill nhất quán và reset trong `beforeEach()`.
4. **Kiểm tra Layout & Responsive:**
   - Sử dụng kiểm thử thực tế với Playwright để xác minh các trạng thái responsive (1280x800, 1600x900, 900x600, 768x500).
   - Đảm bảo thanh công cụ vẽ, header, và sidebar không bị tràn hoặc che khuất ở kích thước nhỏ.
