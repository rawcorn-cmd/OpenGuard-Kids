# THÀNH PHẦN 09: MÁY CHỦ QUẢN TRỊ TRUNG TÂM FASTAPI & BẢO MẬT ORM

> **Mô-đun:** [`src/server/app.py`](file:///home/cornar/Projects/OpenGuard-Kids/src/server/app.py)  
> **Framework:** FastAPI, Starlette, Uvicorn ASGI  
> **ORM & Cơ sở dữ liệu:** SQLAlchemy 2.0, SQLite (WAL mode)  
> **Bảo mật mật mã:** Argon2id (RFC 9106), HttpOnly Cookies, IDOR Mitigation

---

## 1. Nền Tảng Công Cụ & Framework Kỹ Thuật

Máy chủ trung tâm OpenGuard Kids được thiết kế theo tiêu chuẩn API hiện đại, an toàn và có khả năng mở rộng cao:

1. **Framework FastAPI & Uvicorn ASGI Web Server:**
   * FastAPI tận dụng chuẩn gợi ý kiểu (Python Type Hints) và Pydantic để tự động xác thực dữ liệu đầu vào (Input Validation), ngăn chặn các cuộc tấn công tiêm mã (Injection Attacks).
   * Uvicorn cung cấp máy chủ web bất đồng bộ tốc độ cao trên chuẩn ASGI, xử lý đồng thời hàng nghìn kết nối mà không bị nghẽn luồng.
2. **Hệ Thống Băm Mật Khẩu Tiên Tiến Argon2id (RFC 9106):**
   * Là thuật toán chiến thắng trong cuộc thi băm mật khẩu quốc tế (Password Hashing Competition).
   * Argon2id kết hợp cả khả năng chống tấn công kênh bên (Side-channel attacks) và chống vét cạn bằng phần cứng GPU chuyên dụng thông qua cấu hình chi phí bộ nhớ cao:
     * `memory_cost = 65536 KB` (64 MB RAM cho mỗi lần tính toán hash).
     * `time_cost = 2` (2 vòng lặp tính toán).
     * `parallelism = 1`.
3. **ORM SQLAlchemy 2.0 (Declarative Mapping):**
   * Sử dụng cơ chế tham số hóa truy vấn (Parameterized Queries) 100%, triệt tiêu hoàn toàn nguy cơ tấn công SQL Injection.

---

## 2. Chức Năng Cốt Lõi

* **Quản Trị Người Dùng & Phân Quyền Gia Đình:** Quản lý tài khoản phụ huynh, hồ sơ các con và các thiết bị máy tính liên kết.
* **Cung Cấp REST API Đồng Bộ Dữ Liệu:** Tiếp nhận gói tin sự kiện định kỳ từ các máy con và cung cấp chính sách quản lý (Hạn ngạch, Lịch tuần, Danh sách cấm).
* **Phòng Chống Lỗ Hổng IDOR (Insecure Direct Object Reference):** Đảm bảo phụ huynh của gia đình này tuyệt đối không thể đọc hay can thiệp vào dữ liệu của con thuộc gia đình khác.

---

## 3. Cơ Chế Vận Hành Chuyên Sâu

### 3.1. Cơ Chế Triệt Tiêu Lỗ Hổng IDOR Ở Tầng ORM
Một lỗi bảo mật nghiêm trọng trong các hệ thống quản lý học sinh/trẻ em là phụ huynh đổi ID trên thanh URL (Ví dụ: từ `/child/1` thành `/child/2`) để xem trộm con nhà khác.  
OpenGuard Kids triệt tiêu hoàn toàn nguy cơ này bằng cách luôn gắn chặt ID của phụ huynh đang đăng nhập vào câu truy vấn cơ sở dữ liệu:

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select

router = APIRouter()

@router.get("/api/children/{child_id}/stats")
def get_child_stats(
    child_id: int, 
    current_parent: Parent = Depends(get_current_authenticated_parent),
    db: Session = Depends(get_db)
):
    # RÀNG BUỘC CỐT LÕI: Phải thỏa mãn CẢ child_id VÀ parent_id của phiên đăng nhập
    stmt = select(Child).where(
        Child.id == child_id,
        Child.parent_id == current_parent.id  # TRIỆT TIÊU HOÀN TOÀN IDOR
    )
    child = db.scalar(stmt)
    
    if not child:
        # Trả về 404 Not Found thay vì 403 để không tiết lộ sự tồn tại của ID
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy hồ sơ của con")
        
    return child.get_aggregated_stats()
```

### 3.2. Quản Trị Phiên Làm Việc Qua Cookie Bảo Mật
Sau khi phụ huynh đăng nhập thành công bằng mật khẩu băm Argon2id:
* Server sinh một chuỗi Session Token cryptographically random dài 32 bytes hex.
* Đặt Cookie phản hồi với 3 thuộc tính cấm kỵ vi phạm:
  * `HttpOnly = True`: Ngăn chặn mã độc JavaScript chạy trên trình duyệt truy cập vào cookie (Chống XSS Session Hijacking).
  * `SameSite = 'Lax'`: Trình duyệt từ chối gửi cookie trong các yêu cầu chuyển hướng từ website độc hại bên ngoài (Chống CSRF Attack).
  * `Secure = True`: Chỉ truyền cookie qua kênh mã hóa HTTPS bảo mật.

---

## 4. Cách Liên Kết Với Các Thành Phần Khác

1. **Với Windows Service (Thành phần 1):** Tiếp nhận các kết nối đồng bộ HTTPS và cấp phát cấu hình bảo vệ.
2. **Với Kênh Ghép Đôi Thiết Bị (Thành phần 10):** Sinh và xác thực mã PIN 8 ký tự khi phụ huynh liên kết máy tính mới.
3. **Với WebSocket Hub (Thành phần 11):** Là tầng lưu trữ và quản lý phiên để chuyển tiếp lệnh điều khiển tới WebSocket router.
4. **Với Parent Web Dashboard (Thành phần 12):** Cung cấp toàn bộ dữ liệu thống kê, biểu đồ và hòm thư duyệt thông qua API hoặc Server-side HTML Rendering.

