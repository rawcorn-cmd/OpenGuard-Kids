"""
OpenGuard Kids — FastAPI Server Application
Implements Parent Authentication, Children Management, Device Pairing,
Batch Event Ingestion (NT2 7-field schema), Heartbeat Sync, and Urgent WebSocket Dispatch.
"""

from __future__ import annotations

import secrets
import string
import time
from contextlib import asynccontextmanager
from typing import List, Dict, Any

from fastapi import (
    FastAPI,
    Depends,
    HTTPException,
    Response,
    WebSocket,
    WebSocketDisconnect,
    status,
)
from sqlalchemy.orm import Session

from src.server.database import get_db, init_db
from src.server.models import Parent, Child, Device, Policy, Event, ChildRequest
from src.server.security import (
    hash_password,
    verify_password,
    validate_password_complexity,
    check_account_lockout,
    record_failed_attempt,
)
from src.server.auth import (
    create_parent_session,
    invalidate_parent_session,
    get_current_parent,
    SESSION_TTL_SECONDS,
)
from src.server.schemas import (
    ParentRegisterRequest,
    ParentLoginRequest,
    ParentResponse,
    ChildCreateRequest,
    ChildResponse,
    PairingCodeResponse,
    DeviceEnrollRequest,
    DeviceEnrollResponse,
    EventBatchIngestRequest,
    EventBatchIngestResponse,
    HeartbeatRequest,
    HeartbeatResponse,
)
from src.server.ws_manager import ws_manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="OpenGuard Kids Management Server",
    description="Parental control backend API for OpenGuard Kids",
    version="1.0.0",
    lifespan=lifespan,
)

PAIRING_CHARSET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"  # Unambiguous 32 characters


def generate_pairing_code() -> str:
    """Generates an 8-character pairing code without ambiguous characters."""
    return "".join(secrets.choice(PAIRING_CHARSET) for _ in range(8))


@app.get("/health")
def health_check():
    return {"status": "ok", "app": "OpenGuard Kids Server", "version": "1.0.0"}


# ==========================================
# 1. Parent Authentication Endpoints
# ==========================================

@app.post("/api/v1/auth/register", response_model=ParentResponse, status_code=status.HTTP_201_CREATED)
def register_parent(payload: ParentRegisterRequest, db: Session = Depends(get_db)):
    is_valid, err_msg = validate_password_complexity(payload.password)
    if not is_valid:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=err_msg)

    existing = db.query(Parent).filter(Parent.email == payload.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email này đã được đăng ký trong hệ thống.",
        )

    hashed = hash_password(payload.password)
    parent = Parent(
        email=payload.email,
        hashed_password=hashed,
    )
    db.add(parent)
    db.commit()
    db.refresh(parent)
    return parent


@app.post("/api/v1/auth/login")
def login_parent(
    payload: ParentLoginRequest,
    response: Response,
    db: Session = Depends(get_db),
):
    parent = db.query(Parent).filter(Parent.email == payload.email).first()
    if not parent:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email hoặc mật khẩu không chính xác.",
        )

    is_locked, remaining_sec = check_account_lockout(parent.failed_login_count, parent.locked_until)
    if is_locked:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Tài khoản bị tạm khóa do nhập sai quá nhiều lần. Vui lòng thử lại sau {remaining_sec} giây.",
        )

    if not verify_password(parent.hashed_password, payload.password):
        new_count, locked_until = record_failed_attempt(parent.failed_login_count)
        parent.failed_login_count = new_count
        parent.locked_until = locked_until
        db.commit()

        if new_count >= 5:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Nhập sai mật khẩu 5 lần liên tiếp. Tài khoản đã bị khóa 15 phút.",
            )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Email hoặc mật khẩu không chính xác. (Lần thử {new_count}/5)",
        )

    parent.failed_login_count = 0
    parent.locked_until = 0.0
    db.commit()

    session_token = create_parent_session(parent.id)
    response.set_cookie(
        key="session_token",
        value=session_token,
        max_age=SESSION_TTL_SECONDS,
        httponly=True,
        samesite="lax",
        secure=False,
        path="/",
    )

    return {
        "status": "success",
        "message": "Đăng nhập thành công",
        "session_token": session_token,
        "parent_id": parent.id,
        "email": parent.email,
    }


@app.post("/api/v1/auth/logout")
def logout_parent(response: Response, current_parent: Parent = Depends(get_current_parent)):
    response.delete_cookie("session_token", path="/")
    return {"status": "success", "message": "Đã đăng xuất thành công."}


@app.get("/api/v1/auth/me", response_model=ParentResponse)
def get_me(current_parent: Parent = Depends(get_current_parent)):
    return current_parent


# ==========================================
# 2. Child Management & Pairing Codes (IDOR Protected)
# ==========================================

@app.post("/api/v1/children", response_model=ChildResponse, status_code=status.HTTP_201_CREATED)
def create_child(
    payload: ChildCreateRequest,
    current_parent: Parent = Depends(get_current_parent),
    db: Session = Depends(get_db),
):
    child = Child(
        parent_id=current_parent.id,
        name=payload.name,
        age=payload.age,
    )
    db.add(child)
    db.flush()

    policy = Policy(child_id=child.id)
    db.add(policy)
    db.commit()
    db.refresh(child)
    return child


@app.get("/api/v1/children", response_model=List[ChildResponse])
def list_children(
    current_parent: Parent = Depends(get_current_parent),
    db: Session = Depends(get_db),
):
    return db.query(Child).filter(Child.parent_id == current_parent.id).all()


@app.post("/api/v1/children/{child_id}/pairing-code", response_model=PairingCodeResponse)
def generate_child_pairing_code(
    child_id: str,
    current_parent: Parent = Depends(get_current_parent),
    db: Session = Depends(get_db),
):
    child = (
        db.query(Child)
        .filter(Child.id == child_id, Child.parent_id == current_parent.id)
        .first()
    )
    if not child:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy hồ sơ trẻ hoặc bạn không có quyền truy cập.",
        )

    code = generate_pairing_code()
    ttl = 600
    expires_at = time.time() + ttl

    device = (
        db.query(Device)
        .filter(Device.child_id == child.id, Device.is_enrolled == False)
        .first()
    )
    if not device:
        device = Device(child_id=child.id)
        db.add(device)

    device.pairing_code = code
    device.pairing_expires_at = expires_at
    db.commit()

    return PairingCodeResponse(
        child_id=child.id,
        pairing_code=code,
        expires_at=expires_at,
        ttl_seconds=ttl,
    )


# ==========================================
# 3. Device Enrollment (Windows Agent Calling)
# ==========================================

@app.post("/api/v1/enroll/device", response_model=DeviceEnrollResponse)
def enroll_device(payload: DeviceEnrollRequest, db: Session = Depends(get_db)):
    clean_code = payload.pairing_code.strip().upper()
    now = time.time()

    device = (
        db.query(Device)
        .filter(Device.pairing_code == clean_code)
        .first()
    )

    if not device:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mã ghép đôi không chính xác.",
        )

    if device.pairing_expires_at < now:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mã ghép đôi đã hết hạn (quá thời hạn 10 phút). Vui lòng tạo mã mới từ ứng dụng Phụ huynh.",
        )

    device_token = f"ogk_dev_{secrets.token_hex(24)}"

    device.is_enrolled = True
    device.hostname = payload.hostname
    device.device_fingerprint = payload.device_fingerprint or secrets.token_hex(16)
    device.pairing_code = None
    device.pairing_expires_at = 0.0
    device.last_heartbeat = now
    db.commit()

    return DeviceEnrollResponse(
        device_id=device.id,
        child_id=device.child_id,
        device_token=device_token,
        status="ENROLLED",
    )


# ==========================================
# 4. Event Ingestion & Heartbeat Sync (Week 3 - F5 / NT2)
# ==========================================

@app.post("/api/v1/events/batch", response_model=EventBatchIngestResponse)
def ingest_events_batch(payload: EventBatchIngestRequest, db: Session = Depends(get_db)):
    """
    Ingests batch of enforcement events from Agent.
    Strictly verifies 7-field privacy schema (NT2).
    Prevents duplicate insertion via idempotency_key.
    """
    acknowledged: List[str] = []

    for item in payload.events:
        # Check if already ingested (Idempotency)
        existing = db.query(Event).filter(Event.idempotency_key == item.idempotency_key).first()
        if existing:
            acknowledged.append(item.idempotency_key)
            continue

        event = Event(
            id=item.id or secrets.token_hex(16),
            device_id=item.device_id,
            child_id=item.child_id,
            type=item.type,
            subject=item.subject,
            duration_sec=item.duration_sec,
            ts=item.ts,
            idempotency_key=item.idempotency_key,
        )
        db.add(event)
        acknowledged.append(item.idempotency_key)

    db.commit()

    return EventBatchIngestResponse(
        ingested_count=len(acknowledged),
        acknowledged_keys=acknowledged,
        status="SUCCESS",
    )


@app.post("/api/v1/heartbeat", response_model=HeartbeatResponse)
def device_heartbeat(payload: HeartbeatRequest, db: Session = Depends(get_db)):
    """
    Periodic (60s) heartbeat from Windows Agent.
    Updates device status and returns pending offline commands as fallback.
    """
    device = db.query(Device).filter(Device.id == payload.device_id).first()
    if not device:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Thiết bị không tồn tại.")

    device.last_heartbeat = time.time()
    db.commit()

    # Retrieve any pending commands queued for this device
    pending = ws_manager.pop_pending_commands(device.id)

    return HeartbeatResponse(
        server_time=time.time(),
        pending_commands=pending,
        policy_version=1,
    )


@app.post("/api/v1/devices/{device_id}/command")
async def send_device_command(
    device_id: str,
    payload: Dict[str, Any],
    current_parent: Parent = Depends(get_current_parent),
    db: Session = Depends(get_db),
):
    """
    Dispatches urgent command from Parent to Agent ('LOCK_URGENT', 'UNLOCK', 'ADD_TIME').
    Enforces IDOR check: device -> child -> parent.
    """
    # IDOR Check
    device = (
        db.query(Device)
        .join(Child, Device.child_id == Child.id)
        .filter(Device.id == device_id, Child.parent_id == current_parent.id)
        .first()
    )
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy thiết bị hoặc bạn không có quyền điều khiển.",
        )

    command_type = payload.get("command", "")
    if command_type not in ("LOCK_URGENT", "UNLOCK", "ADD_TIME"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Loại lệnh không hợp lệ.")

    # Dispatch via WebSocket (<5s benchmark) with Heartbeat fallback
    is_immediate = await ws_manager.dispatch_urgent_command(
        device_id=device_id,
        command_type=command_type,
        payload=payload.get("payload", {}),
    )

    return {
        "status": "success",
        "command": command_type,
        "dispatched_immediately": is_immediate,
    }


# ==========================================
# 5. Real-Time WebSockets (< 5s Latency F4.1)
# ==========================================

@app.websocket("/ws/device/{device_id}")
async def websocket_device_endpoint(websocket: WebSocket, device_id: str):
    await ws_manager.connect_device(device_id, websocket)
    try:
        while True:
            # Keep connection alive, listen for agent status pings
            data = await websocket.receive_json()
    except WebSocketDisconnect:
        ws_manager.disconnect_device(device_id)
    except Exception:
        ws_manager.disconnect_device(device_id)


# ==========================================
# 6. Parent Dashboard & Privacy Operations (Week 5 — F3.2, F3.4)
# ==========================================

from fastapi.responses import HTMLResponse
import os

TEMPLATES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")

@app.get("/dashboard/{child_id}", response_class=HTMLResponse)
def render_dashboard_page(child_id: str):
    """Serves mobile-friendly Parent Dashboard HTML (F3.2)."""
    html_path = os.path.join(TEMPLATES_DIR, "dashboard.html")
    if os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>OpenGuard Kids Dashboard</h1>"


@app.get("/api/v1/dashboard/summary/{child_id}")
def get_dashboard_summary(
    child_id: str,
    current_parent: Parent = Depends(get_current_parent),
    db: Session = Depends(get_db),
):
    """
    F3.2: Generates summary reports:
    - Today's screen-time & 7-day weekly history
    - Top 10 applications & Top 10 domains
    - Total blocked count & Pending child requests
    """
    child = (
        db.query(Child)
        .filter(Child.id == child_id, Child.parent_id == current_parent.id)
        .first()
    )
    if not child:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy hồ sơ trẻ hoặc bạn không có quyền truy cập.",
        )

    now = time.time()
    today_start = now - (now % 86400)  # Start of UTC day

    # 1. Screen-time today
    today_events = (
        db.query(Event)
        .filter(Event.child_id == child_id, Event.type == "screen_time", Event.ts >= today_start)
        .all()
    )
    screen_time_today_seconds = sum(e.duration_sec for e in today_events)

    # 2. Weekly screen-time (past 7 days)
    weekly_history = []
    for day_offset in range(6, -1, -1):
        day_ts_start = today_start - (day_offset * 86400)
        day_ts_end = day_ts_start + 86400
        day_duration = sum(
            e.duration_sec
            for e in db.query(Event)
            .filter(
                Event.child_id == child_id,
                Event.type == "screen_time",
                Event.ts >= day_ts_start,
                Event.ts < day_ts_end,
            )
            .all()
        )
        weekly_history.append({"day_offset": day_offset, "seconds": day_duration})

    # 3. Top 10 Apps
    app_events = (
        db.query(Event)
        .filter(Event.child_id == child_id, Event.type.in_(["app_start", "process_blocked", "screen_time"]))
        .all()
    )
    app_counts: Dict[str, int] = {}
    for ev in app_events:
        app_counts[ev.subject] = app_counts.get(ev.subject, 0) + 1
    top_10_apps = sorted(
        [{"app": k, "count": v} for k, v in app_counts.items()],
        key=lambda x: x["count"],
        reverse=True,
    )[:10]

    # 4. Top 10 Domains
    domain_events = (
        db.query(Event)
        .filter(Event.child_id == child_id, Event.type.in_(["domain_query", "blocked_domain"]))
        .all()
    )
    domain_counts: Dict[str, int] = {}
    for ev in domain_events:
        domain_counts[ev.subject] = domain_counts.get(ev.subject, 0) + 1
    top_10_domains = sorted(
        [{"domain": k, "count": v} for k, v in domain_counts.items()],
        key=lambda x: x["count"],
        reverse=True,
    )[:10]

    # 5. Total blocked events
    total_blocked_count = (
        db.query(Event)
        .filter(Event.child_id == child_id, Event.type.in_(["blocked_domain", "process_blocked"]))
        .count()
    )

    # 6. Pending child requests
    pending_requests = (
        db.query(ChildRequest)
        .filter(ChildRequest.child_id == child_id, ChildRequest.status == "PENDING")
        .all()
    )

    return {
        "child_id": child.id,
        "child_name": child.name,
        "screen_time_today_seconds": screen_time_today_seconds,
        "screen_time_today_minutes": round(screen_time_today_seconds / 60, 1),
        "weekly_history": weekly_history,
        "top_10_apps": top_10_apps,
        "top_10_domains": top_10_domains,
        "total_blocked_count": total_blocked_count,
        "pending_requests_count": len(pending_requests),
        "pending_requests": [
            {
                "id": r.id,
                "type": r.type,
                "subject": r.subject,
                "minutes_requested": r.minutes_requested,
                "created_at": r.created_at,
            }
            for r in pending_requests
        ],
    }


@app.post("/api/v1/dashboard/requests/{request_id}/review")
async def review_child_request(
    request_id: str,
    payload: Dict[str, str],
    current_parent: Parent = Depends(get_current_parent),
    db: Session = Depends(get_db),
):
    """
    Parent reviews child agency request: approves or rejects.
    If approved and type is ADD_TIME, pushes bonus time to agent.
    """
    decision = payload.get("decision", "").upper()
    if decision not in ("APPROVED", "REJECTED"):
        raise HTTPException(status_code=400, detail="Quyết định phải là APPROVED hoặc REJECTED.")

    req = (
        db.query(ChildRequest)
        .join(Child, ChildRequest.child_id == Child.id)
        .filter(ChildRequest.id == request_id, Child.parent_id == current_parent.id)
        .first()
    )
    if not req:
        raise HTTPException(status_code=404, detail="Không tìm thấy yêu cầu hoặc bạn không có quyền.")

    req.status = decision
    db.commit()

    # If approved ADD_TIME, dispatch urgent command to child's devices
    if decision == "APPROVED" and req.type == "ADD_TIME":
        devices = db.query(Device).filter(Device.child_id == req.child_id).all()
        for dev in devices:
            await ws_manager.dispatch_urgent_command(
                device_id=dev.id,
                command_type="ADD_TIME",
                payload={"minutes": req.minutes_requested},
            )

    return {"status": "SUCCESS", "request_id": req.id, "decision": decision}


@app.delete("/api/v1/children/{child_id}/purge-data")
async def atomic_dual_deletion(
    child_id: str,
    current_parent: Parent = Depends(get_current_parent),
    db: Session = Depends(get_db),
):
    """
    F3.4: Atomic Dual Deletion button ('Xóa toàn bộ dữ liệu của con tôi').
    Deletes all activity events simultaneously on server and local agent cache.
    """
    child = (
        db.query(Child)
        .filter(Child.id == child_id, Child.parent_id == current_parent.id)
        .first()
    )
    if not child:
        raise HTTPException(status_code=404, detail="Không tìm thấy hồ sơ trẻ.")

    # 1. Delete all events on Central Server database
    deleted_events = db.query(Event).filter(Event.child_id == child.id).delete()
    # 2. Delete all requests
    db.query(ChildRequest).filter(ChildRequest.child_id == child.id).delete()
    db.commit()

    # 3. Dispatch WebSocket command to Agent to purge local SQLite cache
    devices = db.query(Device).filter(Device.child_id == child.id).all()
    for dev in devices:
        await ws_manager.dispatch_urgent_command(
            device_id=dev.id,
            command_type="PURGE_LOCAL_CACHE",
            payload={"child_id": child.id},
        )

    return {
        "status": "SUCCESS",
        "message": f"Đã thực hiện Xóa dữ liệu kép thành công. Đã xóa {deleted_events} sự kiện trên máy chủ và phát lệnh xóa bộ đệm cục bộ của máy tính trẻ.",
        "deleted_events_count": deleted_events,
    }


@app.post("/api/v1/maintenance/purge-expired")
def purge_expired_90_day_data(db: Session = Depends(get_db)):
    """
    F3.4: 90-day retention automated cleanup worker.
    Deletes records older than 90 days.
    """
    cutoff = time.time() - (90 * 86400.0)
    purged_count = db.query(Event).filter(Event.ts < cutoff).delete()
    db.commit()
    return {"status": "SUCCESS", "purged_count": purged_count, "cutoff_timestamp": cutoff}
