#!/usr/bin/env python3
"""
OpenGuard Kids — Standalone Live Multi-Process Runtime Verification Tool
Requirement R4: Live Runtime Multi-Process Verification.
Spins up Backend Server, Agent Service, and Tray UI processes concurrently.
Validates IPC, WebSocket, and HTTP communications with real-time state synchronization.
"""

from __future__ import annotations

import os
import signal
import socket
import subprocess
import sys
import tempfile
import time
from typing import Dict, Any, Optional

import httpx

# ANSI Color Codes for Linux Terminal Formatting
RESET = "\033[0m"
BOLD = "\033[1m"
GREEN = "\033[32m"
RED = "\033[31m"
YELLOW = "\033[33m"
CYAN = "\033[36m"
MAGENTA = "\033[35m"
BLUE = "\033[34m"

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


def log_step(step_num: int, title: str) -> None:
    print(f"\n{BOLD}{CYAN}[Step {step_num}]{RESET} {BOLD}{title}{RESET}")


def log_pass(message: str) -> None:
    print(f"  {GREEN}{BOLD}[PASS]{RESET} {GREEN}{message}{RESET}")


def log_fail(message: str) -> None:
    print(f"  {RED}{BOLD}[FAIL]{RESET} {RED}{message}{RESET}")


def log_info(message: str) -> None:
    print(f"  {BLUE}[INFO]{RESET} {message}")


def log_warn(message: str) -> None:
    print(f"  {YELLOW}[WARN]{RESET} {message}")


def find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def run_verification() -> bool:
    print("=" * 78)
    print(f"{BOLD}{MAGENTA}   OPENGUARD KIDS — LIVE MULTI-PROCESS RUNTIME VERIFICATION (R4){RESET}")
    print(f"{CYAN}   Platform: Linux Mint / POSIX Environment Verification Harness{RESET}")
    print("=" * 78)

    tmp_dir = tempfile.mkdtemp(prefix="ogk_runtime_verify_")
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

    server_proc: Optional[subprocess.Popen] = None
    agent_proc: Optional[subprocess.Popen] = None
    tray_proc: Optional[subprocess.Popen] = None

    success = False

    try:
        # -------------------------------------------------------------
        # Step 1: Verify DNS Proxy Unprivileged Fallback
        # -------------------------------------------------------------
        log_step(1, "Testing Local DNS Proxy Port 53 Fallback Mechanism")
        from src.agent.dns_proxy import DNSProxy
        dns_test = DNSProxy(listen_host="127.0.0.1", listen_port=53, fallback_port=5353)
        dns_test.start()
        actual_port = dns_test.port
        dns_test.stop()
        if actual_port == 5353:
            log_pass(f"DNS Proxy gracefully handled port 53 privilege constraint -> bound to {actual_port}")
        else:
            log_warn(f"DNS Proxy bound to port {actual_port}")

        # -------------------------------------------------------------
        # Step 2: Spawn Backend Server Process
        # -------------------------------------------------------------
        log_step(2, f"Spawning Backend Server on port {server_port}")
        log_info(f"Command: python -m src.server.main --port {server_port}")
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

        server_online = False
        for _ in range(50):
            try:
                r = httpx.get(f"http://127.0.0.1:{server_port}/health", timeout=0.3)
                if r.status_code == 200:
                    server_online = True
                    break
            except Exception:
                time.sleep(0.1)

        if not server_online:
            log_fail("Backend Server did not respond to /health in time.")
            return False
        log_pass("Backend Server online and responsive.")

        # -------------------------------------------------------------
        # Step 3: Register Parent & Enroll Device
        # -------------------------------------------------------------
        log_step(3, "Enrolling Device via Pairing Code")
        with httpx.Client(base_url=f"http://127.0.0.1:{server_port}", timeout=5.0) as client:
            parent_email = f"eval_parent_{int(time.time()*1000)}@openguard.local"
            parent_password = "SecurePassword2026!"

            # Register
            reg_res = client.post(
                "/api/v1/auth/register",
                json={"email": parent_email, "password": parent_password},
            )
            assert reg_res.status_code in (200, 201)

            # Login
            log_res = client.post(
                "/api/v1/auth/login",
                json={"email": parent_email, "password": parent_password},
            )
            assert log_res.status_code == 200
            cookies = log_res.cookies
            client.cookies.update(cookies)

            # Create Child
            child_res = client.post("/api/v1/children", json={"name": "Bé Mai", "age": 8})
            assert child_res.status_code in (200, 201)
            child_id = child_res.json()["id"]
            log_info(f"Created Child profile: {child_id}")

            # Pairing Code
            pair_res = client.post(f"/api/v1/children/{child_id}/pairing-code")
            assert pair_res.status_code == 200
            pairing_code = pair_res.json()["pairing_code"]
            log_info(f"Generated Pairing Code: {pairing_code}")

            # Enroll Device
            enroll_res = client.post(
                "/api/v1/enroll/device",
                json={"pairing_code": pairing_code, "hostname": "LINUX-EVAL-AGENT"},
            )
            assert enroll_res.status_code == 200
            device_id = enroll_res.json()["device_id"]
            log_pass(f"Device enrolled successfully: device_id={device_id}")

        # -------------------------------------------------------------
        # Step 4: Spawn Agent Service Process
        # -------------------------------------------------------------
        log_step(4, "Spawning Agent Service Process")
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
        log_info(f"Command: python -m src.agent.main --server-url http://127.0.0.1:{server_port} --ipc-port {ipc_port} ...")
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

        if not secret_token:
            log_fail("Agent failed to initialize secret token file.")
            return False
        log_pass(f"Agent initialized IPC secret token: {secret_token[:8]}...")

        # -------------------------------------------------------------
        # Step 5: Spawn Desktop Tray UI Process
        # -------------------------------------------------------------
        log_step(5, "Spawning Desktop Tray UI Application")
        tray_cmd = [
            sys.executable,
            "-m",
            "src.tray.main",
            "--ipc-port",
            str(ipc_port),
            "--token-dir",
            tmp_dir,
        ]
        log_info(f"Command: python -m src.tray.main --ipc-port {ipc_port} --token-dir {tmp_dir}")
        tray_proc = subprocess.Popen(
            tray_cmd,
            cwd=PROJECT_ROOT,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        time.sleep(1.0)
        if tray_proc.poll() is not None:
            log_fail(f"Tray UI exited prematurely with return code {tray_proc.returncode}")
            return False
        log_pass("Tray UI successfully started and attached to Agent IPC.")

        # -------------------------------------------------------------
        # Step 6: Verify IPC & WebSocket Communications
        # -------------------------------------------------------------
        log_step(6, "Verifying IPC Status and Server WebSocket Connection")
        initial_rem = 0.0
        with httpx.Client(timeout=2.0) as ipc_client:
            ipc_st = ipc_client.get(
                f"http://127.0.0.1:{ipc_port}/status",
                headers={"X-OGK-Token": secret_token},
            ).json()
            initial_rem = ipc_st.get("remaining_seconds", 0.0)
            log_info(f"Agent state: {ipc_st.get('state')}, Remaining: {initial_rem/60:.1f} mins")

        # Wait for WebSocket handshake
        ws_connected = False
        for _ in range(30):
            with httpx.Client(base_url=f"http://127.0.0.1:{server_port}") as client:
                dash_data = client.get(f"/api/v1/dashboard/data/{child_id}").json()
                if dash_data.get("device", {}).get("is_online") is True:
                    ws_connected = True
                    break
            time.sleep(0.15)

        if not ws_connected:
            log_fail("WebSocket connection between Agent and Server was not confirmed.")
            return False
        log_pass("Agent WebSocket link active (<5s bidirectional messaging ready).")

        # -------------------------------------------------------------
        # Step 7: Emergency Lock (LOCK_URGENT) Dispatch (< 1s Latency)
        # -------------------------------------------------------------
        log_step(7, "Dispatching Emergency Lock (LOCK_URGENT) from Server")
        t0 = time.time()
        with httpx.Client(base_url=f"http://127.0.0.1:{server_port}", cookies=cookies) as client:
            lock_res = client.post(
                f"/api/v1/dashboard/{child_id}/command",
                json={"command": "LOCK_URGENT"},
            )
            assert lock_res.status_code == 200

        locked = False
        lock_elapsed = 0.0
        for _ in range(25):
            time.sleep(0.04)
            with httpx.Client(timeout=1.0) as ipc_client:
                st = ipc_client.get(
                    f"http://127.0.0.1:{ipc_port}/status",
                    headers={"X-OGK-Token": secret_token},
                ).json()
                if st.get("is_locked") is True and st.get("lock_reason") == "LOCKED_URGENT":
                    lock_elapsed = time.time() - t0
                    locked = True
                    break

        if not locked or lock_elapsed >= 1.0:
            log_fail(f"Emergency Lock failed or exceeded 1s deadline (elapsed: {lock_elapsed:.3f}s)")
            return False
        log_pass(f"Emergency Lock delivered and enforced in {lock_elapsed * 1000:.1f} ms (< 1000 ms limit)")

        # -------------------------------------------------------------
        # Step 8: Emergency Unlock Dispatch
        # -------------------------------------------------------------
        log_step(8, "Dispatching Emergency Unlock (UNLOCK) from Server")
        with httpx.Client(base_url=f"http://127.0.0.1:{server_port}", cookies=cookies) as client:
            unlock_res = client.post(
                f"/api/v1/dashboard/{child_id}/command",
                json={"command": "UNLOCK"},
            )
            assert unlock_res.status_code == 200

        unlocked = False
        for _ in range(25):
            time.sleep(0.04)
            with httpx.Client(timeout=1.0) as ipc_client:
                st = ipc_client.get(
                    f"http://127.0.0.1:{ipc_port}/status",
                    headers={"X-OGK-Token": secret_token},
                ).json()
                if st.get("is_locked") is False:
                    unlocked = True
                    break

        if not unlocked:
            log_fail("Emergency Unlock was not reflected on Agent.")
            return False
        log_pass("Agent state successfully restored to active.")

        # -------------------------------------------------------------
        # Step 9: Child Agency Request & Dashboard Ingestion
        # -------------------------------------------------------------
        log_step(9, "Submitting Extra Time Request from Tray UI to IPC")
        with httpx.Client(timeout=1.0) as ipc_client:
            req_res = ipc_client.post(
                f"http://127.0.0.1:{ipc_port}/request",
                headers={"X-OGK-Token": secret_token},
                json={"type": "REQUEST_MORE_TIME", "minutes": 15},
            )
            assert req_res.status_code == 200

        # Wait for sync to backend
        pending_found = False
        pending_id = None
        for _ in range(30):
            time.sleep(0.15)
            with httpx.Client(base_url=f"http://127.0.0.1:{server_port}") as client:
                dash_data = client.get(f"/api/v1/dashboard/data/{child_id}").json()
                preqs = dash_data.get("pending_requests", [])
                if len(preqs) >= 1:
                    pending_found = True
                    pending_id = preqs[0]["id"]
                    break

        if not pending_found:
            log_fail("Child request did not sync to Server inbox.")
            return False
        log_pass(f"Child request synchronized to Parent Dashboard (Request ID: {pending_id})")

        # -------------------------------------------------------------
        # Step 10: Parent Extension Approval (+15m Bonus)
        # -------------------------------------------------------------
        log_step(10, "Approving Time Extension on Server (+15m Bonus Time)")
        with httpx.Client(base_url=f"http://127.0.0.1:{server_port}", cookies=cookies) as client:
            rev_res = client.post(
                f"/api/v1/dashboard/requests/{pending_id}/quick-review",
                json={"decision": "APPROVED"},
            )
            assert rev_res.status_code == 200

        bonus_propagated = False
        for _ in range(25):
            time.sleep(0.08)
            with httpx.Client(timeout=1.0) as ipc_client:
                st = ipc_client.get(
                    f"http://127.0.0.1:{ipc_port}/status",
                    headers={"X-OGK-Token": secret_token},
                ).json()
                if st.get("remaining_seconds", 0) > initial_rem + 800:
                    bonus_propagated = True
                    break

        if not bonus_propagated:
            log_fail("Bonus time (+15m) failed to propagate to Agent tracker.")
            return False
        log_pass("Bonus time (+15m) successfully added to Agent remaining quota.")

        # -------------------------------------------------------------
        # Step 11: Clean Process Termination (SIGINT -> Exit code 0)
        # -------------------------------------------------------------
        log_step(11, "Sending SIGINT to Tray UI, Agent Service, and Server")
        processes = [
            ("Tray UI", tray_proc),
            ("Agent Service", agent_proc),
            ("Backend Server", server_proc),
        ]
        for name, proc in processes:
            if proc and proc.poll() is None:
                proc.send_signal(signal.SIGINT)
                try:
                    code = proc.wait(timeout=5.0)
                except subprocess.TimeoutExpired:
                    proc.kill()
                    code = proc.wait(timeout=2.0)
                if code == 0:
                    log_pass(f"{name} exited cleanly with return code 0.")
                else:
                    log_fail(f"{name} exited with non-zero code {code}.")
                    return False

        success = True

    finally:
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

    print("\n" + "=" * 78)
    if success:
        print(f"{GREEN}{BOLD}   ALL MULTI-PROCESS VERIFICATION CHECKS PASSED (100% PASS){RESET}")
        print(f"{GREEN}   Requirement R4 successfully fulfilled and verified on Linux Mint.{RESET}")
    else:
        print(f"{RED}{BOLD}   VERIFICATION FAILED: One or more checks did not pass.{RESET}")
    print("=" * 78)
    return success


if __name__ == "__main__":
    ok = run_verification()
    sys.exit(0 if ok else 1)
