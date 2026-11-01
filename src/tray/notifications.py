"""
OpenGuard Kids — Cross-Platform Toast Notification Dispatcher
Supports:
  - Linux Mint / Cinnamon: Native desktop notifications via /usr/bin/notify-send
  - Windows 10/11: Native toast notifications, balloon alerts, and winsound audio cues
  - Universal Desktop: Tkinter Toplevel borderless toast window fallback
  - System Tray: Pystray Icon.notify fallback
  - Terminal & Logging: Trace logging for headless / debug sessions
"""

from __future__ import annotations

import logging
import os
import shutil
import subprocess
import sys
from typing import Any, Optional

logger = logging.getLogger("OGK.Notifications")

# Check Tkinter availability safely
try:
    import tkinter as tk
    HAS_TKINTER = True
except (ImportError, ModuleNotFoundError):
    tk = None  # type: ignore
    HAS_TKINTER = False


class CrossPlatformNotifier:
    """
    Cross-platform desktop toast notification dispatcher.
    Ensures visual notifications are displayed on Linux Mint evaluation host
    and target Windows 10/11 environments.
    """

    def __init__(self, root: Optional[Any] = None, icon: Optional[Any] = None):
        self.root = root
        self.icon = icon
        self.active_toast_duration: int = 0
        self.current_toast: Optional[Any] = None
        self.notify_send_bin: Optional[str] = shutil.which("notify-send") if sys.platform.startswith("linux") else None
        self._last_notif_time: dict[str, float] = {}

    def show_toast(
        self,
        level: str,
        message: str,
        title: str = "",
        duration_ms: Optional[int] = None,
    ) -> None:
        """
        Dispatches a visual notification according to platform capabilities.
        Durations:
          - 10M warning: 6000ms
          - 5M warning:  8000ms
          - 1M warning: 10000ms (+ Windows sound)
          - Locked / Critical: 10000ms
          - Default / Info: 5000ms
        """
        if duration_ms is not None:
            duration = duration_ms
        elif level == "10M":
            duration = 6000
        elif level == "5M":
            duration = 8000
        elif level in ("1M", "CRITICAL", "LOCKED", "LOST_CONNECTION"):
            duration = 10000
        else:
            duration = 5000

        self.active_toast_duration = duration
        disp_title = title or f"OpenGuard Kids — Cảnh báo {level}"

        # 1. Windows Sound Alert (1M, CRITICAL, LOCKED)
        if sys.platform == "win32" and level in ("1M", "CRITICAL", "LOCKED"):
            try:
                import winsound
                winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
            except Exception as e:
                logger.debug("winsound.MessageBeep skipped: %s", e)

        # 2. Linux Mint Native Desktop Notification via notify-send
        is_suppressed = bool(os.environ.get("OGK_SUPPRESS_NOTIFICATIONS"))
        if sys.platform.startswith("linux") and self.notify_send_bin and not is_suppressed:
            import time
            now = time.time()
            dedup_key = f"{level}:{message}"
            if now - self._last_notif_time.get(dedup_key, 0.0) < 3.0:
                logger.debug("Throttled duplicate notify-send alert: %s", disp_title)
                return
            self._last_notif_time[dedup_key] = now

            urgency = "critical" if level in ("1M", "CRITICAL", "LOCKED") else "normal"
            cmd = [
                self.notify_send_bin,
                "-u", urgency,
                "-t", str(duration),
                "-a", "OpenGuard Kids",
                "-h", "string:synchronous:openguard",
                disp_title,
                message,
            ]
            try:
                subprocess.Popen(
                    cmd,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                logger.debug("Dispatched notify-send alert: %s", disp_title)
            except Exception as e:
                logger.warning("notify-send execution failed: %s", e)

        # 3. Windows Native Toast / Balloon Notification
        if sys.platform == "win32":
            self._dispatch_windows_native_toast(disp_title, message, duration)

        # 4. Pystray Icon Notification Fallback
        if self.icon is not None and hasattr(self.icon, "notify") and callable(self.icon.notify):
            try:
                self.icon.notify(message, disp_title)
            except Exception as e:
                logger.debug("pystray.Icon.notify skipped: %s", e)

        # 5. Tkinter In-App Toast Window Fallback
        if self.root is not None:
            self.dismiss_toast()
            if HAS_TKINTER and hasattr(self.root, "winfo_screenwidth") and tk is not None:
                try:
                    toast = tk.Toplevel(self.root)
                    self.current_toast = toast
                    toast.overrideredirect(True)
                    toast.wm_attributes("-topmost", True)

                    # Win32 non-focus-stealing style
                    if sys.platform == "win32":
                        try:
                            import ctypes
                            hwnd = ctypes.windll.user32.GetParent(toast.winfo_id()) or toast.winfo_id()
                            if hwnd:
                                style = ctypes.windll.user32.GetWindowLongW(hwnd, -20)
                                ctypes.windll.user32.SetWindowLongW(hwnd, -20, style | 0x08000000 | 0x00000008)
                        except Exception:
                            pass

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
                        text=disp_title,
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
                except Exception as e:
                    logger.debug("Tkinter toast window creation failed: %s", e)

            # Schedule auto-dismiss callback on the event loop
            if hasattr(self.root, "after"):
                self.root.after(duration, self.dismiss_toast)

        # 6. Secondary Debug Trace
        logger.info("[TOAST] [%s] %s: %s", level, disp_title, message)

    def _dispatch_windows_native_toast(self, title: str, message: str, duration_ms: int) -> None:
        """Attempts native Windows toast notification using win10toast or Win32 API if available."""
        try:
            from win10toast import ToastNotifier
            toaster = ToastNotifier()
            toaster.show_toast(title, message, duration=max(1, duration_ms // 1000), threaded=True)
            return
        except (ImportError, Exception):
            pass

        # Native balloon notification via pystray is handled in step 4.

    def dismiss_toast(self) -> None:
        """Dismisses the active Tkinter toast window if currently displayed."""
        if self.current_toast is not None:
            try:
                self.current_toast.destroy()
            except Exception:
                pass
            self.current_toast = None
