# Chuyên Đề Nghiên Cứu Chuyên Sâu: Giao Thức HTTP & Sự Tiến Hóa Đến HTTP/3

> **Kho tri thức mạng máy tính:** Môn Mạng Máy Tính (HCMUS / Kurose & Ross Top-Down Approach)  
> **Chuyên đề:** Tầng Application (Chương 2) — Giao thức HTTP, Cơ chế Cookie, Tối ưu hóa độ trễ và Cuộc cách mạng chuyển dịch sang QUIC/UDP.  
> **Tài liệu liên quan trong đồ án:** [02_loopback_ipc_channel.md](file:///home/cornar/Projects/OpenGuard-Kids/docs/components/02_loopback_ipc_channel.md), [05_dns_proxy_safesearch_doh.md](file:///home/cornar/Projects/OpenGuard-Kids/docs/components/05_dns_proxy_safesearch_doh.md), [06_polite_blockpage_server.md](file:///home/cornar/Projects/OpenGuard-Kids/docs/components/06_polite_blockpage_server.md).

---

## 1. Bản Chất Nền Tảng của Web & HTTP (Section 2.2)

### 1.1. Cấu trúc trang Web (Web Objects & URL)
* Một trang Web không phải là một file đơn lẻ mà là một tập hợp các **Objects (Đối tượng)**: bao gồm 1 file HTML cơ sở (*Base HTML file*) và nhiều đối tượng tham chiếu (*Referenced Objects*) như ảnh PNG/JPEG, mã JavaScript, style CSS, video, font chữ.
* Mỗi object được định danh duy nhất thông qua một **URL (Uniform Resource Locator)**:
  $$\text{URL} = \underbrace{\text{http://}}_{\text{Scheme / Protocol}}\ \underbrace{\text{www.example.com}}_{\text{Hostname / Domain}}\ \underbrace{\text{/assets/style.css}}_{\text{Path to Object}}$$

### 1.2. Tính Phi Trạng Thái (Statelessness) & Triết Lý Thiết Kế
* **Định nghĩa:** HTTP server không hề lưu lại bất kỳ thông tin nào về những gì client đã yêu cầu trước đó. Xử lý xong 1 request/response là server "quên sạch" client là ai.
* **Lý do lựa chọn Stateless:**
  * **Tối giản & Hiệu năng cao:** Server không tốn RAM duy trì hàng triệu session states khi lượng truy cập bùng nổ.
  * **Khả năng chịu lỗi (*Fault Tolerance*):** Nếu server bị crash và restart lại ngay lập tức, các client vẫn tiếp tục gửi request bình thường mà không bị lỗi mất phiên làm việc.

---

## 2. Duy Trì Trạng Thái: Công Nghệ Cookie & Session (Section 2.2.4)

Để phục vụ các ứng dụng cần nhớ danh tính (giỏ hàng thương mại điện tử, phiên đăng nhập, cá nhân hóa), cơ chế **Cookies** ra đời (RFC 6265) với **4 thành phần cốt lõi**:

1. **Header `Set-Cookie:` trong HTTP Response:** Do Server gửi về để yêu cầu trình duyệt lưu dữ liệu.
2. **Header `Cookie:` trong HTTP Request:** Do Trình duyệt tự động đính kèm gửi lên Server ở các lần truy cập kế tiếp.
3. **File lưu trữ Cookie trên Client:** Do trình duyệt quản lý an toàn trên ổ cứng người dùng.
4. **Cơ sở dữ liệu ở phía Backend:** Lưu trữ dữ liệu thực tế (thông tin tài khoản, giỏ hàng) gắn với Cookie ID.

### Quy trình tương tác từng bước (Step-by-Step Flow)
```
Client (Browser)                                         Server (E-Commerce)
       |                                                          |
       | ----- 1. GET /index.html (Chưa có cookie) -------------> |
       |                                                          |-- Sinh ID ngẫu nhiên: 1678
       |                                                          |-- Lưu DB: 1678 = User mới
       |                                                          |
       | <---- 2. HTTP/1.1 200 OK ------------------------------- |
       |          Set-Cookie: user_id=1678                        |
       |                                                          |
[Trình duyệt lưu: amazon.com -> user_id=1678]                     |
       |                                                          |
(Các lần truy cập sau đó)                                         |
       |                                                          |
       | ----- 3. GET /cart/add?item=laptop --------------------> |
       |          Host: amazon.com                                |
       |          Cookie: user_id=1678                            |
       |                                                          |-- Tra DB: Nhận diện ra User 1678
       |                                                          |-- Bỏ laptop vào giỏ hàng 1678
       |                                                          |
       | <---- 4. HTTP/1.1 200 OK ------------------------------- |
```

### Các Cờ Bảo Mật của Cookie (Security Flags)
* **`HttpOnly`:** Ngăn chặn JavaScript truy cập qua `document.cookie` $\rightarrow$ Chốt chặn phòng thủ hàng đầu chống tấn công **XSS** (*Cross-Site Scripting*).
* **`Secure`:** Chỉ cho phép trình duyệt gửi cookie qua kết nối đã được mã hóa **HTTPS (TLS)** $\rightarrow$ Chống nghe lén (*Sniffing*) trên mạng Wi-Fi công cộng.
* **`SameSite`:** Chống tấn công mạo danh **CSRF** (*Cross-Site Request Forgery*):
  * `Strict`: Không bao giờ gửi cookie nếu request đến từ trang web khác.
  * `Lax`: Chỉ gửi cookie khi người dùng bấm link điều hướng tự nhiên từ trang khác sang.
* **`Expires` / `Max-Age`:** Xác định cookie là tạm thời (*Session Cookie* - đóng trình duyệt là mất) hay vĩnh viễn (*Persistent Cookie* - lưu đến hạn định).

---

## 3. Cấu Trúc Bản Tin HTTP & Quản Lý Kết Nối

### 3.1. Cấu trúc HTTP Request & Response
```http
[ HTTP REQUEST ]
GET /api/v1/user HTTP/1.1\r\n                   <-- Request Line (Method, URL, Version)
Host: api.openguard.local\r\n                    <-- Headers (Key: Value)
User-Agent: OpenGuard-Agent/1.0\r\n
Authorization: Bearer secret_token\r\n
\r\n                                            <-- Blank line (\r\n)
[Entity Body - Trống với GET, có dữ liệu với POST/PUT]

[ HTTP RESPONSE ]
HTTP/1.1 200 OK\r\n                              <-- Status Line (Version, Code, Phrase)
Date: Wed, 28 Oct 2026 14:00:00 GMT\r\n         <-- Headers
Content-Type: application/json\r\n
Content-Length: 42\r\n
\r\n                                            <-- Blank line (\r\n)
{"status": "active", "mode": "safe_mode"}       <-- Entity Body
```

### 3.2. Non-Persistent vs Persistent HTTP
* **Đo lường RTT (Round-Trip Time):** Thời gian để 1 gói tin nhỏ đi từ Client đến Server rồi quay lại.
* **Non-Persistent (HTTP/1.0):** Mỗi object mở 1 kết nối TCP riêng rồi đóng ngay.
  $$\text{Thời gian tải 1 object} = 2 \times \text{RTT} + \text{Thời gian truyền file (Transmit Time)}$$
  Nếu trang web có 1 HTML + 10 bức ảnh $\rightarrow$ Tốn tới $11 \times 2 = 22\text{ RTT}$!
* **Persistent (HTTP/1.1):** Mở 1 kết nối TCP và duy trì mở (`Connection: keep-alive`) để gửi liên tiếp các request. Chỉ tốn 1 RTT bắt tay ban đầu cho toàn bộ trang web.

### 3.3. Web Caching & Conditional GET
* **Proxy Caching:** Lưu trữ bản sao dữ liệu ở gần người dùng để giảm tải đường truyền ISP và giảm độ trễ.
* **Conditional GET:** Client gửi kèm header `If-Modified-Since: <thời điểm>`. Nếu nội dung chưa bị chỉnh sửa, Server chỉ trả về `HTTP/1.1 304 Not Modified` với **Body rỗng**, tiết kiệm $99\%$ băng thông.

---

## 4. Cuộc Tiến Hóa Vĩ Đại: Từ HTTP/1.0 Đến HTTP/3

```
[ HTTP/1.0 ] (1996) ──> Non-persistent (Mỗi file mở 1 TCP riêng, lãng phí RTT)
      │
[ HTTP/1.1 ] (1997) ──> Persistent (Keep-Alive), Host Header, nhưng bị nghẽn HoL tầng App
      │
      ├───────> [ HTTPS ] (1994/2000): HTTP bọc trong đường hầm mã hóa TLS/SSL (Port 443)
      │
[ HTTP/2   ] (2015) ──> Binary Framing, Multiplexing trên 1 luồng TCP, nén HPACK. Vẫn nghẽn HoL tầng TCP
      │
[ HTTP/3   ] (2022) ──> Bỏ hoàn toàn TCP, chạy trên QUIC (nền UDP), tích hợp TLS 1.3, 0-RTT Handshake
```

### Bảng Đối Chiếu Kỹ Thuật Toàn Diện

| Tiêu chí | HTTP/1.1 | HTTPS | HTTP/2 | HTTP/3 |
| :--- | :--- | :--- | :--- | :--- |
| **Tầng Transport bên dưới** | TCP | TCP + TLS | TCP + TLS | **QUIC (trên nền UDP)** |
| **Cổng mặc định** | 80 | 443 | 443 | 443 (UDP) |
| **Định dạng dữ liệu** | Text ASCII thô | Ciphertext mã hóa | **Nhị phân (Binary Frames)** | **Nhị phân (Binary Frames)** |
| **Quản lý kết nối** | 1 TCP cho nhiều request tuần tự | Tuân theo bản HTTP bên trong | **1 kết nối TCP duy nhất** chứa nhiều Stream | **Nhiều Stream độc lập** trên nền UDP |
| **Nghẽn Head-of-Line (HoL)** | **Bị nghẽn ở Tầng Application** | Kế thừa từ bản HTTP | Hết nghẽn tầng App, **nhưng bị nghẽn ở Tầng TCP** | **Xóa bỏ hoàn toàn $100\%$** |
| **Bảo mật mặc định** | ❌ Không (Plaintext) | ✅ Có (TLS) | ✅ Bắt buộc thực tế trên Browser | ✅ **Tích hợp sẵn mặc định (TLS 1.3)** |
| **Nén Header** | ❌ Không nén | ❌ Không nén | ✅ Nén động bằng **HPACK** | ✅ Nén động bằng **QPACK** |
| **Độ trễ bắt tay kết nối** | $1 \text{ RTT}$ (TCP thô) | $2 - 3 \text{ RTT}$ (TCP + TLS) | $2 - 3 \text{ RTT}$ | **$1 \text{ RTT}$ (mới) / $0 \text{ RTT}$ (kết nối lại)** |
| **Chuyển mạng (Wi-Fi $\leftrightarrow$ 4G)** | Đứt kết nối, bắt tay lại | Đứt kết nối, bắt tay lại | Đứt kết nối, bắt tay lại | **Mượt mà không đứt** (*Connection Migration*) |

---

## 5. Các Vấn Đề Chuyên Sâu Cần Khắc Cốt Ghi Tâm

### 5.1. Head-of-Line (HoL) Blocking: Tại sao HTTP/2 chưa hoàn hảo?
* **Ở HTTP/1.1 (Tầng App):** Khi gửi Request 1 (video nặng) và Request 2 (CSS nhỏ), Request 2 buộc phải xếp hàng đợi Server trả lời xong Request 1 mới được nhận.
* **Ở HTTP/2 (Tầng Transport):** HTTP/2 chia nhỏ thành các frame nhị phân và gửi xen kẽ trên 1 kết nối TCP. Nhưng vì TCP bắt buộc dữ liệu phải tới đích **đúng thứ tự 100% (*In-order delivery*)**, nếu chỉ **1 gói tin TCP trên đường truyền bị rớt**, toàn bộ các frame của mọi stream khác đều phải dừng lại trong RAM chờ gói bị mất truyền lại xong! Ở mạng di động chập chờn (packet loss 2%), HTTP/2 chậm hơn cả HTTP/1.1.
* **Ở HTTP/3 (Giải quyết triệt để):** Chạy trên **QUIC (UDP)**. Mỗi stream có số thứ tự và bộ đệm riêng. Stream 1 mất gói thì chỉ Stream 1 đợi, Stream 2 và 3 vẫn tiếp tục chạy $100\%$ tốc độ.

### 5.2. Sự Không Hoàn Toàn "Mất Tin Cậy" của UDP
* Mặc dù bản thân UDP ở tầng Transport không có ACK hay Retransmission, nhưng **một ứng dụng chạy trên UDP hoàn toàn có thể đạt độ tin cậy $100\%$ nếu tự cài đặt cơ chế tin cậy ở Tầng Ứng dụng** (như QUIC, DNS, game online).
* Lợi ích của việc tự viết cơ chế tin cậy trên UDP:
  * Cho phép **tin cậy có chọn lọc** (gói tọa độ nhân vật thì bỏ qua nếu mất, gói mua đồ thì bắt buộc gửi lại).
  * Tránh hiện tượng HoL Blocking cứng nhắc của TCP.
  * Tối ưu hóa trong **User-space** mà không phụ thuộc vào Kernel hệ điều hành.

### 5.3. QUIC là Giao Thức Tầng 4 hay Tầng 5?
* **Về mặt Logic & Chức năng (IETF RFC 9000):** QUIC là **Giao thức Tầng 4 (Transport Layer)** vì nó đảm nhận toàn bộ việc kiểm soát nghẽn, kiểm soát luồng, truyền tin cậy và mã hóa cho tầng ứng dụng (HTTP/3) bên trên.
* **Về mặt Triển khai thực tế:** QUIC hoạt động như một **User-space Transport** chạy đè lên gói tin UDP (Port 443) nhằm "ngụy trang" vượt qua sự kiểm duyệt cứng nhắc của các thiết bị mạng trung gian (Firewall, Router cũ).

---

## 6. Mối Liên Hệ Thực Tế Với Đồ Án OpenGuard Kids

1. **Local Polite Blockpage Server ([06_polite_blockpage_server.md](file:///home/cornar/Projects/OpenGuard-Kids/docs/components/06_polite_blockpage_server.md)):**
   * Hoạt động như một HTTP Web Server cục bộ tại `127.0.0.1:8088`. Trả về mã `200 OK` kèm giao diện HTML thân thiện khi trẻ truy cập trang bị cấm.
2. **REST API & Loopback IPC ([02_loopback_ipc_channel.md](file:///home/cornar/Projects/OpenGuard-Kids/docs/components/02_loopback_ipc_channel.md)):**
   * Sử dụng HTTP/1.1 và WebSocket qua TCP trên giao diện Loopback `127.0.0.1`. Vì chạy trong RAM máy tính (Packet loss $= 0\%$, RTT $< 0.1\text{ms}$), HTTP/1.1 là giải pháp nhẹ nhàng, đơn giản và ổn định nhất mà không cần đến sự phức tạp của HTTP/2 hay HTTP/3.
3. **DNS over HTTPS - DoH ([05_dns_proxy_safesearch_doh.md](file:///home/cornar/Projects/OpenGuard-Kids/docs/components/05_dns_proxy_safesearch_doh.md)):**
   * Sử dụng HTTP/2 bọc trong TLS để mã hóa các truy vấn DNS gửi lên Cloudflare/Google DNS, ngăn chặn nhà mạng hoặc bên thứ ba theo dõi lịch sử lướt web của trẻ.

