"""
Integration tests for Parent Web Dashboard, Reports (F3.2), Child Request Review,
Atomic Dual-Deletion (F3.4), and 90-Day Retention Auto-Purge.
"""

import time
import pytest
from fastapi.testclient import TestClient

from src.server.app import app
from src.server.models import Event, ChildRequest

client = TestClient(app)


def test_dashboard_summary_reports_and_rankings():
    # 1. Setup Parent, Child & Enrolled Device
    client.post("/api/v1/auth/register", json={"email": "dash_p@test.com", "password": "Password123!@#"})
    token = client.post("/api/v1/auth/login", json={"email": "dash_p@test.com", "password": "Password123!@#"}).json()["session_token"]
    child = client.post("/api/v1/children", json={"name": "Bé Bo", "age": 9}, headers={"Authorization": f"Bearer {token}"}).json()
    child_id = child["id"]

    code = client.post(f"/api/v1/children/{child_id}/pairing-code", headers={"Authorization": f"Bearer {token}"}).json()["pairing_code"]
    dev = client.post("/api/v1/enroll/device", json={"pairing_code": code, "hostname": "BO-PC"}).json()
    device_id = dev["device_id"]

    # 2. Ingest various activity events (7-field schema)
    now = time.time()
    events = [
        {"device_id": device_id, "child_id": child_id, "type": "screen_time", "subject": "session", "duration_sec": 1800, "ts": now, "idempotency_key": "key_00000001"},
        {"device_id": device_id, "child_id": child_id, "type": "screen_time", "subject": "session", "duration_sec": 900, "ts": now, "idempotency_key": "key_00000002"},
        {"device_id": device_id, "child_id": child_id, "type": "app_start", "subject": "zoom.exe", "duration_sec": 0, "ts": now, "idempotency_key": "key_00000003"},
        {"device_id": device_id, "child_id": child_id, "type": "app_start", "subject": "zoom.exe", "duration_sec": 0, "ts": now, "idempotency_key": "key_00000004"},
        {"device_id": device_id, "child_id": child_id, "type": "app_start", "subject": "word.exe", "duration_sec": 0, "ts": now, "idempotency_key": "key_00000005"},
        {"device_id": device_id, "child_id": child_id, "type": "domain_query", "subject": "khanacademy.org", "duration_sec": 0, "ts": now, "idempotency_key": "key_00000006"},
        {"device_id": device_id, "child_id": child_id, "type": "domain_query", "subject": "khanacademy.org", "duration_sec": 0, "ts": now, "idempotency_key": "key_00000007"},
        {"device_id": device_id, "child_id": child_id, "type": "domain_query", "subject": "hcmus.edu.vn", "duration_sec": 0, "ts": now, "idempotency_key": "key_00000008"},
        {"device_id": device_id, "child_id": child_id, "type": "blocked_domain", "subject": "bet88.com", "duration_sec": 0, "ts": now, "idempotency_key": "key_00000009"},
        {"device_id": device_id, "child_id": child_id, "type": "process_blocked", "subject": "hack_game.exe", "duration_sec": 0, "ts": now, "idempotency_key": "key_00000010"},
    ]
    batch_res = client.post("/api/v1/events/batch", json={"events": events})
    assert batch_res.status_code == 200
    assert batch_res.json()["ingested_count"] == 10

    # 3. Query Dashboard Summary (F3.2)
    res = client.get(f"/api/v1/dashboard/summary/{child_id}", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    data = res.json()

    assert data["child_name"] == "Bé Bo"
    assert data["screen_time_today_seconds"] == 2700  # 1800 + 900
    assert data["screen_time_today_minutes"] == 45.0
    assert data["total_blocked_count"] == 2  # bet88.com + hack_game.exe

    # Top apps ranking: zoom.exe (2) > word.exe (1)
    assert len(data["top_10_apps"]) >= 2
    assert data["top_10_apps"][0]["app"] in ("zoom.exe", "session")

    # Top domains ranking: khanacademy.org (2) > hcmus.edu.vn (1)
    assert data["top_10_domains"][0]["domain"] == "khanacademy.org"
    assert data["top_10_domains"][0]["count"] == 2


def test_child_request_parent_review():
    # Setup parent, child, device
    client.post("/api/v1/auth/register", json={"email": "req_parent@test.com", "password": "PasswordReq123!"})
    token = client.post("/api/v1/auth/login", json={"email": "req_parent@test.com", "password": "PasswordReq123!"}).json()["session_token"]
    child = client.post("/api/v1/children", json={"name": "Tom", "age": 10}, headers={"Authorization": f"Bearer {token}"}).json()
    child_id = child["id"]

    # Child submits an agency request via direct API or IPC simulation
    from tests.conftest import TestingSessionLocal
    db = TestingSessionLocal()
    req = ChildRequest(
        id="req-test-1",
        child_id=child_id,
        type="ADD_TIME",
        subject="Lam bai tap",
        minutes_requested=15,
        status="PENDING",
    )
    db.add(req)
    db.commit()
    db.close()

    # Parent approves request
    review_res = client.post(
        "/api/v1/dashboard/requests/req-test-1/review",
        json={"decision": "APPROVED"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert review_res.status_code == 200
    assert review_res.json()["decision"] == "APPROVED"


def test_atomic_dual_deletion():
    """
    F3.4: Atomic Dual Deletion button ('Xóa toàn bộ dữ liệu của con tôi').
    """
    client.post("/api/v1/auth/register", json={"email": "dual_del@test.com", "password": "PasswordDual1!"})
    token = client.post("/api/v1/auth/login", json={"email": "dual_del@test.com", "password": "PasswordDual1!"}).json()["session_token"]
    child = client.post("/api/v1/children", json={"name": "Bé Na", "age": 8}, headers={"Authorization": f"Bearer {token}"}).json()
    child_id = child["id"]

    code = client.post(f"/api/v1/children/{child_id}/pairing-code", headers={"Authorization": f"Bearer {token}"}).json()["pairing_code"]
    dev = client.post("/api/v1/enroll/device", json={"pairing_code": code, "hostname": "NA-PC"}).json()
    device_id = dev["device_id"]

    # Ingest event
    client.post("/api/v1/events/batch", json={"events": [
        {"device_id": device_id, "child_id": child_id, "type": "screen_time", "subject": "study", "duration_sec": 600, "ts": time.time(), "idempotency_key": "key_dual_001"}
    ]})

    # Trigger Atomic Dual Deletion
    del_res = client.delete(f"/api/v1/children/{child_id}/purge-data", headers={"Authorization": f"Bearer {token}"})
    assert del_res.status_code == 200
    assert del_res.json()["status"] == "SUCCESS"
    assert del_res.json()["deleted_events_count"] == 1

    # Verify summary is now zeroed
    sum_res = client.get(f"/api/v1/dashboard/summary/{child_id}", headers={"Authorization": f"Bearer {token}"})
    assert sum_res.json()["screen_time_today_seconds"] == 0


def test_90_day_retention_purge():
    """
    F3.4: 90-day retention automated cleanup.
    """
    from tests.conftest import TestingSessionLocal
    db = TestingSessionLocal()

    now = time.time()
    old_ts = now - (95 * 86400.0)  # 95 days old (> 90 days)
    new_ts = now - (10 * 86400.0)  # 10 days old (< 90 days)

    ev_old = Event(id="old-1", device_id="d1", child_id="c1", type="screen_time", subject="old", duration_sec=10, ts=old_ts, idempotency_key="old-key-1")
    ev_new = Event(id="new-1", device_id="d1", child_id="c1", type="screen_time", subject="new", duration_sec=10, ts=new_ts, idempotency_key="new-key-1")
    db.add_all([ev_old, ev_new])
    db.commit()
    db.close()

    # Trigger maintenance purge
    purge_res = client.post("/api/v1/maintenance/purge-expired")
    assert purge_res.status_code == 200
    assert purge_res.json()["purged_count"] >= 1


def test_dashboard_html_rendering():
    res = client.get("/dashboard/test-child-id")
    assert res.status_code == 200
    assert "Bảng Điều Khiển Phụ Huynh" in res.text
    assert "OpenGuard Kids" in res.text
