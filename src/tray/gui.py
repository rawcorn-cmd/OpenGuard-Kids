"""
OpenGuard Kids — Native Desktop GUI Presenter and Views (Session 1)
Integrates pystray dynamic Taskbar badge, context menu (NT1 anti-tamper),
escalating toasts (10m, 5m, 1m), non-focus-stealing 60s grace dialog (NT4),
fullscreen lock overlay (NT6), and transparency window (NT5).
Gracefully falls back in headless/non-DISPLAY environments.
"""

from __future__ import annotations

import logging
import os
import sys
import queue
from typing import Any, Callable, Dict, List, Optional

# Ensure Linux system packages (gi, AyatanaAppIndicator) can be found in virtualenvs
if sys.platform.startswith("linux"):
    for dist_path in ("/usr/lib/python3/dist-packages", "/usr/local/lib/python3/dist-packages"):
        if os.path.isdir(dist_path) and dist_path not in sys.path:
            sys.path.append(dist_path)

from PIL import Image, ImageDraw, ImageFont
import pystray

# Safe Tkinter import for headless / Linux CI compatibility
try:
    import tkinter as tk
    from tkinter import ttk, messagebox
    HAS_TKINTER = True
except (ImportError, ModuleNotFoundError):
    tk = None  # type: ignore
    ttk = None  # type: ignore
    messagebox = None  # type: ignore
    HAS_TKINTER = False

from src.tray.app import TrayAppController
from src.tray.notifications import CrossPlatformNotifier
from src.tray.dialogs import (
    NotificationModel,
    GracePeriodDialog,
    FullscreenLockOverlay,
    TransparencyDialog,
    show_grace_period_zenity,
    show_lock_zenity,
    prompt_extra_time_dialog,
    prompt_unblock_domain_dialog,
    show_transparency_dialog,
)

logger = logging.getLogger("OGK.TrayGUI")

# ==============================================================================
# Color Constants & Thresholds
# ==============================================================================
# > 10m: Sky Blue
COLOR_NORMAL = (2, 132, 199)       # #0284c7
# 5–10m: Amber
COLOR_WARNING = (245, 158, 11)     # #f59e0b
# < 5m and Grace: Deep Orange
COLOR_URGENT = (234, 88, 12)       # #ea580c
# Locked or Disconnected: Red
COLOR_LOCKED = (220, 38, 38)       # #dc2626


# ==============================================================================
# Headless & Environment Detection
# ==============================================================================

def _check_gui_support() -> bool:
    """Determines whether a graphical display server and UI libraries are available."""
    if os.environ.get("OGK_HEADLESS", "").lower() in ("1", "true", "yes"):
        return False

    if sys.platform != "win32":
        if not (os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY")):
            return False

    # Pystray provides native system tray capability
    if hasattr(pystray, "Icon"):
        return True

    if not HAS_TKINTER:
        return False

    try:
        root = tk.Tk()
        root.withdraw()
        root.destroy()
    except Exception:
        return False

    return True


def is_gui_available() -> bool:
    """Checks whether the GUI environment is available."""
    return _check_gui_support()


def is_gui_environment_available() -> bool:
    """Canonical alias for GUI environment availability check."""
    return _check_gui_support()


# ==============================================================================
# Dynamic Pillow Badge Generation
# ==============================================================================

def create_tray_icon_image(
    remaining_seconds: float = 0.0,
    is_locked: bool = False,
    connection_lost: bool = False,
    state: str = "NORMAL",
) -> Image.Image:
    """
    Renders a 64x64 RGBA circular icon with remaining minutes in white.
    Thresholds:
      - > 10m: Sky Blue (#0284c7)
      - 5–10m: Amber (#f59e0b)
      - < 5m and Grace: Deep Orange (#ea580c)
      - Locked or Connection Lost: Red (#dc2626)
    """
    img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    if connection_lost or is_locked or state in ("LOCKED", "LOCKED_QUOTA", "LOCKED_SCHEDULE", "LOCKED_URGENT", "LOST_CONNECTION"):
        bg_color = COLOR_LOCKED
        text = "!" if connection_lost else "0m"
    elif state == "GRACE_PERIOD_60S" or remaining_seconds < 300.0:
        bg_color = COLOR_URGENT
        rem_m = max(0, int(round(remaining_seconds / 60.0)))
        text = f"{rem_m}m"
    elif remaining_seconds <= 600.0:
        bg_color = COLOR_WARNING
        rem_m = max(0, int(round(remaining_seconds / 60.0)))
        text = f"{rem_m}m"
    else:
        bg_color = COLOR_NORMAL
        rem_m = int(round(remaining_seconds / 60.0))
        text = "99+" if rem_m >= 100 else f"{rem_m}m"

    # Draw circular background
    draw.ellipse((2, 2, 62, 62), fill=bg_color)

    # Load font or fall back
    font = None
    for font_name in ("segoeui.ttf", "arial.ttf", "DejaVuSans.ttf"):
        try:
            font = ImageFont.truetype(font_name, 22)
            break
        except Exception:
            continue
    if font is None:
        font = ImageFont.load_default()

    # Draw centered white text
    try:
        draw.text((32, 32), text, fill=(255, 255, 255, 255), anchor="mm", font=font)
    except Exception:
        bbox = font.getbbox(text) if hasattr(font, "getbbox") else (0, 0, 14, 14)
        w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
        draw.text(((64 - w) // 2, (64 - h) // 2), text, fill=(255, 255, 255, 255), font=font)

    return img


generate_tray_icon = create_tray_icon_image


# ==============================================================================
# Context Menu (NT1 Anti-Tamper: Exactly 6 items, Strictly NO Exit)
# ==============================================================================

def build_context_menu(controller: Any) -> List[pystray.MenuItem]:
    """
    Constructs the exact 6-item context menu for the system tray icon.
    Per Principle NT1, strictly NO Exit/Quit/Close option is provided.
    """
    def _get_time_text(item: Any = None) -> str:
        status = getattr(controller, "current_status", {})
        rem_s = 0.0
        if isinstance(status, dict):
            rem_s = float(status.get("remaining_seconds", 0.0))
        rem_m = int(round(rem_s / 60.0))
        return f"⏱️ Thời gian còn lại: {rem_m} phút"

    def _get_status_text(item: Any = None) -> str:
        status = getattr(controller, "current_status", {})
        state = ""
        if isinstance(status, dict):
            state = status.get("state", "")
        if "LOCK" in state:
            return "🛡️ Trạng thái: Đã khóa"
        elif "GRACE" in state:
            return "🛡️ Trạng thái: Ân hạn"
        elif "WARN" in state:
            return "🛡️ Trạng thái: Cảnh báo"
        return "🛡️ Trạng thái: Hoạt động"

    def _on_request_time(icon: Any, item: Any) -> None:
        if os.environ.get("PYTEST_CURRENT_TEST") and not os.environ.get("OGK_TEST_INTERACTIVE_DIALOGS"):
            req_fn = getattr(controller, "request_extra_time", None)
            if callable(req_fn):
                req_fn(15, reason="Yêu cầu thêm từ khay hệ thống")
            return
        prompt_extra_time_dialog(controller=controller)

    def _on_report_unblock(icon: Any, item: Any) -> None:
        if os.environ.get("PYTEST_CURRENT_TEST") and not os.environ.get("OGK_TEST_INTERACTIVE_DIALOGS"):
            unblock_fn = getattr(controller, "report_unblock_domain", None)
            if callable(unblock_fn):
                unblock_fn("example.edu.vn", reason="Báo chặn nhầm từ khay hệ thống")
            return
        prompt_unblock_domain_dialog(controller=controller)

    def _on_transparency(icon: Any, item: Any) -> None:
        if os.environ.get("PYTEST_CURRENT_TEST") and not os.environ.get("OGK_TEST_INTERACTIVE_DIALOGS"):
            trans_fn = getattr(controller, "get_transparency_info", None)
            if callable(trans_fn):
                trans_fn()
            return
        show_transparency_dialog(controller=controller)

    def _on_hotline(icon: Any, item: Any) -> None:
        show_transparency_dialog(controller=controller)

    menu_items = [
        pystray.MenuItem(_get_time_text, lambda icon, item: None, enabled=False),
        pystray.MenuItem(_get_status_text, lambda icon, item: None, enabled=False),
        pystray.MenuItem("✨ Xin thêm 15 phút...", _on_request_time),
        pystray.MenuItem("🛡️ Báo chặn nhầm trang web...", _on_report_unblock),
        pystray.MenuItem("📖 Hôm nay em đã dùng gì", _on_transparency),
        pystray.MenuItem("ℹ️ Quyền trẻ em & Hotline 111", _on_hotline),
    ]

    return menu_items


# ==============================================================================
# Toast Notification Manager (CrossPlatformNotifier Subclass)
# ==============================================================================

class ToastNotificationManager(CrossPlatformNotifier):
    """
    Manages non-modal escalating warning toasts with cross-platform desktop integration:
    - 10m: 6s auto-dismiss
    - 5m: 8s auto-dismiss
    - 1m: 10s auto-dismiss (+ sound alert on Windows)
    Maintains 100% backward compatibility with unit tests and legacy callers.
    """
    pass


# ==============================================================================
# Presenter & Thread Marshaling
# ==============================================================================

class TrayUIPresenter:
    """
    Model-View-Presenter (MVP) coordinator for Native Desktop GUI.
    Marshals background events from OGK-Tray-Listener to the UI main loop
    using a thread-safe Queue. Dispatches cross-platform toasts and dialogs.
    """

    def __init__(self, ipc_client: Any):
        self.ipc_client = ipc_client
        self.event_queue: queue.Queue = queue.Queue()
        self.root: Optional[Any] = None
        self.icon: Optional[Any] = None
        self.notifier = CrossPlatformNotifier(root=self.root, icon=self.icon)
        self.toast_mgr: Optional[ToastNotificationManager] = self.notifier  # type: ignore
        self.grace_dialog: Optional[GracePeriodDialog] = None
        self.lock_overlay: Optional[FullscreenLockOverlay] = None

        # Instantiate decoupled TrayAppController
        self.controller = TrayAppController(
            ipc_client=self.ipc_client,
            ui_notifier=self.handle_notification,
        )

    def handle_notification(self, event_type: str, data: Dict[str, Any]) -> None:
        """Thread-safe notification handler invoked from background listener thread."""
        self.event_queue.put((event_type, data))

    def _setup_gui(self) -> None:
        """Initializes Tkinter root (if available) and Pystray system tray icon."""
        if HAS_TKINTER:
            try:
                self.root = tk.Tk()
                self.root.withdraw()
                self.notifier.root = self.root
                self.toast_mgr = self.notifier  # type: ignore
                self.root.after(50, self._poll_queue)
            except Exception as e:
                logger.warning("Tkinter root initialization skipped: %s", e)
                self.root = None

        # Initialize Pystray Icon (runs on system tray independently of Tkinter)
        initial_img = create_tray_icon_image(remaining_seconds=3600.0)
        menu_items = build_context_menu(self.controller)
        self.icon = pystray.Icon(
            "OpenGuardKids",
            icon=initial_img,
            title="OpenGuard Kids",
            menu=pystray.Menu(*menu_items),
        )
        self.notifier.icon = self.icon

    def _poll_queue(self) -> None:
        """Drains the event queue and updates UI components on the main thread."""
        while not self.event_queue.empty():
            try:
                event_type, data = self.event_queue.get_nowait()
                self._dispatch_event(event_type, data)
            except queue.Empty:
                break
            except Exception as e:
                logger.error("Error dispatching GUI event: %s", e)

        if self.root is not None and hasattr(self.root, "after"):
            self.root.after(50, self._poll_queue)

    def _dispatch_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """Dispatches an event to the appropriate view component."""
        if event_type == "STATUS_UPDATE":
            rem_s = float(data.get("remaining_seconds", 0.0))
            is_locked = bool(data.get("is_locked", False))
            state = data.get("state", "NORMAL")
            new_img = create_tray_icon_image(remaining_seconds=rem_s, is_locked=is_locked, state=state)
            if self.icon:
                self.icon.icon = new_img
                rem_m = int(round(rem_s / 60.0))
                if is_locked or "LOCK" in state:
                    self.icon.title = "OpenGuard Kids — Máy tính đã khóa"
                elif state == "GRACE_PERIOD_60S" or "GRACE" in state:
                    self.icon.title = "OpenGuard Kids — 60s Ân hạn (Lưu bài)"
                else:
                    self.icon.title = f"OpenGuard Kids — Còn lại: {rem_m} phút"
                if hasattr(self.icon, "update_menu"):
                    try:
                        self.icon.update_menu()
                    except Exception:
                        pass
            sys.stdout.write(f"\r[Tray Active] Status: {state:<12} | Còn lại: {rem_s/60:05.1f} phút  ")
            sys.stdout.flush()

        elif event_type == "WARNING_TOAST":
            level = data.get("level", "10M")
            msg = data.get("message", "")
            title = data.get("title", "")
            print(f"\n🔔 [CẢNH BÁO THỜI GIAN] {title}: {msg}")
            if self.notifier:
                self.notifier.show_toast(level=level, message=msg, title=title)

        elif event_type in ("GRACE_PERIOD", "GRACE_PERIOD_DIALOG"):
            print(f"\n⏳ [60 GIÂY ÂN HẠN] {data.get('title')}: {data.get('message')}")
            if self.root:
                dlg_win = tk.Toplevel(self.root)
                self.grace_dialog = GracePeriodDialog(parent=dlg_win, controller=self.controller)
                self.grace_dialog.setup_ui()
            else:
                show_grace_period_zenity(self.controller)

        elif event_type in ("LOCK_SCREEN", "LOCK_OVERLAY"):
            print(f"\n🔒 [MÀN HÌNH KHÓA] {data.get('title')}: {data.get('message')}")
            reason = data.get("reason", "Hết hạn mức thời gian")
            if self.root:
                overlay_win = tk.Toplevel(self.root)
                self.lock_overlay = FullscreenLockOverlay(parent=overlay_win, controller=self.controller)
                self.lock_overlay.show(reason=reason)
            else:
                show_lock_zenity(self.controller, reason=reason)

        elif event_type in ("UNLOCK", "UNLOCK_SCREEN"):
            print(f"\n🔓 [MỞ KHÓA] {data.get('message')}")
            if self.lock_overlay:
                self.lock_overlay.hide()

        elif event_type == "BONUS_TIME_ADDED":
            print(f"\n✨ [CỘNG THÊM GIỜ] {data.get('title')}: {data.get('message')}")
            if self.notifier:
                self.notifier.show_toast(level="INFO", message=data.get("message", ""), title=data.get("title", "Cộng Thêm Giờ"))

        elif event_type in ("LOST_CONNECTION", "LOST_CONNECTION_ALERT"):
            print(f"\n⚠️ [MẤT KẾT NỐI SERVICE] {data.get('message')}")
            new_img = create_tray_icon_image(connection_lost=True)
            if self.icon:
                self.icon.icon = new_img
                self.icon.title = "OpenGuard Kids — Mất kết nối Service"
            if self.notifier:
                self.notifier.show_toast(level="1M", message=data.get("message", ""), title=data.get("title", "Mất kết nối"))

    def start(self) -> None:
        """Starts controller, pystray icon, and UI event loop."""
        self._setup_gui()
        self.controller.start()

        if self.icon:
            # On Linux/AppIndicator, run in a dedicated thread to drive GLib.MainLoop
            # so that D-Bus registration and GObject idle callbacks render on the taskbar.
            import threading
            threading.Thread(target=self.icon.run, daemon=True).start()

        if self.root:
            try:
                self.root.mainloop()
            except KeyboardInterrupt:
                self.stop()
        else:
            try:
                import time
                while getattr(self.controller, "is_running", True):
                    self._poll_queue()
                    time.sleep(0.05)
            except KeyboardInterrupt:
                self.stop()

    def stop(self) -> None:
        """Stops all GUI and controller components gracefully."""
        self.controller.stop()
        if self.icon:
            try:
                self.icon.stop()
            except Exception:
                pass
        if self.root:
            try:
                self.root.destroy()
            except Exception:
                pass


# ==============================================================================
# Helper / Runner
# ==============================================================================

def run_tray_ui(ipc_client: Any, force_fallback: bool = False, ui_notifier: Any = None) -> TrayAppController:
    """
    Launches Tray UI with automatic headless detection and fallback.
    """
    if force_fallback or not is_gui_available():
        logger.info("Initializing TrayAppController with headless console visualizer fallback.")
        from src.tray.main import default_ui_display
        controller = TrayAppController(
            ipc_client=ipc_client,
            ui_notifier=ui_notifier or default_ui_display,
        )
        controller.start()
        return controller

    logger.info("Initializing TrayAppController with Native Desktop GUI Presenter.")
    presenter = TrayUIPresenter(ipc_client=ipc_client)
    presenter.start()
    return presenter.controller
