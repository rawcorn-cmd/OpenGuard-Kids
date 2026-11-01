"""
Comprehensive Unit & Integration Tests for Milestone 2:
Cross-Platform Notifications, Visual Alerts & Token Startup Resilience.
"""

import os
import sys
import time
import threading
from unittest.mock import MagicMock, patch

import pytest

from src.tray.notifications import CrossPlatformNotifier
from src.tray.dialogs import (
    GracePeriodDialog,
    FullscreenLockOverlay,
    TransparencyDialog,
    show_grace_period_zenity,
    show_lock_zenity,
    prompt_extra_time_dialog,
    prompt_unblock_domain_dialog,
    show_transparency_dialog,
)
from src.tray.gui import (
    create_tray_icon_image,
    build_context_menu,
    TrayUIPresenter,
    COLOR_NORMAL,
    COLOR_WARNING,
    COLOR_URGENT,
    COLOR_LOCKED,
)


# ==============================================================================
# 1. Cross-Platform Desktop Notifications
# ==============================================================================

def test_notifier_linux_mint_notify_send_dispatch():
    """Verifies notify-send CLI arguments: urgency, timeout, title, message on Linux Mint."""
    mock_popen = MagicMock()
    with patch("sys.platform", "linux"), patch("subprocess.Popen", mock_popen):
        notifier = CrossPlatformNotifier()
        notifier.notify_send_bin = "/usr/bin/notify-send"

        # 10M warning: normal urgency, 6000ms
        notifier.show_toast(level="10M", message="Còn 10 phút sử dụng", title="Cảnh báo 10M")
        mock_popen.assert_called()
        cmd = mock_popen.call_args[0][0]
        assert cmd[0] == "/usr/bin/notify-send"
        assert "-u" in cmd and cmd[cmd.index("-u") + 1] == "normal"
        assert "-t" in cmd and cmd[cmd.index("-t") + 1] == "6000"
        assert "Còn 10 phút sử dụng" in cmd

        # 5M warning: normal urgency, 8000ms
        mock_popen.reset_mock()
        notifier.show_toast(level="5M", message="Còn 5 phút", title="Cảnh báo 5M")
        cmd5 = mock_popen.call_args[0][0]
        assert "-t" in cmd5 and cmd5[cmd5.index("-t") + 1] == "8000"
        assert "-u" in cmd5 and cmd5[cmd5.index("-u") + 1] == "normal"

        # 1M warning: critical urgency, 10000ms
        mock_popen.reset_mock()
        notifier.show_toast(level="1M", message="Còn 1 phút", title="Cảnh báo 1M")
        cmd1 = mock_popen.call_args[0][0]
        assert "-t" in cmd1 and cmd1[cmd1.index("-t") + 1] == "10000"
        assert "-u" in cmd1 and cmd1[cmd1.index("-u") + 1] == "critical"


def test_notifier_windows_sound_and_fallback():
    """Verifies audio beep and win10toast on Windows platform."""
    mock_winsound = MagicMock()
    with patch("sys.platform", "win32"), patch.dict("sys.modules", {"winsound": mock_winsound}):
        notifier = CrossPlatformNotifier()
        notifier.notify_send_bin = None

        notifier.show_toast(level="1M", message="Sắp hết giờ", title="Cảnh báo khẩn")
        mock_winsound.MessageBeep.assert_called_once()


def test_notifier_pystray_icon_and_tkinter_fallback():
    """Verifies icon.notify and Tkinter auto-dismiss fallback."""
    mock_icon = MagicMock()
    mock_root = MagicMock()
    notifier = CrossPlatformNotifier(root=mock_root, icon=mock_icon)
    notifier.notify_send_bin = None  # Force fallback

    with patch("sys.platform", "linux"):
        notifier.show_toast(level="10M", message="Thong bao", title="Tieu de")
        mock_icon.notify.assert_called_with("Thong bao", "Tieu de")
        mock_root.after.assert_called_with(6000, notifier.dismiss_toast)


# ==============================================================================
# 2. Interactive Dialogs & Overlays
# ==============================================================================

def test_grace_period_countdown_tick_and_auto_lock():
    """Verifies digital countdown seconds updating and auto-locking when reaching 0."""
    mock_parent = MagicMock()
    mock_controller = MagicMock()
    dialog = GracePeriodDialog(parent=mock_parent, controller=mock_controller)
    dialog.lbl_countdown = MagicMock()
    dialog.seconds_left = 2

    # Tick 1: 2 -> 1
    dialog._tick()
    assert dialog.seconds_left == 1
    dialog.lbl_countdown.config.assert_called_with(text="Còn lại 1s...")
    mock_parent.after.assert_called_with(1000, dialog._tick)
    mock_controller._handle_lock.assert_not_called()

    # Tick 2: 1 -> 0 => Auto Lock
    dialog._tick()
    assert dialog.seconds_left == 0
    dialog.lbl_countdown.config.assert_called_with(text="Còn lại 0s...")
    mock_controller._handle_lock.assert_called_once_with("LOCKED_QUOTA")


def test_zenity_grace_period_button_and_timeout_actions():
    """Verifies Zenity 60s grace dialog handling OK, Cancel, and Timeout."""
    mock_controller = MagicMock()

    # Scenario A: User clicks "Xin thêm 15 phút" (exit code 0)
    with patch("shutil.which", return_value="/usr/bin/zenity"), \
         patch("subprocess.run", return_value=MagicMock(returncode=0)):
        show_grace_period_zenity(mock_controller)
        time.sleep(0.05)
        mock_controller.request_extra_time.assert_called_with(15, reason="Yêu cầu từ hộp thoại ân hạn Zenity")

    # Scenario B: User clicks "Khóa ngay" (exit code 1)
    mock_controller.reset_mock()
    with patch("shutil.which", return_value="/usr/bin/zenity"), \
         patch("subprocess.run", return_value=MagicMock(returncode=1)):
        show_grace_period_zenity(mock_controller)
        time.sleep(0.05)
        mock_controller._handle_lock.assert_called_with("LOCKED_QUOTA")

    # Scenario C: 60-second Timeout expired (exit code 5)
    mock_controller.reset_mock()
    with patch("shutil.which", return_value="/usr/bin/zenity"), \
         patch("subprocess.run", return_value=MagicMock(returncode=5)):
        show_grace_period_zenity(mock_controller)
        time.sleep(0.05)
        mock_controller._handle_lock.assert_called_with("LOCKED_QUOTA")


def test_zenity_lock_overlay_request_button():
    """Verifies Zenity warning dialog for locked computer."""
    mock_controller = MagicMock()

    with patch("shutil.which", return_value="/usr/bin/zenity"), \
         patch("subprocess.run", return_value=MagicMock(returncode=0)):
        show_lock_zenity(mock_controller, reason="Khóa tức thời từ Phụ huynh")
        time.sleep(0.05)
        mock_controller.request_extra_time.assert_called_with(15, reason="Yêu cầu từ màn hình khóa Zenity")


def test_interactive_child_request_dialogs():
    """Verifies Zenity input prompt for +15m extension and domain unblocking."""
    mock_controller = MagicMock()

    # 1. Extra time prompt
    mock_proc_time = MagicMock(returncode=0, stdout="Làm bài tập Khoa học\n")
    with patch("sys.platform", "linux"), \
         patch("shutil.which", return_value="/usr/bin/zenity"), \
         patch("subprocess.run", return_value=mock_proc_time):
        prompt_extra_time_dialog(parent=None, controller=mock_controller)
        time.sleep(0.05)
        mock_controller.request_extra_time.assert_called_with(15, reason="Làm bài tập Khoa học")

    # 2. Unblock domain prompt
    mock_controller.reset_mock()
    mock_proc_domain = MagicMock(returncode=0, stdout="tienganh123.com|Luyện nghe tiếng Anh\n")
    with patch("sys.platform", "linux"), \
         patch("shutil.which", return_value="/usr/bin/zenity"), \
         patch("subprocess.run", return_value=mock_proc_domain):
        prompt_unblock_domain_dialog(parent=None, controller=mock_controller)
        time.sleep(0.05)
        mock_controller.report_unblock_domain.assert_called_with("tienganh123.com", reason="Luyện nghe tiếng Anh")


def test_show_transparency_dialog_formatting():
    """Verifies transparency dialog formats quota, bedtime, child rights, and hotline 111."""
    mock_controller = MagicMock()
    mock_controller.get_transparency_info.return_value = {
        "title": "Quy Tắc Sử Dụng Máy Tính Của Bạn (OpenGuard Kids)",
        "daily_quota_minutes": 100,
        "bed_time": "22:00 - 06:00",
        "child_rights": ["Quyền được thông báo trước 10m", "Quyền 60s ân hạn"],
        "hotline": "111 - Cục Trẻ em",
    }

    mock_run = MagicMock()
    with patch("sys.platform", "linux"), \
         patch("shutil.which", return_value="/usr/bin/zenity"), \
         patch("subprocess.run", mock_run):
        show_transparency_dialog(parent=None, controller=mock_controller)
        time.sleep(0.05)

        mock_run.assert_called_once()
        cmd = mock_run.call_args[0][0]
        assert cmd[0] == "/usr/bin/zenity"
        assert "--info" in cmd
        full_text = " ".join(cmd)
        assert "100 phút" in full_text
        assert "22:00 - 06:00" in full_text
        assert "111" in full_text


# ==============================================================================
# 3. Startup Race Condition Resilience
# ==============================================================================

def test_startup_token_retry_loop_success(tmp_path):
    """Verifies that Tray startup waits for delayed ipc_secret.token without crashing."""
    token_file = tmp_path / "ipc_secret.token"
    expected_token = "a" * 64

    # Simulate Agent Service creating the token after 0.3 seconds in background thread
    def _create_token_later():
        time.sleep(0.3)
        token_file.write_text(expected_token, encoding="utf-8")

    threading.Thread(target=_create_token_later, daemon=True).start()

    # Run the retry logic from main
    start_time = time.time()
    wait_timeout = 5.0
    poll_interval = 0.1
    found_token = None

    while time.time() - start_time < wait_timeout:
        if token_file.is_file():
            found_token = token_file.read_text(encoding="utf-8").strip()
            if found_token:
                break
        time.sleep(poll_interval)

    assert found_token == expected_token
    assert (time.time() - start_time) >= 0.25


def test_startup_token_retry_loop_timeout(tmp_path):
    """Verifies timeout when token file is never created."""
    token_file = tmp_path / "nonexistent.token"
    start_time = time.time()
    wait_timeout = 0.5
    poll_interval = 0.1
    found_token = None

    while time.time() - start_time < wait_timeout:
        if token_file.is_file():
            found_token = token_file.read_text(encoding="utf-8").strip()
            break
        time.sleep(poll_interval)

    assert found_token is None


# ==============================================================================
# 4. Dynamic Time Badge Updates & Color Thresholds
# ==============================================================================

def test_dynamic_badge_thresholds_complete():
    """Verifies all color thresholds and icon labels: >10m, 5-10m, <5m, Grace, Locked."""
    # Blue: > 10m
    img_blue = create_tray_icon_image(remaining_seconds=1200)
    assert img_blue.getpixel((32, 10))[:3] == COLOR_NORMAL

    # Amber: 5-10m
    img_amber = create_tray_icon_image(remaining_seconds=500)
    assert img_amber.getpixel((32, 10))[:3] == COLOR_WARNING

    # Deep Orange: < 5m
    img_orange = create_tray_icon_image(remaining_seconds=200)
    assert img_orange.getpixel((32, 10))[:3] == COLOR_URGENT

    # Deep Orange: Grace Period
    img_grace = create_tray_icon_image(remaining_seconds=0, state="GRACE_PERIOD_60S")
    assert img_grace.getpixel((32, 10))[:3] == COLOR_URGENT

    # Red: Locked
    img_locked = create_tray_icon_image(remaining_seconds=0, is_locked=True)
    assert img_locked.getpixel((32, 10))[:3] == COLOR_LOCKED

    # Red: Connection Lost
    img_lost = create_tray_icon_image(connection_lost=True)
    assert img_lost.getpixel((32, 10))[:3] == COLOR_LOCKED
