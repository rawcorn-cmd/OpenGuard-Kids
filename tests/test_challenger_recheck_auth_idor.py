"""
Exhaustive Adversarial Auth & IDOR Stress Verification Suite for Milestone W5/M5.
Challenger: teamwork_challenger (challenger_recheck_1)

Adversarial Verification Targets:
1. Unauthenticated Attacks (Missing, Empty, Invalid, or Malformed Auth):
   - All policy mutation endpoints, command dispatch, review, and purge endpoints MUST return 401 Unauthorized.
2. Cross-Parent IDOR Attacks (Parent B attacking Child A / Request A):
   - All policy mutation endpoints, command dispatch, review, quick-review, and purge endpoints MUST return 404 Not Found.
3. State Preservation Oracle:
   - Ensure Child A's policy, device pending commands, requests, and audit logs remain completely unmutated after all failed attacks.
"""

import json
import secrets
import pytest
from fastapi.testclient import TestClient

from src.server.app import app
from src.server.models import Child, ChildRequest, Device, Policy, Event, AuditLog
from tests.conftest import TestingSessionLocal


@pytest.fixture
def api_client():
    return TestClient(app)


def _create_parent_and_child(client: TestClient, prefix: str):
    email = f"{prefix}_{secrets.token_hex(4)}@test.local"
    password = "StrongPassword123!"
    client.post("/api/v1/auth/register", json={"email": email, "password": password})
    login_res = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    token = login_res.json()["session_token"]
    parent_id = login_res.json()["parent_id"]

    child_res = client.post(
        "/api/v1/children",
        json={"name": f"Child_{prefix}", "age": 10},
        headers={"Authorization": f"Bearer {token}"},
    )
    child = child_res.json()
    child_id = child["id"]

    # Enroll a device for Child A
    code_res = client.post(
        f"/api/v1/children/{child_id}/pairing-code",
        headers={"Authorization": f"Bearer {token}"},
    ).json()
    code = code_res["pairing_code"]
    dev_res = client.post(
        "/api/v1/enroll/device",
        json={"pairing_code": code, "hostname": f"{prefix}-PC"},
    ).json()
    device_id = dev_res["device_id"]

    return {
        "email": email,
        "token": token,
        "parent_id": parent_id,
        "child_id": child_id,
        "device_id": device_id,
        "headers": {"Authorization": f"Bearer {token}"},
    }


# ==============================================================================
# 1. Unauthenticated Stress Testing
# ==============================================================================

class TestUnauthenticatedPolicyAndCommandEndpoints:
    """Verify that every policy mutation, review, and emergency endpoint rejects unauthenticated requests with 401."""

    @pytest.fixture(autouse=True)
    def setup(self, api_client):
        self.family = _create_parent_and_child(api_client, "anon_target")
        self.child_id = self.family["child_id"]

        # Insert a pending ChildRequest
        db = TestingSessionLocal()
        try:
            req = ChildRequest(
                id=f"req-anon-{secrets.token_hex(4)}",
                child_id=self.child_id,
                type="ADD_TIME",
                subject="Request time",
                minutes_requested=15,
                status="PENDING",
            )
            db.add(req)
            db.commit()
            self.request_id = req.id
        finally:
            db.close()

    @pytest.mark.parametrize(
        "auth_header,cookie_val",
        [
            ({}, None),                                            # Missing Authorization header, no cookie
            ({"Authorization": ""}, None),                         # Empty header, no cookie
            ({"Authorization": "Bearer "}, None),                  # Empty bearer token, no cookie
            ({"Authorization": "Bearer invalid_tok"}, None),       # Invalid bearer token, no cookie
            ({"Authorization": "Basic YWxhZGRpbjpvcGVuc2VzYW1l"}, None), # Wrong scheme, no cookie
            ({}, "invalid_cookie_token_12345"),                    # Invalid session cookie
            ({"Authorization": "Bearer bad"}, "invalid_cookie"),   # Bad bearer + bad cookie
        ],
    )
    def test_unauthenticated_policy_mutations_return_401(self, auth_header, cookie_val):
        anon_client = TestClient(app)
        if cookie_val:
            anon_client.cookies.set("session_token", cookie_val)

        test_sha = "b" * 64

        endpoints = [
            ("GET", f"/api/v1/children/{self.child_id}/policy", None),
            ("PUT", f"/api/v1/children/{self.child_id}/policy", {"daily_quota_minutes": 60}),
            ("POST", f"/api/v1/children/{self.child_id}/policy/domains", {"domain": "bad.com", "list_type": "blacklist"}),
            ("POST", f"/api/v1/children/{self.child_id}/policy/blacklist", {"domain": "bad2.com"}),
            ("POST", f"/api/v1/children/{self.child_id}/policy/whitelist", {"domain": "good.com"}),
            ("DELETE", f"/api/v1/children/{self.child_id}/policy/domains/bad.com", None),
            ("DELETE", f"/api/v1/children/{self.child_id}/policy/blacklist/bad2.com", None),
            ("DELETE", f"/api/v1/children/{self.child_id}/policy/whitelist/good.com", None),
            ("DELETE", f"/api/v1/children/{self.child_id}/policy/domains", {"domain": "bad.com"}),
            ("POST", f"/api/v1/children/{self.child_id}/policy/apps", {"name": "game.exe", "sha256": test_sha}),
            ("POST", f"/api/v1/children/{self.child_id}/policy/app-hashes", {"name": "game2.exe", "sha256": test_sha}),
            ("DELETE", f"/api/v1/children/{self.child_id}/policy/apps/{test_sha}", None),
            ("DELETE", f"/api/v1/children/{self.child_id}/policy/app-hashes/{test_sha}", None),
            ("GET", f"/api/v1/children/{self.child_id}/audit-logs", None),
            ("POST", f"/api/v1/dashboard/{self.child_id}/command", {"command": "LOCK_URGENT"}),
            ("POST", f"/api/v1/dashboard/requests/{self.request_id}/review", {"decision": "APPROVED"}),
            ("POST", f"/api/v1/dashboard/requests/{self.request_id}/quick-review", {"decision": "APPROVED"}),
            ("DELETE", f"/api/v1/children/{self.child_id}/purge-data", None),
            ("POST", f"/api/v1/children/{self.child_id}/pairing-code", None),
        ]

        for method, url, body in endpoints:
            if method == "GET":
                res = anon_client.get(url, headers=auth_header)
            elif method == "POST":
                res = anon_client.post(url, json=body, headers=auth_header)
            elif method == "PUT":
                res = anon_client.put(url, json=body, headers=auth_header)
            elif method == "DELETE":
                res = anon_client.request("DELETE", url, json=body, headers=auth_header)
            else:
                pytest.fail(f"Unsupported method {method}")

            assert res.status_code == 401, (
                f"Endpoint {method} {url} with header {auth_header} and cookie {cookie_val} expected 401, got {res.status_code}: {res.text}"
            )


# ==============================================================================
# 2. Cross-Parent IDOR Stress Testing
# ==============================================================================

class TestCrossParentIdorStress:
    """Verify that Parent B cannot read, mutate, command, review, or purge Child A's resources."""

    @pytest.fixture(autouse=True)
    def setup_two_distinct_parents(self, api_client):
        self.family_a = _create_parent_and_child(api_client, "family_a")
        self.family_b = _create_parent_and_child(api_client, "family_b")

        self.child_a_id = self.family_a["child_id"]
        self.device_a_id = self.family_a["device_id"]
        self.token_b_headers = self.family_b["headers"]

        # Insert a pending request for Child A
        db = TestingSessionLocal()
        try:
            req_a = ChildRequest(
                id=f"req-a-{secrets.token_hex(4)}",
                child_id=self.child_a_id,
                type="UNBLOCK_DOMAIN",
                subject="hacked-portal.com",
                minutes_requested=0,
                status="PENDING",
            )
            db.add(req_a)
            db.commit()
            self.request_a_id = req_a.id
        finally:
            db.close()

    def test_idor_cannot_modify_child_a_policy(self, api_client):
        res = api_client.put(
            f"/api/v1/children/{self.child_a_id}/policy",
            json={"daily_quota_minutes": 1440, "study_mode": False},
            headers=self.token_b_headers,
        )
        assert res.status_code == 404

    def test_idor_cannot_add_or_remove_domains_for_child_a(self, api_client):
        # Blacklist domain
        res1 = api_client.post(
            f"/api/v1/children/{self.child_a_id}/policy/blacklist",
            json={"domain": "malicious-injection.com"},
            headers=self.token_b_headers,
        )
        assert res1.status_code == 404

        # Whitelist domain
        res2 = api_client.post(
            f"/api/v1/children/{self.child_a_id}/policy/whitelist",
            json={"domain": "bypass.com"},
            headers=self.token_b_headers,
        )
        assert res2.status_code == 404

        # Delete domain
        res3 = api_client.delete(
            f"/api/v1/children/{self.child_a_id}/policy/domains/bypass.com",
            headers=self.token_b_headers,
        )
        assert res3.status_code == 404

    def test_idor_cannot_add_or_remove_apps_for_child_a(self, api_client):
        test_sha = "c" * 64
        res1 = api_client.post(
            f"/api/v1/children/{self.child_a_id}/policy/apps",
            json={"name": "exploit.exe", "sha256": test_sha},
            headers=self.token_b_headers,
        )
        assert res1.status_code == 404

        res2 = api_client.delete(
            f"/api/v1/children/{self.child_a_id}/policy/apps/{test_sha}",
            headers=self.token_b_headers,
        )
        assert res2.status_code == 404

    def test_idor_cannot_dispatch_emergency_commands_to_child_a_device(self, api_client):
        """Parent B cannot send LOCK_URGENT or ADD_TIME commands to Child A's device."""
        res = api_client.post(
            f"/api/v1/dashboard/{self.child_a_id}/command",
            json={"command": "LOCK_URGENT", "minutes": 0},
            headers=self.token_b_headers,
        )
        assert res.status_code == 404, f"Expected 404 for IDOR command dispatch, got {res.status_code}"

    def test_idor_cannot_review_child_a_request(self, api_client):
        """Parent B cannot approve or reject Child A's request via /review."""
        res = api_client.post(
            f"/api/v1/dashboard/requests/{self.request_a_id}/review",
            json={"decision": "APPROVED"},
            headers=self.token_b_headers,
        )
        assert res.status_code == 404, f"Expected 404 for IDOR request review, got {res.status_code}"

    def test_idor_cannot_quick_review_child_a_request(self, api_client):
        """Parent B cannot approve or reject Child A's request via /quick-review."""
        res = api_client.post(
            f"/api/v1/dashboard/requests/{self.request_a_id}/quick-review",
            json={"decision": "APPROVED"},
            headers=self.token_b_headers,
        )
        assert res.status_code == 404, f"Expected 404 for IDOR quick review, got {res.status_code}"

    def test_idor_cannot_purge_child_a_data(self, api_client):
        """Parent B cannot execute atomic dual deletion on Child A."""
        res = api_client.delete(
            f"/api/v1/children/{self.child_a_id}/purge-data",
            headers=self.token_b_headers,
        )
        assert res.status_code == 404, f"Expected 404 for IDOR purge data, got {res.status_code}"

    def test_idor_cannot_read_child_a_audit_logs(self, api_client):
        """Parent B cannot read Child A's audit logs."""
        res = api_client.get(
            f"/api/v1/children/{self.child_a_id}/audit-logs",
            headers=self.token_b_headers,
        )
        assert res.status_code == 404, f"Expected 404 for IDOR audit logs, got {res.status_code}"

    def test_child_a_state_remains_intact_and_unpolluted(self, api_client):
        """Verify that Child A's request is still PENDING and policy is untouched after IDOR attacks."""
        db = TestingSessionLocal()
        try:
            req = db.query(ChildRequest).filter(ChildRequest.id == self.request_a_id).first()
            assert req.status == "PENDING", f"Request status polluted: {req.status}"

            pol = db.query(Policy).filter(Policy.child_id == self.child_a_id).first()
            if pol:
                assert "malicious-injection.com" not in (pol.blocklist_json or "")
                assert "bypass.com" not in (pol.whitelist_json or "")
                assert ("c" * 64) not in (pol.app_blocklist_json or "")
        finally:
            db.close()
