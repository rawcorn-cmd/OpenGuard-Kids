# Học Phần 1: Bản Chất Bài Toán & Triết Lý Thiết Kế Nhân Văn

> **Môn học:** Mạng Máy Tính (Computer Networks) — Khoa CNTT, HCMUS  
> **Chuyên đề:** Kiến trúc & Triết lý Thiết kế Nhân văn OpenGuard Kids  
> **Tài liệu tham khảo:** [docs/REQUIREMENTS.md](file:///home/cornar/Projects/OpenGuard-Kids/docs/REQUIREMENTS.md) | [docs/PROJECT_OVERVIEW.md](file:///home/cornar/Projects/OpenGuard-Kids/docs/PROJECT_OVERVIEW.md)  
> **File âm thanh đi kèm:** [audio_lessons/hoc_phan_01.mp3](file:///home/cornar/Projects/OpenGuard-Kids/audio_lessons/hoc_phan_01.mp3)

---

## 1. Bản Chất Bài Toán & Tôn Chỉ Cốt Lõi

OpenGuard Kids là ứng dụng hỗ trợ phụ huynh quản lý việc sử dụng máy tính của trẻ em trên nền tảng **Windows 10/11 (x64)**.

* **Tôn chỉ đề bài:** *"Công cụ đồng hành, không phải phần mềm theo dõi lén"*.
* **Bản chất kỹ thuật:** Hệ thống không phải là phần mềm gián điệp (Spyware). Chúng ta xây dựng một **hiệp ước minh bạch và thỏa thuận** giữa phụ huynh và trẻ em, thay thế cho sự giám sát độc đoán.

---

## 2. Sáu Nguyên Tắc Thiết Kế Nhân Văn Bắt Buộc (NT1 – NT6)

Mọi chức năng khi lập trình và trả lời vấn đáp đều phải chứng minh được việc tuân thủ 6 nguyên tắc này:

### 🔹 NT1 — Trẻ biết mình đang được hỗ trợ
* **Mô tả:** Trẻ luôn nhận thức được phần mềm đang vận hành để đồng hành cùng mình.
* **Hiện thực kỹ thuật:**
  * Biểu tượng khay hệ thống (System Tray Icon) **luôn luôn hiển thị** trên thanh Taskbar.
  * Hiển thị thông báo (Toast Notification) chào mừng khi máy tính khởi động.
  * **Cơ chế chống lén lút (Anti-Abuse Fail-Closed):** Tuyệt đối không có chế độ chạy ẩn (stealth mode). Nếu Tray UI gặp lỗi hoặc bị tắt, toàn bộ Agent phải tự dừng hoạt động.

### 🔹 NT2 — Tối thiểu dữ liệu (Data Minimization)
* **Mô tả:** Chỉ thu thập dữ liệu ở mức tối thiểu tuyệt đối cần thiết để quản lý thời gian.
* **Hiện thực kỹ thuật:** Chỉ ghi nhận đúng **4 trường siêu dữ liệu (Metadata)**:
  1. `process_name`: Tên file thực thi (ví dụ: `code.exe`, `chrome.exe`).
  2. `domain`: Tên miền trang web (ví dụ: `youtube.com`).
  3. `duration_seconds`: Tổng thời lượng sử dụng.
  4. `timestamp`: Dấu mốc thời gian ghi nhận.
* **Nghiêm cấm tuyệt đối:**
  * ❌ Không lưu đường dẫn URL đầy đủ (chỉ lưu domain).
  * ❌ Không chụp ảnh màn hình (No Screenshot).
  * ❌ Không ghi lại phím gõ (No Keylogger).
  * ❌ Không đọc tiêu đề cửa sổ (No Window Title).

### 🔹 NT3 — Trẻ có tiếng nói (Child Agency)
* **Mô tả:** Trẻ có quyền tương tác và phản hồi, không bị tước đoạt quyền giao tiếp.
* **Hiện thực kỹ thuật:**
  * Nút **"Xin thêm giờ"**: Cho phép trẻ gửi yêu cầu kèm lý do đến phụ huynh khi cần hoàn thành bài tập.
  * Nút **"Con nghĩ trang này bị chặn nhầm"**: Cho phép trẻ báo cáo tên miền giáo dục hoặc tài liệu bị hệ thống lọc sai.
  * Mọi yêu cầu được đồng bộ về máy chủ để phụ huynh phê duyệt hoặc từ chối rõ ràng.

### 🔹 NT4 — Mọi hành động chặn phải giải thích được
* **Mô tả:** Không bao giờ im lặng ngắt kết nối khiến trẻ bối rối hoặc hiểu nhầm máy bị hỏng mạng.
* **Hiện thực kỹ thuật:**
  * Khi chặn ứng dụng hoặc website, hiển thị ngay hộp thoại giải thích rõ: **Lý do bị chặn** và **Ai là người đặt quy định** (Cha mẹ hay Chính sách mặc định).
  * Nghiêm cấm việc giả mạo lỗi mạng như `ERR_CONNECTION_REFUSED` hay âm thầm tắt ứng dụng.

### 🔹 NT5 — Minh bạch hai chiều (Two-Way Transparency)
* **Mô tả:** Trẻ có quyền tiếp cận thông tin bình đẳng như cha mẹ.
* **Hiện thực kỹ thuật:**
  * Cung cấp màn hình **"Hôm nay em đã dùng gì"** trên máy của trẻ, hiển thị cùng dữ liệu và biểu đồ thời gian mà phụ huynh xem trên Dashboard.
  * Cung cấp màn hình xem **Audit Log** (Nhật ký thay đổi luật) để trẻ biết cha mẹ đã điều chỉnh những quy định nào.

### 🔹 NT6 — An toàn có ưu tiên tuyệt đối (Permanent Whitelist)
* **Mô tả:** Đảm bảo quyền được bảo vệ và cứu nạn trong mọi tình huống khẩn cấp.
* **Hiện thực kỹ thuật:**
  * Danh sách miễn chặn vĩnh viễn: Cổng thông tin trường học, **Tổng đài quốc gia bảo vệ trẻ em 111**, các dịch vụ cứu hộ khẩn cấp.
  * Khi hết giờ sử dụng và hệ thống khóa máy, tuyệt đối không được cản trở các cuộc gọi khẩn cấp của Windows.

---

## 3. Danh Mục Cấm Tuyệt Đối (Prohibited Catalog)

Trong suốt quá trình làm đồ án, nếu vi phạm một trong các điều sau sẽ bị trừ điểm rất nặng:
1. **Không xâm phạm nội dung riêng tư:** Không đọc nội dung tin nhắn, email, tài liệu cá nhân.
2. **Không kỹ thuật mã độc:** Không ẩn tiến trình, không ẩn dịch vụ Windows, không dùng kỹ thuật rootkit hoặc chống gỡ theo kiểu mã độc.
3. **Không gửi dữ liệu cho bên thứ ba:** Không gửi telemetry, nhật ký sử dụng ra các dịch vụ ngoài (Google Analytics, Firebase, AWS bên ngoài). Toàn bộ dữ liệu nằm trên Server của nhóm.

---

## 4. Ôn Luyện Phản Biện & Vấn Đáp (Defense Q&A)

> [!TIP]
> **Câu hỏi 1:** *"Tại sao nhóm không chụp ảnh màn hình hoặc hook bàn phím để cha mẹ biết con đang làm gì cho chính xác?"*  
> **Trả lời:** Đồ án tuân thủ nghiêm ngặt nguyên tắc **NT2 (Tối thiểu dữ liệu)**. OpenGuard Kids là công cụ đồng hành minh bạch, không phải phần mềm gián điệp. Việc chụp màn hình và ghi phím xâm phạm quyền riêng tư nghiêm trọng của trẻ và bị đề bài nghiêm cấm.

> [!TIP]
> **Câu hỏi 2:** *"Nếu một trang web học tập bị bộ lọc DNS chặn nhầm, hệ thống xử lý thế nào?"*  
> **Trả lời:** Hệ thống tuân thủ **NT3** và **NT4**: Trang web sẽ không bị báo lỗi mạng giả mạo mà hiển thị trang thông báo giải thích lý do, đồng thời cung cấp nút **"Con nghĩ trang này bị chặn nhầm"** để trẻ gửi phản hồi về máy chủ cho phụ huynh mở chặn.

