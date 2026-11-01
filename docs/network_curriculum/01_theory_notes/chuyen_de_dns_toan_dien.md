# Chuyên Đề Nghiên Cứu Chuyên Sâu: Giao Thức DNS (Domain Name System)

> **Kho tri thức mạng máy tính:** Môn Mạng Máy Tính (HCMUS / Kurose & Ross Top-Down Approach)  
> **Chuyên đề:** Tầng Application (Chương 2, Mục 2.4) — Giao thức DNS, Cơ sở dữ liệu phân tán, Cấu trúc bản ghi RR, Cơ chế Caching và Ứng dụng trong Bảo vệ Trẻ em.  
> **Tài liệu cốt lõi trong OpenGuard Kids:** [05_dns_proxy_safesearch_doh.md](file:///home/cornar/Projects/OpenGuard-Kids/docs/components/05_dns_proxy_safesearch_doh.md), [06_polite_blockpage_server.md](file:///home/cornar/Projects/OpenGuard-Kids/docs/components/06_polite_blockpage_server.md).  
> **Thực hành liên quan:** [wireshark_dns_v8.0.md](file:///home/cornar/Projects/OpenGuard-Kids/docs/network_curriculum/03_wireshark_labs/wireshark_dns_v8.0.md).

---

## 1. Bản Chất và Vai Trò Cốt Lõi Của DNS

Con người ghi nhớ thế giới trực quan qua các danh từ có ý nghĩa ngữ nghĩa (như `google.com`, `facebook.com`, `vnexpress.net`), nhưng các thiết bị mạng và bộ định tuyến (Router) trong lõi Internet chỉ có thể định tuyến các gói tin dựa trên các con số nhị phân 32-bit (IPv4) hoặc 128-bit (IPv6).

👉 **DNS là "Cuốn Danh Bạ Toàn Cầu của Internet"**, đảm nhiệm 2 vai trò cốt lõi:
1. **Một Cơ sở Dữ liệu Phân tán (Distributed Database):** Được triển khai trên một hệ thống phân cấp gồm hàng nghìn máy chủ DNS trên toàn thế giới, lưu trữ hàng tỷ ánh xạ tên miền $\leftrightarrow$ địa chỉ IP và thông tin định tuyến dịch vụ.
2. **Một Giao thức Tầng Ứng dụng (Application-layer Protocol):** Cho phép các máy trạm (Hosts) gửi các câu hỏi truy vấn (Queries) và nhận lại các câu trả lời (Replies), vận hành chủ yếu trên nền **UDP cổng 53** (và dùng TCP cổng 53 khi gói tin vượt quá 512 byte hoặc khi đồng bộ vùng dữ liệu Zone Transfer).

### Các Dịch Vụ Bổ Trợ Sống Còn Của DNS:
* **Host Aliasing (Bí danh tên miền):** Một máy chủ có thể có tên chính quy rất phức tạp (ví dụ: `relay1.west-coast.enterprise.com`), nhưng có thể tạo nhiều bí danh ngắn gọn dễ nhớ (`www.enterprise.com`, `ftp.enterprise.com`) nhờ bản ghi CNAME.
* **Mail Server Aliasing:** Cho phép tên miền của máy chủ Web và máy chủ Thư tín trùng nhau hoàn toàn (ví dụ: truy cập web là `company.com` và gửi email tới `user@company.com`), DNS dùng bản ghi MX để điều hướng gói tin thư tới đúng máy chủ nhận thư.
* **Load Distribution (Cân bằng tải cụm máy chủ):** Với các website quy mô lớn, một tên miền có thể gắn với một mảng gồm hàng chục địa chỉ IP khác nhau. Khi client truy vấn, máy chủ DNS sẽ xoay vòng thứ tự các địa chỉ IP trong gói tin trả lời (*Round-Robin DNS*), giúp phân bổ đều lưu lượng tải cho toàn bộ trung tâm dữ liệu.

---

## 2. Tại Sao DNS Bắt Buộc Phải Phân Tán (Không Thể Tập Trung)?

> 💡 **Câu hỏi phỏng vấn/thi cử:** *"Tại sao người ta không gom toàn bộ cơ sở dữ liệu DNS của toàn cầu vào một siêu máy chủ DNS duy nhất?"*

Giáo trình Kurose & Ross khẳng định một thiết kế tập trung sẽ sụp đổ vì 4 lý do:
1. **Điểm Chết Duy Nhất (Single Point of Failure):** Nếu máy chủ tập trung gặp sự cố, bị tấn công mạng hoặc đứt cáp quang, **toàn bộ Internet trên hành tinh sẽ ngừng hoạt động ngay lập tức**!
2. **Lưu Lượng Quá Tải (Traffic Volume):** Hàng tỷ thiết bị smartphone, laptop, server trên toàn cầu liên tục gửi hàng triệu truy vấn mỗi giây; không một hạ tầng máy chủ đơn lẻ nào có thể gánh nổi lượng băng thông khổng lồ đó.
3. **Độ Trễ Khoảng Cách Địa Lý (Distant Centralized Database):** Một người dùng ở Việt Nam muốn mở một tờ báo nội địa nhưng phải gửi tín hiệu sang tận máy chủ ở Bắc Mỹ chỉ để hỏi địa chỉ IP, gây trễ hàng trăm mili-giây cho mỗi thao tác click chuột.
4. **Bảo Trì & Vận Hành Bất Khả Thi (Maintenance Nightmare):** Mỗi ngày có hàng triệu tên miền mới được đăng ký, thay đổi IP hoặc hủy bỏ. Một cơ sở dữ liệu đơn khối không thể liên tục cập nhật theo thời gian thực mà không bị khóa bảng (*locking bottleneck*).

---

## 3. Kiến Trúc Phân Cấp Hình Cây Của DNS (DNS Hierarchy)

Cơ sở dữ liệu DNS được tổ chức thành cấu trúc cây phân cấp nghiêm ngặt:

```
                            [ ROOT DNS Servers ]
                           (13 Nhãn định danh logic)
                                     |
             +-----------------------+-----------------------+
             |                                               |
       [ .com TLD ]                                    [ .vn TLD ]
     (Top-Level Domain)                              (Top-Level Domain)
             |                                               |
     [ google.com ]                                    [ hcmus.edu.vn ]
    (Authoritative)                                   (Authoritative)
```

### 3.1. Root DNS Servers (Máy chủ gốc)
* Nằm ở đỉnh chóp của cây phân cấp. Có **13 định danh nhãn logic** (từ `a.root-servers.net` đến `m.root-servers.net`), được quản lý bởi tổ chức ICANN.
* Trong thực tế vật lý, 13 nhãn này được nhân bản thành hơn **1.500 cụm máy chủ vật lý** phân tán khắp các châu lục thông qua kỹ thuật định tuyến **IP Anycast**.
* **Nhiệm vụ:** Root server không trực tiếp lưu địa chỉ IP của từng trang web, mà chỉ cung cấp địa chỉ IP của các máy chủ **TLD** phụ trách phần đuôi tên miền tương ứng.

### 3.2. Top-Level Domain (TLD) Servers (Máy chủ tên miền cấp cao nhất)
* Quản lý các đuôi tên miền quốc tế dùng chung (*gTLD*: `.com`, `.org`, `.net`, `.edu`) do các tập đoàn như Verisign quản lý, và các tên miền mã quốc gia (*ccTLD*: `.vn`, `.jp`, `.uk`, `.de`) do các trung tâm Internet quốc gia quản lý (như VNNIC tại Việt Nam).
* **Nhiệm vụ:** Chỉ đường tới máy chủ có thẩm quyền (*Authoritative Server*) của tổ chức sở hữu tên miền đó.

### 3.3. Authoritative DNS Servers (Máy chủ có thẩm quyền)
* Là máy chủ do chính tổ chức/doanh nghiệp đó sở hữu hoặc thuê từ các nhà cung cấp hạ tầng đám mây (Cloudflare, AWS Route 53, Google Cloud DNS).
* **Nhiệm vụ:** Đây là nơi lưu trữ hồ sơ gốc chính thức chứa địa chỉ IP thực tế của các máy chủ web, mail, api của tổ chức.

### 3.4. Local DNS Server (Default Name Server / Recursive Resolver)
* Không nằm trên cấu trúc cây chính thức nhưng đóng vai trò là "người thư ký mẫn cán" đại diện cho máy tính người dùng.
* Thường do nhà mạng Internet (ISP: Viettel, VNPT, FPT) cấp qua DHCP, hoặc người dùng chủ động cấu hình sang các dịch vụ Public DNS nổi tiếng như Google (`8.8.8.8`) hay Cloudflare (`1.1.1.1`).
* Khi một ứng dụng (trình duyệt, game) cần tra cứu IP, nó gửi yêu cầu trực tiếp đến Local DNS Server này.

---

## 4. Cơ Chế Phân Giải: Iterative (Truy Vấn Lặp) vs Recursive (Truy Vấn Đệ Quy)

Khi máy tính của Alice muốn truy cập `gaia.cs.umass.edu`, quy trình phân giải diễn ra như sau:

```
Máy của Alice                                  Local DNS Server
  (Client)                                    (192.168.1.1 / ISP)
      |                                                |
      | --- 1. Xin IP gaia.cs.umass.edu -------------> | \
      |        (Truy vấn ĐỆ QUY - Recursive)           |  |
      |                                                |  |--- 2. Hỏi Root: "Ai quản lý .edu?" (Iterative)
      |                                                |  |<-- 3. Root: "Hỏi TLD Server của đuôi .edu"
      |                                                |  |
      |                                                |  |--- 4. Hỏi TLD .edu: "Ai quản lý umass.edu?"
      |                                                |  |<-- 5. TLD: "Hỏi Authoritative DNS của UMass"
      |                                                |  |
      |                                                |  |--- 6. Hỏi UMass DNS: "IP gaia là bao nhiêu?"
      |                                                |  |<-- 7. UMass: "IP của nó là 128.119.245.12"
      |                                                | /
      | <-- 8. IP của bạn là 128.119.245.12 ---------- |
```

* **Truy vấn Đệ quy (Recursive Query):** 
  * Diễn ra ở bước 1 giữa **Client $\rightarrow$ Local DNS Server**.
  * Bản chất: Client ủy thác toàn bộ gánh nặng tìm kiếm cho Local DNS: *"Tôi chỉ hỏi bạn 1 lần duy nhất, bạn phải bằng mọi giá đi tìm và mang kết quả IP về cho tôi!"*.
* **Truy vấn Lặp (Iterative Query):**
  * Diễn ra ở các bước 2, 4, 6 giữa **Local DNS Server $\rightarrow$ Root $\rightarrow$ TLD $\rightarrow$ Authoritative**.
  * Bản chất: Các máy chủ cấp cao trả lời theo kiểu "chỉ đường": *"Tôi không biết IP cụ thể của máy chủ đó, nhưng hãy đến gặp máy chủ tiếp theo này để hỏi tiếp"*. Local DNS Server phải tự mình đi gõ cửa từng nơi cho đến khi gặp máy chủ có thẩm quyền.

---

## 5. Cơ Chế DNS Caching (Bộ Nhớ Đệm DNS)

* Để tối ưu hóa độ trễ và giảm tải áp lực cho các Root Server, ngay sau khi nhận được câu trả lời từ máy chủ có thẩm quyền, **Local DNS Server sẽ lưu tạm cặp (Domain, IP) vào bộ nhớ RAM của mình (DNS Cache)**.
* Mỗi bản ghi DNS đều có một trường số nguyên gọi là **TTL (Time-To-Live)** tính bằng giây:
  * Trong khoảng thời gian TTL còn hiệu lực, bất kỳ client nào khác trong mạng hỏi cùng tên miền đó, Local DNS Server sẽ trả lời **ngay lập tức trong $1\text{ms}$** mà không cần liên hệ lại hệ thống phân cấp.
  * Khi bộ đếm TTL giảm về 0, bản ghi sẽ tự động bị xóa khỏi Cache để đảm bảo hệ thống luôn cập nhật địa chỉ IP mới nếu website đổi máy chủ.

---

## 6. Các Loại Bản Ghi Tài Nguyên Cốt Lõi (Resource Records - RR)

Mọi bản ghi trong cơ sở dữ liệu DNS đều có cấu trúc dạng bộ tứ 4 phần tử:
$$\text{RR} = (\text{Name}, \text{Value}, \text{Type}, \text{TTL})$$

| Type | Ý Nghĩa Kỹ Thuật | Ví Dụ Name | Ví Dụ Value | Mô Tả |
| :--- | :--- | :--- | :--- | :--- |
| **`A`** | IPv4 Address | `google.com` | `142.250.190.46` | Ánh xạ hostname sang địa chỉ IPv4 32-bit tiêu chuẩn. |
| **`AAAA`** | IPv6 Address | `google.com` | `2404:6800:4003:c03::64` | Ánh xạ hostname sang địa chỉ IPv6 128-bit thế hệ mới. |
| **`CNAME`** | Canonical Name | `mail.google.com` | `googlemail.l.google.com` | Ánh xạ tên bí danh về tên chính thức của máy chủ. |
| **`NS`** | Name Server | `hcmus.edu.vn` | `ns1.hcmus.edu.vn` | Chỉ định máy chủ DNS có thẩm quyền quản lý vùng tên miền. |
| **`MX`** | Mail Exchange | `hcmus.edu.vn` | `mail.hcmus.edu.vn` (Pref: 10) | Định tuyến các bức thư điện tử gửi tới đuôi `@hcmus.edu.vn`. |
| **`TXT`** | Text Record | `google.com` | `"v=spf1 include:_spf.google.com ~all"` | Lưu trữ chuỗi ký tự bất kỳ, dùng để chống giả mạo email (**SPF, DKIM, DMARC**). |

---

## 7. Cấu Trúc Khung Bản Tin DNS (DNS Packet Format)

Bản tin truy vấn (Query) và phản hồi (Reply) của DNS dùng chung một định dạng chuẩn gồm 12 byte Header cố định:

```
 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-----------------------------------+-----------------------------------+
|       Identification (16-bit ID)  |      Flags (QR, Opcode, AA, TC,   |
|                                   |             RD, RA, RCODE)        |
+-----------------------------------+-----------------------------------+
|       Question Count (QDCOUNT)    |      Answer Count (ANCOUNT)       |
+-----------------------------------+-----------------------------------+
|       Authority Count (NSCOUNT)   |      Additional Count (ARCOUNT)   |
+-----------------------------------+-----------------------------------+
|                    Questions (Tên miền cần tra cứu)                   |
+-----------------------------------+-----------------------------------+
|                    Answers (Các bản ghi RRs trả về)                   |
+-----------------------------------+-----------------------------------+
|                    Authority (Các bản ghi máy chủ NS)                 |
+-----------------------------------+-----------------------------------+
|                    Additional Information (Các bản ghi IP bổ trợ)     |
+-----------------------------------+-----------------------------------+
```

* **Identification (16-bit):** Mã số ngẫu nhiên do Client sinh ra để ghép đôi chính xác câu trả lời trả về với câu hỏi gửi đi.
* **Flags (16-bit):**
  * `QR (Query/Response)`: `0` là câu hỏi, `1` là câu trả lời.
  * `AA (Authoritative Answer)`: `1` nếu câu trả lời đến từ máy chủ có thẩm quyền.
  * `RD (Recursion Desired)`: Client đặt `1` để yêu cầu phân giải đệ quy.
  * `RA (Recursion Available)`: Server đặt `1` để báo có hỗ trợ đệ quy.
  * `RCODE (Response Code)`: Mã lỗi trả về (`0`: Không lỗi, `3`: **NXDOMAIN** - Tên miền không tồn tại).

---

## 8. Các Nguy Cơ Bảo Mật & Công Nghệ Hiện Đại Của DNS

1. **DNS Spoofing / Cache Poisoning (Đầu độc bộ nhớ đệm DNS):**
   * Kẻ tấn công đoán đúng Transaction ID và gửi câu trả lời giả mạo về Local DNS Server trước khi server thật kịp phản hồi.
   * Local DNS lưu IP giả mạo vào Cache $\rightarrow$ Mọi người dùng trong mạng khi gõ `facebook.com` đều bị điều hướng sang trang web lừa đảo của hacker.
   * *Giải pháp phòng chống:* **DNSSEC (Domain Name System Security Extensions)** — ký số mã hóa cho từng bản ghi DNS để xác thực nguồn gốc dữ liệu.
2. **DDoS vào Root Servers:** Kẻ tấn công dùng mạng botnet khổng lồ bắn bão gói tin UDP vào các Root Server. Kỹ thuật Anycast hiện nay đã giúp phân tán tải và dập tắt các cuộc tấn công này hiệu quả.
3. **Quyền Riêng Tư & Sự Ra Đời Của DoH / DoT:**
   * DNS truyền thống chạy qua UDP 53 hoàn toàn là **văn bản thô (Plaintext)**. Nhà mạng (ISP) và kẻ nghe lén trên Wi-Fi có thể theo dõi chính xác từng website bạn truy cập.
   * **DoH (DNS-over-HTTPS - RFC 8484):** Bọc các truy vấn DNS bên trong kết nối HTTPS (TLS port 443). Mọi truy vấn tên miền bị mã hóa, nhà mạng chỉ nhìn thấy một kết nối HTTPS bình thường.

---

## 9. Vận Dụng Sáng Tạo Trong Đồ Án OpenGuard Kids

Trong OpenGuard Kids, thành phần **DNS Proxy ([05_dns_proxy_safesearch_doh.md](file:///home/cornar/Projects/OpenGuard-Kids/docs/components/05_dns_proxy_safesearch_doh.md))** là "trái tim" bảo vệ trẻ em trên không gian mạng:

1. **Local DNS Interception (Lắng nghe tại `127.0.0.1:53`):**
   * Windows Service cấu hình Windows Adapter để trỏ DNS cục bộ về `127.0.0.1`.
   * Mọi yêu cầu tra cứu từ Chrome, Edge, game đều phải đi qua DNS Proxy của OpenGuard Kids.
2. **Canary Domain Vô Hiệu Hóa DoH của Trình Duyệt:**
   * Các trình duyệt hiện đại (Firefox, Chrome) tự động kích hoạt DoH để vượt mặt DNS máy tính.
   * OpenGuard Kids áp dụng chuẩn RFC: Bắt trọn truy vấn tên miền canary `use-application-dns.net` và trả về ngay mã lỗi **`NXDOMAIN` (RCODE = 3)**. Trình duyệt nhận được tín hiệu này sẽ tự động tắt DoH và quay về sử dụng DNS của hệ thống!
3. **SafeSearch Injection Bằng Bản Ghi CNAME:**
   * Khi trẻ tìm kiếm trên Google: Trả về bản ghi `CNAME: forcesafesearch.google.com`.
   * Khi trẻ xem video trên YouTube: Trả về bản ghi `CNAME: restrict.youtube.com`.
   * Trình duyệt buộc phải phân giải tiếp CNAME này sang dải IP an toàn của Google, ép bật tính năng lọc video bạo lực/nội dung người lớn 100%.
4. **Điều Hướng Sang Local Blockpage Server ([06_polite_blockpage_server.md](file:///home/cornar/Projects/OpenGuard-Kids/docs/components/06_polite_blockpage_server.md)):**
   * Khi trẻ truy cập các trang web độc hại nằm trong Blacklist, DNS Proxy không gửi ra Internet mà trả về ngay bản ghi **`Type A` trỏ về `127.0.0.1:8080`**. Trình duyệt mở ra trang web giáo dục lịch sự kèm đường dây nóng bảo vệ trẻ em Hotline 111.

