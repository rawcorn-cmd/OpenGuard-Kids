# OpenGuard Kids — Tuần 1: Khung Sườn Dự Án & 3 Spike Kỹ Thuật Rủi Ro Cao

> **Khóa học:** Mạng máy tính (*Computer Networks*) — Khoa Công nghệ Thông tin, Trường ĐH Khoa học Tự nhiên (HCMUS)  
> **Mã yêu cầu đồ án:** F2.3 (DNS Filtering, SafeSearch), F5 (Security Foundations), NT1 (Transparency & Openness)  
> **Trạng thái kiểm thử:** **16/16 unit tests PASSED (100%)**

---

## 1. MỤC TIÊU VÀ ĐẶT VẤN ĐỀ TUẦN 1

Trước khi xây dựng bất kỳ logic nghiệp vụ phức tạp nào, một hệ thống kiểm soát phụ huynh an toàn trên Windows phải giải quyết triệt để **3 rủi ro kỹ thuật mang tính sống còn**:

1. **Rủi ro mất mạng Internet máy tính:** Nếu bộ lọc DNS bị crash hoặc cấu hình sai, toàn bộ máy tính của người dùng sẽ mất kết nối mạng. Cần có cơ chế phục hồi khẩn cấp 1-click và phân giải dự phòng.
2. **Rủi ro sập cơ sở dữ liệu khi mất điện đột ngột:** SQLite mặc định có thể bị khóa hoặc lỗi file nếu ứng dụng đột ngột mất điện lúc đang ghi đĩa. Đồng thời, lưu trữ mật khẩu phải đạt chuẩn hiện đại (Argon2id) để chống brute-force bằng GPU.
3. **Rủi ro leo thang đặc quyền & tiến trình lạ chiếm quyền:** Service chạy ở Session 0 (`LocalSystem`) cần giao tiếp với giao diện Tray UI ở Session 1 (User). Nếu mở cổng mạng cục bộ không có bảo vệ, bất kỳ phần mềm độc hại nào trên máy cũng có thể gửi lệnh điều khiển.

---

## 2. KIẾN TRÚC HỆ THỐNG TUẦN 1

```
+-----------------------------------------------------------------------------------+
|                        MÁY TÍNH CỦA TRẺ (WINDOWS 10/11 x64)                       |
|                                                                                   |
|  [SESSION 0: WINDOWS SERVICE - NT AUTHORITY\LocalSystem]                          |
|   +----------------------------------------------------------------------------+  |
|   | 1. DNSProxy Engine (UDP 127.0.0.1:53)                                      |  |
|   |    - Chặn DoH: use-application-dns.net -> NXDOMAIN                         |  |
|   |    - CNAME SafeSearch: google.com -> forcesafesearch.google.com            |  |
|   |    - Trỏ tên miền cấm về 127.0.0.1 (Blockpage)                             |  |
|   |    - Kịch bản cứu hộ mạng: restore_dns.bat (netsh DHCP)                    |  |
|   +----------------------------------------------------------------------------+  |
|   | 2. SQLite Database & Security Hub (src/server/database.py, security.py)    |  |
|   |    - PRAGMA journal_mode=WAL; PRAGMA foreign_keys=ON;                      |  |
|   |    - Argon2id Password Hashing (RFC 9106)                                  |  |
|   |    - Khóa tài khoản 15 phút sau 5 lần thử sai                              |  |
|   +----------------------------------------------------------------------------+  |
|   | 3. Loopback IPC Server (127.0.0.1:8765)                                    |  |
|   |    - Token bí mật ngẫu nhiên 64-hex (File NTFS phân quyền System)          |  |
|   |    - Xác thực header X-OGK-Token bắt buộc cho mọi yêu cầu                  |  |
|   +-------------------------------------+--------------------------------------+  |
|                                         | Loopback HTTP (127.0.0.1:8765)           |
|                                         | Header: X-OGK-Token: <64-hex>           |
|                                         v                                         |
|  [SESSION 1: USER DESKTOP]                                                        |
|   +----------------------------------------------------------------------------+  |
|   | Tray UI / Diagnostic Scripts (Giao tiếp bảo mật với Service)               |  |
|   +----------------------------------------------------------------------------+  |
+-----------------------------------------------------------------------------------+
```

---

## 3. CHI TIẾT CÀI ĐẶT CÁC THÀNH PHẦN MÃ NGUỒN

### 3.1. Kịch bản phục hồi mạng khẩn cấp (`restore_dns.bat`)
* **Vị trí tệp:** `restore_dns.bat`
* **Nhiệm vụ:** Đảm bảo nguyên tắc an toàn tối thượng của đồ án: Không bao giờ làm hỏng cấu hình mạng của người dùng.
* **Cơ chế:**
  - Chạy với quyền Administrator.
  - Sử dụng lệnh `netsh interface ip set dns name="Wi-Fi" source=dhcp` và `Ethernet` để trả DNS về bộ phát Wi-Fi gốc.
  - Gọi `ipconfig /flushdns` để xóa sạch cache DNS phân giải cục bộ.

### 3.2. Động cơ phân giải và lọc tên miền DNS (`src/agent/dns_proxy.py`)
* **Vị trí tệp:** `src/agent/dns_proxy.py`
* **Nhiệm vụ:** Đón bắt các gói tin DNS trên UDP cổng 53, thực thi chính sách an toàn cho trẻ.
* **Các tính năng kỹ thuật cốt lõi:**
  1. **Khắc chế DNS-over-HTTPS (DoH):**
     - Các trình duyệt hiện đại (Chrome, Firefox, Edge) cố gắng bỏ qua DNS của máy để gửi DNS qua HTTPS.
     - Firefox & Chrome truy vấn tên miền canary `use-application-dns.net`. Nếu nhận được `NXDOMAIN`, trình duyệt sẽ tự động vô hiệu hóa DoH và quay về sử dụng DNS của hệ điều hành.
     - `DNSProxy` tự động chặn và trả về `NXDOMAIN` cho tên miền này.
  2. **Ép buộc Tìm kiếm An toàn (SafeSearch CNAME Rewriting):**
     - Khi trẻ truy vấn `google.com`, `www.google.com`, proxy trả về bản ghi `CNAME` trỏ sang `forcesafesearch.google.com`.
     - Khi trẻ truy vấn `bing.com`, `www.bing.com`, proxy trỏ `CNAME` sang `strict.bing.com`.
  3. **Lọc tên miền cấm (Blocklist & Wildcard):**
     - Nhận diện đuôi tên miền con (Wildcard subdomains): cấm `badsite.com` thì tự động cấm `sub.badsite.com`, `deep.sub.badsite.com`.
     - Phân giải tên miền cấm về địa chỉ loopback `127.0.0.1` (máy chủ HTTP Blockpage).
  4. **Danh sách trắng vĩnh viễn (Permanent Whitelist):**
     - Các tên miền bảo vệ trẻ em và giáo dục (`treem.gov.vn`, `tongdai111.vn`, `hcmus.edu.vn`, `edu.vn`) không bao giờ bị chặn trong bất kỳ chế độ nào.

### 3.3. Cơ sở dữ liệu SQLite chuẩn WAL & Bảo mật Argon2id
* **Vị trí tệp:** `src/server/database.py`, `src/server/models.py`, `src/server/security.py`
* **Nhiệm vụ:** Quản lý dữ liệu quan hệ an toàn, chống hỏng file, băm mật khẩu chuẩn hiện đại.
* **Chi tiết kỹ thuật:**
  1. **Tối ưu hóa SQLite Engine:**
     - Thiết lập `PRAGMA journal_mode=WAL;`: Chế độ Write-Ahead Logging cho phép đọc và ghi diễn ra đồng thời mà không bị khóa (non-blocking concurrency).
     - Thiết lập `PRAGMA foreign_keys=ON;`: Đảm bảo toàn vẹn dữ liệu quan hệ, kích hoạt tính năng xóa liên hoàn `CASCADE DELETE`.
     - Thiết lập `PRAGMA synchronous=NORMAL;`: Tối ưu hiệu năng ghi đĩa mà vẫn chống lỗi hỏng database khi sập nguồn.
  2. **Lược đồ quan hệ đầy đủ (7 Entities):**
     - `Parent`: Tài khoản phụ huynh (email, mật khẩu băm, đếm số lần sai, cờ khóa tài khoản).
     - `Child`: Hồ sơ trẻ em (tên, năm sinh, giới hạn giờ hàng ngày, giờ giới nghiêm).
     - `Device`: Thiết bị máy tính của trẻ (tên máy tính, mã PIN ghép đôi 8 ký tự, trạng thái ghép).
     - `Policy`: Chính sách chặn lọc (danh sách cấm, danh sách trắng, từ khóa).
     - `Event`: Dữ liệu nhật ký sử dụng (đúng chuẩn 7 trường riêng tư NT2).
     - `ChildRequest`: Hòm thư phê duyệt yêu cầu xin thêm giờ / mở trang web.
     - `AuditLog`: Nhật ký kiểm toán mọi thay đổi cấu hình.
  3. **Thuật toán băm mật khẩu Argon2id:**
     - Đạt chuẩn RFC 9106, chống lại tấn công vét cạn (brute-force) bằng phần cứng chuyên dụng (GPU, FPGA, ASIC).
     - Tham số an toàn: `time_cost=3`, `memory_cost=64MB` ($65536$ KiB), `parallelism=4`.
  4. **Chính sách mật khẩu & Khóa tài khoản:**
     - Độ dài tối thiểu 10 ký tự, bao gồm ít nhất 1 chữ hoa, 1 chữ thường, 1 chữ số và 1 ký tự đặc biệt.
     - Khóa tài khoản 15 phút nếu nhập sai mật khẩu 5 lần liên tiếp (`failed_login_attempts >= 5`).

### 3.4. Giao tiếp nội bộ liên phiên IPC (`src/agent/ipc.py`)
* **Vị trí tệp:** `src/agent/ipc.py`
* **Nhiệm vụ:** Kết nối dịch vụ hệ thống ngầm Session 0 với ứng dụng giao diện người dùng Session 1.
* **Chi tiết kỹ thuật:**
  - Khởi tạo máy chủ HTTP nội bộ nhẹ tại địa chỉ `127.0.0.1:8765`.
  - Sinh mã token ngẫu nhiên 64 ký tự hex (`secrets.token_hex(32)`).
  - Mọi yêu cầu từ Tray UI phải đính kèm header `X-OGK-Token`. Nếu thiếu hoặc sai token, máy chủ lập tức từ chối với mã lỗi `403 Forbidden`.

---

## 4. KẾT QUẢ KIỂM THỬ TỰ ĐỘNG (16 TESTS)

Chạy kiểm thử cho Tuần 1:
```bash
.venv/bin/pytest tests/test_dns_proxy.py tests/test_database_and_security.py tests/test_ipc.py -v
```

| Tệp kiểm thử | Tên bài test | Nội dung xác thực | Kết quả |
| :--- | :--- | :--- | :---: |
| `test_dns_proxy.py` | `test_canary_domain_returns_nxdomain` | Canary DoH `use-application-dns.net` trả về `NXDOMAIN` | **PASSED** |
| `test_dns_proxy.py` | `test_blocklist_redirection_to_blockpage` | Tên miền cấm trỏ về `127.0.0.1` | **PASSED** |
| `test_dns_proxy.py` | `test_wildcard_subdomain_blocking` | Chặn triệt để tên miền con đa cấp | **PASSED** |
| `test_dns_proxy.py` | `test_heuristic_keyword_blocking` | Lọc theo từ khóa độc hại | **PASSED** |
| `test_dns_proxy.py` | `test_safesearch_cname_rewriting` | Bẻ hướng Google/Bing sang CNAME an toàn | **PASSED** |
| `test_dns_proxy.py` | `test_permanent_whitelist` | Danh sách trắng nhà nước/giáo dục không bị chặn | **PASSED** |
| `test_dns_proxy.py` | `test_study_mode_whitelist_only` | Chế độ giờ học chỉ mở danh sách trắng | **PASSED** |
| `test_dns_proxy.py` | `test_live_udp_socket_resolution` | Giao tiếp thực tế qua UDP socket cổng 53 | **PASSED** |
| `test_database_and_security.py` | `test_sqlite_wal_and_foreign_keys_pragma` | Bật thành công WAL mode và Foreign Key constraint | **PASSED** |
| `test_database_and_security.py` | `test_argon2id_password_hashing` | Băm và xác thực Argon2id chính xác | **PASSED** |
| `test_database_and_security.py` | `test_password_complexity_validator` | Bắt buộc chữ hoa, số, ký tự đặc biệt | **PASSED** |
| `test_database_and_security.py` | `test_brute_force_lockout_after_five_attempts` | Khóa tài khoản sau 5 lần đăng nhập thất bại | **PASSED** |
| `test_database_and_security.py` | `test_models_relational_cascade_deletion` | Xóa tài khoản phụ huynh tự động xóa sạch bảng liên kết | **PASSED** |
| `test_ipc.py` | `test_ipc_status_with_valid_token` | Tray UI gửi đúng Token 64-hex nhận HTTP 200 OK | **PASSED** |
| `test_ipc.py` | `test_ipc_forbidden_with_invalid_token` | Sai Token hoặc không có Token bị trả 403 Forbidden | **PASSED** |
| `test_ipc.py` | `test_ipc_heartbeat_and_child_request` | Gửi nhịp tim và yêu cầu xin quyền qua kênh IPC thành công | **PASSED** |

---

## 5. BỘ CÂU HỎI VẤN ĐÁP BẢO VỆ ĐỒ ÁN (DEFENSE Q&A)

### Câu 1: Tại sao nhóm không dùng MD5, SHA-256 hay bcrypt mà lại chọn Argon2id?
> **Trả lời:**  
> MD5 và SHA-256 là các hàm băm thông thường, tính toán cực kỳ nhanh, dẫn đến nguy cơ bị tin tặc dùng card màn hình (GPU) thử hàng tỷ mật khẩu mỗi giây để bẻ khóa. Bcrypt tuy an toàn hơn nhưng chỉ tốn CPU mà không tốn bộ nhớ RAM.  
> **Argon2id** (đạt giải quán quân cuộc thi Password Hashing Competition và chuẩn RFC 9106) là thuật toán *memory-hard*. Bằng cách ép sử dụng $64\text{ MB}$ RAM cho mỗi lần tính toán, Argon2id vô hiệu hóa hoàn toàn sức mạnh tính toán song song của các dàn máy đào GPU/ASIC, bảo vệ an toàn tối đa cho mật khẩu phụ huynh.

### Câu 2: Trình duyệt ngày nay dùng DNS-over-HTTPS (DoH) mã hóa luồng tin, DNS Proxy cổng 53 làm sao chặn được?
> **Trả lời:**  
> Trình duyệt gửi DoH trực tiếp qua HTTPS cổng 443 nên DNS truyền thống cổng 53 không thể nhìn thấy gói tin. Tuy nhiên, các nhà phát triển trình duyệt (Mozilla, Google) có cung cấp cơ chế thỏa thuận: trước khi bật DoH, trình duyệt gửi truy vấn kiểm tra tới tên miền **Canary Domain** (`use-application-dns.net`).  
> DNS Proxy của nhóm bắt truy vấn này và trả về `NXDOMAIN`. Khi nhận được tín hiệu này, trình duyệt hiểu rằng mạng đang có chính sách kiểm soát của phụ huynh/doanh nghiệp, và tự động tắt DoH để quay về sử dụng DNS hệ thống trên cổng 53.

### Câu 3: Nếu phần mềm bị crash hoặc tắt đột ngột, làm sao người dùng không bị mất mạng Internet?
> **Trả lời:**  
> Nhóm chuẩn bị sẵn kịch bản cứu hộ `restore_dns.bat`. Khi chạy, kịch bản dùng lệnh hệ thống `netsh interface ip set dns` để chuyển DNS của mọi card mạng về chế độ tự động (DHCP), đồng thời xóa bộ đệm phân giải (`ipconfig /flushdns`). Người dùng có thể chạy tệp này chỉ với một cú nhấp chuột để mạng trở lại bình thường ngay lập tức.

