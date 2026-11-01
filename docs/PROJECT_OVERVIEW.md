# OpenGuard Kids — Tổng Quan Dự Án & Sổ Tay Kiến Trúc Kỹ Thuật

> **Đồ án môn học:** Mạng Máy Tính (Computer Networks) — Khoa CNTT, Trường Đại học Khoa học Tự nhiên, ĐHQG-HCM (HCMUS)  
> **Tài liệu tham khảo & ôn luyện vấn đáp:** Cung cấp bức tranh toàn cảnh về triết lý thiết kế, kiến trúc mạng và hệ thống Windows/Server, vai trò kỹ thuật chi tiết của từng công cụ/thư viện, và sự phân công nhiệm vụ cho nhóm 3 sinh viên.  
> **Nguồn gốc đề bài:** [docs/ASSIGNMENT.docx](file:///home/cornar/Projects/OpenGuard-Kids/docs/ASSIGNMENT.docx) — *Đồ án môn học: Xây dựng ứng dụng hỗ trợ quản lý việc sử dụng máy tính của trẻ em ("Công cụ đồng hành, không phải phần mềm theo dõi lén")*, Khoa CNTT, HCMUS.

---

## 1. Bản Chất Dự Án & Triết Lý Thiết Kế Bắt Buộc

### 1.1 Mục tiêu và Tôn chỉ cốt lõi
OpenGuard Kids là ứng dụng hỗ trợ phụ huynh quản lý việc sử dụng máy tính của trẻ em trên nền tảng **Windows 10/11 (x64)**.
* **Tôn chỉ đề bài:** *"Công cụ đồng hành, không phải phần mềm theo dõi lén"*.
* Hệ thống được xây dựng trên tinh thần thỏa thuận minh bạch giữa phụ huynh và trẻ em, tuyệt đối **không phải phần mềm gián điệp (spyware)**.

### 1.2 Sáu nguyên tắc thiết kế nhân văn bắt buộc (NT1 – NT6)
Mọi chức năng khi xây dựng và trả lời vấn đáp đều phải chứng minh được việc tuân thủ 6 nguyên tắc này:

| Mã | Nguyên tắc | Biểu hiện cụ thể trong sản phẩm | Ý nghĩa bảo vệ đồ án |
| :--- | :--- | :--- | :--- |
| **NT1** | **Trẻ biết mình đang được hỗ trợ** | Biểu tượng khay hệ thống (System Tray Icon) **luôn luôn hiển thị** khi Agent chạy. Có thông báo chào trẻ khi hệ điều hành khởi động. Tuyệt đối không có chế độ chạy ẩn (stealth mode). Nếu Tray UI bị lỗi/tắt, Agent phải tự dừng để tránh chạy ngầm. | Thể hiện tính minh bạch, không theo dõi lén lút. |
| **NT2** | **Tối thiểu dữ liệu (Data Minimization)** | Chỉ thu thập **siêu dữ liệu** (Metadata) sử dụng: Tên ứng dụng (`process_name`), tên miền (`domain`), thời lượng (`duration_seconds`), dấu thời gian (`timestamp`).<br>❌ **Nghiêm cấm:** Không lưu URL đầy đủ, không lưu tiêu đề cửa sổ, không ghi phím (keylogger), không chụp màn hình. | Đảm bảo quyền riêng tư tối thượng của trẻ em. |
| **NT3** | **Trẻ có tiếng nói (Child Agency)** | Cung cấp 2 nút tương tác trực tiếp trên giao diện của trẻ:<br>1. `"Xin thêm giờ"` (ví dụ: làm bài tập nhóm quá giờ).<br>2. `"Con nghĩ trang này bị chặn nhầm"` (báo cáo tên miền giáo dục bị lọc sai).<br>Mọi yêu cầu đều được gửi về máy chủ để phụ huynh phê duyệt/từ chối và có phản hồi rõ ràng. | Biến việc kiểm soát thành sự lắng nghe và thỏa hiệp. |
| **NT4** | **Mọi hành động phải giải thích được** | Khi ứng dụng hoặc trang web bị chặn, hệ thống phải hiển thị màn hình thông báo giải thích rõ: **Lý do bị chặn** và **Ai là người đặt ra luật** (Cha mẹ hay Chính sách hệ thống). Không được im lặng tắt app hay giả vờ lỗi mạng/mất kết nối. | Tôn trọng nhận thức của trẻ, giúp trẻ hiểu lý do. |
| **NT5** | **Minh bạch hai chiều** | Trẻ được quyền xem cùng bộ báo cáo sử dụng mà cha mẹ xem (thông qua giao diện thân thiện với trẻ em). Đồng thời trẻ xem được nhật ký kiểm toán (Audit Log) ghi nhận các lần cha mẹ thay đổi luật. | Tạo sự công bằng và tin cậy giữa hai thế hệ. |
| **NT6** | **An toàn có ưu tiên tuyệt đối (Permanent Whitelist)** | Danh sách an toàn vĩnh viễn không bao giờ được phép chặn: Cổng thông tin trường học, **Tổng đài quốc gia bảo vệ trẻ em 111**, các dịch vụ cấp cứu/khẩn cấp. Việc khóa máy khi hết giờ tuyệt đối không chặn cuộc gọi khẩn cấp của Windows. | Đảm bảo tính mạng và sự trợ giúp khẩn cấp cho trẻ. |

### 1.3 Danh mục cấm tuyệt đối (Prohibited Catalog)
1. **Không đọc nội dung:** Tin nhắn riêng tư, email, tài liệu cá nhân.
2. **Không kỹ thuật độc hại:** Ẩn tiến trình, ẩn Windows service, kỹ thuật rootkit, hoặc chống gỡ theo kiểu mã độc.
3. **Không gửi dữ liệu cho bên thứ ba:** Không tích hợp SDK quảng cáo, theo dõi của bên ngoài.
4. **Không thử nghiệm trên trẻ em thật:** Hoặc máy tính người khác mà chưa có sự đồng ý.

---

## 2. Kiến Trúc Hệ Thống & Bài Toán Kỹ Thuật Trên Windows

### 2.1 Sơ đồ phân tầng tổng thể

```
   [ MÁY CỦA TRẺ - WINDOWS 10/11 x64 ]                         [ MÁY CHỦ QUẢN LÝ (SERVER) ]
 +----------------------------------------+                  +--------------------------------+
 | OGK-Agent: Session 0 (LocalSystem)     |                  | OGK-Server (FastAPI + Uvicorn) |
 |  - Screen-Time Engine (Active/Idle)    |   HTTPS (Sync)   |  - API Xác thực & Cấp Policy   |
 |  - App Controller (psutil + SHA-256)   |<---------------->|  - API Nhận Sự kiện (Metadata) |
 |  - DNS Proxy (dnslib @ 127.0.0.1:53)   |  Heartbeat (60s) |  - WebSocket Dispatcher (< 5s) |
 |  - Local SQLite WAL (Offline Cache)    |                  |  - SQLite Database (WAL Mode)  |
 +----------------------------------------+                  +----------------+---------------+
                     |                                                        |
     Local IPC       | (HTTP 127.0.0.1 + Token bí mật                         | HTTPS
     (Nội bộ máy)    |  trong %ProgramData%)                                  v
                     v                                       +--------------------------------+
 +----------------------------------------+                  | Parent Web Dashboard           |
 | OGK-Agent: Session 1 (User Desktop)    |                  | (Jinja2 + HTMX)                |
 |  - Biểu tượng khay (Taskbar Icon)      |                  |  - Quản lý lịch tuần 7x48      |
 |  - Đồng hồ đếm lùi thời gian còn lại   |                  |  - Biểu đồ thời gian dùng máy  |
 |  - Hộp thoại cảnh báo (10m, 5m, 1m)    |                  |  - Hộp thư duyệt đơn xin giờ   |
 |  - Nút 'Xin thêm giờ' & 'Báo nhầm'     |                  |  - Lịch sử kiểm toán (Audit)   |
 +----------------------------------------+                  +--------------------------------+
```

### 2.2 Vấn đề cốt lõi: Tại sao phải tách làm Session 0 (Service) và Session 1 (Tray UI)?
Đây là **câu hỏi trọng tâm bảo vệ đồ án về lập trình hệ thống Windows**:
1. **Tại sao phải chạy Windows Service dưới quyền `NT AUTHORITY\LocalSystem`?**
   * Nếu phần mềm chỉ là một ứng dụng `.exe` thông thường trong phiên làm việc của trẻ (Session 1), trẻ có thể mở Task Manager và bấm **End Task** để vô hiệu hóa toàn bộ luật kiểm soát.
   * Để lắng nghe được cổng mạng đặc quyền **UDP Port 53 (DNS)** trên Windows, tiến trình bắt buộc phải có đặc quyền quản trị viên hệ thống.
   * Do đó, nhân lõi (chặn ứng dụng, lọc DNS, đếm giờ) phải nằm trong Windows Service chạy ngầm.
2. **Tại sao Service không thể tự vẽ giao diện hay hiện icon khay? (Rào cản Session 0 Isolation)**
   * Từ thời Windows Vista, Microsoft đã cô lập hoàn toàn Session 0 khỏi các phiên tương tác người dùng (Session 1, 2...) để ngăn chặn kỹ thuật tấn công mã độc chiếm quyền (Shatter Attack).
   * **Một tiến trình chạy trong Session 0 hoàn toàn không thể tương tác trực tiếp với màn hình desktop của người dùng.**
3. **Giải pháp kiến trúc:**
   * Tách hệ thống trên máy trẻ thành **2 tiến trình**:
     * **OGK Service (Session 0):** Thực thi luật pháp hệ thống, chạy ngầm liên tục dưới quyền SYSTEM.
     * **OGK Tray UI (Session 1):** Chạy trong phiên đăng nhập của người dùng thông thường, phụ trách hiển thị đồng hồ, icon khay và các nút bấm tương tác cho trẻ.
   * **Cơ chế IPC (Inter-Process Communication):** Hai tiến trình giao tiếp nội bộ qua Loopback HTTP (`http://127.0.0.1:<port>`). Để chống các ứng dụng độc hại khác mạo danh gửi lệnh nội bộ, khi Service khởi động sẽ sinh một chuỗi **Bearer Token ngẫu nhiên** ghi vào file `%ProgramData%\OpenGuardKids\ipc_secret.token` (phân quyền NTFS chỉ SYSTEM và Administrator mới đọc được). Tray UI đọc token này để xác thực khi gọi API nội bộ tới Service.

---

## 3. Bảng Tra Cứu Công Cụ, Thư Viện & Vai Trò Kỹ Thuật

| Công cụ / Thư viện | Phạm vi áp dụng | Chức năng cụ thể trong hệ thống OpenGuard Kids | Tại sao lại chọn nó? (Lý do bảo vệ đồ án) |
| :--- | :--- | :--- | :--- |
| **Python 3.11+** | Toàn bộ dự án | Ngôn ngữ phát triển thống nhất cho toàn bộ Server, Windows Agent, và Tooling. | Đa năng, xử lý chuỗi và mạng bất đồng bộ rất mạnh, dễ bảo trì và rút ngắn thời gian phát triển trong khuôn khổ 6–7 tuần. |
| **FastAPI** | Máy chủ (Server) | Xây dựng RESTful API cho Agent đồng bộ dữ liệu, cấp chính sách, và quản lý WebSocket hai chiều. | Tốc độ xử lý hàng đầu (nhờ Starlette và Pydantic), hỗ trợ `async/await` bản địa, tự động sinh tài liệu Swagger/OpenAPI giúp nhóm test nhanh các API. |
| **Uvicorn** | Máy chủ (Server) | Máy chủ ứng dụng ASGI (Asynchronous Server Gateway Interface) vận hành FastAPI. | Chuẩn công nghiệp cho Python Async, duy trì hiệu năng cao cho các kết nối giữ dài (Long-lived WebSocket connections). |
| **SQLAlchemy** | Máy chủ & Agent | Quản lý quan hệ dữ liệu (ORM - Object Relational Mapping). | Lập trình hướng đối tượng an toàn, tự động phòng chống lỗi **SQL Injection**, trừu tượng hóa các bảng dữ liệu: Phụ huynh, Trẻ em, Thiết bị, Chính sách, Sự kiện. |
| **SQLite (WAL Mode)** | Máy chủ & Agent | Cơ sở dữ liệu chính tại Server và cơ sở dữ liệu đệm sự kiện ngoại tuyến (Offline Buffer) tại Agent. | Gọn nhẹ, lưu trong 1 file, không phụ thuộc cài đặt máy chủ DB bên ngoài (như MySQL/PostgreSQL). Kích hoạt **WAL (Write-Ahead Logging)** cho phép đọc dữ liệu đồng thời trong khi đang ghi mà không bị khóa (lock) cơ sở dữ liệu. |
| **Pydantic** | Máy chủ & Common | Xác thực (validation) và chuyển đổi (serialization) dữ liệu JSON đầu vào/đầu ra. | Bắt lỗi dữ liệu ngay từ cổng vào, ngăn chặn dữ liệu sai cấu trúc hoặc vượt quá chuẩn siêu dữ liệu (Metadata 7 trường bắt buộc). |
| **Argon2id (`argon2-cffi`)** | Máy chủ (Server) | Băm mật khẩu (Password Hashing) cho tài khoản phụ huynh. | Đạt giải nhất cuộc thi *Password Hashing Competition*; vượt trội hoàn toàn so với MD5/SHA256, kháng triệt để tấn công vét cạn bằng GPU/ASIC. |
| **pywin32** | Windows Agent | Cầu nối gọi Win32 Native API của hệ điều hành Windows. | Cung cấp `win32serviceutil` để đăng ký Windows Service chính thống vào Service Control Manager (SCM); gọi `GetLastInputInfo` để phát hiện máy nhàn rỗi (idle), phát hiện màn hình khóa (`WTSRegisterSessionNotification`). |
| **psutil** | Windows Agent | Giám sát danh sách các tiến trình (Processes) đang chạy trên Windows. | Lấy thông tin tiến trình nhẹ nhàng, hỗ trợ lấy đường dẫn nhị phân để tính mã băm **SHA-256** (ngăn chặn trẻ gian lận bằng cách đổi tên `game.exe` thành `notepad.exe`). |
| **dnslib** | Windows Agent | Phân tích và đóng gói các gói tin DNS UDP nhị phân ở tầng mạng. | Dựng DNS Proxy nhẹ tại `127.0.0.1:53` thuần Python mà không cần cài thêm Bind9 hay CoreDNS; chặn tên miền đen theo regex/wildcard và viết lại bản ghi CNAME để kích hoạt Google/Bing SafeSearch. |
| **Jinja2 + HTMX** | Web Dashboard | Xây dựng giao diện web cho phụ huynh điều khiển và xem báo cáo. | Tạo trải nghiệm mượt mà (cập nhật bảng, bật/tắt luật không tải lại trang - Single Page Application feel) hoàn toàn trên nền server-side rendering, **không cần phải gánh thêm độ phức tạp của Node.js, Webpack hay React/Vue**. |
| **HTTPX** | Agent & Tests | Thư viện HTTP Client hiện đại (hỗ trợ cả async và sync). | Agent dùng để gửi nhịp tim (Heartbeat 60s) và gửi sự kiện lên Server; đồng thời dùng để viết các bài kiểm thử tích hợp (Integration Tests) tự động. |
| **Pytest** | Toàn bộ dự án | Khung kiểm thử tự động (Unit test, Integration test, Contract test). | Tiêu chuẩn kiểm thử số 1 trong Python, quản lý Fixture tốt, đo độ phủ (Coverage) để phục vụ chấm điểm đồ án. |

---

## 4. Phân Công Trách Nhiệm Trong Nhóm 3 Sinh Viên

Mô hình phân rã công việc song song, độc lập giao tiếp qua hợp đồng API rõ ràng:

### Sinh viên A: Chuyên trách Hệ thống Windows & Desktop Agent
* **Công cụ chính:** `pywin32`, `psutil`, `Pystray/Tkinter`, `hashlib`.
* **Trách nhiệm:**
  1. Xây dựng lõi Windows Service (Session 0) và Tray UI (Session 1).
  2. Xây dựng kênh IPC nội bộ (Loopback HTTP + Token bí mật).
  3. Xây dựng bộ đếm thời gian màn hình (tạm dừng khi máy nhàn rỗi $>5$ phút, phát hiện gian lận lùi đồng hồ hệ thống).
  4. Quét tiến trình và chặn game/ứng dụng cấm theo mã băm SHA-256.
  5. Thiết kế giao diện minh bạch cho trẻ (Đồng hồ đếm lùi, nút *Xin thêm giờ*, bảng *Hôm nay em đã dùng gì*).

### Sinh viên B: Chuyên trách Mạng, Lọc DNS & Tập Dữ Liệu
* **Công cụ chính:** `dnslib`, `socket`, `netsh`, JSON datasets.
* **Trách nhiệm:**
  1. Dựng DNS Proxy cục bộ trên cổng UDP 53; xử lý chuyển tiếp (forwarding) DNS ra Internet.
  2. Hiện thực tính năng ép bật SafeSearch cho Google và Bing.
  3. Viết script khẩn cấp khôi phục mạng (`scripts/restore_dns.bat`) đảm bảo tuyệt đối không làm mất mạng máy tính khi Agent gặp sự cố.
  4. Thu thập và hoàn thiện bộ dữ liệu phân loại $\ge 200$ tên miền/ứng dụng (`data/classification_dataset.json`).
  5. Xây dựng bộ test suite 50 tên miền kiểm tra tỷ lệ chặn $\ge 95\%$ và $0\%$ chặn nhầm trang giáo dục.

### Sinh viên C: Chuyên trách Máy Chủ API & Web Dashboard
* **Công cụ chính:** `FastAPI`, `Uvicorn`, `SQLAlchemy`, `SQLite WAL`, `Argon2id`, `HTMX`.
* **Trách nhiệm:**
  1. Thiết kế cơ sở dữ liệu quan hệ và chính sách dọn dẹp dữ liệu tự động sau 90 ngày (Auto-purge).
  2. Hiện thực hệ thống xác thực phụ huynh bằng Argon2id và mã ghép đôi thiết bị (Pairing Code 8 ký tự).
  3. Xây dựng các API RESTful: Nhận Heartbeat 60s, tiếp nhận sự kiện sử dụng có chống trùng lặp (Idempotency).
  4. Triển khai kênh WebSocket gửi lệnh khẩn cấp (Khóa ngay, Mở khóa, Thêm 15 phút) với thời gian phản hồi $<5$ giây.
  5. Phát triển giao diện Web Dashboard thân thiện trên di động (Ma trận lịch tuần 7x48, biểu đồ Top 10 ứng dụng/web, hộp thư duyệt đơn của con).

---

## 5. Các Câu Hỏi Vấn Đáp Thường Gặp (Defense FAQ)

> [!TIP]
> **Q1: Tại sao không dùng Hook bàn phím hoặc chụp ảnh màn hình để biết trẻ đang làm gì?**  
> **Trả lời:** Đồ án tuân thủ nghiêm ngặt nguyên tắc **NT2 (Tối thiểu dữ liệu)** và **Danh mục cấm** của đề bài. Đây là công cụ đồng hành minh bạch, không phải phần mềm gián điệp. Việc ghi phím và chụp màn hình vi phạm quyền riêng tư nghiêm trọng của trẻ em.

> [!TIP]
> **Q2: Nếu trẻ đổi tên file `game.exe` thành `calculator.exe`, phần mềm có chặn được không?**  
> **Trả lời:** Chặn được hoàn toàn. Hệ thống không chỉ kiểm tra tên file tiến trình (`psutil.Process.name()`) mà còn đọc file thực thi trên đĩa và tính mã băm **SHA-256**. Danh sách cấm lưu trữ mã băm SHA-256 của các game/ứng dụng phổ biến, do đó việc đổi tên file là vô hiệu.

> [!TIP]
> **Q3: Trẻ dùng trình duyệt có bật DNS-over-HTTPS (DoH) thì DNS Proxy có chặn được không?**  
> **Trả lời:** Hệ thống nhận diện các máy chủ DoH phổ biến (như Cloudflare `1.1.1.1/dns-query`, Google `8.8.8.8`) và chặn truy vấn tới các endpoint này thông qua danh sách IP/Domain cấm. Khi trình duyệt không kết nối được DoH, theo tiêu chuẩn RFC nó sẽ tự động rơi (fallback) về DNS mặc định của hệ điều hành, tức là đi qua DNS Proxy `127.0.0.1:53` của OpenGuard Kids.

> [!TIP]
> **Q4: Lỡ Agent bị crash thì máy trẻ có bị mất mạng Internet vĩnh viễn không?**  
> **Trả lời:** Hệ thống có 3 lớp bảo vệ:  
> 1. Service Control Manager (SCM) của Windows được cấu hình tự động khởi động lại Service khi gặp sự cố.  
> 2. Cơ chế khôi phục trước khi thoát (Exit Trap / Signal Handler) tự động trả DNS về DHCP nếu service dừng có kiểm soát.  
> 3. Cung cấp sẵn kịch bản cứu hộ độc lập [scripts/restore_dns.bat](file:///home/cornar/Projects/OpenGuard-Kids/scripts/restore_dns.bat) sử dụng lệnh `netsh` hoàn trả DNS về tự động chỉ với 1 cú click chuột của phụ huynh.

