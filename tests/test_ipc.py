"""
Unit Tests for Service-to-Tray IPC Engine (Session 0 to Session 1 communication)
"""

import os
import time
import pytest
import httpx

from src.agent.ipc import IPCManager, IPCClient


@pytest.fixture
def ipc_setup(tmp_path):
    """Start IPCManager on dynamic ephemeral port and return (manager, client, port, token)."""
    token_dir = str(tmp_path)

    def mock_status():
        return {
            "status": "ACTIVE",
            "remaining_seconds": 1800,
            "policy_version": 3,
        }

    received_requests = []

    def mock_request(payload):
        received_requests.append(payload)
        return {"status": "ACCEPTED", "request_id": "req-123"}

    # Use port 0 to let OS assign an available port
    manager = IPCManager(
        host="127.0.0.1",
        port=0,
        token_dir=token_dir,
        status_callback=mock_status,
        request_callback=mock_request,
    )
    manager.start()
    time.sleep(0.1)

    actual_port = manager.port
    client = IPCClient(host="127.0.0.1", port=actual_port, token=manager.secret_token)
    yield manager, client, actual_port, manager.secret_token, received_requests

    manager.stop()


def test_ipc_status_with_valid_token(ipc_setup):
    """Valid token should return status JSON from the service."""
    _, client, _, _, _ = ipc_setup
    status = client.get_status()

    assert status["status"] == "ACTIVE"
    assert status["remaining_seconds"] == 1800
    assert status["policy_version"] == 3


def test_ipc_forbidden_with_invalid_token(ipc_setup):
    """Missing or invalid token must return 403 Forbidden."""
    _, _, port, _, _ = ipc_setup

    with httpx.Client() as http_client:
        # Request with NO token
        res_no_token = http_client.get(f"http://127.0.0.1:{port}/status")
        assert res_no_token.status_code == 403

        # Request with WRONG token
        res_wrong_token = http_client.get(
            f"http://127.0.0.1:{port}/status",
            headers={"X-OGK-Token": "bad-token-123456"},
        )
        assert res_wrong_token.status_code == 403


def test_ipc_heartbeat_and_child_request(ipc_setup):
    """Tray heartbeat and child requests must be processed and recorded."""
    _, client, _, _, received_requests = ipc_setup

    # 1. Send heartbeat
    hb_ok = client.send_heartbeat(timestamp=time.time())
    assert hb_ok is True

    # 2. Send Child agency request (Request 15 extra minutes)
    req_resp = client.send_request(req_type="add_time", minutes=15, subject="Study Math")
    assert req_resp["status"] == "ACCEPTED"
    assert req_resp["request_id"] == "req-123"

    assert len(received_requests) == 1
    assert received_requests[0]["type"] == "add_time"
    assert received_requests[0]["minutes"] == 15
