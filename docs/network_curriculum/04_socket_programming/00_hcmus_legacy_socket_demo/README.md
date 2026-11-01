# Tài Liệu Tham Khảo: Đồ Án Socket Cũ Của Khoa CNTT - HCMUS

> **Nguồn gốc:** Thư mục `/home/cornar/Downloads/Giáo trình/Mạng máy tính/Đồ án /Lap trinh socket`

### 1. Mô tả kiến trúc bài làm cũ của sinh viên khóa trước:
* Được viết bằng ngôn ngữ **C# (.NET Framework Windows Forms)**.
* Gồm 2 phần:
  * `Source/server/`: Máy chủ điều khiển từ xa.
  * `Source/client/`: Máy con cài trên máy mục tiêu.
* **Các chức năng đã hiện thực:**
  * Giám sát danh sách ứng dụng (`client.listApp.cs`).
  * Tắt tiến trình từ xa (`client.Kill.cs`).
  * Ghi phím (`Keylog.cs`) và Chụp ảnh màn hình (`picScreen.Png`).

### 2. Sự khác biệt cốt lõi với Đồ án OpenGuard Kids của chúng ta:
| Tiêu chí | Đồ án C# cũ | Đồ án OpenGuard Kids hiện tại |
| :--- | :--- | :--- |
| **Bản chất** | Phần mềm theo dõi lén / Gián điệp (Spyware/Trojan) | Công cụ đồng hành minh bạch (Parental Control) |
| **Chụp màn hình / Ghi phím** | Có (Vi phạm nghiêm trọng nguyên tắc NT2 của đề bài mới) | **TUYỆT ĐỐI CẤM** (Chỉ thu thập 4 trường siêu dữ liệu) |
| **Công nghệ** | C# WinForms cổ điển | Python 3.11+, FastAPI, Windows Service, DNS Proxy |
