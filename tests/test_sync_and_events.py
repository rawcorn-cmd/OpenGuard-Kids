"""
Integration tests for OpenGuard Kids Event Batch Ingestion, Heartbeat Sync, and Urgent Command Dispatch.
Verifies the 7-field privacy schema (NT2), deduplication via idempotency_key, and offline fallback delivery.
"""

import time
import pytest
from fastapi.testclient import TestClient

from src.server.app import app
from src.server.models import Parent, Child, Device

client = TestClient(app)


def test_batch_event_ingestion_and_idempotency():
    # 1. Register parent and create child + device
    client.post("/api/v1/auth/register", json={"email": "parent_event@test.com", "password": "Password123!@#"})
    login_res = client.post("/api/v1/auth/login", json={"email": "parent_event@test.com", "password": "Password123!@#"}).json()
    token = login_res["session_token"]

    child = client.post("/api/v1/children", json={"name": "Tom", "age": 8}, headers={"Authorization": f"Bearer {token}"}).json()
    code = client.post(f"/api/v1/children/{child['id']}/pairing-code", headers={"Authorization": f"Bearer {token}"}).json()["pairing_code"]
    dev = client.post("/api/v1/enroll/device", json={"pairing_code": code, "hostname": "TOM-PC"}).json()

    # 2. Ingest batch of events (7-field schema)
    events_payload = {
        "events": [
            {
                "device_id": dev["device_id"],
                "child_id": child["id"],
                "type": "blocked_domain",
                "subject": "bad-gambling.com",
                "duration_sec": 0,
                "ts": time.time(),
                "idempotency_key": "evt-unique-001",
            },
            {
                "device_id": dev["device_id"],
                "child_id": child["id"],
                "type": "screen_time",
                "subject": "active_study",
                "duration_sec": 300,
                "ts": time.time(),
                "idempotency_key": "evt-unique-002",
            }
        ]
    }

    res = client.post("/api/v1/events/batch", json=events_payload)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "SUCCESS"
    assert data["ingested_count"] == 2
    assert "evt-unique-001" in data["acknowledged_keys"]

    # 3. Re-post the identical batch (Idempotency test)
    res_repeat = client.post("/api/v1/events/batch", json=events_payload)
    assert res_repeat.status_code == 200
    # Must acknowledge both keys without database unique constraint error
    assert res_repeat.json()["ingested_count"] == 2


def test_heartbeat_and_urgent_command_fallback():
    # 1. Setup Parent, Child, Device
    client.post("/api/v1/auth/register", json={"email": "parent_cmd@test.com", "password": "PasswordCmd123!"})
    login_res = client.post("/api/v1/auth/login", json={"email": "parent_cmd@test.com", "password": "PasswordCmd123!"}).json()
    token = login_res["session_token"]

    child = client.post("/api/v1/children", json={"name": "Alice", "age": 10}, headers={"Authorization": f"Bearer {token}"}).json()
    code = client.post(f"/api/v1/children/{child['id']}/pairing-code", headers={"Authorization": f"Bearer {token}"}).json()["pairing_code"]
    dev = client.post("/api/v1/enroll/device", json={"pairing_code": code, "hostname": "ALICE-PC"}).json()
    device_id = dev["device_id"]

    # 2. Parent sends urgent command "LOCK_URGENT" ("Khóa ngay")
    cmd_res = client.post(
        f"/api/v1/devices/{device_id}/command",
        json={"command": "LOCK_URGENT"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert cmd_res.status_code == 200
    assert cmd_res.json()["status"] == "success"

    # 3. Agent calls periodic 60s HTTP heartbeat
    hb_res = client.post(
        "/api/v1/heartbeat",
        json={"device_id": device_id, "screen_time_remaining": 1200.0, "status": "ACTIVE"},
    )
    assert hb_res.status_code == 200
    hb_data = hb_res.json()
    assert "server_time" in hb_data

    # Verify pending command was delivered via heartbeat fallback!
    assert len(hb_data["pending_commands"]) == 1
    assert hb_data["pending_commands"][0]["command"] == "LOCK_URGENT"

    # Subsequent heartbeat: queue is now cleared
    hb_res2 = client.post(
        "/api/v1/heartbeat",
        json={"device_id": device_id, "screen_time_remaining": 1200.0, "status": "ACTIVE"},
    )
    assert len(hb_res2.json()["pending_commands"]) == 0


def test_idor_protection_on_device_command():
    # Parent A
    client.post("/api/v1/auth/register", json={"email": "pA@test.com", "password": "PassParentA123!"})
    token_a = client.post("/api/v1/auth/login", json={"email": "pA@test.com", "password": "PassParentA123!"}).json()["session_token"]

    # Parent B
    client.post("/api/v1/auth/register", json={"email": "pB@test.com", "password": "PassParentB123!"})
    token_b = client.post("/api/v1/auth/login", json={"email": "pB@test.com", "password": "PassParentB123!"}).json()["session_token"]

    # Parent A creates child and device
    child_a = client.post("/api/v1/children", json={"name": "Bob", "age": 7}, headers={"Authorization": f"Bearer {token_a}"}).json()
    code_a = client.post(f"/api/v1/children/{child_a['id']}/pairing-code", headers={"Authorization": f"Bearer {token_a}"}).json()["pairing_code"]
    dev_a = client.post("/api/v1/enroll/device", json={"pairing_code": code_a, "hostname": "BOB-PC"}).json()

    # IDOR ATTACK: Parent B tries to lock Parent A's child PC -> MUST BE REJECTED 404
    attack_res = client.post(
        f"/api/v1/devices/{dev_a['device_id']}/command",
        json={"command": "LOCK_URGENT"},
        headers={"Authorization": f"Bearer {token_b}"},
    )
    assert attack_res.status_code == 404
