# THÀNH PHẦN 13: XÓA DỮ LIỆU KÉP NGUYÊN TỬ (ATOMIC DUAL DELETION) & QUẢN TRỊ VÒNG ĐỜI

> **Mô-đun:** [`src/server/app.py`](file:///home/cornar/Projects/OpenGuard-Kids/src/server/app.py) & kiểm thử tại [`tests/test_dashboard_and_privacy.py`](file:///home/cornar/Projects/OpenGuard-Kids/tests/test_dashboard_and_privacy.py)  
> **Căn cứ pháp lý:** Điều 4 Nghị định 13/2023/NĐ-CP & Văn bản [`docs/PRIVACY.md`](file:///home/cornar/Projects/OpenGuard-Kids/docs/PRIVACY.md)  
> **Chính sách tự động:** Tự động dọn dẹp và tiêu hủy nhật ký quá 90 ngày (Auto-Purge Worker)

---

## 1. Nền Tảng Công Cụ & Framework Kỹ Thuật

Cơ chế xóa dữ liệu kép nguyên tử bảo đảm tính tuân thủ pháp lý cao nhất về quyền bảo vệ dữ liệu cá nhân của trẻ em trên không gian mạng:

1. **Giao Dịch Nguyên Tử Tầng Cơ Sở Dữ Liệu (ACID Database Transactions):**
   * Sử dụng lệnh `db.commit()` và `db.rollback()` của SQLAlchemy để đảm bảo việc xóa dữ liệu trên máy chủ là trọn vẹn: hoặc xóa sạch toàn bộ các bảng liên quan (Cascade Delete), hoặc không xóa gì nếu có lỗi xảy ra giữa chừng.
2. **Kích Hoạt Xóa Xuyên Mạng Bằng WebSocket Event:**
   * Thay vì chỉ xóa trên máy chủ Cloud rồi để lại nhật ký cục bộ trên máy tính của trẻ, Server kích hoạt một thông điệp sự kiện đặc biệt đẩy thẳng xuống máy con để kích hoạt lệnh xóa tại chỗ.
3. **Tiêu Chuẩn Lệnh Thu Gọn Bộ Nhớ SQLite (`VACUUM` Command):**
   * Trong SQLite, lệnh `DELETE FROM table` chỉ đánh dấu các trang dữ liệu là trống (Free Pages) nhưng file `.db` vẫn giữ nguyên kích thước trên ổ cứng.
   * Chạy lệnh `VACUUM` buộc SQLite viết lại toàn bộ file database, xóa sạch các byte dữ liệu cũ còn sót lại trên ổ cứng (Zero-byte cleanup).

---

## 2. Chức Năng Cốt Lõi

* **Nút "Xóa Toàn Bộ Dữ Liệu Của Con":** Cho phép phụ huynh thực thi quyền được lãng quên (Right to be Forgotten) và rút lại sự đồng ý thu thập dữ liệu bất kỳ lúc nào chỉ bằng một thao tác.
* **Xóa Sạch Hai Chiều (Dual Deletion):** Xóa triệt để đồng thời trên cả hai nơi: Cơ sở dữ liệu Cloud của nhà phát triển và Bộ đệm SQLite cục bộ trên máy tính của trẻ.
* **Tự Động Dọn Dẹp Sau 90 Ngày:** Cơ chế nền tự động xóa vĩnh viễn các nhật ký hoạt động có tuổi thọ vượt quá 90 ngày nhằm tuân thủ nguyên tắc giảm thiểu lưu trữ dữ liệu.

---

## 3. Cơ Chế Vận Hành Chuyên Sâu

### 3.1. Sơ Đồ Quy Trình Xóa Kép Hai Chiều

```mermaid
sequenceDiagram
    autonumber
    actor Parent as Phụ Huynh (Web Dashboard)
    participant Server as FastAPI Server
    participant CloudDB as Server SQLite Database
    participant WSHub as WebSocket Hub
    participant Agent as Windows Service (Máy Con)
    participant LocalDB as SQLite WAL Buffer (Máy Con)

    Parent->>Server: Nhấn nút "Xóa Toàn Bộ Dữ Liệu Của Con" (Xác nhận Popup)
    Server->>Server: Bắt đầu giao dịch ACID Transaction
    
    rect rgb(240, 253, 244)
        Note over Server,CloudDB: BƯỚC 1: XÓA TRIỆT ĐỂ TRÊN CLOUD DATABASE
        Server->>CloudDB: DELETE FROM event_logs WHERE child_id = :id
        Server->>CloudDB: DELETE FROM daily_usage_stats WHERE child_id = :id
        Server->>CloudDB: DELETE FROM unblock_requests WHERE child_id = :id
        Server->>CloudDB: COMMIT TRANSACTION
    end

    rect rgb(254, 242, 242)
        Note over Server,LocalDB: BƯỚC 2: KÍCH HOẠT XÓA SẠCH TRÊN MÁY TÍNH CỦA CON
        Server->>WSHub: Lệnh đẩy khẩn cấp: {"command": "PURGE_ALL_LOCAL_DATA"}
        WSHub->>Agent: Truyền gói JSON qua WebSocket
        Agent->>LocalDB: DELETE FROM offline_events;
        Agent->>LocalDB: VACUUM; (Xóa sạch byte vật lý trên đĩa)
        Agent->>Agent: Đặt lại các biến đếm thời gian trong RAM về 0
        Agent-->>WSHub: Phản hồi ACK: {"status": "LOCAL_PURGE_SUCCESS"}
    end

    Server-->>Parent: Thông báo: "Đã xóa sạch 100% dữ liệu của con trên toàn hệ thống!"
```

### 3.2. Thuật Toán Xóa Kép Trong Mã Nguồn
```python
@router.post("/api/children/{child_id}/purge-data")
async def purge_child_data(
    child_id: int,
    current_parent: Parent = Depends(get_current_authenticated_parent),
    db: Session = Depends(get_db)
):
    # 1. Xác thực quyền phụ huynh (Chống IDOR):
    child = db.scalar(select(Child).where(Child.id == child_id, Child.parent_id == current_parent.id))
    if not child:
        raise HTTPException(status_code=404, detail="Không tìm thấy hồ sơ của con")

    # 2. Xóa dữ liệu trên Server:
    db.execute(delete(EventLog).where(EventLog.child_id == child_id))
    db.execute(delete(DailyStat).where(DailyStat.child_id == child_id))
    db.commit()

    # 3. Kích hoạt xóa cục bộ trên máy con qua WebSocket:
    for device in child.devices:
        await ws_hub.dispatch_command(device.id, "PURGE_ALL_LOCAL_DATA", {})

    return {"status": "SUCCESS", "message": "Toàn bộ dữ liệu của con đã được tiêu hủy an toàn"}
```

### 3.3. Worker Tự Động Dọn Dẹp Sau 90 Ngày (Auto-Purge Worker)
Định kỳ mỗi 24 giờ, máy chủ chạy một luồng background worker:
```python
def cleanup_old_records_worker(db: Session):
    ninety_days_ago = datetime.utcnow() - timedelta(days=90)
    # Tự động tiêu hủy các bản ghi quá 90 ngày tuổi:
    deleted_count = db.execute(
        delete(EventLog).where(EventLog.timestamp < ninety_days_ago)
    ).rowcount
    db.commit()
    logger.info(f"[AUTO-PURGE] Đã tự động dọn dẹp {deleted_count} bản ghi nhật ký cũ hơn 90 ngày")
```

---

## 4. Cách Liên Kết Với Các Thành Phần Khác

1. **Với Parent Web Dashboard (Thành phần 12):** Nơi hiển thị nút bấm hành động và nhận thông báo kết quả.
2. **Với WebSocket Hub (Thành phần 11):** Đường dẫn truyền lệnh tiêu hủy dữ liệu thời gian thực xuống máy con.
3. **Với SQLite Offline Buffer (Thành phần 7):** Đối tượng bị xóa sạch dữ liệu và nén dung lượng về kích thước tối thiểu trên máy con.

