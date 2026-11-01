"""
OpenGuard Kids — Agent Service & Orchestration Tests
Verifies that AgentService coordinates all underlying engines:
  - ScreenTimeTracker
  - DNSProxy
  - LocalBlockPageServer
  - ProcessMonitor
  - OfflineEventBuffer
  - IPCServer
  - Background Sync & Server Command Application
"""

import os
import time
import tempfile
import pytest

from src.agent.service import AgentService
from src.agent.ipc import IPCClient
from src.agent.screen_time import ScreenTimeState
from src.common.constants import DEFAULT_TEST_DNS_PORT


@pytest.fixture
def temp_agent_dir():
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


def test_agent_service_lifecycle_and_ipc(temp_agent_dir):
    service = AgentService(
        device_id="DEV-TEST-001",
        child_id="101",
        server_url=None,  # Offline mode for isolated test
        data_dir=temp_agent_dir,
        dns_port=DEFAULT_TEST_DNS_PORT + 10,
        blockpage_port=18081,
        ipc_port=18766,
        daily_limit_minutes=60.0,
        sync_interval_seconds=1.0,
    )

    try:
        service.start()
        assert service.is_running is True

        # Test IPC communication with valid secret token
        client = IPCClient(
            host="127.0.0.1",
            port=18766,
            token=service.ipc_manager.secret_token,
        )

        status = client.get_status()
        assert status is not None
        assert status.get("status") == ScreenTimeState.ACTIVE_COUNTING.value
        assert status.get("is_locked") is False
        assert 3590.0 <= status.get("remaining_seconds") <= 3600.0

        # Send child request via IPC
        req_res = client.send_request("MORE_TIME", minutes=15, subject="Doing homework")
        assert req_res.get("status") == "SUCCESS"

        # Check offline event buffer for enqueued request
        batch = service.buffer.peek_unsynced_batch(limit=10)
        assert len(batch) >= 1
        assert any(row["type"] == "time_extension_request" for row in batch)

        # Trigger screen-time urgent lock
        service.tracker.set_urgent_lock(True)
        status_after_lock = client.get_status()
        assert status_after_lock.get("is_locked") is True
        assert status_after_lock.get("status") == ScreenTimeState.LOCKED_URGENT.value

    finally:
        service.stop()
        assert service.is_running is False


def test_agent_service_command_dispatch(temp_agent_dir):
    service = AgentService(
        device_id="DEV-TEST-002",
        child_id="102",
        server_url=None,
        data_dir=temp_agent_dir,
        dns_port=DEFAULT_TEST_DNS_PORT + 11,
        blockpage_port=18082,
        ipc_port=18767,
        daily_limit_minutes=30.0,
    )

    try:
        # Test applying parental urgent lock command
        service._apply_server_command({
            "command": "LOCK_URGENT",
            "payload": {"reason": "Bedtime"},
        })
        assert service.tracker.is_locked() is True
        assert service.tracker.state == ScreenTimeState.LOCKED_URGENT

        # Test applying parental unlock command
        service._apply_server_command({
            "command": "UNLOCK",
            "payload": {},
        })
        assert service.tracker.is_locked() is False

        # Test applying bonus minutes
        service._apply_server_command({
            "command": "ADD_TIME",
            "payload": {"minutes": 20.0},
        })
        assert service.tracker.bonus_seconds_today == 20.0 * 60

        # Enqueue dummy event and test PURGE_DATA command
        service.buffer.enqueue_event(
            device_id="DEV-TEST-002",
            child_id="102",
            event_type="dns_blocked",
            subject="gambling.com",
        )
        assert len(service.buffer.peek_unsynced_batch(limit=10)) >= 1

        service._apply_server_command({
            "command": "PURGE_DATA",
            "payload": {"child_id": "102"},
        })
        assert len(service.buffer.peek_unsynced_batch(limit=10)) == 0

    finally:
        service.stop()
