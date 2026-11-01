# THÀNH PHẦN 06: MÁY CHỦ TRANG CHẶN GIÁO DỤC POLITE BLOCKPAGE (PORT 8080)

> **Mô-đun:** [`src/agent/blockpage.py`](file:///home/cornar/Projects/OpenGuard-Kids/src/agent/blockpage.py)  
> **Giao thức:** HTTP trên giao diện Loopback `127.0.0.1:8080`  
> **Nguyên tắc nhân văn:** NT4 (Chặn phải giải thích được), NT3 (Trẻ có tiếng nói), NT6 (Tổng đài cứu trợ 111)

---

## 1. Nền Tảng Công Cụ & Framework Kỹ Thuật

Trang chặn giáo dục Polite Blockpage được thiết kế theo triết lý "Sư phạm tích cực", thay thế hoàn toàn thông điệp lỗi mạng khô khan của trình duyệt:

1. **Micro HTTP Server Bằng Thư Viện Chuẩn Python:**
   * Sử dụng `http.server.HTTPServer` hoặc máy chủ HTTP phi đồng bộ gắn vào tiến trình Service.
   * Dung lượng bộ nhớ cực thấp (< 5MB RAM), phục vụ trang web tĩnh được nhúng sẵn (Inlined HTML/CSS) mà không cần nạp file từ bên ngoài.
2. **Thiết Kế Giao Diện HTML5 Thân Thiện (Child-Centric Responsive UI):**
   * Sử dụng màu sắc nhẹ nhàng (xanh dương pastel và vàng cam ấm áp), tránh màu đỏ rực mang tính dọa nạt hoặc trừng phạt.
   * Icon vector SVG minh họa rõ ràng nội dung lý do bị chặn.
3. **Cơ Chế Phản Hồi Tức Thời (Form Action via Local REST API):**
   * Tích hợp form gửi yêu cầu đối chiếu trực tiếp về Loopback IPC của hệ thống.

---

## 2. Chức Năng Cốt Lõi

* **Giải Thích Rõ Ràng Lý Do Chặn:** Thông báo minh bạch cho trẻ biết website bị chặn vì lý do gì (Ví dụ: *Nội dung bạo lực*, *Trò chơi cờ bạc*, hoặc *Đã hết giờ dùng máy tính*).
* **Nút "Báo Chặn Nhầm" (Child Agency Button):** Cho phép trẻ gửi yêu cầu xem xét lại một trang web học tập bị hệ thống chặn nhầm trực tiếp lên Dashboard của cha mẹ.
* **Tích Hợp Cứu Trợ Khẩn Cấp Quốc Gia (Tổng Đài 111):** Luôn hiện diện số điện thoại và nút bấm gọi đường dây nóng bảo vệ trẻ em quốc gia để trẻ liên hệ trong mọi trường hợp khẩn cấp.

---

## 3. Cơ Chế Vận Hành Chuyên Sâu

### 3.1. Luồng Điều Hướng Từ DNS Tới Blockpage
1. Trẻ gõ trên trình duyệt: `http://bad-website.com`.
2. DNS Proxy chặn tên miền và trả về địa chỉ IP `127.0.0.1`.
3. Trình duyệt gửi HTTP GET tới `127.0.0.1:80` hoặc `127.0.0.1:8080` (thông qua chuyển hướng tường lửa hoặc port mapping).
4. Blockpage Server phân tích Header `Host: bad-website.com` để trích xuất tên miền đang bị truy cập.
5. Render động mã HTML chứa thông tin cá nhân hóa cho tên miền đó và trả về Client kèm mã trạng thái `HTTP 200 OK`.

### 3.2. Cấu Trúc Mã Nguồn Giao Diện Blockpage
```html
<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="UTF-8">
  <title>OpenGuard Kids — Trang Web Đã Được Tạm Khóa</title>
  <style>
    body { font-family: 'Segoe UI', Arial, sans-serif; background-color: #f0fdf4; text-align: center; padding: 40px; }
    .card { background: white; border-radius: 12px; padding: 30px; max-width: 520px; margin: 0 auto; box-shadow: 0 4px 12px rgba(0,0,0,0.08); }
    h1 { color: #0284c7; font-size: 22px; }
    .reason { background: #fef3c7; color: #b45309; padding: 10px; border-radius: 6px; font-weight: bold; }
    .btn-agency { background: #16a34a; color: white; border: none; padding: 10px 20px; border-radius: 6px; cursor: pointer; font-size: 14px; }
    .hotline { margin-top: 25px; border-top: 1px solid #e2e8f0; padding-top: 15px; color: #64748b; font-size: 13px; }
  </style>
</head>
<body>
  <div class="card">
    <img src="/static/shield.svg" width="64" alt="Shield">
    <h1>Trang web đã được tạm khóa an toàn</h1>
    <p>Trang web <strong>{blocked_domain}</strong> hiện chưa nằm trong danh mục an toàn.</p>
    <div class="reason">Lý do: {block_reason}</div>
    <p style="margin: 20px 0;">Nếu em thấy đây là trang phục vụ học tập bị chặn nhầm:</p>
    <form action="/report-unblock" method="POST">
      <input type="hidden" name="domain" value="{blocked_domain}">
      <button type="submit" class="btn-agency">Gửi Yêu Cầu "Báo Chặn Nhầm" Cho Cha Mẹ</button>
    </form>
    <div class="hotline">
      Tổng đài Quốc gia Bảo vệ Trẻ em: <strong>111</strong> (Miễn phí 24/7)
    </div>
  </div>
</body>
</html>
```

### 3.3. Xử Lý Yêu Cầu "Báo Chặn Nhầm"
* Khi trẻ bấm nút gửi, form gửi yêu cầu `POST /report-unblock` tới Blockpage Server.
* Blockpage Server chuyển tiếp yêu cầu sang `Loopback IPC` (`127.0.0.1:8765/report-unblock`).
* Yêu cầu được lưu vào hàng đợi và đồng bộ lên Cloud Server để hiển thị trong mục "Hòm thư duyệt" trên Dashboard của phụ huynh.

---

## 4. Cách Liên Kết Với Các Thành Phần Khác

1. **Với DNS Proxy (Thành phần 5):** Nhận lưu lượng HTTP chuyển hướng từ các tên miền bị chặn.
2. **Với Loopback IPC (Thành phần 2):** Tiếp nhận yêu cầu báo chặn nhầm từ trẻ và chuyển tiếp vào hàng đợi hệ thống.
3. **Với Parent Dashboard (Thành phần 12):** Hiển thị phản ánh của trẻ để cha mẹ có thể nhấn nút "Mở chặn ngay" nếu đúng là trang phục vụ bài học của con.

