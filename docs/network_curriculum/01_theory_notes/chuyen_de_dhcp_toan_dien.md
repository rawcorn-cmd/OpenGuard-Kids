# Chuyên Đề Nghiên Cứu Chuyên Sâu: Giao Thức DHCP (Dynamic Host Configuration Protocol)

> **Kho tri thức mạng máy tính:** Môn Mạng Máy Tính (HCMUS / Kurose & Ross Top-Down Approach)  
> **Chuyên đề:** Cấp phát địa chỉ IP động — Giao thức DHCP, Quy trình DORA, Cơ chế thuê/gia hạn và Bảo mật mạng LAN.  
> **Tài liệu liên quan trong đồ án:** [05_dns_proxy_safesearch_doh.md](file:///home/cornar/Projects/OpenGuard-Kids/docs/components/05_dns_proxy_safesearch_doh.md), [14_fail_open_philosophy_child_rights.md](file:///home/cornar/Projects/OpenGuard-Kids/docs/components/14_fail_open_philosophy_child_rights.md).  
> **Thực hành liên quan:** [wireshark_dhcp_v8.0.md](file:///home/cornar/Projects/OpenGuard-Kids/docs/network_curriculum/03_wireshark_labs/wireshark_dhcp_v8.0.md).

---

## 1. Bản Chất và Vai Trò của DHCP

Trong môi trường mạng có nhiều thiết bị di động (laptop, smartphone ra vào liên tục), việc cấu hình địa chỉ IP thủ công (**Static IP**) bộc lộ nhiều nhược điểm nghiêm trọng:
* Dễ nhầm lẫn dẫn đến hiện tượng **Xung đột IP (IP Conflict)**.
* Lãng phí tài nguyên địa chỉ khi người dùng đã ngắt kết nối nhưng IP vẫn bị "giữ chỗ".
* Khó quản lý khi thay đổi Default Gateway hoặc DNS Server trên quy mô toàn mạng.

👉 **DHCP** là giao thức **Plug-and-Play (Cắm vào là chạy)**, cho phép thiết bị khi tham gia mạng tự động nhận được:
1. **Địa chỉ IPv4 của chính nó** (*Client IP address*).
2. **Subnet Mask** (Mặt nạ mạng con để xác định dải mạng nội bộ).
3. **Default Gateway** (Địa chỉ IP của Router biên để định tuyến ra ngoài Internet).
4. **DNS Servers** (Máy chủ phân giải tên miền để tra cứu IP từ domain).

---

## 2. Nghịch Lý Vị Trí Tầng Mạng: DHCP Nằm Ở Đâu?

> ⚠️ **Điểm cốt lõi cần nhớ:** Dù phục vụ cấu hình tham số cho **Tầng Network (Tầng 3)**, nhưng bản thân DHCP được cài đặt và vận hành hoàn toàn ở **TẦNG APPLICATION (Tầng Ứng dụng)** trên nền giao thức **UDP**:
* **DHCP Server** lắng nghe tại cổng: **UDP port 67**.
* **DHCP Client** lắng nghe tại cổng: **UDP port 68**.

### Cơ chế gửi gói tin khi Client chưa có IP
Client sử dụng các địa chỉ đặc biệt ở header tầng Transport và Network:
* **Source IP:** `0.0.0.0` (Biểu thị máy gửi chưa có địa chỉ IP hợp lệ).
* **Destination IP:** `255.255.255.255` (Địa chỉ Broadcast toàn mạng LAN nội bộ, các Router biên sẽ chặn không cho gói tin này đi ra Internet).
* **Destination MAC:** `FF:FF:FF:FF:FF:FF` (Broadcast tầng liên kết dữ liệu / Ethernet).

---

## 3. Quy Trình 4 Bước Kinh Điển: D-O-R-A

```
       DHCP Client                                            DHCP Server
 (Vừa kết nối, chưa có IP)                                   (Router/Server)
            |                                                        |
            | ----- 1. DHCP DISCOVER (Broadcast) ------------------> |
            |       src: 0.0.0.0:68                                  |
            |       dest: 255.255.255.255:67                         |
            |       Transaction ID: 0x654321                         |
            |                                                        |-- Chọn IP rảnh trong Pool:
            |                                                        |-- 192.168.1.105
            |                                                        |
            | <---- 2. DHCP OFFER (Broadcast / Unicast) ------------ |
            |       src: 192.168.1.1:67                              |
            |       dest: 255.255.255.255:68                         |
            |       yiaddr (Your IP): 192.168.1.105                  |
            |       IP Lease Time: 86400s (24 giờ)                   |
            |                                                        |
            | ----- 3. DHCP REQUEST (Broadcast) -------------------> |
            |       src: 0.0.0.0:68                                  |
            |       dest: 255.255.255.255:67                         |
            |       Server Identifier: 192.168.1.1                   |
            |       Requested IP: 192.168.1.105                      |
            |                                                        |
            | <---- 4. DHCP ACK (Broadcast / Unicast) -------------- |
            |       src: 192.168.1.1:67                              |
            |       dest: 255.255.255.255:68                         |
            |       yiaddr: 192.168.1.105                            |
            |       Subnet Mask: 255.255.255.0                       |
            |       Router (Gateway): 192.168.1.1                    |
            |       DNS Server: 8.8.8.8                              |
            |                                                        |
[Client chính thức cấu hình IP 192.168.1.105 vào card mạng]
```

### Chi tiết các trường thông tin trong D-O-R-A:

1. **DHCP DISCOVER (Khám phá):**
   * Client broadcast gói tin tìm kiếm bất kỳ DHCP Server nào đang hoạt động trong mạng LAN.
   * Mang theo một mã số giao dịch ngẫu nhiên (**Transaction ID**) để đối chiếu các phản hồi sau này.
2. **DHCP OFFER (Đề xuất):**
   * Mỗi DHCP Server nhận được Discover sẽ chọn một IP còn rỗi trong dải cấp phát (*IP Pool*), tạm khóa IP đó lại và gửi Offer kèm thông số:
     * `yiaddr` (*Your IP Address*): Địa chỉ IP đề xuất cho máy khách.
     * `IP Address Lease Time`: Thời gian cho phép thuê IP (ví dụ: 86400 giây = 1 ngày).
3. **DHCP REQUEST (Yêu cầu nhận IP):**
   * *Tại sao bước này vẫn gửi Broadcast?* Vì trong mạng LAN có thể có nhiều DHCP Server cùng trả về Offer. Khi Client chọn Server nào, nó sẽ broadcast công khai tên của Server đó (`Server Identifier`).
   * Việc broadcast giúp các Server còn lại biết mình đã bị từ chối, từ đó mở khóa và thu hồi IP đề xuất về lại kho cho thiết bị khác.
4. **DHCP ACK (Xác nhận chốt hợp đồng):**
   * Server được chọn gửi gói ACK chốt hợp đồng thuê IP, kèm toàn bộ cấu hình mạng: IP, Subnet Mask, Gateway, DNS.

---

## 4. Quá Trình Thuê, Gia Hạn & Giải Phóng IP (Lease Lifecycle)

Địa chỉ IP do DHCP cấp **mang tính chất thuê mượn có thời hạn**:

* **Mốc $50\%$ thời hạn thuê ($T_1$ - Renewing):**
  * Client tự động gửi một gói tin `DHCP REQUEST` trực tiếp dạng **Unicast** đến đúng Server đã cấp IP để xin gia hạn.
  * Nếu Server phản hồi `DHCP ACK`, thời hạn thuê được reset lại $100\%$.
* **Mốc $87.5\%$ thời hạn thuê ($T_2$ - Rebinding):**
  * Nếu Server cũ không phản hồi (do sập nguồn hoặc đứt cáp), Client sẽ phát **Broadcast** `DHCP REQUEST` ra toàn mạng để tìm bất kỳ DHCP Server nào khác trong mạng xin gia hạn hoặc cấp mới.
* **Mốc $100\%$ thời hạn (Expiration):**
  * Nếu không được gia hạn, Client **buộc phải giải phóng IP ngay lập tức** và dừng mọi hoạt động giao tiếp mạng cho đến khi thực hiện xong chu trình DORA mới.
* **DHCP RELEASE (Giải phóng chủ động):**
  * Khi người dùng ngắt kết nối mạng hoặc gõ lệnh `ipconfig /release`, Client gửi gói `DHCP RELEASE` lên Server để trả lại địa chỉ IP vào Pool.

---

## 5. DHCP Relay Agent (Khi Client và Server Khác Subnet)

* Gói tin Broadcast `255.255.255.255` không bao giờ đi qua được Router (Router là ranh giới phân tách Broadcast Domain).
* Nếu doanh nghiệp có nhiều mạng con (Subnet/VLAN), họ không cần phải dựng mỗi Subnet một máy chủ DHCP vật lý.
* 👉 **DHCP Relay Agent:** Tính năng này được kích hoạt trên Router biên của mỗi Subnet. Khi Router bắt được gói tin Discover broadcast từ Client, nó sẽ bọc lại thành gói tin **Unicast** có địa chỉ đích là IP của máy chủ DHCP trung tâm.

---

## 6. Các Nguy Cơ An Ninh Mạng với DHCP

1. **Rogue DHCP Server (Máy chủ DHCP Giả Mạo):**
   * Kẻ tấn công dựng một DHCP server giả trong mạng LAN và phản hồi gói Offer nhanh hơn Server thật.
   * Server giả này cấp Default Gateway và DNS Server trỏ về máy của hacker $\rightarrow$ Thực hiện tấn công **Man-in-the-Middle (MitM)** nghe lén toàn bộ dữ liệu người dùng.
   * *Giải pháp phòng chống:* Tính năng **DHCP Snooping** trên Switch (chỉ cho phép các cổng Switch đáng tin cậy - *Trusted Ports* mới được gửi gói tin DHCP Server).
2. **DHCP Starvation Attack (Tấn công làm cạn kiệt IP Pool):**
   * Hacker dùng công cụ giả lập hàng nghìn địa chỉ MAC ảo khác nhau, liên tục gửi hàng loạt gói DHCP Discover để xin hết sạch địa chỉ IP trong Pool, khiến người dùng thật không thể kết nối mạng (Tấn công DoS mạng nội bộ).
   * *Giải pháp phòng chống:* Tính năng **Port Security** trên Switch (giới hạn số lượng MAC trên mỗi cổng mạng).

---

## 7. Mối Liên Hệ Thực Tế Với Đồ Án OpenGuard Kids

1. **Can thiệp và Ghi đè DNS do DHCP cấp ([05_dns_proxy_safesearch_doh.md](file:///home/cornar/Projects/OpenGuard-Kids/docs/components/05_dns_proxy_safesearch_doh.md)):**
   * Bình thường, card mạng nhận cấu hình DNS từ Router qua DHCP.
   * Windows Service của OpenGuard Kids can thiệp vào Windows Network Adapter, đổi DNS từ *"Obtain automatically (DHCP)"* sang **Static DNS `127.0.0.1`** để bắt trọn lưu lượng phân giải tên miền vào bộ lọc phụ huynh.
2. **Triết lý Khôi phục Hệ thống (Fail-Open - [14_fail_open_philosophy_child_rights.md](file:///home/cornar/Projects/OpenGuard-Kids/docs/components/14_fail_open_philosophy_child_rights.md)):**
   * Khi phụ huynh gỡ cài đặt phần mềm hoặc Service dừng hoạt động, phần mềm tự động khôi phục card mạng về trạng thái **DHCP động** ban đầu. Nhờ đó, máy tính của trẻ vẫn nhận lại DNS của router nhà và lướt web bình thường mà không bị mất mạng.

