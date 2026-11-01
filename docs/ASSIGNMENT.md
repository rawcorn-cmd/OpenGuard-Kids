# XÂY DỰNG ỨNG DỤNG HỖ TRỢ QUẢN LÝ VIỆC SỬ DỤNG MÁY TÍNH CỦA TRẺ EM

> *'Công cụ đồng hành, không phải phần mềm theo dõi lén'*


| Hạng mục | Nội dung |
| --- | --- |
| Hình thức | Đồ án môn học theo nhóm — 03 sinh viên/nhóm |
| Thời lượng | 07 tuần |
| Nền tảng | Agent trên Windows 10/11 (x64) |
| Công nghệ | Python 3.11+ · FastAPI · SQLite · SQLAlchemy · Uvicorn · pywin32/psutil |
| Trọng tâm đánh giá | Kỹ thuật lập trình hệ thống và mạng |
| Hình thức chấm | Sản phẩm + báo cáo  và vấn đáp cá nhân |



## 1. Triết lý thiết kế bắt buộc: minh bạch với trẻ


| # | Nguyên tắc | Biểu hiện bắt buộc trong sản phẩm |
| --- | --- | --- |
| NT1 | Trẻ biết mình đang được hỗ trợ | Biểu tượng khay hệ thống luôn hiển thị khi agent chạy; thông báo khi agent khởi động. |
| NT2 | Tối thiểu dữ liệu | Chỉ thu thập siêu dữ liệu sử dụng: tên ứng dụng, tên miền, thời lượng, dấu thời gian. [Không lưu URL đầy đủ, tiêu đề cửa sổ, nội dung gõ phím, ảnh chụp màn hình.] |
| NT3 | Trẻ có tiếng nói | Nút 'Xin thêm giờ' và 'Con nghĩ trang này bị chặn nhầm' gửi yêu cầu tới phụ huynh; mọi yêu cầu được ghi nhận và có phản hồi. |
| NT4 | Mọi hành động phải giải thích được | Khi chặn ứng dụng hoặc trang web, hiển thị lý do và ai đặt ra luật đó; không im lặng hoặc giả vờ lỗi mạng. |
| NT5 | Minh bạch hai chiều | Trẻ được xem cùng bộ báo cáo mà phụ huynh xem (giao diện thân thiện) và xem được nhật ký thay đổi luật của phụ huynh. |
| NT6 | An toàn có ưu tiên tuyệt đối | Danh sách miễn chặn vĩnh viễn: cổng thông tin trường học, Tổng đài quốc gia bảo vệ trẻ em 111, dịch vụ cứu hộ khẩn cấp. Việc khóa máy không bao giờ chặn cuộc gọi khẩn cấp của hệ điều hành... |



> [!CAUTION]
> **DANH MỤC CẤM Không hiện thực: (1) đọc nội dung tin nhắn, email, tài liệu; (2) ẩn tiến trình, ẩn dịch vụ, kỹ thuật rootkit hoặc chống gỡ theo kiểu mã độc; (3) gửi dữ liệu tới dịch vụ bên thứ ba; (4) thử nghiệm trên trẻ em thật hoặc trên máy của người khác mà không có sự đồng ý.**


## 2. Kiến trúc hệ thống


### 2.1. Sơ đồ tổng thể

```text
   MÁY CỦA TRẺ (Windows 10/11)                    MÁY CHỦ (LAN hoặc VPS lab)
 +---------------------------------+           +-------------------------------+
 |  OGK-Agent (Python)             |           |  OGK-Server (FastAPI)         |
 |  +---------------------------+  |  HTTPS    |  +-------------------------+  |
 |  | Windows Service (SYSTEM)  |  |  TLS1.2+  |  | /auth  /enroll  /policy |  |
 |  |  - Policy Enforcer        |<-+---------->+->| /events /commands       |  |
 |  |  - Screen-time Counter    |  | heartbeat |  | /reports /audit         |  |
 |  |  - App Controller         |  |   60s     |  +-------------------------+  |
 |  |  - DNS Proxy 127.0.0.1:53 |  |           |  |  SQLite + SQLAlchemy    |  |
 |  |  - Local cache (SQLite)   |  | WebSocket |  |  (policy, event, audit) |  |
 |  +---------------------------+  | lenh gap  |  +-------------------------+  |
 |  +---------------------------+  |           +---------------^---------------+
 |  | Tray UI (quyen user)      |  |                           | HTTPS
 |  |  - Dong ho con lai        |  |                  +--------+--------+
 |  |  - Nut 'Xin them gio'     |  |                  | Dashboard phu   |
 |  |  - Man hinh minh bach     |  |                  | huynh (web)     |
 |  +---------------------------+  |                  | Lich - Bao cao  |
 +---------------------------------+                  +-----------------+
```

^ named pipe / localhost                      Cau hinh tu xa, moi thiet bi


### 2.2. Thành phần và trách nhiệm


| Thành phần | Trách nhiệm chính | Ghi chú kỹ thuật |
| --- | --- | --- |
| OGK-Agent — Service | Áp dụng chính sách, đếm thời gian, chặn ứng dụng, phân giải DNS có lọc, đệm sự kiện khi mất mạng | Chạy dưới LocalSystem; dùng pywin32 (win32serviceutil), psutil; khởi động lại bằng Service Recovery Options của SCM |
| OGK-Agent — Tray UI | Giao diện dành cho trẻ: thời gian còn lại, lý do bị chặn, gửi yêu cầu | Chạy trong phiên người dùng; giao tiếp với service qua named pipe hoặc HTTP 127.0.0.1 có token cục bộ |
| OGK-Server | Xác thực phụ huynh, quản lý thiết bị/trẻ, phát hành chính sách, nhận sự kiện, tổng hợp báo cáo, ghi nhật ký kiểm toán | FastAPI + Uvicorn + TLS; SQLite với WAL; phân trang và giới hạn tần suất (rate limit) |
| Dashboard phụ huynh | Cấu hình từ xa: quota, lịch tuần, danh sách ứng dụng/miền, duyệt yêu cầu, xem báo cáo | Jinja2 + HTMX hoặc React nhẹ; phải dùng được trên trình duyệt điện thoại |
| Kho dữ liệu cục bộ | Bản sao chính sách gần nhất + hàng đợi sự kiện | SQLite trong ProgramData với ACL chỉ SYSTEM/Administrators được ghi |



### 2.3. Vòng đời và giao thức (bắt buộc đặc tả trong báo cáo)

Ghép đôi (enrollment): phụ huynh tạo mã ghép 8 ký tự có hạn 10 phút trên dashboard; agent gửi mã kèm device fingerprint; server trả device_id và cặp token (access ngắn hạn, refresh dài hạn). Đây chính là điểm ghi nhận sự đồng ý của cha mẹ theo Nghị định 13/2023.

Nhịp tim (heartbeat) 60 giây: agent gửi trạng thái, quota đã dùng, policy_version hiện có; server trả policy_version mới nhất và danh sách lệnh chờ. Lệch phiên bản thì agent gọi GET /policy.

Lệnh khẩn qua WebSocket: khóa ngay, mở khóa, cộng thêm 15 phút — yêu cầu độ trễ dưới 5 giây.

Chế độ ngoại tuyến: agent áp chính sách trong bộ nhớ đệm, tiếp tục đếm giờ, đệm sự kiện; khi có mạng thì đồng bộ theo lô, có khóa chống trùng (idempotency key) để sự kiện không bị đếm hai lần.

Chính sách hết hạn: nhóm phải tự quyết định fail-open hay fail-closed sau N ngày mất kết nối và bảo vệ lựa chọn đó khi vấn đáp.


## 3. Đặc tả chức năng

Ký hiệu: BẮT BUỘC = điều kiện cần để được chấm; NÊN CÓ = tính vào điểm khá/giỏi; CÓ THÌ TỐT = điểm thưởng, không bắt buộc.


### F1. Quản lý thời gian sử dụng


| Mức | Yêu cầu | Tiêu chí nghiệm thu |
| --- | --- | --- |
| BẮT BUỘC | Hạn mức theo ngày (ví dụ 90 phút), cấu hình riêng cho ngày thường và cuối tuần | Đặt quota 3 phút, hệ thống khóa đúng hạn |
| BẮT BUỘC | Lịch tuần cho phép/khóa với độ phân giải 30 phút (ma trận 7×48) | Ngoài khung giờ cho phép, máy bị khóa trong 5 giây |
| BẮT BUỘC | Đếm thời gian sử dụng thực: không tính khi máy khóa hoặc không có thao tác quá 5 phút | Sai số ≤ ±30 giây trên mỗi giờ so với đồng hồ bấm tay |
| BẮT BUỘC | Cảnh báo trước 10, 5 và 1 phút; có khoảng ân hạn 60 giây để trẻ lưu bài | Quan sát được trong demo D1 |
| BẮT BUỘC | Chống chỉnh đồng hồ hệ thống để kéo dài thời gian | Lùi đồng hồ 3 giờ: quota không được tăng, sự kiện bị ghi nhận |
| NÊN CÓ | Ngân sách theo nhóm ứng dụng (ví dụ: học tập không giới hạn, trò chơi 45 phút) | Hai bộ đếm độc lập hoạt động đúng |
| CÓ THÌ TỐT | Cơ chế thưởng giờ khi hoàn thành nhiệm vụ do phụ huynh giao | — |



### F2. Lọc và kiểm soát ứng dụng/website theo độ tuổi


| Mức | Yêu cầu | Tiêu chí nghiệm thu |
| --- | --- | --- |
| BẮT BUỘC | Kiểm soát ứng dụng theo danh sách cho phép/chặn, đối chiếu tên tiến trình kèm mã băm SHA-256 của tệp thực thi | Đổi tên notepad.exe thành game.exe vẫn bị nhận diện đúng |
| BẮT BUỘC | Khi chặn: kết thúc tiến trình và hiển thị cửa sổ giải thích lý do, không im lặng | Quan sát trong demo |
| BẮT BUỘC | Lọc website bằng DNS proxy cục bộ tại 127.0.0.1:53, hỗ trợ chặn theo tên miền và toàn bộ tên miền con | Chặn ≥ 95% trong bộ 50 tên miền kiểm thử; 0 dương tính giả trên 20 tên miền giáo dục |
| BẮT BUỘC | Hạ tầng phân loại theo 6 nhóm: giáo dục, giải trí, mạng xã hội, trò chơi, không phù hợp lứa tuổi, chưa phân loại — có chính sách mặc định cho trẻ 6–11 tuổi | Bảng phân loại nộp kèm, tối thiểu 200 mục |
| BẮT BUỘC | Cưỡng chế SafeSearch của công cụ tìm kiếm bằng bản ghi DNS (ví dụ ánh xạ sang forcesafesearch) | Kiểm chứng bằng nslookup và bằng trình duyệt |


Quy định về dữ liệu kiểm thử: bộ 50 tên miền phải dùng địa chỉ công khai, an toàn (ví dụ các miền example, miền của trường học, báo điện tử). Tuyệt đối không sử dụng, truy cập hay đính kèm tên miền có nội dung người lớn để 'thử nghiệm'. Nhóm nào nộp danh sách như vậy sẽ bị trừ điểm.


### F3. Ghi nhận và báo cáo hoạt động (minh bạch)

BẮT BUỘC — Lược đồ sự kiện chỉ gồm: ts, device_id, child_id, type, subject, duration_sec, policy_id. Trong đó type thuộc {app_start, app_stop, domain_query, blocked_app, blocked_domain, quota_warning, locked, unlock_request, override_granted}. Trường subject là tên ứng dụng hoặc tên miền cấp hai, không phải URL đầy đủ.

BẮT BUỘC — Dashboard phụ huynh: biểu đồ thời lượng theo ngày và theo tuần, top 10 ứng dụng, top 10 tên miền, số lần bị chặn, danh sách yêu cầu của trẻ.

BẮT BUỘC — Màn hình 'Hôm nay em đã dùng gì' cho trẻ, hiển thị cùng dữ liệu bằng ngôn ngữ đơn giản và hình ảnh minh họa.

BẮT BUỘC — Thời hạn lưu trữ 90 ngày, có tác vụ tự động xóa; nút 'Xóa toàn bộ dữ liệu của con tôi' xóa đồng thời trên server và trong bộ đệm của agent.

BẮT BUỘC — Tệp PRIVACY.md dạng bảng: mỗi trường dữ liệu ↔ mục đích ↔ thời hạn lưu ↔ ai xem được. Trường nào không giải thích được mục đích thì phải loại khỏi lược đồ.


### F4. Agent, bảng điều khiển và cấu hình từ xa

BẮT BUỘC — Mô hình dữ liệu hỗ trợ 1 phụ huynh : n trẻ : m thiết bị.

BẮT BUỘC — Thay đổi chính sách trên dashboard có hiệu lực trên máy trẻ trong vòng 60 giây; lệnh khẩn (khóa ngay, cộng giờ) trong vòng 5 giây.

BẮT BUỘC — Chính sách có đánh số phiên bản và ký hiệu toàn vẹn (HMAC hoặc chữ ký) để agent từ chối chính sách bị sửa đổi.

BẮT BUỘC — Nhật ký kiểm toán mọi thay đổi: ai, lúc nào, từ địa chỉ IP nào, giá trị cũ và mới. Trẻ được quyền xem nhật ký này (nguyên tắc NT5).


### F5. Bảo mật và quyền riêng tư


| Hạng mục | Yêu cầu tối thiểu |
| --- | --- |
| Xác thực phụ huynh | Băm mật khẩu bằng Argon2id hoặc scrypt (passlib); tối thiểu 10 ký tự; khóa tạm 15 phút sau 5 lần sai; giới hạn tần suất theo IP. TOTP hai yếu tố là điểm cộng. |
| Phiên làm việc | Cookie HttpOnly, Secure, SameSite=Lax; hạn phiên 12 giờ; đăng xuất hủy phiên phía máy chủ; chống CSRF cho mọi thao tác ghi. |
| Kênh truyền | TLS 1.2+ (có thể dùng CA tự ký trong môi trường phòng lab); agent ghim chứng chỉ (certificate pinning) và từ chối kết nối khi không khớp. |
| Định danh thiết bị | Token truy cập hạn 15 phút + refresh token; gắn với device_id; danh sách thu hồi khi gỡ thiết bị. |
| Dữ liệu lưu trữ | Mã hóa trường nhạy cảm bằng AES-GCM; khóa lấy từ biến môi trường hoặc DPAPI, không hardcode; băm bí mật thiết bị. |
| Phân quyền | Ba vai trò: parent, child-view, admin. Bắt buộc kiểm tra quyền sở hữu ở tầng truy vấn để chống IDOR (không chỉ ẩn nút trên giao diện). |
| Đặc quyền cục bộ | Tài khoản của trẻ không thuộc nhóm Administrators; thư mục cấu hình của agent đặt ACL chỉ SYSTEM và Administrators được ghi. |
| Chống lạm dụng | Sản phẩm không được có chế độ ẩn. Nếu không thể hiển thị biểu tượng, agent phải tự dừng. Tài liệu phải nêu rõ phạm vi sử dụng hợp pháp. |


Phụ lục. Bộ dữ liệu kiểm thử gợi ý


| Nhóm | Số lượng | Nguyên tắc chọn |
| --- | --- | --- |
| Giáo dục | 20 | Cổng thông tin trường học, thư viện số, từ điển, nền tảng học trực tuyến — dùng để kiểm tra dương tính giả |
| Giải trí phù hợp lứa tuổi | 10 | Kênh video thiếu nhi, trang truyện tranh giáo dục |
| Mạng xã hội | 8 | Kiểm tra chính sách mặc định cho nhóm 6–11 tuổi |
| Trò chơi trực tuyến | 7 | Kiểm tra ngân sách thời gian theo nhóm ứng dụng |
| Điểm cuối DoH | 5 | Kiểm tra khả năng phát hiện và xử lý DNS-over-HTTPS |
| Tên miền mô phỏng cần chặn | 10 | Bắt buộc dùng tên miền thử nghiệm trung tính hoặc miền do nhóm tự đăng ký; tuyệt đối không dùng nội dung người lớn thật |


— Hết —
