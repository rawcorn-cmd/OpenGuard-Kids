"""
Unit & Integration tests for OpenGuard Kids Desktop Tray Application (Week 4).
Verifies StateListener, Warning Toasts (10m, 5m, 1m), 60s Grace Period, Lock Overlay,
Anti-Abuse connection loss safeguard (NT1, F5), Child Agency requests (NT4),
Transparency screen (NT5), and the Complete Demo D1 Acceptance Flow.
"""

import time
from src.agent.ipc import IPCManager, IPCClient
from src.tray.state_listener import StateListener
from src.tray.dialogs import NotificationModel
from src.tray.app import TrayAppController


def test_state_listener_polling_and_heartbeat():
    service_status = {
        "state": "ACTIVE_COUNTING",
        "is_locked": False,
        "remaining_seconds": 3600.0,
        "daily_quota_seconds": 7200,
    }

    ipc = IPCManager(host="127.0.0.1", port=0, status_callback=lambda: service_status)
    ipc.start()
    client = IPCClient(host="127.0.0.1", port=ipc.port, token=ipc.secret_token)

    captured_updates = []
    listener = StateListener(
        ipc_client=client,
        on_status_update=lambda st: captured_updates.append(st),
    )

    try:
        res = listener.poll_once()
        assert res is not None
        assert res["state"] == "ACTIVE_COUNTING"
        assert len(captured_updates) == 1
        assert ipc.server.last_tray_heartbeat > 0.0
    finally:
        ipc.stop()


def test_warning_toasts_and_grace_period_triggers():
    mock_status = {"state": "ACTIVE_COUNTING", "is_locked": False, "remaining_seconds": 1200.0}

    ipc = IPCManager(host="127.0.0.1", port=0, status_callback=lambda: mock_status)
    ipc.start()
    client = IPCClient(host="127.0.0.1", port=ipc.port, token=ipc.secret_token)

    ui_events = []

    def on_ui(evt_type, data):
        ui_events.append((evt_type, data))

    controller = TrayAppController(ipc_client=client, ui_notifier=on_ui)

    try:
        # 1. 10-Minute Warning
        mock_status["state"] = "WARNING_10M"
        mock_status["remaining_seconds"] = 580.0
        controller.listener.poll_once()
        assert controller.active_view == "WARNING_TOAST"
        assert any(e[0] == "WARNING_TOAST" and "10 phút" in e[1]["title"] for e in ui_events)

        # 2. 5-Minute Warning
        mock_status["state"] = "WARNING_5M"
        mock_status["remaining_seconds"] = 280.0
        controller.listener.poll_once()
        assert controller.active_view == "WARNING_TOAST"
        assert any(e[0] == "WARNING_TOAST" and "5 phút" in e[1]["title"] for e in ui_events)

        # 3. 1-Minute Warning
        mock_status["state"] = "WARNING_1M"
        mock_status["remaining_seconds"] = 50.0
        controller.listener.poll_once()
        assert controller.active_view == "WARNING_TOAST"
        assert any(e[0] == "WARNING_TOAST" and "1 phút" in e[1]["title"] for e in ui_events)

        # 4. 60-Second Grace Period (Save Work Dialog)
        mock_status["state"] = "GRACE_PERIOD_60S"
        mock_status["remaining_seconds"] = 0.0
        controller.listener.poll_once()
        assert controller.active_view == "GRACE_PERIOD"
        assert any(e[0] == "GRACE_PERIOD_DIALOG" for e in ui_events)

        # 5. Lock Quota Trigger
        mock_status["state"] = "LOCKED_QUOTA"
        mock_status["is_locked"] = True
        controller.listener.poll_once()
        assert controller.active_view == "LOCKED"
        assert any(e[0] == "LOCK_SCREEN" for e in ui_events)

    finally:
        ipc.stop()


def test_anti_abuse_connection_lost_safeguard():
    """
    NT1 & F5 Rule: If Tray loses contact with Service > 15 seconds,
    anti-abuse safeguard is triggered to prevent stealth/tamper operation.
    """
    client = IPCClient(host="127.0.0.1", port=59999, token="invalid")

    lost_contact_called = []
    listener = StateListener(
        ipc_client=client,
        on_connection_lost=lambda: lost_contact_called.append(True),
    )

    listener.last_successful_contact = time.time() - 20.0

    res = listener.poll_once()
    assert res is None
    assert len(lost_contact_called) == 1
    assert listener.connection_lost is True


def test_child_agency_and_transparency():
    """
    Verifies child agency requests (NT4) and transparency screen (NT5).
    """
    requests_received = []

    def handle_request(req):
        requests_received.append(req)
        return {"status": "SUCCESS", "request_id": "req-999"}

    ipc = IPCManager(
        host="127.0.0.1",
        port=0,
        request_callback=handle_request,
    )
    ipc.start()
    client = IPCClient(host="127.0.0.1", port=ipc.port, token=ipc.secret_token)
    controller = TrayAppController(ipc_client=client)

    try:
        # 1. Child requests extra time ("Xin thêm 15 phút")
        res_time = controller.request_extra_time(minutes=15, reason="Em can hoan thanh bai tap Toan")
        assert res_time["status"] == "SUCCESS"
        assert len(requests_received) == 1
        assert requests_received[0]["type"] == "ADD_TIME"
        assert requests_received[0]["minutes"] == 15

        # 2. Child reports unblock domain ("Báo chặn nhầm")
        res_domain = controller.report_unblock_domain("edu.vn", reason="Web truong hoc")
        assert res_domain["status"] == "SUCCESS"
        assert len(requests_received) == 2
        assert requests_received[1]["type"] == "UNBLOCK_DOMAIN"

        # 3. Child Transparency Info (NT5)
        controller.current_status = {
            "policy": {
                "daily_quota_minutes": 90,
                "bed_time_start": "21:30",
                "bed_time_end": "06:30",
            }
        }
        trans_info = controller.get_transparency_info()
        assert trans_info["daily_quota_minutes"] == 90
        assert "111" in trans_info["hotline"]
        assert len(trans_info["child_rights"]) == 4

    finally:
        ipc.stop()


def test_complete_demo_d1_acceptance_sequence():
    """
    Full simulation of the Demo D1 Acceptance Flow:
    1. Active usage ->
    2. 10m / 5m / 1m advance warnings ->
    3. 60-second grace period dialog ->
    4. Screen locked overlay ->
    5. Child clicks "Xin thêm 15 phút" ->
    6. Parent approves -> Unlocks back to normal active view!
    """
    state_sim = {
        "state": "ACTIVE_COUNTING",
        "is_locked": False,
        "remaining_seconds": 1800.0,
    }

    requests_captured = []

    def mock_request_handler(payload):
        requests_captured.append(payload)
        return {"status": "SUBMITTED"}

    ipc = IPCManager(
        host="127.0.0.1",
        port=0,
        status_callback=lambda: state_sim,
        request_callback=mock_request_handler,
    )
    ipc.start()
    client = IPCClient(host="127.0.0.1", port=ipc.port, token=ipc.secret_token)
    controller = TrayAppController(ipc_client=client)

    try:
        # Step 1: Active
        controller.listener.poll_once()
        assert controller.active_view == "NORMAL"

        # Step 2: Warnings
        state_sim["state"] = "WARNING_10M"
        state_sim["remaining_seconds"] = 550.0
        controller.listener.poll_once()
        assert controller.active_view == "WARNING_TOAST"

        # Step 3: Grace period dialog
        state_sim["state"] = "GRACE_PERIOD_60S"
        state_sim["remaining_seconds"] = 0.0
        controller.listener.poll_once()
        assert controller.active_view == "GRACE_PERIOD"

        # Step 4: Lock
        state_sim["state"] = "LOCKED_QUOTA"
        state_sim["is_locked"] = True
        controller.listener.poll_once()
        assert controller.active_view == "LOCKED"

        # Step 5: Child asks for 15 minutes
        req_res = controller.request_extra_time(15, "Xin them gio lam bai")
        assert req_res["status"] == "SUCCESS"
        assert len(requests_captured) == 1

        # Step 6: Parent approves bonus time -> System returns to active
        state_sim["state"] = "ACTIVE_COUNTING"
        state_sim["is_locked"] = False
        state_sim["remaining_seconds"] = 900.0
        controller.listener.poll_once()

        # Successfully unlocked!
        assert controller.active_view == "NORMAL"

    finally:
        ipc.stop()
