"""
Unit & Integration Verification Suite for Milestone 1:
End-to-End Time and State Synchronization (Backend & Agent).
Tests:
1. ScreenTimeTracker weekday vs. weekend quotas and bedtime curfew enforcement.
2. ScreenTimeTracker dynamic update_policy() method.
3. AgentService screen_time usage event enqueuing into OfflineEventBuffer.
4. Device telemetry persistence in POST /api/v1/heartbeat.
5. Local midnight and bonus minutes calculation in dashboard summary.
6. Child agency ingestion creating ChildRequest records in POST /api/v1/events/batch.
7. Token-authenticated device policy endpoint GET /api/v1/devices/{device_id}/policy.
8. AgentService handling POLICY_UPDATE command.
"""

import time
import tempfile
from datetime import datetime
import pytest
from fastapi.testclient import TestClient

from src.agent.screen_time import ScreenTimeTracker, ScreenTimeState
from src.agent.service import AgentService
from src.server.app import app
from tests.conftest import TestingSessionLocal as SessionLocal
from src.server.models import Parent, Child, Device, Policy, Event, ChildRequest


@pytest.fixture
def client():
    return TestClient(app)


# -----------------------------------------------------------------------------
# 1. ScreenTimeTracker Weekday/Weekend Quota and Bedtime Curfew
# -----------------------------------------------------------------------------

def test_screen_time_tracker_weekday_vs_weekend_quota():
    # Thursday: 2026-10-29 12:00:00 (weekday=3)
    wall_weekday = datetime(2026, 10, 29, 12, 0, 0).timestamp()
    tracker_thursday = ScreenTimeTracker(
        daily_quota_seconds=7200,
        daily_quota_weekday_seconds=3600,   # 60m on weekdays
        daily_quota_weekend_seconds=10800,  # 180m on weekends
        wall_time_provider=lambda: wall_weekday,
        monotonic_time_provider=lambda: 1000.0,
    )
    assert tracker_thursday.get_quota_today_seconds() == 3600.0
    assert tracker_thursday.get_remaining_seconds() == 3600.0

    # Saturday: 2026-10-31 12:00:00 (weekday=5)
    wall_weekend = datetime(2026, 10, 31, 12, 0, 0).timestamp()
    tracker_saturday = ScreenTimeTracker(
        daily_quota_seconds=7200,
        daily_quota_weekday_seconds=3600,
        daily_quota_weekend_seconds=10800,
        wall_time_provider=lambda: wall_weekend,
        monotonic_time_provider=lambda: 1000.0,
    )
    assert tracker_saturday.get_quota_today_seconds() == 10800.0
    assert tracker_saturday.get_remaining_seconds() == 10800.0


def test_screen_time_tracker_bedtime_curfew_midnight_crossover():
    # Bedtime curfew: 21:30 to 06:30
    # Test time 1: 22:00 (inside curfew -> LOCKED_SCHEDULE)
    wall_in_curfew = datetime(2026, 11, 1, 22, 0, 0).timestamp()
    tracker = ScreenTimeTracker(
        daily_quota_seconds=7200,
        bed_time_start="21:30",
        bed_time_end="06:30",
        wall_time_provider=lambda: wall_in_curfew,
        monotonic_time_provider=lambda: 1000.0,
    )
    assert tracker.is_in_bedtime() is True
    assert tracker.state == ScreenTimeState.LOCKED_SCHEDULE
    assert tracker.is_locked() is True

    # Test time 2: 05:00 (early morning, still inside curfew)
    wall_early = datetime(2026, 11, 1, 5, 0, 0).timestamp()
    tracker.last_wall_time = wall_early
    assert tracker.is_in_bedtime(datetime.fromtimestamp(wall_early)) is True

    # Test time 3: 14:00 (afternoon, outside curfew)
    wall_outside = datetime(2026, 11, 1, 14, 0, 0).timestamp()
    assert tracker.is_in_bedtime(datetime.fromtimestamp(wall_outside)) is False


def test_screen_time_tracker_update_policy():
    wall_time = datetime(2026, 11, 1, 12, 0, 0).timestamp()
    tracker = ScreenTimeTracker(
        daily_quota_seconds=7200,
        wall_time_provider=lambda: wall_time,
        monotonic_time_provider=lambda: 1000.0,
    )
    assert tracker.daily_quota_seconds == 7200

    # Dynamically update policy
    tracker.update_policy({
        "daily_quota_minutes": 45,
        "weekend_quota_minutes": 90,
        "bed_time_start": "21:00",
        "bed_time_end": "07:00",
    })
    assert tracker.daily_quota_weekday_seconds == 2700
    assert tracker.daily_quota_weekend_seconds == 5400
    assert tracker.bed_time_start == "21:00"
    assert tracker.bed_time_end == "07:00"


# -----------------------------------------------------------------------------
# 2. AgentService Screen-Time Event Enqueuing
# -----------------------------------------------------------------------------

def test_agent_service_screen_time_event_enqueuing():
    with tempfile.TemporaryDirectory() as tmpdir:
        service = AgentService(
            device_id="DEV-SYNC-01",
            child_id="101",
            server_url=None,
            data_dir=tmpdir,
            daily_limit_minutes=60.0,
            ipc_port=0,
        )

        try:
            # Simulate 25 seconds of active usage accumulation
            service.tracker.consumed_seconds_today = 25.0
            service._screen_time_worker_once = False

            # Call flush helper directly
            service._flush_active_screen_time_to_buffer(min_seconds=15.0)

            batch = service.buffer.peek_unsynced_batch(limit=10)
            assert len(batch) >= 1
            st_event = next((e for e in batch if e["type"] == "screen_time"), None)
            assert st_event is not None
            assert st_event["subject"] == "active_usage"
            assert st_event["duration_sec"] == 25
            assert st_event["device_id"] == "DEV-SYNC-01"
            assert st_event["child_id"] == "101"

            # Verify consecutive flushes only capture newly elapsed delta
            service.tracker.consumed_seconds_today = 35.0
            service._flush_active_screen_time_to_buffer(min_seconds=5.0)

            batch2 = service.buffer.peek_unsynced_batch(limit=10)
            st_events = [e for e in batch2 if e["type"] == "screen_time"]
            assert len(st_events) == 2
            assert st_events[1]["duration_sec"] == 10

        finally:
            service.stop()


# -----------------------------------------------------------------------------
# 3. Server Heartbeat Telemetry & Persistence
# -----------------------------------------------------------------------------

def test_server_device_heartbeat_telemetry_persistence(client):
    device_id = "DEV-TELEMETRY-999"
    hb_payload = {
        "device_id": device_id,
        "remaining_seconds": 3120.5,
        "screen_time_remaining": 3120.5,
        "status": "ACTIVE_COUNTING",
        "is_locked": False,
    }

    res = client.post("/api/v1/heartbeat", json=hb_payload)
    assert res.status_code == 200

    # Query device from database and verify telemetry persisted
    db = SessionLocal()
    try:
        dev = db.query(Device).filter(Device.id == device_id).first()
        assert dev is not None
        assert dev.remaining_seconds == 3120.5
        assert dev.current_status == "ACTIVE_COUNTING"
        assert dev.is_locked is False

        # Now send locked status
        hb_locked = {
            "device_id": device_id,
            "remaining_seconds": 0.0,
            "status": "LOCKED_QUOTA",
            "is_locked": True,
        }
        res2 = client.post("/api/v1/heartbeat", json=hb_locked)
        assert res2.status_code == 200

        db.refresh(dev)
        assert dev.remaining_seconds == 0.0
        assert dev.current_status == "LOCKED_QUOTA"
        assert dev.is_locked is True
    finally:
        db.close()


# -----------------------------------------------------------------------------
# 4. Device Policy Token Authenticated Endpoint
# -----------------------------------------------------------------------------

def test_device_policy_endpoint_auth(client):
    # 1. Setup parent and child
    client.post("/api/v1/auth/register", json={"email": "dev_pol_p@test.com", "password": "PasswordDev1!"})
    login_res = client.post("/api/v1/auth/login", json={"email": "dev_pol_p@test.com", "password": "PasswordDev1!"}).json()
    token = login_res["session_token"]

    child = client.post("/api/v1/children", json={"name": "Bé Bin", "age": 8}, headers={"Authorization": f"Bearer {token}"}).json()
    child_id = child["id"]

    code = client.post(f"/api/v1/children/{child_id}/pairing-code", headers={"Authorization": f"Bearer {token}"}).json()["pairing_code"]
    dev = client.post("/api/v1/enroll/device", json={"pairing_code": code, "hostname": "BIN-PC"}).json()
    device_id = dev["device_id"]
    device_token = dev["device_token"]

    # 2. Missing token -> 401
    res_no_auth = client.get(f"/api/v1/devices/{device_id}/policy")
    assert res_no_auth.status_code == 401

    # 3. Invalid token -> 401
    res_bad_auth = client.get(f"/api/v1/devices/{device_id}/policy", headers={"Authorization": "Bearer bad_tok"})
    assert res_bad_auth.status_code == 401

    # 4. Valid device token -> 200
    res_valid_dev = client.get(f"/api/v1/devices/{device_id}/policy", headers={"Authorization": f"Bearer {device_token}"})
    assert res_valid_dev.status_code == 200
    pol = res_valid_dev.json()
    assert pol["child_id"] == child_id
    assert "daily_quota_minutes" in pol

    # 5. Non-existent device -> 404
    res_missing = client.get("/api/v1/devices/NON-EXISTENT-DEV/policy", headers={"Authorization": "Bearer some_token"})
    assert res_missing.status_code == 404


# -----------------------------------------------------------------------------
# 5. Child Agency Event Ingestion into ChildRequest
# -----------------------------------------------------------------------------

def test_child_agency_event_ingestion_creates_child_request(client):
    db = SessionLocal()
    try:
        # Create a parent and child
        parent = Parent(id="p-agency-test", email="agency@test.com", hashed_password="HASH")
        child = Child(id="c-agency-test", parent_id=parent.id, name="Bé Bi", age=7)
        device = Device(id="dev-agency-test", child_id=child.id, hostname="BI-PC", is_enrolled=True)
        db.add(parent)
        db.add(child)
        db.add(device)
        db.commit()

        # Ingest time extension request and unblock request
        events_payload = {
            "events": [
                {
                    "device_id": device.id,
                    "child_id": child.id,
                    "type": "time_extension_request",
                    "subject": "15m",
                    "duration_sec": 0,
                    "ts": time.time(),
                    "idempotency_key": f"key_add_time_{time.time()}",
                },
                {
                    "device_id": device.id,
                    "child_id": child.id,
                    "type": "unblock_request",
                    "subject": "scratch.mit.edu",
                    "duration_sec": 0,
                    "ts": time.time(),
                    "idempotency_key": f"key_unblock_{time.time()}",
                },
            ]
        }

        res = client.post("/api/v1/events/batch", json=events_payload)
        assert res.status_code == 200
        assert res.json()["ingested_count"] == 2

        # Verify ChildRequest records created in database
        reqs = db.query(ChildRequest).filter(ChildRequest.child_id == child.id, ChildRequest.status == "PENDING").all()
        assert len(reqs) == 2

        time_req = next((r for r in reqs if r.type == "ADD_TIME"), None)
        assert time_req is not None
        assert time_req.minutes_requested == 15

        unblock_req = next((r for r in reqs if r.type == "UNBLOCK_DOMAIN"), None)
        assert unblock_req is not None
        assert unblock_req.subject == "scratch.mit.edu"
        assert unblock_req.minutes_requested == 0

    finally:
        db.close()


# -----------------------------------------------------------------------------
# 6. Bonus Minutes and Lock States in Dashboard Summary
# -----------------------------------------------------------------------------

def test_dashboard_summary_bonus_minutes_and_lock_states(client):
    db = SessionLocal()
    try:
        parent = Parent(id="p-bonus-test", email="bonus@test.com", hashed_password="HASH")
        child = Child(id="c-bonus-test", parent_id=parent.id, name="Bé Na", age=10)
        policy = Policy(child_id=child.id, daily_quota_minutes=60, daily_quota_weekend_minutes=120)
        device = Device(
            id="dev-bonus-test",
            child_id=child.id,
            hostname="NA-PC",
            is_enrolled=True,
            last_heartbeat=time.time(),
            remaining_seconds=1800.0,
            bonus_minutes_today=15,
            is_locked=False,
            current_status="ACTIVE_COUNTING",
        )
        db.add(parent)
        db.add(child)
        db.add(policy)
        db.add(device)
        db.commit()

        # Check summary endpoint
        from src.server.app import _build_child_summary
        summary = _build_child_summary(child, db)

        assert summary["bonus_minutes_today"] == 15
        assert summary["is_locked"] is False
        assert summary["device"]["bonus_minutes_today"] == 15
        assert summary["device"]["is_locked"] is False

        # Quota remaining includes bonus minutes: 60 + 15 - 0 = 75 minutes
        assert summary["quota_remaining_minutes"] >= 75.0

    finally:
        db.close()


# -----------------------------------------------------------------------------
# 7. AgentService POLICY_UPDATE Command Application
# -----------------------------------------------------------------------------

def test_agent_service_apply_policy_update():
    with tempfile.TemporaryDirectory() as tmpdir:
        service = AgentService(
            device_id="DEV-CMD-01",
            child_id="105",
            server_url=None,
            data_dir=tmpdir,
            daily_limit_minutes=120.0,
            ipc_port=0,
        )

        try:
            cmd = {
                "command": "POLICY_UPDATE",
                "payload": {
                    "policy": {
                        "version": 3,
                        "daily_quota_minutes": 45,
                        "weekend_quota_minutes": 90,
                        "bed_time_start": "21:30",
                        "bed_time_end": "06:30",
                        "blocklist": ["gambling.com", "tiktok.com"],
                        "whitelist": ["khanacademy.org"],
                        "study_mode": True,
                        "blocked_apps": [{"name": "game.exe", "sha256": "a" * 64}],
                    }
                }
            }

            service._apply_server_command(cmd)

            # Assert tracker updated
            assert service.tracker.daily_quota_weekday_seconds == 45 * 60
            assert service.tracker.daily_quota_weekend_seconds == 90 * 60
            assert service.tracker.bed_time_start == "21:30"
            assert service.tracker.bed_time_end == "06:30"

            # Assert DNS proxy updated
            assert "gambling.com" in service.dns_proxy.blocklist
            assert "tiktok.com" in service.dns_proxy.blocklist
            assert "khanacademy.org" in service.dns_proxy.whitelist
            assert service.dns_proxy.study_mode is True

            # Assert Process monitor updated
            assert "game.exe" in service.process_monitor.blocked_names
            assert "a" * 64 in service.process_monitor.blocked_hashes
            assert service.process_monitor.study_mode is True

        finally:
            service.stop()
