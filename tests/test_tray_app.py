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


# ==============================================================================
# Native Desktop GUI Unit Tests (M1 / M2 Upgrade)
# ==============================================================================

def test_dynamic_tray_icon_generation_and_colors():
    """
    R1: Verifies dynamic Pillow icon generation across all 4 time/state tiers:
    - Normal (> 10m): Blue (#0284c7)
    - Warning (5-10m): Amber (#f59e0b)
    - Urgent (< 5m & Grace): Deep Orange (#ea580c)
    - Locked / Connection Lost: Red (#dc2626)
    """
    from PIL import Image
    from src.tray.gui import (
        create_tray_icon_image,
        generate_tray_icon,
        COLOR_NORMAL,
        COLOR_WARNING,
        COLOR_URGENT,
        COLOR_LOCKED,
    )

    # 1. Normal (> 10m)
    img_normal = create_tray_icon_image(remaining_seconds=1800, is_locked=False, connection_lost=False)
    assert isinstance(img_normal, Image.Image)
    assert img_normal.size == (64, 64)
    assert img_normal.mode == "RGBA"
    pixel_normal = img_normal.getpixel((32, 10))
    assert pixel_normal[:3] == COLOR_NORMAL

    # 2. Warning (5-10m)
    img_warn = create_tray_icon_image(remaining_seconds=420, is_locked=False, connection_lost=False)
    assert img_warn.size == (64, 64)
    pixel_warn = img_warn.getpixel((32, 10))
    assert pixel_warn[:3] == COLOR_WARNING

    # 3. Urgent (< 5m & Grace)
    img_urgent = create_tray_icon_image(remaining_seconds=180, is_locked=False, connection_lost=False)
    assert img_urgent.size == (64, 64)
    pixel_urgent = img_urgent.getpixel((32, 10))
    assert pixel_urgent[:3] == COLOR_URGENT

    # Grace state
    img_grace = create_tray_icon_image(remaining_seconds=0, state="GRACE_PERIOD_60S")
    pixel_grace = img_grace.getpixel((32, 10))
    assert pixel_grace[:3] == COLOR_URGENT

    # 4. Locked
    img_locked = create_tray_icon_image(remaining_seconds=0, is_locked=True, connection_lost=False)
    assert img_locked.size == (64, 64)
    pixel_locked = img_locked.getpixel((32, 10))
    assert pixel_locked[:3] == COLOR_LOCKED

    # 5. Connection Lost
    img_lost = generate_tray_icon(remaining_seconds=1800, is_locked=False, connection_lost=True)
    assert img_lost.size == (64, 64)
    pixel_lost = img_lost.getpixel((32, 10))
    assert pixel_lost[:3] == COLOR_LOCKED


def test_tray_context_menu_items_and_no_exit_option():
    """
    R1 & NT1: Context menu must contain exactly 6 items and NO exit/quit item.
    Also verifies child agency and informational callbacks.
    """
    from unittest.mock import MagicMock
    from src.tray.gui import build_context_menu

    controller = MagicMock()
    controller.current_status = {
        "remaining_seconds": 1800.0,
        "state": "ACTIVE_COUNTING",
        "is_locked": False,
    }
    menu_items = build_context_menu(controller)

    # Must have exactly 6 menu items
    assert len(menu_items) == 6

    # Extract titles/labels (evaluating dynamic callable if present)
    labels = [item.text(item) if callable(item.text) else str(item.text) for item in menu_items]

    # Verify expected items exist
    assert any("Thời gian còn lại" in lbl for lbl in labels)
    assert any("Trạng thái" in lbl for lbl in labels)
    assert any("Xin thêm 15 phút" in lbl for lbl in labels)
    assert any("Báo chặn nhầm" in lbl for lbl in labels)
    assert any("Hôm nay em đã dùng gì" in lbl for lbl in labels)
    assert any("Hotline 111" in lbl for lbl in labels)

    # NT1 Anti-Tamper: NO Exit/Quit option permitted!
    for lbl in labels:
        assert "thoát" not in lbl.lower()
        assert "đóng" not in lbl.lower()
        assert "exit" not in lbl.lower()
        assert "quit" not in lbl.lower()

    # Trigger action callbacks
    for item in menu_items:
        action_fn = getattr(item, "action", getattr(item, "_action", None))
        if callable(action_fn):
            try:
                action_fn(None, item)
            except Exception:
                pass
    # Verify child agency requests were dispatched
    controller.request_extra_time.assert_called_once()
    controller.report_unblock_domain.assert_called_once()


def test_realtime_toast_notifications_escalation_and_timers():
    """
    R2: Verifies auto-dismiss durations for toast alerts (10m -> 6s, 5m -> 8s, 1m -> 10s).
    """
    from src.tray.gui import ToastNotificationManager
    from unittest.mock import MagicMock, patch

    mock_root = MagicMock()
    toast_mgr = ToastNotificationManager(root=mock_root)

    # 10m warning -> 6000ms dismiss
    toast_mgr.show_toast(level="10M", message="Còn 10 phút", title="Nhắc nhở")
    assert toast_mgr.active_toast_duration == 6000
    mock_root.after.assert_called_with(6000, toast_mgr.dismiss_toast)

    # 5m warning -> 8000ms dismiss
    toast_mgr.show_toast(level="5M", message="Còn 5 phút", title="Sắp hết giờ")
    assert toast_mgr.active_toast_duration == 8000
    mock_root.after.assert_called_with(8000, toast_mgr.dismiss_toast)

    # 1m warning -> 10000ms dismiss + audio alert on Windows
    mock_winsound = MagicMock()
    with patch("sys.platform", "win32"), patch.dict("sys.modules", {"winsound": mock_winsound}):
        toast_mgr.show_toast(level="1M", message="Còn 1 phút", title="Khẩn cấp")
        assert toast_mgr.active_toast_duration == 10000
        mock_root.after.assert_called_with(10000, toast_mgr.dismiss_toast)
        mock_winsound.MessageBeep.assert_called_once()


def test_grace_period_dialog_non_focus_stealing_and_actions():
    """
    R2 & NT4: 60s Grace period dialog MUST use WS_EX_NOACTIVATE on Windows
    and MUST NOT steal focus (no grab_set or focus_force) to preserve Ctrl+S.
    Also verifies countdown and button actions.
    """
    from unittest.mock import MagicMock, patch
    from src.tray.gui import GracePeriodDialog

    mock_toplevel = MagicMock()
    mock_controller = MagicMock()

    with patch("sys.platform", "win32"), patch("ctypes.windll", create=True) as mock_windll:
        mock_windll.user32.GetWindowLongW.return_value = 0
        mock_windll.user32.GetParent.return_value = 12345

        dialog = GracePeriodDialog(parent=mock_toplevel, controller=mock_controller)
        dialog.setup_ui()

        # Verify Win32 WS_EX_NOACTIVATE (0x08000000) and WS_EX_TOPMOST (0x00000008) applied
        mock_windll.user32.SetWindowLongW.assert_called_once()
        applied_style = mock_windll.user32.SetWindowLongW.call_args[0][2]
        assert applied_style & 0x08000000  # WS_EX_NOACTIVATE
        assert applied_style & 0x00000008  # WS_EX_TOPMOST

        # Verify non-focus-stealing: grab_set and focus_force MUST NOT be called!
        mock_toplevel.grab_set.assert_not_called()
        mock_toplevel.focus_force.assert_not_called()

        # Verify initial countdown state
        assert dialog.seconds_left == 60

        # Verify action buttons
        dialog.on_lock_now_clicked()
        mock_controller._handle_lock.assert_called_once_with("LOCKED_QUOTA")

        dialog.on_request_time_clicked()
        mock_controller.request_extra_time.assert_called_with(15, reason="Yêu cầu từ hộp thoại ân hạn")


def test_fullscreen_lock_overlay_attributes_and_hotline():
    """
    R2 & NT6: Fullscreen lock overlay covers display, forces grab_set, blocks Alt+F4/Esc,
    and provides Hotline 111 and child extra time request.
    """
    from unittest.mock import MagicMock
    from src.tray.gui import FullscreenLockOverlay

    mock_toplevel = MagicMock()
    mock_controller = MagicMock()

    overlay = FullscreenLockOverlay(parent=mock_toplevel, controller=mock_controller)
    overlay.show(reason="Hết hạn mức thời gian")

    # Fullscreen overlay assertions
    mock_toplevel.overrideredirect.assert_called_with(True)
    mock_toplevel.wm_attributes.assert_called_with("-topmost", True)
    mock_toplevel.grab_set.assert_called_once()

    # Intercept close shortcuts
    bindings = [call[0][0] for call in mock_toplevel.bind.call_args_list]
    assert "<Alt-F4>" in bindings or "<Alt-KeyPress-F4>" in bindings
    assert "<Escape>" in bindings

    # Child agency action
    overlay.on_request_time_clicked()
    mock_controller.request_extra_time.assert_called_with(15, reason="Yêu cầu từ màn hình khóa")

    # Hide overlay
    overlay.hide()
    mock_toplevel.grab_release.assert_called_once()
    mock_toplevel.withdraw.assert_called_once()


def test_transparency_window_content_and_child_rights():
    """
    NT5: Transparency window loads parental dashboard mirror data,
    4 child rights, and National Hotline 111.
    """
    from unittest.mock import MagicMock
    from src.tray.gui import TransparencyDialog

    mock_toplevel = MagicMock()
    mock_controller = MagicMock()
    mock_controller.get_transparency_info.return_value = {
        "title": "Quy Tắc Sử Dụng Máy Tính Của Bạn (OpenGuard Kids)",
        "daily_quota_minutes": 120,
        "bed_time": "22:00 - 06:00",
        "child_rights": [
            "Được cảnh báo trước 10 phút, 5 phút và 1 phút trước khi hết giờ.",
            "Có 60 giây ân hạn để lưu tài liệu bài tập, không bị tắt máy đột ngột.",
            "Được quyền gửi yêu cầu xin thêm giờ và báo chặn nhầm trang web học tập.",
            "Không bị chụp trộm màn hình hay ghi phím bấm bí mật (Bảo vệ quyền riêng tư).",
        ],
        "hotline": "111 - Cục Trẻ em",
    }

    dialog = TransparencyDialog(parent=mock_toplevel, controller=mock_controller)
    data = dialog.load_data()

    assert data["daily_quota_minutes"] == 120
    assert "22:00" in data["bed_time"]
    assert len(data["child_rights"]) == 4
    assert "111" in data["hotline"]


def test_headless_detection_and_graceful_fallback():
    """
    R3: If DISPLAY is missing or tkinter/pystray fails, system gracefully falls back
    to console visualizer without crashing or raising TclError/ModuleNotFoundError.
    """
    from unittest.mock import patch, MagicMock
    from src.tray.gui import is_gui_available, is_gui_environment_available, run_tray_ui
    from src.tray.main import is_gui_environment_available as main_is_gui_avail

    # 1. Force headless condition via mock
    with patch("src.tray.gui._check_gui_support", return_value=False):
        assert is_gui_available() is False
        assert is_gui_environment_available() is False
        assert main_is_gui_avail() is False

        # Ensure running tray UI invokes console fallback cleanly
        mock_client = MagicMock()
        mock_client.get_status.return_value = {"state": "ACTIVE_COUNTING", "remaining_seconds": 3600.0}

        controller = run_tray_ui(ipc_client=mock_client, force_fallback=True)
        assert controller is not None
        assert controller.active_view == "NORMAL"
        controller.stop()

    # 2. Test OGK_HEADLESS env var detection
    with patch.dict("os.environ", {"OGK_HEADLESS": "1"}):
        from src.tray.gui import _check_gui_support
        assert _check_gui_support() is False

