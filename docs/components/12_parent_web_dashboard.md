# THÀNH PHẦN 12: BẢNG ĐIỀU KHIỂN PHỤ HUYNH PARENT WEB DASHBOARD

> **Mô-đun:** [`src/server/app.py`](file:///home/cornar/Projects/OpenGuard-Kids/src/server/app.py) & Giao diện Web Templates  
> **Công nghệ giao diện:** HTML5 Responsive, Jinja2 Templates, HTMX, CSS3 Flexbox/Grid  
> **Tương thích:** Trình duyệt máy tính (Desktop) & Màn hình cảm ứng điện thoại (Mobile)

---

## 1. Nền Tảng Công Cụ & Framework Kỹ Thuật

Bảng điều khiển phụ huynh được thiết kế theo phong cách hiện đại, trực quan và tối ưu hóa trải nghiệm trên điện thoại thông minh:

1. **Thư viện HTMX (High-Power Tools for HTML):**
   * Cho phép cập nhật động từng phần của trang web (Partial Page Updates) qua AJAX mà không cần viết các khung JavaScript cồng kềnh như React hay Angular.
   * Giúp việc duyệt đơn xin thêm giờ của con diễn ra mượt mà, tức thì ngay trên dòng danh sách mà không phải tải lại toàn bộ trang web.
2. **Thiết Kế Thích Ứng Di Động (Mobile-First Responsive Layout):**
   * Sử dụng CSS3 Viewport, Media Queries và Flexbox/Grid.
   * Cha mẹ có thể mở Dashboard trên điện thoại iPhone/Android qua trình duyệt Safari/Chrome với giao diện thẻ (Card-based UI) trực quan, các nút bấm to rõ, dễ thao tác bằng một ngón tay cái.
3. **Thư Viện Biểu Đồ Nhẹ (SVG Data Visualizations):**
   * Vẽ biểu đồ thanh (Bar chart) tổng thời lượng sử dụng và biểu đồ tròn phân bố ứng dụng bằng mã SVG nhúng trực tiếp, tải siêu nhanh và không tốn tài nguyên máy chủ.

---

## 2. Chức Năng Cốt Lõi

* **Trung Tâm Điều Khiển Thời Gian Thực:** Cung cấp các nút bấm can thiệp nhanh: *"Khóa máy ngay"*, *"Mở khóa"*, *"Cộng thêm 15 phút"*.
* **Báo Cáo Thống Kê Trực Quan:** Hiển thị tổng thời gian sử dụng trong ngày so với hạn ngạch cho phép, kèm biểu đồ xu hướng 7 ngày gần nhất.
* **Bảng Xếp Hạng Top Ứng Dụng & Tên Miền:** Tổng hợp thời lượng sử dụng của các phần mềm và website được dùng nhiều nhất, giúp cha mẹ hiểu sở thích của con mà không xâm phạm quyền riêng tư chi tiết.
* **Hòm Thư Xử Lý Yêu Cầu Của Con (Child Request Inbox):** Tiếp nhận các đề xuất xin thêm 15 phút hoặc báo cáo chặn nhầm từ trẻ kèm hai nút lựa chọn *"Duyệt"* hoặc *"Từ chối"*.

---

## 3. Cơ Chế Vận Hành Chuyên Sâu

### 3.1. Cấu Trúc Bố Cục Giao Diện Dashboard

```
+-------------------------------------------------------------------------+
| [Logo OpenGuard Kids]  Xin chào: Phụ huynh Nguyễn Văn A      [Đăng Xuất]|
+-------------------------------------------------------------------------+
| THIẾT BỊ: Laptop Học Tập (Con: Bé Nam - 10 tuổi)    [Trạng thái: ONLINE]|
|                                                                         |
| [KHÓA MÁY NGAY]         [MỞ KHÓA]         [TẶNG +15 PHÚT DÙNG MÁY]      |
+-------------------------------------------------------------------------+
| [ BIỂU ĐỒ HÔM NAY ]                    | [ HÒM THƯ DUYỆT CỦA CON ]      |
| Đã dùng: 1h 45m / Hạn ngạch: 2h 00m    |                                |
| [========================......] 87%   | * 17:30: Xin thêm 15 phút      |
|                                        |   Lý do: "Làm nốt bài tiếng Anh"|
| Xu hướng 7 ngày: [T2][T3][T4][T5][T6]  |   [ ĐỒNG Ý ]    [ TỪ CHỐI ]    |
+----------------------------------------+--------------------------------+
| TOP 5 ỨNG DỤNG SỬ DỤNG NHIỀU NHẤT      | TOP 5 WEBSITE TRUY CẬP         |
| 1. Microsoft Word (55 phút)            | 1. scratch.mit.edu (40 phút)   |
| 2. Scratch 3 Desktop (35 phút)         | 2. hoc247.net (25 phút)        |
| 3. Chrome Browser (15 phút)            | 3. google.com (10 phút)        |
+-------------------------------------------------------------------------+
| [CÀI ĐẶT NÂNG CAO]                     | [VÙNG NGUY HIỂM]               |
| Chỉnh hạn ngạch & Lịch tuần            | [ XÓA TOÀN BỘ DỮ LIỆU CỦA CON ]|
+-------------------------------------------------------------------------+
```

### 3.2. Cơ Chế Cập Nhật Động Bằng HTMX
Khi phụ huynh bấm nút "ĐỒNG Ý" trên một yêu cầu xin giờ trong hòm thư:
```html
<div id="request-box-123">
  <p>Bé Nam: "Em xin thêm 15 phút để làm nốt bài tập"</p>
  <button 
    hx-post="/api/requests/123/approve" 
    hx-target="#request-box-123" 
    hx-swap="outerHTML"
    class="btn-approve">
    Đồng Ý Duyệt (+15m)
  </button>
</div>
```
* Trình duyệt gửi yêu cầu `POST /api/requests/123/approve` ngầm.
* Server duyệt yêu cầu, kích hoạt lệnh WebSocket đẩy xuống máy con, và trả về đoạn HTML xác nhận: `<div class="badge-success">&#10003; Đã duyệt thành công và cộng giờ cho con!</div>`.
* Đoạn mã trên thay thế trực tiếp vào vị trí nút bấm mà không làm giật hay tải lại trang.

---

## 4. Cách Liên Kết Với Các Thành Phần Khác

1. **Với FastAPI Server (Thành phần 9):** Là giao diện thể hiện dữ liệu được cấp phát từ tầng ORM và REST API.
2. **Với WebSocket Hub (Thành phần 11):** Gửi các tín hiệu điều khiển khẩn cấp trực tiếp xuống luồng socket của máy con.
3. **Với Xóa Kép Nguyên Tử (Thành phần 13):** Cung cấp nút bấm màu đỏ "Xóa toàn bộ dữ liệu của con" với hộp thoại xác nhận 2 bước an toàn.

