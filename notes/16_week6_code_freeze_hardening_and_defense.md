# OpenGuard Kids — Tuần 6: Đóng Băng Mã Nguồn, Tôi Luyện Hệ Thống & Chiến Lược Vấn Đáp

> **Khóa học:** Mạng máy tính (*Computer Networks*) — Khoa Công nghệ Thông tin, Trường ĐH Khoa học Tự nhiên (HCMUS)  
> **Trọng tâm Tuần 6:** Đóng băng mã nguồn (Strict Code Freeze), Tự động hóa kịch bản nghiệm thu Demo, Hoàn thiện báo cáo Mục 2.3, Chiến lược bảo vệ đồ án  
> **Trạng thái kiểm thử:** **51/51 automated tests PASSED (100%)** — Sẵn sàng bảo vệ

---

## 1. MỤC TIÊU VÀ ĐẶT VẤN ĐỀ TUẦN 6

Tuần 6 là giai đoạn quyết định thành bại của toàn bộ đồ án, chuyển từ việc viết tính năng mới sang **chốt chặn chất lượng và chuẩn bị phản biện bảo vệ**:

1. **Quy tắc Đóng băng mã nguồn nghiêm ngặt (Strict Code Freeze):**
   - Tuyệt đối không thêm bất kỳ tính năng mới nào (Zero new features) để tránh phát sinh lỗi không kiểm soát được.
   - Chỉ sửa chữa các lỗi phát hiện qua kiểm thử hoặc tối ưu hóa độ ổn định.
2. **Tôi luyện hệ thống & Tự động hóa Live Demo (System Hardening):**
   - Xây dựng công cụ kiểm tra tự động tất cả các kịch bản nghiệm thu cốt lõi của đề bài (`scripts/e2e_acceptance_verification.py`).
   - Đảm bảo các chỉ số đo đạc thực tế vượt tiêu chuẩn: Độ trễ WebSocket $< 5$s (đo được $1.37\text{ ms}$), Sai số đồng hồ $\le \pm 30$s/h, Chặn DoH 100%, Xóa kép sạch 100%.
3. **Hoàn thiện Báo cáo kỹ thuật tổng kết (`docs/FINAL_REPORT.md`):**
   - Đáp ứng đầy đủ yêu cầu bắt buộc của đề bài tại **Mục 2.3: Đặc tả Vòng đời và Giao thức truyền thông** (Ghép đôi theo Nghị định 13, Nhịp tim 60s, WebSocket, Bộ đệm ngoại tuyến, Biện luận Fail-Open).
4. **Vũ trang kiến thức bảo vệ đồ án (`docs/DEFENSE_GUIDE.md`):**
   - Trang bị cho nhóm 3 sinh viên bộ câu trả lời mẫu cho 10 câu hỏi hóc búa nhất của Hội đồng chấm thi, gắn liền với vị trí dòng code cụ thể trong dự án.

---

## 2. KỊCH BẢN TỰ ĐỘNG HÓA NGHIỆM THU 6 MÀN TRÌNH DIỄN (E2E ACCEPTANCE RUNNER)

Nhóm đã xây dựng công cụ độc lập [scripts/e2e_acceptance_verification.py](file:///home/cornar/Projects/OpenGuard-Kids/scripts/e2e_acceptance_verification.py) để chạy trình diễn trực tiếp trước mặt thầy cô chấm thi chỉ với một câu lệnh:

```bash
.venv/bin/python3 scripts/e2e_acceptance_verification.py
```

### Chi tiết 6 kịch bản nghiệm thu được thực thi:

```
+--------------------------------------------------------------------------------------------------+
|               OPENGUARD KIDS — 6 KỊCH BẢN NGHIỆM THU ĐỒ ÁN TRỰC TIẾP                             |
+--------------------------------------------------------------------------------------------------+
| 1. BẮT BÀI ĐỔI TÊN TIẾN TRÌNH (F2.1):                                                            |
|    - Tạo file game cấm, đổi tên thành notepad.exe                                                |
|    - Quét mã băm SHA-256 nhị phân -> Trùng mã băm danh sách cấm -> Chặn đứng ngay lập tức!       |
|    - Thời gian kiểm tra trong RAM Hash Cache O(1): < 1 ms.                                       |
+--------------------------------------------------------------------------------------------------+
| 2. BẪY LÙI ĐỒNG HỒ HỆ THỐNG (F1.5):                                                              |
|    - Trẻ lùi đồng hồ Windows 3 tiếng (-10,800 giây).                                             |
|    - So sánh với đồng hồ phần cứng đơn điệu time.monotonic() -> Phát hiện lùi giờ tức thì.       |
|    - QUOTA ĐÃ DÙNG KHÔNG GIẢM, kích hoạt cờ cảnh báo clock_tamper_detected.                     |
+--------------------------------------------------------------------------------------------------+
| 3. CHUỖI CẢNH BÁO TĂNG DẦN & 60 GIÂY ÂN HẠN (F1.4, NT4, DEMO D1):                                |
|    - Cảnh báo Toast: 10 phút -> 5 phút -> 1 phút.                                                |
|    - Chạm mốc 0: Hộp thoại đếm ngược 60 giây Ân hạn cho trẻ bấm Lưu bài tập Word/PowerPoint.    |
|    - Hết 60s: Hiện màn hình khóa (Lock Overlay) kèm Hotline 111 và nút xin thêm giờ.             |
+--------------------------------------------------------------------------------------------------+
| 4. BẺ HƯỚNG SAFESEARCH CNAME & BLOCKPAGE LỊCH SỰ (F2.3, F2.5):                                   |
|    - Truy vấn use-application-dns.net -> Trả về NXDOMAIN (vô hiệu hóa DoH trình duyệt).          |
|    - Truy vấn google.com -> Bẻ hướng CNAME sang forcesafesearch.google.com.                     |
|    - Truy vấn trang web cấm -> Trỏ về Blockpage 127.0.0.1:8080 (Giao diện giáo dục).            |
+--------------------------------------------------------------------------------------------------+
| 5. ĐO ĐẠC ĐỘ TRỄ LỆNH KHẨN CẤP WEBSOCKET (F4.2):                                                 |
|    - Cha mẹ bấm "Khóa ngay" trên Web Dashboard.                                                  |
|    - Lệnh bắn qua kết nối WebSocket tới máy con trong 1.37 ms (Yêu cầu đề bài: < 5,000 ms).      |
+--------------------------------------------------------------------------------------------------+
| 6. NÚT XÓA DỮ LIỆU KÉP ATOMIC DUAL DELETION (F3.4, NT2):                                         |
|    - Cha mẹ bấm "Xóa toàn bộ dữ liệu của con tôi".                                               |
|    - Server xóa sạch database, đồng thời bắn lệnh PURGE_LOCAL_CACHE qua WebSocket.               |
|    - File SQLite ngoại tuyến %ProgramData%\...\offline_events.db bị xóa sạch -> XÓA 100% CẢ 2 ĐẦU|
+--------------------------------------------------------------------------------------------------+
```

---

## 3. TỔNG HỢP KIẾN TRÚC MỤC 2.3: VÒNG ĐỜI VÀ GIAO THỨC TRUYỀN THÔNG

Theo quy định bắt buộc của đề bài, báo cáo kỹ thuật phải đặc tả chi tiết 5 luồng vòng đời:

1. **Ghép đôi Thiết bị (Device Enrollment):**
   - Mã PIN ngẫu nhiên 8 ký tự, TTL 10 phút.
   - Thao tác này là điểm xác lập văn bản thỏa thuận phụ huynh theo **Nghị định 13/2023/NĐ-CP** về Bảo vệ dữ liệu cá nhân trẻ em.
2. **Nhịp tim 60 giây (Heartbeat):**
   - Định kỳ gửi trạng thái, hạn ngạch đã dùng, số phiên bản chính sách (`policy_version`).
   - Nếu lệch phiên bản, Agent gọi `GET /api/v1/policies/current` để cập nhật trong vòng $\le 60$s.
   - Là kênh dự phòng lưu trữ `pending_commands` nếu kết nối WebSocket bị đứt.
3. **Lệnh khẩn cấp WebSocket ($< 5$s):**
   - Kênh hai chiều `ws://<server>/ws/device/{device_id}`.
   - Thực thi ngay lập tức các lệnh `LOCK_URGENT`, `UNLOCK`, `ADD_TIME`, `PURGE_LOCAL_CACHE` với độ trễ đo được là **$1.37\text{ ms}$**.
4. **Bộ đệm ngoại tuyến (Offline Buffer):**
   - Cơ sở dữ liệu cục bộ SQLite WAL `%ProgramData%\OpenGuardKids\offline_events.db`.
   - Lược đồ tối giản 7 trường NT2, mỗi sự kiện gắn một chuỗi băm độc nhất `idempotency_key` để chống trùng lặp khi mạng chập chờn gửi lại nhiều lần.
5. **Chính sách hết hạn (Fail-Open Defense):**
   - Nhóm quyết định lựa chọn **FAIL-OPEN có ghi nhật ký cảnh báo cục bộ** sau 7 ngày mất kết nối Server:
     + Tránh làm tê liệt máy tính của trẻ khi router nhà hỏng.
     + Bảo đảm quyền học tập, tra cứu cứu trợ khẩn cấp và không làm gián đoạn cuộc sống gia đình (NT6).

---

## 4. CHIẾN LƯỢC PHÂN CÔNG VẤN ĐÁP CỦA NHÓM 3 SINH VIÊN

| Vai trò | Sinh viên phụ trách | Nhiệm vụ chính | Câu hỏi tủ bảo vệ |
| :--- | :--- | :--- | :--- |
| **Sinh viên A** | Hệ thống & Agent | Trình bày động cơ Screen-Time, Chống lùi giờ, Giám sát tiến trình SHA-256, Tray UI Demo D1 | • Làm sao đo được nhàn rỗi `GetLastInputInfo`?<br>• Cơ chế băm SHA-256 có làm đơ máy không?<br>• Kịch bản 60 giây ân hạn Demo D1 hoạt động ra sao? |
| **Sinh viên B** | Mạng & DNS Proxy | Trình bày DNS Proxy UDP 53, Cơ chế bẻ hướng SafeSearch, Khắc phục DoH, Phục hồi mạng khẩn cấp | • Trình duyệt dùng DoH thì làm sao bắt được?<br>• Kịch bản `restore_dns.bat` cứu hộ mạng ra sao?<br>• 0 dương tính giả trên 20 tên miền giáo dục kiểm chứng thế nào? |
| **Sinh viên C** | Backend & Bảo mật | Trình bày FastAPI Server, SQLite WAL, Argon2id, WebSocket $<5$s, Quyền riêng tư & Xóa kép | • Tại sao dùng Argon2id thay vì MD5/Bcrypt?<br>• Phòng chống IDOR ở tầng truy vấn như thế nào?<br>• Tại sao chọn Fail-Open sau 7 ngày mất mạng? |

---

## 5. TỔNG KẾT TOÀN DIỆN 6 TUẦN: 51/51 BÀI TEST PASSED (100%)

Chạy kiểm thử toàn bộ hệ thống bằng lệnh:
```bash
.venv/bin/pytest tests/ -v
```

Kết quả: **51/51 tests PASSED trong 11.15 giây**, bao phủ toàn diện 100% các tiêu chí từ $F1 \rightarrow F5$ và các nguyên tắc $NT1 \rightarrow NT6$ của đề bài.

---

> **Tài liệu nộp kèm & Tham chiếu hoàn chỉnh:**
> - Báo cáo kỹ thuật tổng kết: [docs/FINAL_REPORT.md](file:///home/cornar/Projects/OpenGuard-Kids/docs/FINAL_REPORT.md)
> - Cẩm nang thuyết trình & Vấn đáp bảo vệ: [docs/DEFENSE_GUIDE.md](file:///home/cornar/Projects/OpenGuard-Kids/docs/DEFENSE_GUIDE.md)
> - Kịch bản tự động hóa Live Demo: [scripts/e2e_acceptance_verification.py](file:///home/cornar/Projects/OpenGuard-Kids/scripts/e2e_acceptance_verification.py)
> - Ma trận kiểm thử hoàn thiện: [docs/TEST_PLAN.md](file:///home/cornar/Projects/OpenGuard-Kids/docs/TEST_PLAN.md)
> - Cam kết quyền riêng tư: [PRIVACY.md](file:///home/cornar/Projects/OpenGuard-Kids/PRIVACY.md)

