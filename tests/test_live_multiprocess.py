"""
OpenGuard Kids — Milestone 4: Live Multi-Process Runtime Verification & Unprivileged DNS Fallback
Tests end-to-end multi-process execution (Server, Agent, Tray UI) across IPC, HTTP, and WebSocket channels.
Requirements: R1, R2, R3, R4.
"""

from __future__ import annotations

import logging
import os
import signal
import socket
import subprocess
import sys
import tempfile
import time
from typing import Generator, Tuple

import httpx
import pytest

from src.agent.dns_proxy import DNSProxy

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def find_free_port() -> int:
    """Find an available TCP/UDP port on localhost."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def test_dns_unprivileged_fallback(caplog):
    """
    Requirement 1: Unprivileged DNS Port Fallback.
    When binding to privileged port 53 raises PermissionError/EACCES,
    DNSProxy must fall back to unprivileged port 5353 (or configured fallback),
    log the exact warning, and update self.port to the actual bound port.
    """
    with caplog.at_level(logging.WARNING, logger="OGK.DNSProxy"):
        proxy = DNSProxy(listen_host="127.0.0.1", listen_port=53, fallback_port=5353)
        proxy.start()
        try:
            assert proxy.port == 5353
            assert proxy.listen_port == 5353
            assert any(
                "Permission denied binding UDP port 53; falling back to unprivileged port 5353 for local testing"
                in record.message
                for record in caplog.records
            )
        finally:
            proxy.stop()


def test_live_multiprocess_e2e():
    """
    Requirement 2 & R4: Automated Live Multi-Process Test Suite.
    Launches Server, Agent, and Tray UI processes concurrently via subprocess.Popen.
    Verifies:
      1. Device enrollment via pairing code
      2. Tray UI connection to Agent IPC (/status)
      3. Agent connection to Server WebSocket (/ws/v1/agent/{device_id})
      4. Emergency lock (LOCK_URGENT) propagates in <1 second
      5. Emergency unlock (UNLOCK) restores active state
      6. Extra time request from Tray UI (POST /request) reflects in Server pending_requests >= 1
      7. Server approving time extension propagates bonus time to Agent
      8. Clean SIGINT termination of all 3 processes with return code 0.
    """
    tmp_dir = tempfile.mkdtemp(prefix="ogk_live_mp_")
    db_path = os.path.join(tmp_dir, "server.db")

    env = os.environ.copy()
    env["PYTHONPATH"] = PROJECT_ROOT
    env["OGK_HEADLESS"] = "1"
    env["OGK_DATABASE_URL"] = f"sqlite:///{db_path}"
    env["PYTHONUNBUFFERED"] = "1"

    server_port = find_free_port()
    ipc_port = find_free_port()
    blockpage_port = find_free_port()
    dns_port = 5353

    server_proc = None
    agent_proc = None
    tray_proc = None

    try:
        # -------------------------------------------------------------
        # 1. Start Server Process
        # -------------------------------------------------------------
        server_cmd = [
            sys.executable,
            "-m",
            "src.server.main",
            "--port",
            str(server_port),
        ]
        server_proc = subprocess.Popen(
            server_cmd,
            cwd=PROJECT_ROOT,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        # Wait for server to become responsive
        server_ready = False
        for _ in range(50):
            try:
                r = httpx.get(f"http://127.0.0.1:{server_port}/health", timeout=0.4)
                if r.status_code == 200:
                    server_ready = True
                    break
            except Exception:
                time.sleep(0.1)

        assert server_ready, "Server failed to start and respond on /health"

        # -------------------------------------------------------------
        # 2. Parent Registration, Child Creation, Device Enrollment
        # -------------------------------------------------------------
        with httpx.Client(base_url=f"http://127.0.0.1:{server_port}", timeout=5.0) as client:
            # Register parent
            parent_email = f"parent_{int(time.time()*1000)}@example.com"
            parent_password = "SecurePassword123!"
            reg_res = client.post(
                "/api/v1/auth/register",
                json={
                    "email": parent_email,
                    "password": parent_password,
                },
            )
            assert reg_res.status_code in (200, 201), f"Register failed: {reg_res.text}"

            # Login parent to obtain session cookie
            login_res = client.post(
                "/api/v1/auth/login",
                json={
                    "email": parent_email,
                    "password": parent_password,
                },
            )
            assert login_res.status_code == 200, f"Login failed: {login_res.text}"
            cookies = login_res.cookies
            client.cookies.update(cookies)

            # Create Child Profile
            child_res = client.post(
                "/api/v1/children",
                json={"name": "Bé Lan", "age": 10},
            )
            assert child_res.status_code in (200, 201), f"Create child failed: {child_res.text}"
            child_id = child_res.json()["id"]

            # Generate Pairing Code
            pair_res = client.post(
                f"/api/v1/children/{child_id}/pairing-code",
            )
            assert pair_res.status_code == 200, f"Pairing code failed: {pair_res.text}"
            pairing_code = pair_res.json()["pairing_code"]

            # Enroll Device
            enroll_res = client.post(
                "/api/v1/enroll/device",
                json={
                    "pairing_code": pairing_code,
                    "hostname": "TEST-AGENT-PC",
                },
            )
            assert enroll_res.status_code == 200, f"Enroll failed: {enroll_res.text}"
            device_id = enroll_res.json()["device_id"]

        # -------------------------------------------------------------
        # 3. Start Agent Process
        # -------------------------------------------------------------
        agent_cmd = [
            sys.executable,
            "-m",
            "src.agent.main",
            "--server-url",
            f"http://127.0.0.1:{server_port}",
            "--device-id",
            str(device_id),
            "--child-id",
            str(child_id),
            "--ipc-port",
            str(ipc_port),
            "--dns-port",
            str(dns_port),
            "--blockpage-port",
            str(blockpage_port),
            "--data-dir",
            tmp_dir,
            "--sync-interval",
            "1.0",
        ]
        agent_proc = subprocess.Popen(
            agent_cmd,
            cwd=PROJECT_ROOT,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        token_file = os.path.join(tmp_dir, "ipc_secret.token")
        secret_token = None
        for _ in range(50):
            if os.path.isfile(token_file):
                try:
                    with open(token_file, "r", encoding="utf-8") as f:
                        candidate = f.read().strip()
                    if candidate:
                        secret_token = candidate
                        break
                except Exception:
                    pass
            time.sleep(0.1)

        assert secret_token is not None, "Agent failed to write ipc_secret.token within timeout"

        # Verify Agent IPC status endpoint responds
        agent_ipc_ready = False
        initial_remaining_seconds = 0.0
        for _ in range(30):
            try:
                with httpx.Client(timeout=1.0) as ipc_client:
                    r = ipc_client.get(
                        f"http://127.0.0.1:{ipc_port}/status",
                        headers={"X-OGK-Token": secret_token},
                    )
                    if r.status_code == 200:
                        st = r.json()
                        initial_remaining_seconds = st.get("remaining_seconds", 0.0)
                        agent_ipc_ready = True
                        break
            except Exception:
                time.sleep(0.1)

        assert agent_ipc_ready, "Agent IPC endpoint /status failed to respond"

        # -------------------------------------------------------------
        # 4. Start Tray UI Process
        # -------------------------------------------------------------
        tray_cmd = [
            sys.executable,
            "-m",
            "src.tray.main",
            "--ipc-port",
            str(ipc_port),
            "--token-dir",
            tmp_dir,
        ]
        tray_proc = subprocess.Popen(
            tray_cmd,
            cwd=PROJECT_ROOT,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        time.sleep(1.0)
        assert tray_proc.poll() is None, "Tray UI process exited prematurely"

        # -------------------------------------------------------------
        # 5. Verify WebSocket Connection between Agent and Server
        # -------------------------------------------------------------
        agent_ws_online = False
        for _ in range(40):
            with httpx.Client(base_url=f"http://127.0.0.1:{server_port}") as client:
                dash_res = client.get(f"/api/v1/dashboard/data/{child_id}")
                if dash_res.status_code == 200:
                    dev_data = dash_res.json().get("device") or {}
                    if dev_data.get("is_online") is True:
                        agent_ws_online = True
                        break
            time.sleep(0.15)

        assert agent_ws_online, "Agent did not establish online WebSocket connection to Server"

        # -------------------------------------------------------------
        # 6. Emergency Lock (LOCK_URGENT) Dispatch (< 1s Latency)
        # -------------------------------------------------------------
        t_start_lock = time.time()
        with httpx.Client(base_url=f"http://127.0.0.1:{server_port}", cookies=cookies) as client:
            cmd_res = client.post(
                f"/api/v1/dashboard/{child_id}/command",
                json={"command": "LOCK_URGENT"},
            )
            assert cmd_res.status_code == 200, f"Lock command failed: {cmd_res.text}"

        agent_locked = False
        lock_elapsed = 0.0
        for _ in range(20):
            time.sleep(0.04)
            with httpx.Client(timeout=1.0) as ipc_client:
                st = ipc_client.get(
                    f"http://127.0.0.1:{ipc_port}/status",
                    headers={"X-OGK-Token": secret_token},
                ).json()
                if st.get("is_locked") is True and st.get("lock_reason") == "LOCKED_URGENT":
                    lock_elapsed = time.time() - t_start_lock
                    agent_locked = True
                    break

        assert agent_locked, "Agent did not lock in response to LOCK_URGENT"
        assert lock_elapsed < 1.0, f"LOCK_URGENT took {lock_elapsed:.3f}s (must be <1.0s)"

        # -------------------------------------------------------------
        # 7. Emergency Unlock (UNLOCK) Dispatch
        # -------------------------------------------------------------
        with httpx.Client(base_url=f"http://127.0.0.1:{server_port}", cookies=cookies) as client:
            cmd_res = client.post(
                f"/api/v1/dashboard/{child_id}/command",
                json={"command": "UNLOCK"},
            )
            assert cmd_res.status_code == 200, f"Unlock command failed: {cmd_res.text}"

        agent_unlocked = False
        for _ in range(25):
            time.sleep(0.04)
            with httpx.Client(timeout=1.0) as ipc_client:
                st = ipc_client.get(
                    f"http://127.0.0.1:{ipc_port}/status",
                    headers={"X-OGK-Token": secret_token},
                ).json()
                if st.get("is_locked") is False:
                    agent_unlocked = True
                    break

        assert agent_unlocked, "Agent did not unlock in response to UNLOCK command"

        # -------------------------------------------------------------
        # 8. Extra Time Request from Tray UI (POST /request on IPC)
        # -------------------------------------------------------------
        with httpx.Client(timeout=1.0) as ipc_client:
            req_res = ipc_client.post(
                f"http://127.0.0.1:{ipc_port}/request",
                headers={"X-OGK-Token": secret_token},
                json={"type": "REQUEST_MORE_TIME", "minutes": 15},
            )
            assert req_res.status_code == 200, f"IPC request failed: {req_res.text}"
            assert req_res.json().get("status") == "SUCCESS"

        # Wait for Agent sync worker to flush request to Server
        pending_found = False
        pending_request_id = None
        for _ in range(30):
            time.sleep(0.15)
            with httpx.Client(base_url=f"http://127.0.0.1:{server_port}") as client:
                dash_data = client.get(f"/api/v1/dashboard/data/{child_id}").json()
                pending_reqs = dash_data.get("pending_requests", [])
                if len(pending_reqs) >= 1:
                    pending_found = True
                    pending_request_id = pending_reqs[0]["id"]
                    break

        assert pending_found, "Server dashboard data did not reflect pending_requests >= 1"

        # -------------------------------------------------------------
        # 9. Approve Time Extension on Server (+15m Propagation)
        # -------------------------------------------------------------
        with httpx.Client(base_url=f"http://127.0.0.1:{server_port}", cookies=cookies) as client:
            review_res = client.post(
                f"/api/v1/dashboard/requests/{pending_request_id}/quick-review",
                json={"decision": "APPROVED"},
            )
            assert review_res.status_code == 200, f"Quick review failed: {review_res.text}"

        bonus_propagated = False
        for _ in range(25):
            time.sleep(0.08)
            with httpx.Client(timeout=1.0) as ipc_client:
                st = ipc_client.get(
                    f"http://127.0.0.1:{ipc_port}/status",
                    headers={"X-OGK-Token": secret_token},
                ).json()
                curr_remaining = st.get("remaining_seconds", 0.0)
                # 15 minutes = 900 seconds bonus
                if curr_remaining > initial_remaining_seconds + 800:
                    bonus_propagated = True
                    break

        assert bonus_propagated, "Bonus time (+15m) did not propagate to Agent tracker"

        # -------------------------------------------------------------
        # 10. Clean Process Termination (SIGINT -> Exit code 0)
        # -------------------------------------------------------------
        processes = [
            ("Tray UI", tray_proc),
            ("Agent", agent_proc),
            ("Server", server_proc),
        ]

        for name, proc in processes:
            if proc and proc.poll() is None:
                proc.send_signal(signal.SIGINT)
                try:
                    exit_code = proc.wait(timeout=5.0)
                except subprocess.TimeoutExpired:
                    proc.kill()
                    exit_code = proc.wait(timeout=2.0)
                assert exit_code == 0, f"{name} process exited with code {exit_code}, expected 0"

    finally:
        # Guarantee cleanup even on failure
        for proc in (tray_proc, agent_proc, server_proc):
            if proc and proc.poll() is None:
                try:
                    proc.send_signal(signal.SIGINT)
                    proc.wait(timeout=2.0)
                except Exception:
                    try:
                        proc.kill()
                    except Exception:
                        pass
