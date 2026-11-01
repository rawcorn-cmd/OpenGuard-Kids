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
from src.tray.dialogs import NotificationModel

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
        req_fn = getattr(controller, "request_extra_time", None)
        if callable(req_fn):
            req_fn(15, reason="Yêu cầu thêm từ khay hệ thống")

    def _on_report_unblock(icon: Any, item: Any) -> None:
        unblock_fn = getattr(controller, "report_unblock_domain", None)
        if callable(unblock_fn):
            unblock_fn("example.edu.vn", reason="Báo chặn nhầm từ khay hệ thống")

    def _on_transparency(icon: Any, item: Any) -> None:
        trans_fn = getattr(controller, "get_transparency_info", None)
        if callable(trans_fn):
            trans_fn()

    menu_items = [
        pystray.MenuItem(_get_time_text, lambda icon, item: None, enabled=False),
        pystray.MenuItem(_get_status_text, lambda icon, item: None, enabled=False),
        pystray.MenuItem("✨ Xin thêm 15 phút...", _on_request_time),
        pystray.MenuItem("🛡️ Báo chặn nhầm trang web...", _on_report_unblock),
        pystray.MenuItem("📖 Hôm nay em đã dùng gì", _on_transparency),
        pystray.MenuItem("ℹ️ Quyền trẻ em & Hotline 111", lambda icon, item: None),
    ]

    return menu_items


# ==============================================================================
# Real-Time Escalating Toast Notifications (F1.4)
# ==============================================================================

class ToastNotificationManager:
    """
    Manages non-modal escalating warning toasts:
    - 10m: 6s auto-dismiss
    - 5m: 8s auto-dismiss
    - 1m: 10s auto-dismiss (+ sound alert on Windows)
    """

    def __init__(self, root: Any = None):
        self.root = root
        self.active_toast_duration = 0
        self.current_toast = None

    def show_toast(self, level: str, message: str, title: str = "") -> None:
        if level == "10M":
            duration = 6000
        elif level == "5M":
            duration = 8000
        elif level == "1M":
            duration = 10000
            if sys.platform == "win32":
                try:
                    import winsound
                    winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
                except Exception:
                    pass
        else:
            duration = 5000

        self.active_toast_duration = duration

        if self.root is not None and hasattr(self.root, "after"):
            try:
                self.dismiss_toast()
                if HAS_TKINTER and hasattr(self.root, "winfo_screenwidth"):
                    toast = tk.Toplevel(self.root)
                    self.current_toast = toast
                    toast.overrideredirect(True)
                    toast.wm_attributes("-topmost", True)

                    sw = toast.winfo_screenwidth()
                    sh = toast.winfo_screenheight()
                    w, h = 380, 100
                    x = sw - w - 20
                    y = sh - h - 50
                    toast.geometry(f"{w}x{h}+{x}+{y}")

                    border_color = (
                        "#0284c7" if level == "10M" else (
                            "#f59e0b" if level == "5M" else "#ea580c"
                        )
                    )
                    frame = tk.Frame(toast, bg="#1e293b", highlightbackground=border_color, highlightthickness=2)
                    frame.pack(fill="both", expand=True)

                    lbl_title = tk.Label(
                        frame,
                        text=title or f"OpenGuard Kids — Cảnh báo {level}",
                        fg="#ffffff",
                        bg="#1e293b",
                        font=("Arial", 10, "bold"),
                    )
                    lbl_title.pack(anchor="w", padx=10, pady=(8, 2))

                    lbl_msg = tk.Label(
                        frame,
                        text=message,
                        fg="#cbd5e1",
                        bg="#1e293b",
                        font=("Arial", 9),
                        wraplength=350,
                        justify="left",
                    )
                    lbl_msg.pack(anchor="w", padx=10, pady=(0, 8))

                self.root.after(duration, self.dismiss_toast)
            except Exception as e:
                logger.debug("Toast display bypassed: %s", e)

    def dismiss_toast(self) -> None:
        if self.current_toast is not None:
            try:
                self.current_toast.destroy()
            except Exception:
                pass
            self.current_toast = None


# ==============================================================================
# 60-Second Grace Period Dialog (NT3, NT4, Non-Focus-Stealing WS_EX_NOACTIVATE)
# ==============================================================================

class GracePeriodDialog:
    """
    60-second grace dialog allowing child to save Word/PowerPoint documents safely.
    Configured with Win32 WS_EX_NOACTIVATE and WS_EX_TOPMOST.
    Crucially: strictly NO grab_set() and NO focus_force() so keystrokes (Ctrl+S)
    are delivered directly to the active application.
    """

    def __init__(self, parent: Any, controller: Any):
        self.parent = parent
        self.controller = controller
        self.seconds_left = 60

    def setup_ui(self) -> None:
        # Win32 non-focus-stealing integration
        if sys.platform == "win32":
            try:
                import ctypes
                GWL_EXSTYLE = -20
                WS_EX_NOACTIVATE = 0x08000000
                WS_EX_TOPMOST = 0x00000008
                hwnd = 0
                if hasattr(self.parent, "winfo_id"):
                    hwnd = ctypes.windll.user32.GetParent(self.parent.winfo_id()) or self.parent.winfo_id()
                if hwnd:
                    style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
                    ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style | WS_EX_NOACTIVATE | WS_EX_TOPMOST)
            except Exception as e:
                logger.warning("Could not set WS_EX_NOACTIVATE: %s", e)

        # Strictly DO NOT call grab_set() or focus_force()!
        try:
            if hasattr(self.parent, "wm_attributes"):
                self.parent.wm_attributes("-topmost", True)
            if hasattr(self.parent, "title"):
                self.parent.title("Thời gian đã hết — 60 Giây Ân Hạn")
        except Exception:
            pass

    def on_lock_now_clicked(self) -> None:
        """Voluntary immediate lock by child ('Em đã lưu xong bài, Khóa ngay')."""
        if hasattr(self.controller, "_handle_lock"):
            self.controller._handle_lock("LOCKED_QUOTA")
        elif hasattr(self.controller, "on_lock"):
            self.controller.on_lock("LOCKED_QUOTA")
        if self.parent and hasattr(self.parent, "destroy"):
            try:
                self.parent.destroy()
            except Exception:
                pass

    def on_request_time_clicked(self) -> None:
        """Child requests extra 15 minutes extension."""
        if hasattr(self.controller, "request_extra_time"):
            self.controller.request_extra_time(15, reason="Yêu cầu từ hộp thoại ân hạn")


# ==============================================================================
# Fullscreen Lock Overlay (NT6 Topmost, Intercepts Alt+F4 / Esc, Hotline 111)
# ==============================================================================

class FullscreenLockOverlay:
    """
    Borderless topmost fullscreen lock overlay covering the entire display resolution.
    Captures focus (grab_set), intercepts Alt+F4 / Esc, displays transparent reason,
    National Child Protection Hotline 111, and child extension request button.
    """

    def __init__(self, parent: Any, controller: Any):
        self.parent = parent
        self.controller = controller

    def show(self, reason: str = "Hết hạn mức thời gian") -> None:
        if hasattr(self.parent, "overrideredirect"):
            self.parent.overrideredirect(True)
        if hasattr(self.parent, "wm_attributes"):
            self.parent.wm_attributes("-topmost", True)
        if hasattr(self.parent, "grab_set"):
            self.parent.grab_set()

        # Intercept window close hotkeys
        if hasattr(self.parent, "bind"):
            self.parent.bind("<Alt-F4>", lambda e: "break")
            self.parent.bind("<Alt-KeyPress-F4>", lambda e: "break")
            self.parent.bind("<Escape>", lambda e: "break")
            self.parent.bind("<Control-w>", lambda e: "break")
            self.parent.bind("<Control-q>", lambda e: "break")

    def on_request_time_clicked(self) -> None:
        """Sends extra time request directly from lock screen."""
        if hasattr(self.controller, "request_extra_time"):
            self.controller.request_extra_time(15, reason="Yêu cầu từ màn hình khóa")

    def hide(self) -> None:
        if hasattr(self.parent, "grab_release"):
            try:
                self.parent.grab_release()
            except Exception:
                pass
        if hasattr(self.parent, "withdraw"):
            try:
                self.parent.withdraw()
            except Exception:
                pass


# ==============================================================================
# Data Transparency Window ("Hôm nay em đã dùng gì" — NT5)
# ==============================================================================

class TransparencyDialog:
    """
    Two-Way Transparency Window (NT5) presenting 1:1 reflection of data seen
    by parents, plus 4 child rights and National Hotline 111.
    """

    def __init__(self, parent: Any, controller: Any):
        self.parent = parent
        self.controller = controller

    def load_data(self) -> Dict[str, Any]:
        """Loads transparency data from controller."""
        if hasattr(self.controller, "get_transparency_info"):
            return self.controller.get_transparency_info()
        return {}


# ==============================================================================
# Presenter & Thread Marshaling
# ==============================================================================

class TrayUIPresenter:
    """
    Model-View-Presenter (MVP) coordinator for Native Desktop GUI.
    Marshals background events from OGK-Tray-Listener to the Tkinter main thread
    using a thread-safe Queue drained by root.after(50, ...).
    """

    def __init__(self, ipc_client: Any):
        self.ipc_client = ipc_client
        self.event_queue: queue.Queue = queue.Queue()
        self.root: Optional[Any] = None
        self.icon: Optional[Any] = None
        self.toast_mgr: Optional[ToastNotificationManager] = None
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
        """Initializes Tkinter root and Pystray system tray icon."""
        if not HAS_TKINTER:
            return

        self.root = tk.Tk()
        self.root.withdraw()

        self.toast_mgr = ToastNotificationManager(root=self.root)

        # Initialize Pystray Icon
        initial_img = create_tray_icon_image(remaining_seconds=3600.0)
        menu_items = build_context_menu(self.controller)
        self.icon = pystray.Icon(
            "OpenGuardKids",
            icon=initial_img,
            title="OpenGuard Kids",
            menu=pystray.Menu(*menu_items),
        )

        # Schedule queue polling on main thread
        self.root.after(50, self._poll_queue)

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

        elif event_type == "WARNING_TOAST":
            level = data.get("level", "10M")
            msg = data.get("message", "")
            title = data.get("title", "")
            if self.toast_mgr:
                self.toast_mgr.show_toast(level=level, message=msg, title=title)

        elif event_type in ("GRACE_PERIOD", "GRACE_PERIOD_DIALOG"):
            if self.root:
                dlg_win = tk.Toplevel(self.root)
                self.grace_dialog = GracePeriodDialog(parent=dlg_win, controller=self.controller)
                self.grace_dialog.setup_ui()

        elif event_type in ("LOCK_SCREEN", "LOCK_OVERLAY"):
            if self.root:
                overlay_win = tk.Toplevel(self.root)
                self.lock_overlay = FullscreenLockOverlay(parent=overlay_win, controller=self.controller)
                self.lock_overlay.show(reason=data.get("reason", "Hết hạn mức thời gian"))

        elif event_type in ("UNLOCK", "UNLOCK_SCREEN"):
            if self.lock_overlay:
                self.lock_overlay.hide()

        elif event_type == "BONUS_TIME_ADDED":
            if self.toast_mgr:
                self.toast_mgr.show_toast(level="INFO", message=data.get("message", ""), title=data.get("title", "Cộng Thêm Giờ"))

        elif event_type in ("LOST_CONNECTION", "LOST_CONNECTION_ALERT"):
            new_img = create_tray_icon_image(connection_lost=True)
            if self.icon:
                self.icon.icon = new_img
            if self.toast_mgr:
                self.toast_mgr.show_toast(level="1M", message=data.get("message", ""), title=data.get("title", "Mất kết nối"))

    def start(self) -> None:
        """Starts controller, pystray icon, and Tkinter main loop."""
        self._setup_gui()
        self.controller.start()

        if self.icon:
            self.icon.run_detached()

        if self.root:
            try:
                self.root.mainloop()
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
