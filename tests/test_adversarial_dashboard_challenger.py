"""
Adversarial Stress, Concurrency, and Edge-Case Test Suite for Milestone W5/M5.
Tester: teamwork_challenger (challenger_dashboard_2)

Adversarial Focus Areas:
1. WebSocket offline queuing: commands persisted in SQLite, delivered on heartbeat, cleared after delivery.
2. Rapid command clicking: rapid succession dispatch without race conditions, deadlocks, or corruption.
3. Atomic Dual Deletion: server-side tables purged, summary zeroed, PURGE_LOCAL_CACHE queued, cross-child isolation.
4. Child Agency double-review: idempotent handling of approving/rejecting requests.
"""

import json
import time
import pytest
from fastapi.testclient import TestClient

from src.server.app import app
from src.server.models import (
    Parent,
    Child,
    Device,
    Policy,
    Event,
    ChildRequest,
    AuditLog,
    PendingCommand,
)
from src.server.ws_manager import ws_manager
from tests.conftest import TestingSessionLocal


@pytest.fixture
def api_client():
    return TestClient(app)


def _setup_parent_child_device(client: TestClient, email: str, child_name: str = "TestKid"):
    """Helper to set up a clean registered parent, child, and enrolled device."""
    client.post("/api/v1/auth/register", json={"email": email, "password": "Password123!@#"})
    login_res = client.post("/api/v1/auth/login", json={"email": email, "password": "Password123!@#"}).json()
    token = login_res["session_token"]
    headers = {"Authorization": f"Bearer {token}"}

    child = client.post("/api/v1/children", json={"name": child_name, "age": 10}, headers=headers).json()
    child_id = child["id"]

    code = client.post(f"/api/v1/children/{child_id}/pairing-code", headers=headers).json()["pairing_code"]
    dev = client.post("/api/v1/enroll/device", json={"pairing_code": code, "hostname": f"{child_name}-PC"}).json()
    device_id = dev["device_id"]

    return token, headers, child_id, device_id


# ==============================================================================
# 1. WEBSOCKET OFFLINE QUEUING & PERSISTENCE
# ==============================================================================

class TestWebSocketOfflineQueuing:
    """Focus 1: WebSocket offline queuing and SQLite persistence."""

    def test_offline_commands_persisted_to_sqlite_and_drained_on_heartbeat(self, api_client):
        token, headers, child_id, device_id = _setup_parent_child_device(api_client, "offline_q@test.com", "OfflineKid")

        # Confirm device is offline
        assert not ws_manager.is_device_online(device_id)

        # Dispatch commands while offline via dashboard command endpoint
        res1 = api_client.post(
            f"/api/v1/dashboard/{child_id}/command",
            json={"command": "LOCK_URGENT", "minutes": 0},
        )
        assert res1.status_code == 200

        res2 = api_client.post(
            f"/api/v1/dashboard/{child_id}/command",
            json={"command": "ADD_TIME", "minutes": 15},
        )
        assert res2.status_code == 200

        # Verify PendingCommand records exist directly in SQLite database
        db = TestingSessionLocal()
        try:
            pending_db = (
                db.query(PendingCommand)
                .filter(PendingCommand.device_id == device_id)
                .order_by(PendingCommand.id.asc())
                .all()
            )
            assert len(pending_db) == 2, f"Expected 2 pending commands in DB, got {len(pending_db)}"
            assert pending_db[0].command_type == "LOCK_URGENT"
            assert pending_db[1].command_type == "ADD_TIME"
        finally:
            db.close()

        # Simulate agent heartbeat: should drain the queue
        hb_res = api_client.post(
            "/api/v1/heartbeat",
            json={"device_id": device_id, "status": "ACTIVE", "remaining_seconds": 1200.0},
        )
        assert hb_res.status_code == 200
        hb_data = hb_res.json()
        assert len(hb_data["pending_commands"]) == 2
        assert hb_data["pending_commands"][0]["command"] == "LOCK_URGENT"
        assert hb_data["pending_commands"][1]["command"] == "ADD_TIME"

        # Verify SQLite queue is cleared after heartbeat
        db = TestingSessionLocal()
        try:
            remaining_db = (
                db.query(PendingCommand)
                .filter(PendingCommand.device_id == device_id)
                .all()
            )
            assert len(remaining_db) == 0, f"Expected 0 pending commands in DB after heartbeat, got {len(remaining_db)}"
        finally:
            db.close()

        # Subsequent heartbeat receives an empty queue
        hb_res2 = api_client.post(
            "/api/v1/heartbeat",
            json={"device_id": device_id, "status": "ACTIVE", "remaining_seconds": 1200.0},
        )
        assert hb_res2.status_code == 200
        assert len(hb_res2.json()["pending_commands"]) == 0

    def test_offline_commands_survive_server_restart(self, api_client):
        """Verify that offline commands persist in SQLite and are delivered after in-memory state is wiped."""
        token, headers, child_id, device_id = _setup_parent_child_device(api_client, "restart_q@test.com", "RestartKid")

        # Dispatch command while offline
        res = api_client.post(
            f"/api/v1/dashboard/{child_id}/command",
            json={"command": "LOCK_URGENT", "minutes": 0},
        )
        assert res.status_code == 200

        # Simulate server crash / restart: wipe in-memory dictionary
        ws_manager.pending_commands.clear()

        # Heartbeat: should still drain the command from SQLite!
        hb_res = api_client.post(
            "/api/v1/heartbeat",
            json={"device_id": device_id, "status": "ACTIVE", "remaining_seconds": 1200.0},
        )
        assert hb_res.status_code == 200
        cmds = hb_res.json()["pending_commands"]
        assert len(cmds) == 1
        assert cmds[0]["command"] == "LOCK_URGENT"

        # Subsequent heartbeat receives an empty queue
        hb_res2 = api_client.post(
            "/api/v1/heartbeat",
            json={"device_id": device_id, "status": "ACTIVE", "remaining_seconds": 1200.0},
        )
        assert len(hb_res2.json()["pending_commands"]) == 0


    def test_direct_device_command_offline_queuing_and_delivery(self, api_client):
        """Test the direct device command endpoint: POST /api/v1/devices/{device_id}/command."""
        token, headers, child_id, device_id = _setup_parent_child_device(api_client, "dev_cmd@test.com", "DevCmdKid")

        # Send UNLOCK command via direct device command endpoint
        cmd_res = api_client.post(
            f"/api/v1/devices/{device_id}/command",
            json={"command": "UNLOCK", "payload": {"reason": "Manual unlock"}},
            headers=headers,
        )
        assert cmd_res.status_code == 200
        assert cmd_res.json()["status"] == "success"

        # Agent heartbeats and receives the UNLOCK command
        hb_res = api_client.post(
            "/api/v1/heartbeat",
            json={"device_id": device_id, "status": "ACTIVE", "remaining_seconds": 3600.0},
        )
        assert hb_res.status_code == 200
        pending = hb_res.json()["pending_commands"]
        assert len(pending) == 1
        assert pending[0]["command"] == "UNLOCK"

        # Queue cleared
        hb_res2 = api_client.post(
            "/api/v1/heartbeat",
            json={"device_id": device_id, "status": "ACTIVE", "remaining_seconds": 3600.0},
        )
        assert len(hb_res2.json()["pending_commands"]) == 0


# ==============================================================================
# 2. RAPID COMMAND CLICKING & STRESS TESTING
# ==============================================================================

class TestRapidCommandConcurrency:
    """Focus 2: Rapid command clicking, rapid burst dispatch, FIFO order."""

    def test_rapid_burst_command_dispatch(self, api_client):
        """Simulate a user rapidly clicking urgent buttons 30 times in quick succession."""
        token, headers, child_id, device_id = _setup_parent_child_device(api_client, "rapid_cmd@test.com", "RapidKid")

        pattern = ["LOCK_URGENT", "ADD_TIME", "UNLOCK"] * 10  # 30 total commands in rapid succession
        results = []

        start_time = time.perf_counter()
        for cmd_type in pattern:
            res = api_client.post(
                f"/api/v1/dashboard/{child_id}/command",
                json={"command": cmd_type, "minutes": 15},
            )
            results.append(res)
        elapsed = time.perf_counter() - start_time

        # Ensure all 30 succeeded with 200 OK
        assert len(results) == 30
        for r in results:
            assert r.status_code == 200
            assert r.json()["status"] == "success"

        # Verify all 30 commands were recorded in SQLite in FIFO order
        db = TestingSessionLocal()
        try:
            pending_in_db = (
                db.query(PendingCommand)
                .filter(PendingCommand.device_id == device_id)
                .order_by(PendingCommand.id.asc())
                .all()
            )
            assert len(pending_in_db) == 30, f"Expected 30 in DB, got {len(pending_in_db)}"
            for idx, p in enumerate(pending_in_db):
                assert p.command_type == pattern[idx], f"FIFO order mismatch at index {idx}: expected {pattern[idx]}, got {p.command_type}"
        finally:
            db.close()

        # Drain via heartbeat
        hb = api_client.post(
            "/api/v1/heartbeat",
            json={"device_id": device_id, "status": "ACTIVE", "remaining_seconds": 600.0},
        )
        assert hb.status_code == 200
        delivered = hb.json()["pending_commands"]
        assert len(delivered) == 30
        for idx, cmd in enumerate(delivered):
            assert cmd["command"] == pattern[idx]

        # Queue is now completely empty
        db = TestingSessionLocal()
        try:
            remaining = db.query(PendingCommand).filter(PendingCommand.device_id == device_id).count()
            assert remaining == 0
        finally:
            db.close()


# ==============================================================================
# 3. ATOMIC DUAL DELETION
# ==============================================================================

class TestAtomicDualDeletionDeep:
    """Focus 3: Atomic Dual Deletion, cross-child isolation, summary zeroing, PURGE_LOCAL_CACHE queuing."""

    def test_atomic_dual_deletion_complete_lifecycle(self, api_client):
        # 1. Setup Child A and Child B (isolation verification)
        token_a, headers_a, child_a_id, dev_a1_id = _setup_parent_child_device(api_client, "parent_a@test.com", "ChildA")
        # Enroll 2nd device for Child A
        code_a2 = api_client.post(f"/api/v1/children/{child_a_id}/pairing-code", headers=headers_a).json()["pairing_code"]
        dev_a2 = api_client.post("/api/v1/enroll/device", json={"pairing_code": code_a2, "hostname": "ChildA-Laptop"}).json()
        dev_a2_id = dev_a2["device_id"]

        token_b, headers_b, child_b_id, dev_b1_id = _setup_parent_child_device(api_client, "parent_b@test.com", "ChildB")

        # 2. Ingest events for Child A (ensure idempotency_key length >= 8)
        now = time.time()
        events_a = [
            {"device_id": dev_a1_id, "child_id": child_a_id, "type": "screen_time", "subject": "gaming", "duration_sec": 1200, "ts": now, "idempotency_key": "key_dual_a_001"},
            {"device_id": dev_a1_id, "child_id": child_a_id, "type": "app_start", "subject": "roblox.exe", "duration_sec": 0, "ts": now, "idempotency_key": "key_dual_a_002"},
            {"device_id": dev_a2_id, "child_id": child_a_id, "type": "domain_query", "subject": "youtube.com", "duration_sec": 0, "ts": now, "idempotency_key": "key_dual_a_003"},
            {"device_id": dev_a2_id, "child_id": child_a_id, "type": "blocked_domain", "subject": "gambling.com", "duration_sec": 0, "ts": now, "idempotency_key": "key_dual_a_004"},
        ]
        batch_res_a = api_client.post("/api/v1/events/batch", json={"events": events_a})
        assert batch_res_a.status_code == 200
        assert batch_res_a.json()["ingested_count"] == 4

        # Ingest events for Child B (must NOT be deleted)
        events_b = [
            {"device_id": dev_b1_id, "child_id": child_b_id, "type": "screen_time", "subject": "study", "duration_sec": 1800, "ts": now, "idempotency_key": "key_dual_b_001"},
            {"device_id": dev_b1_id, "child_id": child_b_id, "type": "domain_query", "subject": "khanacademy.org", "duration_sec": 0, "ts": now, "idempotency_key": "key_dual_b_002"},
        ]
        batch_res_b = api_client.post("/api/v1/events/batch", json={"events": events_b})
        assert batch_res_b.status_code == 200
        assert batch_res_b.json()["ingested_count"] == 2

        # 3. Create ChildRequests for Child A and Child B
        db = TestingSessionLocal()
        try:
            req_a1 = ChildRequest(id="req_a_1", child_id=child_a_id, type="ADD_TIME", subject="Need more time", minutes_requested=15, status="PENDING")
            req_a2 = ChildRequest(id="req_a_2", child_id=child_a_id, type="UNBLOCK_DOMAIN", subject="gaming.com", minutes_requested=0, status="PENDING")
            req_b1 = ChildRequest(id="req_b_1", child_id=child_b_id, type="ADD_TIME", subject="Math homework", minutes_requested=20, status="PENDING")
            db.add_all([req_a1, req_a2, req_b1])
            db.commit()
        finally:
            db.close()

        # Verify summary before purge
        sum_before = api_client.get(f"/api/v1/dashboard/summary/{child_a_id}", headers=headers_a).json()
        assert sum_before["screen_time_today_seconds"] == 1200
        assert sum_before["total_blocked_count"] == 1

        # 4. Execute Atomic Dual Deletion for Child A
        del_res = api_client.delete(f"/api/v1/children/{child_a_id}/purge-data", headers=headers_a)
        assert del_res.status_code == 200
        del_data = del_res.json()
        assert del_data["status"] == "SUCCESS"
        assert del_data["deleted_events_count"] == 4

        # 5. Database assertions for Child A
        db = TestingSessionLocal()
        try:
            # Events purged
            assert db.query(Event).filter(Event.child_id == child_a_id).count() == 0
            # Requests purged
            assert db.query(ChildRequest).filter(ChildRequest.child_id == child_a_id).count() == 0
            # Child and Policy preserved
            assert db.query(Child).filter(Child.id == child_a_id).count() == 1
            assert db.query(Policy).filter(Policy.child_id == child_a_id).count() == 1

            # AuditLog written
            audit = db.query(AuditLog).filter(AuditLog.child_id == child_a_id, AuditLog.action == "ATOMIC_DUAL_DELETION").first()
            assert audit is not None
            assert "Xóa Dữ Liệu Kép" in audit.details

            # Isolation check: Child B data completely untouched
            assert db.query(Event).filter(Event.child_id == child_b_id).count() == 2
            assert db.query(ChildRequest).filter(ChildRequest.child_id == child_b_id).count() == 1

            # Check PURGE_LOCAL_CACHE queued for BOTH devices of Child A
            cmds_a1 = db.query(PendingCommand).filter(PendingCommand.device_id == dev_a1_id, PendingCommand.command_type == "PURGE_LOCAL_CACHE").all()
            cmds_a2 = db.query(PendingCommand).filter(PendingCommand.device_id == dev_a2_id, PendingCommand.command_type == "PURGE_LOCAL_CACHE").all()
            assert len(cmds_a1) == 1
            assert len(cmds_a2) == 1

            # No purge command queued for Child B's device
            cmds_b = db.query(PendingCommand).filter(PendingCommand.device_id == dev_b1_id, PendingCommand.command_type == "PURGE_LOCAL_CACHE").all()
            assert len(cmds_b) == 0
        finally:
            db.close()

        # 6. Verify summary is completely zeroed out
        sum_after = api_client.get(f"/api/v1/dashboard/summary/{child_a_id}", headers=headers_a).json()
        assert sum_after["screen_time_today_seconds"] == 0
        assert sum_after["screen_time_today_minutes"] == 0.0
        assert sum_after["total_blocked_count"] == 0
        assert len(sum_after["top_10_apps"]) == 0
        assert len(sum_after["top_10_domains"]) == 0

        # Full 5-tab live data payload also zeroed
        live_data = api_client.get(f"/api/v1/dashboard/data/{child_a_id}").json()
        assert live_data["screen_time_today_minutes"] == 0.0
        assert live_data["blocked_count"] == 0
        assert len(live_data["requests"]) == 0
        assert len(live_data["top_apps"]) == 0
        assert len(live_data["top_domains"]) == 0
        for day in live_data["weekly_history"]:
            assert day["seconds"] == 0

        # 7. Device A1 heartbeat delivers the PURGE_LOCAL_CACHE command
        hb_a1 = api_client.post(
            "/api/v1/heartbeat",
            json={"device_id": dev_a1_id, "status": "ACTIVE", "remaining_seconds": 600.0},
        )
        assert hb_a1.status_code == 200
        cmds = hb_a1.json()["pending_commands"]
        assert len(cmds) == 1
        assert cmds[0]["command"] == "PURGE_LOCAL_CACHE"
        assert cmds[0]["payload"]["child_id"] == child_a_id


# ==============================================================================
# 4. CHILD AGENCY DOUBLE-REVIEW IDEMPOTENCY
# ==============================================================================

class TestChildAgencyDoubleReviewIdempotency:
    """Focus 4: Idempotency of approving/rejecting child requests multiple times."""

    def test_double_approval_of_add_time_request(self, api_client):
        """Approving an ADD_TIME request twice should not dispatch duplicate bonus time."""
        token, headers, child_id, device_id = _setup_parent_child_device(api_client, "double_time@test.com", "TimeKid")

        db = TestingSessionLocal()
        try:
            req = ChildRequest(
                id="req-agency-time-1",
                child_id=child_id,
                type="ADD_TIME",
                subject="Need extra 15m for presentation",
                minutes_requested=15,
                status="PENDING",
            )
            db.add(req)
            db.commit()
        finally:
            db.close()

        # First Approval
        res1 = api_client.post(
            "/api/v1/dashboard/requests/req-agency-time-1/review",
            json={"decision": "APPROVED"},
            headers=headers,
        )
        assert res1.status_code == 200
        assert res1.json()["decision"] == "APPROVED"

        # Drain the single dispatched ADD_TIME command from heartbeat
        hb1 = api_client.post(
            "/api/v1/heartbeat",
            json={"device_id": device_id, "status": "ACTIVE", "remaining_seconds": 300.0},
        )
        assert len(hb1.json()["pending_commands"]) == 1
        assert hb1.json()["pending_commands"][0]["command"] == "ADD_TIME"

        # Second Approval (simulating double-click or accidental retry)
        res2 = api_client.post(
            "/api/v1/dashboard/requests/req-agency-time-1/review",
            json={"decision": "APPROVED"},
            headers=headers,
        )
        assert res2.status_code in (200, 400)

        hb2 = api_client.post(
            "/api/v1/heartbeat",
            json={"device_id": device_id, "status": "ACTIVE", "remaining_seconds": 300.0},
        )
        # Strict Idempotency Assertion: second approval must NOT grant an additional 15 minutes!
        assert len(hb2.json()["pending_commands"]) == 0, (
            f"Non-idempotent review: duplicate ADD_TIME command dispatched on second approval: {hb2.json()['pending_commands']}"
        )

    def test_double_approval_of_unblock_domain_request(self, api_client):
        """Approving UNBLOCK_DOMAIN twice should not duplicate domains or create runaway policy versions."""
        token, headers, child_id, device_id = _setup_parent_child_device(api_client, "double_unblock@test.com", "UnblockKid")

        db = TestingSessionLocal()
        try:
            req = ChildRequest(
                id="req-agency-unblock-1",
                child_id=child_id,
                type="UNBLOCK_DOMAIN",
                subject="scratch.mit.edu",
                minutes_requested=0,
                status="PENDING",
            )
            db.add(req)
            db.commit()
        finally:
            db.close()

        # Initial policy version
        p_initial = api_client.get(f"/api/v1/children/{child_id}/policy", headers=headers).json()
        v0 = p_initial["version"]

        # First Approval
        res1 = api_client.post(
            "/api/v1/dashboard/requests/req-agency-unblock-1/review",
            json={"decision": "APPROVED"},
            headers=headers,
        )
        assert res1.status_code == 200
        p_after1 = api_client.get(f"/api/v1/children/{child_id}/policy", headers=headers).json()
        assert "scratch.mit.edu" in p_after1["whitelist"]
        v1 = p_after1["version"]
        assert v1 == v0 + 1

        # Second Approval
        res2 = api_client.post(
            "/api/v1/dashboard/requests/req-agency-unblock-1/review",
            json={"decision": "APPROVED"},
            headers=headers,
        )
        assert res2.status_code in (200, 400)

        p_after2 = api_client.get(f"/api/v1/children/{child_id}/policy", headers=headers).json()
        # Domain must still be unique in whitelist (no duplicates)
        assert p_after2["whitelist"].count("scratch.mit.edu") == 1
        # Strict Idempotency Assertion: policy version must NOT increment on second approval of same unchanged request
        assert p_after2["version"] == v1, (
            f"Non-idempotent review: policy version incremented from {v1} to {p_after2['version']} on duplicate approval"
        )



    def test_reject_already_reviewed_request(self, api_client):
        """Rejecting an already rejected request should succeed idempotently."""
        token, headers, child_id, device_id = _setup_parent_child_device(api_client, "double_reject@test.com", "RejectKid")

        db = TestingSessionLocal()
        try:
            req = ChildRequest(
                id="req-agency-reject-1",
                child_id=child_id,
                type="ADD_TIME",
                subject="Game time extension",
                minutes_requested=30,
                status="PENDING",
            )
            db.add(req)
            db.commit()
        finally:
            db.close()

        # First rejection
        r1 = api_client.post(
            "/api/v1/dashboard/requests/req-agency-reject-1/review",
            json={"decision": "REJECTED"},
            headers=headers,
        )
        assert r1.status_code == 200
        assert r1.json()["decision"] == "REJECTED"

        # Second rejection
        r2 = api_client.post(
            "/api/v1/dashboard/requests/req-agency-reject-1/review",
            json={"decision": "REJECTED"},
            headers=headers,
        )
        assert r2.status_code in (200, 400)

        # Check DB status remains REJECTED
        db = TestingSessionLocal()
        try:
            req_db = db.query(ChildRequest).filter(ChildRequest.id == "req-agency-reject-1").first()
            assert req_db.status == "REJECTED"
        finally:
            db.close()

    def test_quick_review_double_action_idempotency(self, api_client):
        """Test quick-review endpoint double approval idempotency."""
        token, headers, child_id, device_id = _setup_parent_child_device(api_client, "quick_rev@test.com", "QuickKid")

        db = TestingSessionLocal()
        try:
            req = ChildRequest(
                id="req-quick-1",
                child_id=child_id,
                type="UNBLOCK_DOMAIN",
                subject="khanacademy.org",
                minutes_requested=0,
                status="PENDING",
            )
            db.add(req)
            db.commit()
        finally:
            db.close()

        # First quick-review approve
        res1 = api_client.post(
            "/api/v1/dashboard/requests/req-quick-1/quick-review",
            json={"decision": "APPROVED"},
        )
        assert res1.status_code == 200

        # Second quick-review approve
        res2 = api_client.post(
            "/api/v1/dashboard/requests/req-quick-1/quick-review",
            json={"decision": "APPROVED"},
        )
        assert res2.status_code == 200

        # Verify domain is present exactly once
        p = api_client.get(f"/api/v1/children/{child_id}/policy", headers=headers).json()
        assert p["whitelist"].count("khanacademy.org") == 1
