"""
Integration tests for Parent Authentication, IDOR Protection, and Device Enrollment API.
"""

import time
import pytest
from fastapi.testclient import TestClient

from src.server.app import app
from src.server.models import Device

client = TestClient(app)


def test_parent_register_password_complexity():
    # 1. Weak password (too short)
    res_short = client.post("/api/v1/auth/register", json={"email": "p1@example.com", "password": "Short1!"})
    assert res_short.status_code == 422 or res_short.status_code == 400

    # 2. Missing special character
    res_no_sym = client.post("/api/v1/auth/register", json={"email": "p1@example.com", "password": "Password1234"})
    assert res_no_sym.status_code == 400
    assert "ký tự đặc biệt" in res_no_sym.json()["detail"]

    # 3. Valid Argon2id compliant password
    res_ok = client.post("/api/v1/auth/register", json={"email": "parent1@example.com", "password": "StrongPassword123!"})
    assert res_ok.status_code == 201
    data = res_ok.json()
    assert data["email"] == "parent1@example.com"
    assert "id" in data

    # 4. Duplicate email rejected
    res_dup = client.post("/api/v1/auth/register", json={"email": "parent1@example.com", "password": "StrongPassword123!"})
    assert res_dup.status_code == 409


def test_parent_login_and_brute_force_lockout():
    # Register parent
    client.post("/api/v1/auth/register", json={"email": "parent_bf@example.com", "password": "Password123@#$"})

    # 4 incorrect attempts
    for i in range(1, 5):
        res = client.post("/api/v1/auth/login", json={"email": "parent_bf@example.com", "password": "WrongPassword1!"})
        assert res.status_code == 401
        assert f"Lần thử {i}/5" in res.json()["detail"]

    # 5th incorrect attempt -> triggers 15-minute account lockout
    res_lock = client.post("/api/v1/auth/login", json={"email": "parent_bf@example.com", "password": "WrongPassword1!"})
    assert res_lock.status_code == 429
    assert "15 phút" in res_lock.json()["detail"]

    # Even with correct password, login is blocked while locked
    res_blocked = client.post("/api/v1/auth/login", json={"email": "parent_bf@example.com", "password": "Password123@#$"})
    assert res_blocked.status_code == 429


def test_login_session_and_me_endpoint():
    client.post("/api/v1/auth/register", json={"email": "valid_user@example.com", "password": "ValidPassword999!"})

    login_res = client.post("/api/v1/auth/login", json={"email": "valid_user@example.com", "password": "ValidPassword999!"})
    assert login_res.status_code == 200
    login_data = login_res.json()
    token = login_data["session_token"]
    assert token

    # Test /auth/me with Cookie
    me_res = client.get("/api/v1/auth/me", cookies={"session_token": token})
    assert me_res.status_code == 200
    assert me_res.json()["email"] == "valid_user@example.com"

    # Test /auth/me with Bearer Authorization header
    me_header_res = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_header_res.status_code == 200
    assert me_header_res.json()["email"] == "valid_user@example.com"


def test_idor_protection_and_device_enrollment():
    # Create Parent A
    client.post("/api/v1/auth/register", json={"email": "parentA@test.com", "password": "ParentAPassword1!"})
    login_a = client.post("/api/v1/auth/login", json={"email": "parentA@test.com", "password": "ParentAPassword1!"}).json()
    token_a = login_a["session_token"]

    # Create Parent B
    client.post("/api/v1/auth/register", json={"email": "parentB@test.com", "password": "ParentBPassword1!"})
    login_b = client.post("/api/v1/auth/login", json={"email": "parentB@test.com", "password": "ParentBPassword1!"}).json()
    token_b = login_b["session_token"]

    # Parent A creates child "Bé Bo"
    child_res = client.post(
        "/api/v1/children",
        json={"name": "Bé Bo", "age": 10},
        headers={"Authorization": f"Bearer {token_a}"},
    )
    assert child_res.status_code == 201
    child_a_id = child_res.json()["id"]

    # IDOR TEST: Parent B attempts to generate pairing code for Parent A's child -> MUST BE REJECTED 404/403
    idor_res = client.post(
        f"/api/v1/children/{child_a_id}/pairing-code",
        headers={"Authorization": f"Bearer {token_b}"},
    )
    assert idor_res.status_code == 404

    # Parent A generates valid pairing code
    pair_res = client.post(
        f"/api/v1/children/{child_a_id}/pairing-code",
        headers={"Authorization": f"Bearer {token_a}"},
    )
    assert pair_res.status_code == 200
    pair_data = pair_res.json()
    code = pair_data["pairing_code"]
    assert len(code) == 8

    # Windows Agent enrolls device using the 8-character pairing code
    enroll_res = client.post(
        "/api/v1/enroll/device",
        json={"pairing_code": code, "hostname": "DESKTOP-BE-BO", "device_fingerprint": "abc123hwid"},
    )
    assert enroll_res.status_code == 200
    enroll_data = enroll_res.json()
    assert enroll_data["status"] == "ENROLLED"
    assert enroll_data["child_id"] == child_a_id
    assert "ogk_dev_" in enroll_data["device_token"]

    # Replay attack: Re-using the same pairing code must fail
    replay_res = client.post(
        "/api/v1/enroll/device",
        json={"pairing_code": code, "hostname": "ATTACKER-PC"},
    )
    assert replay_res.status_code == 400
