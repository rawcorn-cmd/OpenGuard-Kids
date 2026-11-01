"""
OpenGuard Kids — Challenger Adversarial Verification Test Suite
Target: Milestone W5/M5 Parent Web Dashboard & Policy Synchronization Engine

Adversarial Challenge Focus:
1. HMAC-SHA256 signature tampering:
   - Modifying any byte, field, or key in policy fails HMAC verification.
2. Monotonic versioning:
   - Client cannot freeze or inject arbitrary versions.
   - Concurrent/rapid sequential updates monotonically increment policy version.
   - Policy consumer/agent rejection oracle for stale or non-advancing version.
3. Bedtime curfew crossing midnight (21:30 - 06:00):
   - Boundary checks at 21:29:59, 21:30:00, 23:59:59, 00:00:00, 05:59:59, 06:00:00.
   - 7x48 schedule matrix slot translation across midnight.
   - ScreenTimeTracker live state machine transition across midnight curfew.
4. Input validation:
   - Quota boundary values (14, 15, 1440, 1441, -1).
   - SHA-256 app hash format enforcement (length != 64, non-hex, empty).
   - Malformed/corrupted JSON payloads (non-list matrix, non-list blocklist).
5. Multi-child isolation (IDOR):
   - Comprehensive cross-child access/mutation denial across all policy, domain, app, audit, and purge endpoints.
"""

from __future__ import annotations

import json
import secrets
from datetime import datetime, time as dtime
from typing import Dict, Any, List

import pytest
from fastapi.testclient import TestClient

from src.server.app import app
from src.server.security import calculate_policy_hmac, verify_policy_hmac
from src.agent.screen_time import ScreenTimeTracker, ScreenTimeState


client = TestClient(app)


# ==============================================================================
# Helper Fixtures & Setup
# ==============================================================================

def create_parent_and_child(prefix: str):
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
    return {"token": token, "parent_id": parent_id, "child_id": child["id"], "child": child}


# ==============================================================================
# 1. HMAC-SHA256 Signature Tampering Adversarial Tests
# ==============================================================================

class TestHmacSignatureTamperingAdversarial:
    """Stress tests cryptographic integrity of canonical policy JSON."""

    def test_tamper_every_individual_field_fails_hmac(self):
        """Modifying any single key or value must cause HMAC verification to fail."""
        base_policy: Dict[str, Any] = {
            "child_id": "child-test-123",
            "version": 3,
            "daily_quota_minutes": 120,
            "daily_quota_weekend_minutes": 180,
            "bed_time_start": "21:30",
            "bed_time_end": "06:00",
            "study_mode": False,
            "safesearch_enabled": True,
            "blocklist": ["badsite.com", "malware.org"],
            "whitelist": ["wikipedia.org", "school.edu"],
            "blocked_apps": [{"name": "game.exe", "sha256": "a" * 64}],
            "schedule_matrix": [[True] * 48 for _ in range(7)],
        }

        valid_hmac = calculate_policy_hmac(base_policy)
        assert verify_policy_hmac(base_policy, valid_hmac) is True

        # List of mutations across all policy parameters
        mutations = [
            ("child_id", "child-test-999"),
            ("version", 4),
            ("version", 2),
            ("version", 0),
            ("daily_quota_minutes", 121),
            ("daily_quota_minutes", 0),
            ("daily_quota_weekend_minutes", 240),
            ("bed_time_start", "21:31"),
            ("bed_time_start", "22:00"),
            ("bed_time_end", "06:01"),
            ("bed_time_end", "05:59"),
            ("study_mode", True),
            ("safesearch_enabled", False),
            ("blocklist", ["badsite.com"]),
            ("blocklist", ["badsite.com", "malware.org", "extra.com"]),
            ("whitelist", ["wikipedia.org"]),
            ("blocked_apps", [{"name": "game.exe", "sha256": "b" * 64}]),
        ]

        for field, new_val in mutations:
            tampered = dict(base_policy)
            tampered[field] = new_val
            assert verify_policy_hmac(tampered, valid_hmac) is False, (
                f"HMAC verification unexpectedly passed when tampering field '{field}' to {new_val}"
            )

    def test_tamper_schedule_matrix_single_bit_fails_hmac(self):
        """Flipping a single boolean slot in the 7x48 matrix must break the signature."""
        matrix = [[True] * 48 for _ in range(7)]
        policy = {
            "child_id": "child-test-matrix",
            "version": 1,
            "daily_quota_minutes": 60,
            "daily_quota_weekend_minutes": 60,
            "bed_time_start": "21:30",
            "bed_time_end": "06:00",
            "study_mode": False,
            "safesearch_enabled": True,
            "blocklist": [],
            "whitelist": [],
            "blocked_apps": [],
            "schedule_matrix": matrix,
        }
        valid_hmac = calculate_policy_hmac(policy)

        # Mutate day 0, slot 43 (Monday 21:30)
        matrix_tampered = [list(row) for row in matrix]
        matrix_tampered[0][43] = False
        tampered_policy = dict(policy, schedule_matrix=matrix_tampered)

        assert verify_policy_hmac(tampered_policy, valid_hmac) is False

    def test_tamper_signature_bytes(self):
        """Corrupting characters of the signature must be rejected."""
        policy = {
            "child_id": "c1",
            "version": 1,
            "daily_quota_minutes": 90,
            "daily_quota_weekend_minutes": 90,
            "bed_time_start": "21:30",
            "bed_time_end": "06:00",
            "study_mode": False,
            "safesearch_enabled": True,
            "blocklist": [],
            "whitelist": [],
            "blocked_apps": [],
            "schedule_matrix": [],
        }
        sig = calculate_policy_hmac(policy)

        # 1. Flip last character
        flipped_char = '0' if sig[-1] != '0' else '1'
        corrupted_sig = sig[:-1] + flipped_char
        assert verify_policy_hmac(policy, corrupted_sig) is False

        # 2. Truncate signature
        assert verify_policy_hmac(policy, sig[:32]) is False

        # 3. Append garbage
        assert verify_policy_hmac(policy, sig + "deadbeef") is False

        # 4. Empty and None signatures
        assert verify_policy_hmac(policy, "") is False
        assert verify_policy_hmac(policy, None) is False

    def test_injected_extra_keys_fail_hmac(self):
        """Attacker injecting unauthorized attributes must fail HMAC validation."""
        policy = {
            "child_id": "c1",
            "version": 1,
            "daily_quota_minutes": 90,
            "daily_quota_weekend_minutes": 90,
            "bed_time_start": "21:30",
            "bed_time_end": "06:00",
            "study_mode": False,
            "safesearch_enabled": True,
            "blocklist": [],
            "whitelist": [],
            "blocked_apps": [],
            "schedule_matrix": [],
        }
        valid_hmac = calculate_policy_hmac(policy)

        injected_policy = dict(policy)
        injected_policy["is_admin"] = True
        injected_policy["bypass_all_restrictions"] = True

        assert verify_policy_hmac(injected_policy, valid_hmac) is False

    def test_secret_key_mismatch_fails(self):
        """Signatures produced under an attacker's key are rejected under server secret."""
        policy = {
            "child_id": "c1",
            "version": 1,
            "daily_quota_minutes": 90,
            "daily_quota_weekend_minutes": 90,
            "bed_time_start": "21:30",
            "bed_time_end": "06:00",
            "study_mode": False,
            "safesearch_enabled": True,
            "blocklist": [],
            "whitelist": [],
            "blocked_apps": [],
            "schedule_matrix": [],
        }
        fake_secret = "attacker_rogue_secret_key_12345"
        forged_sig = calculate_policy_hmac(policy, secret_key=fake_secret)

        # Verification with default server key must fail
        assert verify_policy_hmac(policy, forged_sig) is False

    def test_canonical_json_key_order_independence(self):
        """Canonical JSON normalization guarantees that dict key ordering does not alter HMAC."""
        policy1 = {
            "child_id": "c1",
            "version": 1,
            "daily_quota_minutes": 60,
            "daily_quota_weekend_minutes": 60,
            "bed_time_start": "21:30",
            "bed_time_end": "06:00",
            "study_mode": False,
            "safesearch_enabled": True,
            "blocklist": [],
            "whitelist": [],
            "blocked_apps": [],
            "schedule_matrix": [],
        }
        # Reverse insertion order
        policy2 = {k: policy1[k] for k in reversed(list(policy1.keys()))}

        hmac1 = calculate_policy_hmac(policy1)
        hmac2 = calculate_policy_hmac(policy2)
        assert hmac1 == hmac2
        assert verify_policy_hmac(policy2, hmac1) is True


# ==============================================================================
# 2. Monotonic Versioning Adversarial Tests
# ==============================================================================

class TestMonotonicVersioningAdversarial:
    """Tests anti-rollback and monotonic version progression."""

    def test_client_cannot_freeze_or_rollback_version_via_put(self):
        """Client attempting to set version=1 or downgrade version must be ignored; server strictly increments."""
        ctx = create_parent_and_child("mono1")
        child_id = ctx["child_id"]
        token = ctx["token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Initial get -> version 1
        p_init = client.get(f"/api/v1/children/{child_id}/policy", headers=headers).json()
        assert p_init["version"] == 1

        # Attempt to pass version: 1 in update
        res1 = client.put(
            f"/api/v1/children/{child_id}/policy",
            json={"daily_quota_minutes": 90, "version": 1},
            headers=headers,
        ).json()
        assert res1["version"] == 2  # Incremented to 2 despite client passing version: 1

        # Attempt to pass version: 0 (downgrade)
        res2 = client.put(
            f"/api/v1/children/{child_id}/policy",
            json={"daily_quota_minutes": 80, "version": 0},
            headers=headers,
        ).json()
        assert res2["version"] == 3  # Incremented to 3

        # Attempt to pass huge version: 9999
        res3 = client.put(
            f"/api/v1/children/{child_id}/policy",
            json={"daily_quota_minutes": 70, "version": 9999},
            headers=headers,
        ).json()
        assert res3["version"] == 4  # Strictly increments to 4

    def test_rapid_sequential_updates_strictly_advance_version(self):
        """10 rapid sequential updates must produce strictly increasing versions with valid HMACs."""
        ctx = create_parent_and_child("mono_rapid")
        child_id = ctx["child_id"]
        token = ctx["token"]
        headers = {"Authorization": f"Bearer {token}"}

        previous_version = client.get(f"/api/v1/children/{child_id}/policy", headers=headers).json()["version"]

        for i in range(1, 11):
            quota = 60 + i * 5
            res = client.put(
                f"/api/v1/children/{child_id}/policy",
                json={"daily_quota_minutes": quota},
                headers=headers,
            )
            assert res.status_code == 200
            data = res.json()
            current_version = data["version"]

            assert current_version == previous_version + 1, (
                f"Version did not strictly increment by 1: previous={previous_version}, current={current_version}"
            )
            assert verify_policy_hmac(data, data["hmac_signature"]) is True
            previous_version = current_version

    def test_agent_monotonic_version_guard_oracle(self):
        """
        Emulates Agent policy sync verification oracle:
        - Replay attack (incoming_version <= current_version) -> REJECT
        - Fresh version with valid HMAC -> ACCEPT
        - Fresh version with invalid HMAC -> REJECT
        """
        agent_current_version = 5

        # Oracle function implemented by Agent
        def evaluate_incoming_policy(incoming_policy: Dict[str, Any], agent_version: int) -> str:
            inc_version = incoming_policy.get("version", 0)
            sig = incoming_policy.get("hmac_signature") or incoming_policy.get("signature", "")
            if inc_version <= agent_version:
                return "REJECT_STALE_OR_REPLAY"
            if not verify_policy_hmac(incoming_policy, sig):
                return "REJECT_INVALID_HMAC"
            return "ACCEPT_AND_APPLY"

        policy_template = {
            "child_id": "c_agent",
            "version": 4,
            "daily_quota_minutes": 120,
            "daily_quota_weekend_minutes": 120,
            "bed_time_start": "21:30",
            "bed_time_end": "06:00",
            "study_mode": False,
            "safesearch_enabled": True,
            "blocklist": [],
            "whitelist": [],
            "blocked_apps": [],
            "schedule_matrix": [],
        }

        # 1. Replay of version 4 when agent is at 5
        policy_v4 = dict(policy_template, version=4)
        policy_v4["hmac_signature"] = calculate_policy_hmac(policy_v4)
        assert evaluate_incoming_policy(policy_v4, agent_current_version) == "REJECT_STALE_OR_REPLAY"

        # 2. Duplicate version 5
        policy_v5 = dict(policy_template, version=5)
        policy_v5["hmac_signature"] = calculate_policy_hmac(policy_v5)
        assert evaluate_incoming_policy(policy_v5, agent_current_version) == "REJECT_STALE_OR_REPLAY"

        # 3. Valid version 6 with valid HMAC
        policy_v6 = dict(policy_template, version=6)
        policy_v6["hmac_signature"] = calculate_policy_hmac(policy_v6)
        assert evaluate_incoming_policy(policy_v6, agent_current_version) == "ACCEPT_AND_APPLY"

        # 4. Version 7 with tampered HMAC
        policy_v7 = dict(policy_template, version=7)
        policy_v7["hmac_signature"] = "deadbeef" * 8
        assert evaluate_incoming_policy(policy_v7, agent_current_version) == "REJECT_INVALID_HMAC"


# ==============================================================================
# 3. Bedtime Curfew Crossing Midnight (21:30 - 06:00) Boundary Adversarial Tests
# ==============================================================================

class TestBedtimeCurfewCrossingMidnightAdversarial:
    """Verifies boundary calculations and state machine behavior for midnight-crossing curfews."""

    @staticmethod
    def is_curfew_active(check_time: dtime, curfew_start: dtime, curfew_end: dtime) -> bool:
        """
        Standard mathematical time-interval evaluation for bedtime curfews.
        If start > end (crosses midnight, e.g. 21:30 - 06:00):
            active if time >= start OR time < end
        """
        if curfew_start > curfew_end:
            return check_time >= curfew_start or check_time < curfew_end
        else:
            return curfew_start <= check_time < curfew_end

    def test_midnight_crossing_boundary_mathematics(self):
        """Validates all critical boundary instants for 21:30 - 06:00."""
        start = dtime(21, 30)
        end = dtime(6, 0)

        # 21:29:59 -> Outside curfew (Active allowed)
        assert self.is_curfew_active(dtime(21, 29, 59), start, end) is False

        # 21:30:00 -> Curfew begins (Locked)
        assert self.is_curfew_active(dtime(21, 30, 0), start, end) is True

        # 22:00:00 -> In curfew (Locked)
        assert self.is_curfew_active(dtime(22, 0, 0), start, end) is True

        # 23:59:59 -> Last instant before midnight (Locked)
        assert self.is_curfew_active(dtime(23, 59, 59), start, end) is True

        # 00:00:00 -> Midnight transition (Locked)
        assert self.is_curfew_active(dtime(0, 0, 0), start, end) is True

        # 03:30:00 -> Deep night (Locked)
        assert self.is_curfew_active(dtime(3, 30, 0), start, end) is True

        # 05:59:59 -> Last second of curfew (Locked)
        assert self.is_curfew_active(dtime(5, 59, 59), start, end) is True

        # 06:00:00 -> Curfew ends (Allowed)
        assert self.is_curfew_active(dtime(6, 0, 0), start, end) is False

        # 06:00:01 -> Morning allowed
        assert self.is_curfew_active(dtime(6, 0, 1), start, end) is False

        # 12:00:00 -> Noon allowed
        assert self.is_curfew_active(dtime(12, 0, 0), start, end) is False

    def test_7x48_schedule_matrix_curfew_slot_mapping(self):
        """
        In 7x48 schedule matrix (30m per slot):
        Slot index = (hour * 60 + minute) // 30
        - 21:29 -> Slot 42 (Allowed: True)
        - 21:30 -> Slot 43 (Curfew: False)
        - 23:59 -> Slot 47 (Curfew: False)
        - 00:00 -> Slot 0  (Curfew: False)
        - 05:59 -> Slot 11 (Curfew: False)
        - 06:00 -> Slot 12 (Allowed: True)
        """
        # Construct matrix with 21:30 - 06:00 blocked on every day
        matrix = [[True] * 48 for _ in range(7)]
        for d in range(7):
            for s in range(43, 48):  # 21:30 to 24:00
                matrix[d][s] = False
            for s in range(0, 12):   # 00:00 to 06:00
                matrix[d][s] = False

        def is_slot_allowed(dt: datetime) -> bool:
            day_idx = dt.weekday()
            slot_idx = (dt.hour * 60 + dt.minute) // 30
            return matrix[day_idx][slot_idx]

        # Monday 21:29 -> Allowed
        assert is_slot_allowed(datetime(2026, 11, 2, 21, 29, 0)) is True

        # Monday 21:30 -> Blocked
        assert is_slot_allowed(datetime(2026, 11, 2, 21, 30, 0)) is False

        # Monday 23:59 -> Blocked
        assert is_slot_allowed(datetime(2026, 11, 2, 23, 59, 0)) is False

        # Tuesday 00:00 -> Blocked across midnight
        assert is_slot_allowed(datetime(2026, 11, 3, 0, 0, 0)) is False

        # Tuesday 05:59 -> Blocked
        assert is_slot_allowed(datetime(2026, 11, 3, 5, 59, 0)) is False

        # Tuesday 06:00 -> Allowed (Curfew ends)
        assert is_slot_allowed(datetime(2026, 11, 3, 6, 0, 0)) is True

    def test_screen_time_tracker_state_transitions_across_midnight(self):
        """
        Tests live ScreenTimeTracker transitions across the 21:30 -> 06:00 boundary.
        Verifies:
        1. 21:29: ACTIVE_COUNTING
        2. 21:30: LOCKED_SCHEDULE
        3. 00:01 (Midnight rollover): remains LOCKED_SCHEDULE
        4. 05:59: remains LOCKED_SCHEDULE
        5. 06:00: automatically unlocks to ACTIVE_COUNTING
        """
        matrix = [[True] * 48 for _ in range(7)]
        for d in range(7):
            for s in range(43, 48):  # 21:30 - 24:00
                matrix[d][s] = False
            for s in range(0, 12):   # 00:00 - 06:00
                matrix[d][s] = False

        # Start on Monday 2026-11-02 at 21:20:00
        start_dt = datetime(2026, 11, 2, 21, 20, 0)
        curr_wall = start_dt.timestamp()
        curr_mono = 1000.0

        def get_wall():
            return curr_wall

        def get_mono():
            return curr_mono

        def get_idle():
            return 0.0

        tracker = ScreenTimeTracker(
            daily_quota_seconds=7200,
            schedule_matrix=matrix,
            idle_provider=get_idle,
            wall_time_provider=get_wall,
            monotonic_time_provider=get_mono,
        )

        # 1. 21:20: ACTIVE_COUNTING
        assert tracker.state == ScreenTimeState.ACTIVE_COUNTING
        assert not tracker.is_locked()

        # 2. Advance 9 minutes to 21:29:00 -> Still allowed
        curr_wall += 9 * 60.0
        curr_mono += 9 * 60.0
        state = tracker.tick()
        assert state == ScreenTimeState.ACTIVE_COUNTING
        assert not tracker.is_locked()

        # 3. Advance 2 minutes to 21:31:00 -> Crosses curfew start (21:30) -> LOCKED_SCHEDULE
        curr_wall += 2 * 60.0
        curr_mono += 2 * 60.0
        state = tracker.tick()
        assert state == ScreenTimeState.LOCKED_SCHEDULE
        assert tracker.is_locked() is True

        # 4. Advance into midnight (Tuesday 00:05:00) -> Must remain LOCKED_SCHEDULE
        curr_wall = datetime(2026, 11, 3, 0, 5, 0).timestamp()
        curr_mono += 164 * 60.0  # elapsed monotonic
        state = tracker.tick()
        assert state == ScreenTimeState.LOCKED_SCHEDULE
        assert tracker.is_locked() is True

        # 5. Advance to 05:58:00 -> Must remain LOCKED_SCHEDULE
        curr_wall = datetime(2026, 11, 3, 5, 58, 0).timestamp()
        curr_mono += 353 * 60.0
        state = tracker.tick()
        assert state == ScreenTimeState.LOCKED_SCHEDULE
        assert tracker.is_locked() is True

        # 6. Advance to 06:01:00 -> Curfew ends -> ACTIVE_COUNTING (Unlocks)
        curr_wall = datetime(2026, 11, 3, 6, 1, 0).timestamp()
        curr_mono += 3 * 60.0
        state = tracker.tick()
        assert state == ScreenTimeState.ACTIVE_COUNTING
        assert tracker.is_locked() is False


# ==============================================================================
# 4. Input Validation Adversarial Tests
# ==============================================================================

class TestInputValidationAdversarial:
    """Tests boundary values, format restrictions, and corrupted payload handling."""

    def test_daily_quota_boundary_values(self):
        """Enforces 15 <= daily_quota_minutes <= 1440."""
        ctx = create_parent_and_child("val_quota")
        child_id = ctx["child_id"]
        headers = {"Authorization": f"Bearer {ctx['token']}"}

        # Value < 15 -> 422
        res = client.put(f"/api/v1/children/{child_id}/policy", json={"daily_quota_minutes": 14}, headers=headers)
        assert res.status_code == 422

        # Value = 15 -> 200 OK
        res = client.put(f"/api/v1/children/{child_id}/policy", json={"daily_quota_minutes": 15}, headers=headers)
        assert res.status_code == 200

        # Value = 1440 (24h) -> 200 OK
        res = client.put(f"/api/v1/children/{child_id}/policy", json={"daily_quota_minutes": 1440}, headers=headers)
        assert res.status_code == 200

        # Value > 1440 -> 422
        res = client.put(f"/api/v1/children/{child_id}/policy", json={"daily_quota_minutes": 1441}, headers=headers)
        assert res.status_code == 422

        # Negative value -> 422
        res = client.put(f"/api/v1/children/{child_id}/policy", json={"daily_quota_minutes": -30}, headers=headers)
        assert res.status_code == 422

    def test_app_hash_sha256_format_enforcement(self):
        """Verifies strict 64-char hexadecimal regex validation for app hashes."""
        ctx = create_parent_and_child("val_hash")
        child_id = ctx["child_id"]
        headers = {"Authorization": f"Bearer {ctx['token']}"}

        # 63 hex chars (too short) -> 400
        res = client.post(
            f"/api/v1/children/{child_id}/policy/apps",
            json={"name": "app.exe", "sha256": "a" * 63},
            headers=headers,
        )
        assert res.status_code == 400

        # 65 hex chars (too long) -> 400
        res = client.post(
            f"/api/v1/children/{child_id}/policy/apps",
            json={"name": "app.exe", "sha256": "a" * 65},
            headers=headers,
        )
        assert res.status_code == 400

        # 64 chars containing non-hex characters 'g', 'z' -> 400
        bad_hex = "a" * 60 + "gggg"
        res = client.post(
            f"/api/v1/children/{child_id}/policy/apps",
            json={"name": "app.exe", "sha256": bad_hex},
            headers=headers,
        )
        assert res.status_code == 400

        # Special chars and spaces -> 400
        res = client.post(
            f"/api/v1/children/{child_id}/policy/apps",
            json={"name": "app.exe", "sha256": " " * 64},
            headers=headers,
        )
        assert res.status_code == 400

        # Empty string -> 400
        res = client.post(
            f"/api/v1/children/{child_id}/policy/apps",
            json={"name": "app.exe", "sha256": ""},
            headers=headers,
        )
        assert res.status_code == 400

        # Valid 64-char lowercase hex -> 200
        valid_hex = "0123456789abcdef" * 4
        res = client.post(
            f"/api/v1/children/{child_id}/policy/apps",
            json={"name": "valid.exe", "sha256": valid_hex},
            headers=headers,
        )
        assert res.status_code == 200

        # Valid 64-char uppercase hex -> 200 (normalized to lowercase)
        valid_upper = ("0123456789ABCDEF" * 4)
        res = client.post(
            f"/api/v1/children/{child_id}/policy/apps",
            json={"name": "valid2.exe", "sha256": valid_upper},
            headers=headers,
        )
        assert res.status_code == 200

    def test_domain_rule_input_validation(self):
        """Verifies domain rules require non-empty domain string."""
        ctx = create_parent_and_child("val_domain")
        child_id = ctx["child_id"]
        headers = {"Authorization": f"Bearer {ctx['token']}"}

        # Empty domain -> 400
        res = client.post(
            f"/api/v1/children/{child_id}/policy/domains",
            json={"domain": "", "list_type": "blacklist"},
            headers=headers,
        )
        assert res.status_code == 400

        # Whitespace domain -> 400
        res = client.post(
            f"/api/v1/children/{child_id}/policy/domains",
            json={"domain": "   ", "list_type": "blacklist"},
            headers=headers,
        )
        assert res.status_code == 400

        # Valid domain -> 200
        res = client.post(
            f"/api/v1/children/{child_id}/policy/domains",
            json={"domain": "evil-casino.com", "list_type": "blacklist"},
            headers=headers,
        )
        assert res.status_code == 200

    def test_corrupted_json_payload_types(self):
        """Sending incompatible types (e.g. string for matrix, number for blocklist) triggers 422."""
        ctx = create_parent_and_child("val_types")
        child_id = ctx["child_id"]
        headers = {"Authorization": f"Bearer {ctx['token']}"}

        # schedule_matrix as string
        res = client.put(
            f"/api/v1/children/{child_id}/policy",
            json={"schedule_matrix": "not_a_matrix"},
            headers=headers,
        )
        assert res.status_code == 422

        # blocklist as number
        res = client.put(
            f"/api/v1/children/{child_id}/policy",
            json={"blocklist": 12345},
            headers=headers,
        )
        assert res.status_code == 422

        # bedtime format not HH:MM
        res = client.put(
            f"/api/v1/children/{child_id}/policy",
            json={"bed_time_start": "twenty_one_thirty"},
            headers=headers,
        )
        assert res.status_code == 422


# ==============================================================================
# 5. Multi-Child Isolation (IDOR) Adversarial Tests
# ==============================================================================

class TestMultiChildIsolationIdorAdversarial:
    """Verifies that Parent B cannot read, mutate, or purge Child A's resources."""

    @pytest.fixture(autouse=True)
    def setup_two_families(self):
        self.family_a = create_parent_and_child("fam_a")
        self.family_b = create_parent_and_child("fam_b")
        self.token_a = self.family_a["token"]
        self.child_a_id = self.family_a["child_id"]
        self.token_b = self.family_b["token"]
        self.child_b_id = self.family_b["child_id"]

    def test_idor_get_child_policy(self):
        """Parent B cannot view Child A's policy."""
        res = client.get(
            f"/api/v1/children/{self.child_a_id}/policy",
            headers={"Authorization": f"Bearer {self.token_b}"},
        )
        assert res.status_code == 404

    def test_idor_put_child_policy(self):
        """Parent B cannot modify Child A's policy."""
        res = client.put(
            f"/api/v1/children/{self.child_a_id}/policy",
            json={"daily_quota_minutes": 15},
            headers={"Authorization": f"Bearer {self.token_b}"},
        )
        assert res.status_code == 404

    def test_idor_add_and_delete_domain(self):
        """Parent B cannot add or remove domains from Child A's policy."""
        # Add domain attack
        res_add = client.post(
            f"/api/v1/children/{self.child_a_id}/policy/domains",
            json={"domain": "unauthorized-domain.com", "list_type": "blacklist"},
            headers={"Authorization": f"Bearer {self.token_b}"},
        )
        assert res_add.status_code == 404

        # Delete domain attack
        res_del = client.delete(
            f"/api/v1/children/{self.child_a_id}/policy/domains/unauthorized-domain.com",
            headers={"Authorization": f"Bearer {self.token_b}"},
        )
        assert res_del.status_code == 404

    def test_idor_add_and_delete_app_hash(self):
        """Parent B cannot add or remove blocked app hashes from Child A."""
        test_hash = "f" * 64
        # Add hash attack
        res_add = client.post(
            f"/api/v1/children/{self.child_a_id}/policy/apps",
            json={"name": "trojan.exe", "sha256": test_hash},
            headers={"Authorization": f"Bearer {self.token_b}"},
        )
        assert res_add.status_code == 404

        # Delete hash attack
        res_del = client.delete(
            f"/api/v1/children/{self.child_a_id}/policy/apps/{test_hash}",
            headers={"Authorization": f"Bearer {self.token_b}"},
        )
        assert res_del.status_code == 404

    def test_idor_audit_logs_isolation(self):
        """Parent B cannot access Child A's audit logs."""
        res = client.get(
            f"/api/v1/children/{self.child_a_id}/audit-logs",
            headers={"Authorization": f"Bearer {self.token_b}"},
        )
        assert res.status_code == 404

    def test_idor_purge_data_isolation(self):
        """Parent B cannot purge Child A's data (Atomic Dual Deletion IDOR)."""
        res = client.delete(
            f"/api/v1/children/{self.child_a_id}/purge-data",
            headers={"Authorization": f"Bearer {self.token_b}"},
        )
        assert res.status_code == 404

    def test_idor_pairing_code_isolation(self):
        """Parent B cannot generate a pairing code for Child A."""
        res = client.post(
            f"/api/v1/children/{self.child_a_id}/pairing-code",
            headers={"Authorization": f"Bearer {self.token_b}"},
        )
        assert res.status_code == 404

    def test_child_a_policy_integrity_preserved_after_idor_assault(self):
        """Verify that Child A's policy state is completely pristine after Parent B's failed attacks."""
        res_a = client.get(
            f"/api/v1/children/{self.child_a_id}/policy",
            headers={"Authorization": f"Bearer {self.token_a}"},
        )
        assert res_a.status_code == 200
        data_a = res_a.json()
        assert data_a["version"] == 1
        assert "unauthorized-domain.com" not in data_a["blocklist"]
        assert len(data_a["blocked_apps"]) == 0
        assert verify_policy_hmac(data_a, data_a["hmac_signature"]) is True
