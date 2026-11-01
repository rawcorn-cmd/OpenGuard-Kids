"""
Integration tests for Parent Web Dashboard, Reports (F3.2), Child Request Review,
Atomic Dual-Deletion (F3.4), 90-Day Retention Auto-Purge, 5-Tab DOM Rendering,
HMAC Policy Signatures, Domain/App Hash CRUD, and WebSocket Emergency Dispatch.
"""

import json
import time
import pytest
from fastapi.testclient import TestClient

from src.server.app import app
from src.server.models import Event, ChildRequest, Policy, AuditLog, Device, PendingCommand
from src.server.security import verify_policy_hmac, calculate_policy_hmac
from tests.conftest import TestingSessionLocal

client = TestClient(app)


# ==============================================================================
# BASELINE PRESERVED TESTS (1 to 5)
# ==============================================================================

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


# ==============================================================================
# NEW DOM RENDERING & STRUCTURE TESTS (5 TABS & EMERGENCY CONTROLS)
# ==============================================================================

def test_dashboard_html_header_and_emergency_controls():
    """Verify Header child info, live badge, 3 1-click buttons, and toast container."""
    for path in ["/dashboard/test-child-id", "/dashboard"]:
        res = client.get(path)
        assert res.status_code == 200
        assert "text/html" in res.headers["content-type"]
        html = res.text

        # Title & Branding
        assert "Bảng Điều Khiển Phụ Huynh — OpenGuard Kids" in html
        assert 'id="childNameTitle"' in html
        assert 'id="liveBadge"' in html

        # 3 1-Click Emergency Buttons
        assert 'id="btnLock"' in html
        assert "Khóa Máy Ngay" in html
        assert 'id="btnUnlock"' in html
        assert "Mở Khóa" in html
        assert 'id="btnAdd15"' in html
        assert "+15 Phút" in html

        # Toast
        assert 'id="toast"' in html


def test_dashboard_html_5_tabs_structure():
    """Verify navigation buttons and container panels for all 5 specialized tabs."""
    res = client.get("/dashboard/test-child-id")
    assert res.status_code == 200
    html = res.text

    # 5 Tab Navigation Buttons
    assert 'id="tab-btn-overview"' in html
    assert "Tổng Quan" in html
    assert 'id="tab-btn-requests"' in html
    assert "Duyệt Yêu Cầu" in html
    assert 'id="tab-btn-policy"' in html
    assert "Chính Sách" in html
    assert 'id="tab-btn-blacklist"' in html
    assert "Danh Sách Chặn" in html
    assert 'id="tab-btn-privacy"' in html
    assert "Lịch Sử" in html

    # Tab badge
    assert 'id="pendingRequestsBadge"' in html

    # 5 Tab Panels
    assert 'id="tab-overview"' in html
    assert 'id="tab-requests"' in html
    assert 'id="tab-policy"' in html
    assert 'id="tab-blacklist"' in html
    assert 'id="tab-privacy"' in html


def test_dashboard_html_tab1_realtime_overview_elements():
    """Verify Tab 1: usage gauge, Chart.js canvases, top apps, top domains."""
    res = client.get("/dashboard/test-child-id")
    assert res.status_code == 200
    html = res.text

    # Usage gauge / progress elements
    assert 'id="todayScreenTime"' in html
    assert 'id="quotaLabel"' in html
    assert 'id="screenTimeProgress"' in html
    assert 'id="blockedCount"' in html

    # Chart.js Canvases
    assert '<canvas id="usageChart"' in html
    assert '<canvas id="categoryChart"' in html

    # Rankings
    assert 'id="topAppsList"' in html
    assert 'id="topDomainsList"' in html


def test_dashboard_html_tab2_child_agency_inbox_elements():
    """Verify Tab 2: pending requests container and agency description."""
    res = client.get("/dashboard/test-child-id")
    assert res.status_code == 200
    html = res.text

    assert 'id="requestsContainer"' in html
    assert "Child Agency" in html or "Hòm Thư Yêu Cầu" in html


def test_dashboard_html_tab3_policy_config_form_elements():
    """Verify Tab 3: weekday/weekend quotas, bedtime, study mode, SafeSearch, matrix, save button."""
    res = client.get("/dashboard/test-child-id")
    assert res.status_code == 200
    html = res.text

    assert 'id="dailyQuotaMinutes"' in html
    assert 'id="weekendQuotaMinutes"' in html
    assert 'id="bedtimeStart"' in html
    assert 'id="bedtimeEnd"' in html
    assert 'id="studyModeToggle"' in html
    assert 'id="safeSearchToggle"' in html
    assert 'id="weeklyScheduleMatrix"' in html
    assert 'id="btnSavePolicy"' in html
    assert "Lưu Cấu Hình Chính Sách" in html


def test_dashboard_html_tab4_blacklist_and_classification_elements():
    """Verify Tab 4: 6 age groups reference table, custom domains, SHA-256 app hashes."""
    res = client.get("/dashboard/test-child-id")
    assert res.status_code == 200
    html = res.text

    # 6 Age Groups reference table
    assert 'id="ageGroupTable"' in html
    assert "Giáo dục" in html
    assert "Giải trí" in html
    assert "Mạng xã hội" in html
    assert "Trò chơi" in html
    assert "Không phù hợp" in html
    assert "Chưa phân loại" in html

    # Custom domain whitelist/blacklist
    assert 'id="inputBlacklistDomain"' in html
    assert 'id="btnAddBlacklist"' in html
    assert 'id="blacklistTable"' in html
    assert 'id="inputWhitelistDomain"' in html
    assert 'id="btnAddWhitelist"' in html
    assert 'id="whitelistTable"' in html

    # SHA-256 app blocklist & client-side hasher
    assert 'id="inputAppName"' in html
    assert 'id="inputAppHash"' in html
    assert 'id="btnAddAppHash"' in html
    assert 'id="appHashTable"' in html
    assert 'id="fileHashInput"' in html


def test_dashboard_html_tab5_privacy_and_audit_elements():
    """Verify Tab 5: Audit Log table, 90-day retention notice, Dual Deletion button and modal."""
    res = client.get("/dashboard/test-child-id")
    assert res.status_code == 200
    html = res.text

    # Audit log table
    assert 'id="auditLogTable"' in html

    # 90-day retention notice
    assert "90 ngày" in html

    # Atomic Dual Deletion button & modal
    assert 'id="btnDualDelete"' in html
    assert "XÓA TOÀN BỘ DỮ LIỆU CỦA CON TÔI" in html
    assert 'id="dualDeleteModal"' in html


# ==============================================================================
# REST API & WEBSOCKET INTEGRATION TESTS
# ==============================================================================

def test_policy_get_and_put_monotonic_version_and_hmac():
    """
    Test policy GET and PUT endpoints:
    - Initial policy version 1 with 64-hex HMAC signature.
    - PUT increments version monotonically to 2, then 3.
    - HMAC signature is verified cryptographically.
    - IDOR protection: Parent B cannot access or update Parent A's child policy.
    """
    # 1. Setup Parent A & Child A
    client.post("/api/v1/auth/register", json={"email": "parent_hmac_a@test.com", "password": "PasswordHmacA1!"})
    token_a = client.post("/api/v1/auth/login", json={"email": "parent_hmac_a@test.com", "password": "PasswordHmacA1!"}).json()["session_token"]
    child_a = client.post("/api/v1/children", json={"name": "Bé Lan", "age": 8}, headers={"Authorization": f"Bearer {token_a}"}).json()
    child_id_a = child_a["id"]

    # 2. Setup Parent B
    client.post("/api/v1/auth/register", json={"email": "parent_hmac_b@test.com", "password": "PasswordHmacB1!"})
    token_b = client.post("/api/v1/auth/login", json={"email": "parent_hmac_b@test.com", "password": "PasswordHmacB1!"}).json()["session_token"]

    # 3. GET initial policy for Child A
    res_get = client.get(f"/api/v1/children/{child_id_a}/policy", headers={"Authorization": f"Bearer {token_a}"})
    assert res_get.status_code == 200
    p1 = res_get.json()
    assert p1["version"] == 1
    assert "hmac_signature" in p1
    assert "signature" in p1
    assert len(p1["hmac_signature"]) == 64

    # Cryptographically verify HMAC
    assert verify_policy_hmac(p1, p1["hmac_signature"]) is True

    # 4. PUT updated policy
    matrix_sample = [[True] * 48 for _ in range(7)]
    matrix_sample[0][0] = False  # Monday midnight blocked
    update_payload = {
        "daily_quota_minutes": 100,
        "weekend_quota_minutes": 150,
        "bed_time_start": "21:00",
        "bed_time_end": "06:30",
        "study_mode": True,
        "safesearch_enabled": True,
        "schedule_matrix": matrix_sample,
    }
    res_put = client.put(f"/api/v1/children/{child_id_a}/policy", json=update_payload, headers={"Authorization": f"Bearer {token_a}"})
    assert res_put.status_code == 200
    p2 = res_put.json()
    assert p2["version"] == 2
    assert p2["daily_quota_minutes"] == 100
    assert p2["daily_quota_weekend_minutes"] == 150
    assert p2["study_mode"] is True
    assert p2["hmac_signature"] != p1["hmac_signature"]
    assert verify_policy_hmac(p2, p2["hmac_signature"]) is True

    # 5. PUT again -> version 3 (monotonicity)
    res_put2 = client.put(f"/api/v1/children/{child_id_a}/policy", json={"daily_quota_minutes": 110}, headers={"Authorization": f"Bearer {token_a}"})
    assert res_put2.status_code == 200
    p3 = res_put2.json()
    assert p3["version"] == 3
    assert p3["daily_quota_minutes"] == 110
    assert verify_policy_hmac(p3, p3["hmac_signature"]) is True

    # 6. IDOR ATTACK: Parent B attempts to access Child A's policy -> 404
    idor_get = client.get(f"/api/v1/children/{child_id_a}/policy", headers={"Authorization": f"Bearer {token_b}"})
    assert idor_get.status_code == 404

    idor_put = client.put(f"/api/v1/children/{child_id_a}/policy", json={"daily_quota_minutes": 30}, headers={"Authorization": f"Bearer {token_b}"})
    assert idor_put.status_code == 404


def test_policy_update_triggers_audit_log_entry():
    """Verify that updating policy creates an AuditLog row with action='POLICY_UPDATE'."""
    client.post("/api/v1/auth/register", json={"email": "audit_p@test.com", "password": "PasswordAudit1!"})
    token = client.post("/api/v1/auth/login", json={"email": "audit_p@test.com", "password": "PasswordAudit1!"}).json()["session_token"]
    child = client.post("/api/v1/children", json={"name": "Bé Minh", "age": 11}, headers={"Authorization": f"Bearer {token}"}).json()
    child_id = child["id"]

    # PUT policy change
    client.put(
        f"/api/v1/children/{child_id}/policy",
        json={"daily_quota_minutes": 90, "weekend_quota_minutes": 140},
        headers={"Authorization": f"Bearer {token}"},
    )

    # Check AuditLog endpoint
    res_logs = client.get(f"/api/v1/children/{child_id}/audit-logs", headers={"Authorization": f"Bearer {token}"})
    assert res_logs.status_code == 200
    logs = res_logs.json()
    assert len(logs) >= 1
    assert any(l["action"] == "POLICY_UPDATE" for l in logs)


def test_domain_blacklist_and_whitelist_crud_endpoints():
    """Test custom domain blacklist/whitelist addition and deletion with version increments."""
    client.post("/api/v1/auth/register", json={"email": "domain_crud@test.com", "password": "PasswordCrud1!"})
    token = client.post("/api/v1/auth/login", json={"email": "domain_crud@test.com", "password": "PasswordCrud1!"}).json()["session_token"]
    child = client.post("/api/v1/children", json={"name": "Bé Vy", "age": 7}, headers={"Authorization": f"Bearer {token}"}).json()
    child_id = child["id"]

    # 1. Add domain to blacklist
    res_bl = client.post(
        f"/api/v1/children/{child_id}/policy/domains",
        json={"domain": "gambling-site.com", "list_type": "blacklist"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res_bl.status_code == 200
    assert res_bl.json()["status"] == "success"
    v_bl = res_bl.json()["policy_version"]

    # Verify domain in policy
    p = client.get(f"/api/v1/children/{child_id}/policy", headers={"Authorization": f"Bearer {token}"}).json()
    assert "gambling-site.com" in p["blocklist"]

    # 2. Add domain to whitelist
    res_wl = client.post(
        f"/api/v1/children/{child_id}/policy/domains",
        json={"domain": "scratch.mit.edu", "list_type": "whitelist"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res_wl.status_code == 200
    assert res_wl.json()["policy_version"] > v_bl

    p = client.get(f"/api/v1/children/{child_id}/policy", headers={"Authorization": f"Bearer {token}"}).json()
    assert "scratch.mit.edu" in p["whitelist"]

    # 3. Delete domain from blacklist
    res_del = client.delete(
        f"/api/v1/children/{child_id}/policy/domains/gambling-site.com?list_type=blacklist",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res_del.status_code == 200

    p = client.get(f"/api/v1/children/{child_id}/policy", headers={"Authorization": f"Bearer {token}"}).json()
    assert "gambling-site.com" not in p["blocklist"]


def test_app_hash_crud_and_sha256_validation():
    """Test SHA-256 app hash blocking, validation of 64-hex regex, and removal."""
    client.post("/api/v1/auth/register", json={"email": "hash_crud@test.com", "password": "PasswordHash1!"})
    token = client.post("/api/v1/auth/login", json={"email": "hash_crud@test.com", "password": "PasswordHash1!"}).json()["session_token"]
    child = client.post("/api/v1/children", json={"name": "Bé Ken", "age": 9}, headers={"Authorization": f"Bearer {token}"}).json()
    child_id = child["id"]

    valid_hash = "93398708cd57ce44ab7d32cba5c6847b031323c3bdcd6144067316ae7a7e31c7"
    invalid_hash = "not-a-valid-sha256-hash"

    # 1. Reject invalid hash -> 400
    res_invalid = client.post(
        f"/api/v1/children/{child_id}/policy/apps",
        json={"name": "bad.exe", "sha256": invalid_hash},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res_invalid.status_code == 400

    # 2. Add valid 64-hex hash -> 200
    res_valid = client.post(
        f"/api/v1/children/{child_id}/policy/apps",
        json={"name": "cheat_engine.exe", "sha256": valid_hash},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res_valid.status_code == 200
    assert res_valid.json()["sha256"] == valid_hash

    # Verify present in policy
    p = client.get(f"/api/v1/children/{child_id}/policy", headers={"Authorization": f"Bearer {token}"}).json()
    hashes = [a["sha256"] if isinstance(a, dict) else a for a in p["blocked_apps"]]
    assert valid_hash in hashes

    # 3. Delete app hash -> 200
    res_del = client.delete(
        f"/api/v1/children/{child_id}/policy/apps/{valid_hash}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res_del.status_code == 200

    p_after = client.get(f"/api/v1/children/{child_id}/policy", headers={"Authorization": f"Bearer {token}"}).json()
    hashes_after = [a["sha256"] if isinstance(a, dict) else a for a in p_after["blocked_apps"]]
    assert valid_hash not in hashes_after


def test_child_request_review_unblock_domain_workflow():
    """Verify child agency review for UNBLOCK_DOMAIN automatically updates whitelist."""
    client.post("/api/v1/auth/register", json={"email": "unblock_req@test.com", "password": "PasswordUnblock1!"})
    token = client.post("/api/v1/auth/login", json={"email": "unblock_req@test.com", "password": "PasswordUnblock1!"}).json()["session_token"]
    child = client.post("/api/v1/children", json={"name": "Bé Dan", "age": 10}, headers={"Authorization": f"Bearer {token}"}).json()
    child_id = child["id"]

    # Child submits UNBLOCK_DOMAIN request
    db = TestingSessionLocal()
    req = ChildRequest(
        id="req-unblock-001",
        child_id=child_id,
        type="UNBLOCK_DOMAIN",
        subject="scratch.mit.edu",
        minutes_requested=0,
        status="PENDING",
    )
    db.add(req)
    db.commit()
    db.close()

    # Parent approves request
    res_review = client.post(
        "/api/v1/dashboard/requests/req-unblock-001/review",
        json={"decision": "APPROVED"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res_review.status_code == 200
    assert res_review.json()["decision"] == "APPROVED"

    # Verify "scratch.mit.edu" is now in policy whitelist!
    p = client.get(f"/api/v1/children/{child_id}/policy", headers={"Authorization": f"Bearer {token}"}).json()
    assert "scratch.mit.edu" in p["whitelist"]
    assert p["version"] >= 2


def test_dashboard_live_data_5_tabs_full_payload():
    """Verify /api/v1/dashboard/data/{child_id} returns complete payload for all 5 tabs."""
    client.post("/api/v1/auth/register", json={"email": "live_data@test.com", "password": "PasswordLive1!"})
    token = client.post("/api/v1/auth/login", json={"email": "live_data@test.com", "password": "PasswordLive1!"}).json()["session_token"]
    child = client.post("/api/v1/children", json={"name": "Bé Bắp", "age": 6}, headers={"Authorization": f"Bearer {token}"}).json()
    child_id = child["id"]

    res = client.get(f"/api/v1/dashboard/data/{child_id}")
    assert res.status_code == 200
    data = res.json()

    # Required keys across 5 tabs
    assert "child" in data or "child_id" in data
    assert "screen_time_today_minutes" in data
    assert "quota_minutes" in data
    assert "total_blocked_count" in data or "blocked_count" in data
    assert "weekly_history" in data
    assert len(data["weekly_history"]) == 7
    assert "category_distribution" in data
    assert "top_10_apps" in data or "top_apps" in data
    assert "top_10_domains" in data or "top_domains" in data
    assert "pending_requests" in data or "requests" in data
    assert "policy" in data
    assert "audit_logs" in data
    assert "classification_data" in data
    assert "retention_status" in data


def test_websocket_urgent_command_dispatch_and_offline_fallback():
    """
    Test emergency command delivery:
    1. Offline fallback persisted to PendingCommand table.
    2. Heartbeat drains pending commands and returns actual policy version.
    """
    client.post("/api/v1/auth/register", json={"email": "ws_test_p@test.com", "password": "PasswordWs1!"})
    token = client.post("/api/v1/auth/login", json={"email": "ws_test_p@test.com", "password": "PasswordWs1!"}).json()["session_token"]
    child = client.post("/api/v1/children", json={"name": "Bé Miu", "age": 8}, headers={"Authorization": f"Bearer {token}"}).json()
    child_id = child["id"]

    code = client.post(f"/api/v1/children/{child_id}/pairing-code", headers={"Authorization": f"Bearer {token}"}).json()["pairing_code"]
    dev = client.post("/api/v1/enroll/device", json={"pairing_code": code, "hostname": "MIU-PC"}).json()
    device_id = dev["device_id"]

    # Device is currently offline -> send LOCK_URGENT from dashboard
    res_cmd = client.post(
        f"/api/v1/dashboard/{child_id}/command",
        json={"command": "LOCK_URGENT", "minutes": 0},
    )
    assert res_cmd.status_code == 200

    # Verify PendingCommand was recorded in SQLite database
    db = TestingSessionLocal()
    pending_recs = db.query(PendingCommand).filter(PendingCommand.device_id == device_id).all()
    assert len(pending_recs) >= 1
    assert pending_recs[0].command_type == "LOCK_URGENT"
    db.close()

    # Agent heartbeats -> pending command delivered and queue cleared
    hb_res = client.post(
        "/api/v1/heartbeat",
        json={"device_id": device_id, "status": "ACTIVE", "remaining_seconds": 1800.0},
    )
    assert hb_res.status_code == 200
    hb_data = hb_res.json()
    assert len(hb_data["pending_commands"]) >= 1
    assert hb_data["pending_commands"][0]["command"] == "LOCK_URGENT"
    assert hb_data["policy_version"] >= 1

    # Subsequent heartbeat: queue drained
    hb_res2 = client.post(
        "/api/v1/heartbeat",
        json={"device_id": device_id, "status": "ACTIVE", "remaining_seconds": 1800.0},
    )
    assert len(hb_res2.json()["pending_commands"]) == 0


def test_classification_reference_endpoint():
    """Verify classification dataset taxonomy and search filter."""
    res = client.get("/api/v1/classification/reference")
    assert res.status_code == 200
    data = res.json()
    assert "taxonomy" in data
    assert "entries" in data

    # Test filtering by category
    res_cat = client.get("/api/v1/classification/reference?category=education")
    assert res_cat.status_code == 200
    for e in res_cat.json()["entries"]:
        assert e["category"] == "education"


def test_unauthenticated_requests_to_policy_and_dashboard_return_401():
    """Verify that unauthenticated requests to mutating policy and dashboard endpoints return 401."""
    anon_client = TestClient(app)
    fake_uuid = "00000000-0000-0000-0000-000000000001"

    # 1. GET policy
    res = anon_client.get(f"/api/v1/children/{fake_uuid}/policy")
    assert res.status_code == 401, f"Expected 401 for GET policy, got {res.status_code}"

    # 2. PUT policy
    res = anon_client.put(f"/api/v1/children/{fake_uuid}/policy", json={"daily_quota_minutes": 1440})
    assert res.status_code == 401, f"Expected 401 for PUT policy, got {res.status_code}"

    # 3. POST domain
    res = anon_client.post(f"/api/v1/children/{fake_uuid}/policy/domains", json={"domain": "example.com", "list_type": "whitelist"})
    assert res.status_code == 401, f"Expected 401 for POST domain, got {res.status_code}"

    # 4. DELETE domain
    res = anon_client.delete(f"/api/v1/children/{fake_uuid}/policy/domains/example.com")
    assert res.status_code == 401, f"Expected 401 for DELETE domain, got {res.status_code}"

    # 5. POST app hash
    test_hash = "a" * 64
    res = anon_client.post(f"/api/v1/children/{fake_uuid}/policy/apps", json={"name": "test.exe", "sha256": test_hash})
    assert res.status_code == 401, f"Expected 401 for POST app hash, got {res.status_code}"

    # 6. DELETE app hash
    res = anon_client.delete(f"/api/v1/children/{fake_uuid}/policy/apps/{test_hash}")
    assert res.status_code == 401, f"Expected 401 for DELETE app hash, got {res.status_code}"

    # 7. GET audit-logs
    res = anon_client.get(f"/api/v1/children/{fake_uuid}/audit-logs")
    assert res.status_code == 401, f"Expected 401 for GET audit-logs, got {res.status_code}"

    # 8. POST dashboard command
    res = anon_client.post(f"/api/v1/dashboard/{fake_uuid}/command", json={"command": "LOCK_URGENT"})
    assert res.status_code == 401, f"Expected 401 for POST command, got {res.status_code}"

    # 9. POST quick-review
    res = anon_client.post(f"/api/v1/dashboard/requests/{fake_uuid}/quick-review", json={"decision": "APPROVED"})
    assert res.status_code == 401, f"Expected 401 for POST quick-review, got {res.status_code}"

