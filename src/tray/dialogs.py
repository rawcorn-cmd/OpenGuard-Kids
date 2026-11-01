"""
OpenGuard Kids — Tray UI Dialogs & User Notifications
Provides:
  - Polite Warning Toasts (10m, 5m, 1m) models
  - 60s Grace Period Dialog (NT3, NT4) with digital countdown & save work safeguard
  - Fullscreen Lock Screen Overlay (NT6) with Hotline 111 banner & Alt+F4 interception
  - Child Agency Interactive Request Dialogs (NT4: +15m extension, domain unblock)
  - Data Transparency Window (NT5: "Hôm nay em đã dùng gì")
  - Native Linux Mint Zenity Visual Fallbacks for environments lacking Tkinter
"""

from __future__ import annotations

import logging
import os
import shutil
import subprocess
import sys
import threading
from typing import Any, Callable, Dict, Optional

logger = logging.getLogger("OGK.TrayDialogs")

# Safe Tkinter import
try:
    import tkinter as tk
    from tkinter import ttk
    HAS_TKINTER = True
except (ImportError, ModuleNotFoundError):
    tk = None  # type: ignore
    ttk = None  # type: ignore
    HAS_TKINTER = False


class NotificationModel:
    """
    Decoupled model representing toast notifications and modal dialogs.
    Can be rendered via Tkinter or verified deterministically in automated tests.
    """

    @staticmethod
    def format_warning_message(level: str, remaining_seconds: float) -> Dict[str, str]:
        minutes = int(remaining_seconds // 60)
        if level == "10M":
            return {
                "title": "Cảnh báo thời gian sử dụng — Còn 10 phút",
                "message": f"Bạn còn khoảng {minutes} phút trước khi máy tính tạm khóa. Hãy chuẩn bị hoàn thành bài học nhé!",
                "level": "INFO",
            }
        elif level == "5M":
            return {
                "title": "Cảnh báo thời gian sử dụng — Còn 5 phút",
                "message": "Chỉ còn 5 phút! Hãy lưu lại bài tập hoặc xin thêm giờ nếu cần nhé.",
                "level": "WARNING",
            }
        elif level == "1M":
            return {
                "title": "Cảnh báo thời gian sử dụng — Còn 1 phút",
                "message": "Chỉ còn 1 phút! Hệ thống sẽ kích hoạt 60 giây ân hạn để bạn lưu tài liệu.",
                "level": "CRITICAL",
            }
        return {
            "title": "Thông báo OpenGuard Kids",
            "message": f"Thời gian còn lại: {minutes} phút.",
            "level": "INFO",
        }

    @staticmethod
    def format_grace_period_message() -> Dict[str, str]:
        return {
            "title": "Thời gian đã hết — 60 Giây Ân Hạn",
            "message": "Đã hết thời gian cho phép hôm nay! Bạn có 60 giây để lưu lại bài tập Word, PowerPoint trước khi màn hình khóa.",
            "action": "SAVE_AND_CLOSE",
        }

    @staticmethod
    def format_lock_screen_info(lock_reason: str) -> Dict[str, Any]:
        reason_text = "Hết hạn ngạch thời gian trong ngày"
        if "SCHEDULE" in lock_reason:
            reason_text = "Đang trong khung giờ nghỉ ngơi / giới nghiêm ban đêm"
        elif "URGENT" in lock_reason:
            reason_text = "Khóa tức thời theo yêu cầu từ Phụ huynh"

        return {
            "title": "Máy tính Đang Tạm Khóa",
            "reason": reason_text,
            "instruction": "Bạn có thể bấm 'Xin thêm 15 phút' để gửi thông báo cho Cha/Mẹ.",
            "hotline": "Tổng đài Quốc gia Bảo vệ Trẻ em: 111 (miễn phí 24/7)",
            "allow_request": True,
        }

    @staticmethod
    def format_transparency_info(policy: Dict[str, Any]) -> Dict[str, Any]:
        """Implements NT5: Child Transparency Screen."""
        return {
            "title": "Quy Tắc Sử Dụng Máy Tính Của Bạn (OpenGuard Kids)",
            "daily_quota_minutes": policy.get("daily_quota_minutes", 120),
            "bed_time": f"{policy.get('bed_time_start', '22:00')} - {policy.get('bed_time_end', '06:00')}",
            "safesearch_enforced": True,
            "study_mode": policy.get("study_mode", False),
            "child_rights": [
                "Được cảnh báo trước 10 phút, 5 phút và 1 phút trước khi hết giờ.",
                "Có 60 giây ân hạn để lưu tài liệu bài tập, không bị tắt máy đột ngột.",
                "Được quyền gửi yêu cầu xin thêm giờ và báo chặn nhầm trang web học tập.",
                "Không bị chụp trộm màn hình hay ghi phím bấm bí mật (Bảo vệ quyền riêng tư).",
            ],
            "hotline": "111 - Cục Trẻ em",
        }


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
        self.seconds_left: int = 60
        self.lbl_countdown: Optional[Any] = None

    def setup_ui(self) -> None:
        """Configures dialog styles and renders visual widgets if Tkinter is available."""
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

        # Build visual Tkinter widgets if parent is a live GUI window
        if HAS_TKINTER and tk is not None and hasattr(self.parent, "winfo_screenwidth"):
            try:
                sw = self.parent.winfo_screenwidth()
                sh = self.parent.winfo_screenheight()
                w, h = 480, 240
                self.parent.geometry(f"{w}x{h}+{(sw - w) // 2}+{(sh - h) // 2}")
                self.parent.configure(bg="#0f172a")

                # Main container
                frame = tk.Frame(self.parent, bg="#1e293b", padx=20, pady=16, highlightbackground="#ea580c", highlightthickness=2)
                frame.pack(fill="both", expand=True, padx=10, pady=10)

                lbl_header = tk.Label(
                    frame,
                    text="⏳ ĐÃ HẾT THỜI GIAN SỬ DỤNG HÔM NAY",
                    fg="#f97316",
                    bg="#1e293b",
                    font=("Arial", 12, "bold"),
                )
                lbl_header.pack(anchor="center", pady=(0, 6))

                lbl_sub = tk.Label(
                    frame,
                    text="Bạn có 60 giây để lưu lại tài liệu Word, PowerPoint trước khi máy khóa.",
                    fg="#cbd5e1",
                    bg="#1e293b",
                    font=("Arial", 9),
                    wraplength=420,
                    justify="center",
                )
                lbl_sub.pack(anchor="center", pady=(0, 8))

                self.lbl_countdown = tk.Label(
                    frame,
                    text=f"Còn lại {self.seconds_left}s...",
                    fg="#facc15",
                    bg="#1e293b",
                    font=("Arial", 16, "bold"),
                )
                self.lbl_countdown.pack(anchor="center", pady=(0, 12))

                btn_frame = tk.Frame(frame, bg="#1e293b")
                btn_frame.pack(fill="x", pady=(4, 0))

                btn_lock = tk.Button(
                    btn_frame,
                    text="Em đã lưu xong bài, Khóa ngay",
                    bg="#334155",
                    fg="#f1f5f9",
                    activebackground="#475569",
                    activeforeground="#ffffff",
                    font=("Arial", 9, "bold"),
                    command=self.on_lock_now_clicked,
                    padx=8,
                    pady=4,
                )
                btn_lock.pack(side="left", padx=(0, 8), expand=True, fill="x")

                btn_extra = tk.Button(
                    btn_frame,
                    text="✨ Xin thêm 15 phút",
                    bg="#ea580c",
                    fg="#ffffff",
                    activebackground="#c2410c",
                    activeforeground="#ffffff",
                    font=("Arial", 9, "bold"),
                    command=self.on_request_time_clicked,
                    padx=8,
                    pady=4,
                )
                btn_extra.pack(side="right", padx=(8, 0), expand=True, fill="x")

            except Exception as e:
                logger.debug("Grace period visual widget construction bypassed: %s", e)

        # Start countdown ticking if parent supports after()
        if hasattr(self.parent, "after"):
            try:
                self.parent.after(1000, self._tick)
            except Exception:
                pass

    def _tick(self) -> None:
        """Countdown tick handler decrementing every second."""
        self.seconds_left -= 1
        if self.lbl_countdown is not None and hasattr(self.lbl_countdown, "config"):
            try:
                self.lbl_countdown.config(text=f"Còn lại {self.seconds_left}s...")
            except Exception:
                pass

        if self.seconds_left <= 0:
            self.on_lock_now_clicked()
        elif hasattr(self.parent, "after"):
            try:
                self.parent.after(1000, self._tick)
            except Exception:
                pass

    def on_lock_now_clicked(self) -> None:
        """Voluntary immediate lock by child ('Em đã lưu xong bài, Khóa ngay')."""
        if hasattr(self.controller, "_handle_lock"):
            self.controller._handle_lock("LOCKED_QUOTA")
        elif hasattr(self.controller, "lock_now"):
            self.controller.lock_now()
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

        if self.parent and hasattr(self.parent, "destroy"):
            try:
                self.parent.destroy()
            except Exception:
                pass


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

        # Build visual overlay if Tkinter is available
        if HAS_TKINTER and tk is not None and hasattr(self.parent, "winfo_screenwidth"):
            try:
                sw = self.parent.winfo_screenwidth()
                sh = self.parent.winfo_screenheight()
                self.parent.geometry(f"{sw}x{sh}+0+0")
                self.parent.configure(bg="#090d16")

                container = tk.Frame(self.parent, bg="#0f172a", padx=32, pady=28, highlightbackground="#dc2626", highlightthickness=2)
                container.place(relx=0.5, rely=0.5, anchor="center")

                lbl_icon = tk.Label(container, text="🔒", fg="#ef4444", bg="#0f172a", font=("Arial", 42))
                lbl_icon.pack(pady=(0, 8))

                lbl_title = tk.Label(container, text="MÁY TÍNH ĐANG TẠM KHÓA", fg="#ffffff", bg="#0f172a", font=("Arial", 18, "bold"))
                lbl_title.pack(pady=(0, 6))

                lbl_reason = tk.Label(container, text=f"Lý do: {reason}", fg="#f87171", bg="#0f172a", font=("Arial", 11), wraplength=420)
                lbl_reason.pack(pady=(0, 14))

                lbl_hotline = tk.Label(
                    container,
                    text="Tổng đài Quốc gia Bảo vệ Trẻ em: 111 (miễn phí 24/7)",
                    fg="#94a3b8",
                    bg="#0f172a",
                    font=("Arial", 10),
                )
                lbl_hotline.pack(pady=(0, 16))

                btn_req = tk.Button(
                    container,
                    text="✨ Xin thêm 15 phút học tập",
                    bg="#0284c7",
                    fg="#ffffff",
                    activebackground="#0369a1",
                    activeforeground="#ffffff",
                    font=("Arial", 10, "bold"),
                    command=self.on_request_time_clicked,
                    padx=16,
                    pady=6,
                )
                btn_req.pack()
            except Exception as e:
                logger.debug("Lock overlay visual layout skipped: %s", e)

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
# Native Linux Mint Zenity & Cross-Platform Interactive Dialogs
# ==============================================================================

def show_grace_period_zenity(controller: Any) -> None:
    """
    Spawns a Zenity 60-second grace dialog on Linux Mint in a worker thread.
    Exit codes:
      - 0: OK button ("Xin thêm 15 phút")
      - 1: Cancel button ("Khóa ngay")
      - 5: Timeout (60s expired -> auto lock)
    """
    def _worker():
        zenity_bin = shutil.which("zenity") if sys.platform.startswith("linux") else None
        if not zenity_bin:
            logger.info("Zenity not found, skipping visual dialog.")
            return

        cmd = [
            zenity_bin,
            "--question",
            "--title=OpenGuard Kids - 60 Giây Ân Hạn",
            "--text=Đã hết thời gian cho phép hôm nay!\nBạn có 60 giây để lưu lại tài liệu Word, PowerPoint.\n\nChọn 'Xin thêm 15 phút' để xin phụ huynh duyệt, hoặc 'Khóa ngay'.",
            "--ok-label=Xin thêm 15 phút",
            "--cancel-label=Khóa ngay",
            "--timeout=60",
            "--width=440",
        ]
        try:
            proc = subprocess.run(cmd)
            if proc.returncode == 0:
                if hasattr(controller, "request_extra_time"):
                    controller.request_extra_time(15, reason="Yêu cầu từ hộp thoại ân hạn Zenity")
            elif proc.returncode in (1, 5):
                if hasattr(controller, "_handle_lock"):
                    controller._handle_lock("LOCKED_QUOTA")
                elif hasattr(controller, "lock_now"):
                    controller.lock_now()
        except Exception as e:
            logger.warning("Zenity grace dialog failed: %s", e)

    threading.Thread(target=_worker, daemon=True).start()


def show_lock_zenity(controller: Any, reason: str = "Hết hạn mức thời gian") -> None:
    """Spawns a Zenity warning alert when computer is locked on Linux Mint."""
    def _worker():
        zenity_bin = shutil.which("zenity") if sys.platform.startswith("linux") else None
        if not zenity_bin:
            return

        cmd = [
            zenity_bin,
            "--warning",
            "--title=OpenGuard Kids - MÁY TÍNH ĐANG TẠM KHÓA",
            "--text=🔒 MÁY TÍNH ĐANG TẠM KHÓA\n\n"
                    f"Lý do: {reason}\n\n"
                    "Tổng đài Quốc gia Bảo vệ Trẻ em: 111 (miễn phí 24/7)\n\n"
                    "Bấm 'Xin thêm 15 phút' nếu muốn gửi yêu cầu cho Cha/Mẹ.",
            "--ok-label=Xin thêm 15 phút",
            "--width=450",
        ]
        try:
            proc = subprocess.run(cmd)
            if proc.returncode == 0:
                if hasattr(controller, "request_extra_time"):
                    controller.request_extra_time(15, reason="Yêu cầu từ màn hình khóa Zenity")
        except Exception as e:
            logger.warning("Zenity lock dialog failed: %s", e)

    threading.Thread(target=_worker, daemon=True).start()


def prompt_extra_time_dialog(parent: Any = None, controller: Any = None) -> None:
    """
    Prompts child for an educational reason before dispatching a 15-minute extension request.
    Uses Zenity --entry on Linux Mint and Tkinter Entry dialog on Windows.
    """
    def _worker():
        zenity_bin = shutil.which("zenity") if sys.platform.startswith("linux") else None
        if sys.platform.startswith("linux") and zenity_bin and (parent is None or not HAS_TKINTER):
            cmd = [
                zenity_bin,
                "--entry",
                "--title=OpenGuard Kids — Xin thêm giờ học tập",
                "--text=Nhập lý do xin thêm 15 phút học tập:",
                "--entry-text=Em cần hoàn thành bài tập",
                "--ok-label=Gửi yêu cầu",
                "--cancel-label=Hủy",
                "--width=400",
            ]
            try:
                proc = subprocess.run(cmd, stdout=subprocess.PIPE, text=True)
                if proc.returncode == 0:
                    reason = proc.stdout.strip() or "Em cần hoàn thành bài tập"
                    if controller and hasattr(controller, "request_extra_time"):
                        controller.request_extra_time(15, reason=reason)
            except Exception as e:
                logger.warning("Zenity prompt extra time error: %s", e)
            return

        # Tkinter modal prompt if Tkinter available
        if HAS_TKINTER and tk is not None:
            _show_tkinter_extra_time_prompt(parent, controller)
            return

        # Fallback default dispatch
        if controller and hasattr(controller, "request_extra_time"):
            controller.request_extra_time(15, reason="Yêu cầu thêm từ khay hệ thống")

    threading.Thread(target=_worker, daemon=True).start()


def prompt_unblock_domain_dialog(parent: Any = None, controller: Any = None) -> None:
    """
    Prompts child for domain name and educational reason before dispatching unblock request.
    Uses Zenity --forms on Linux Mint and Tkinter dialog on Windows.
    """
    def _worker():
        zenity_bin = shutil.which("zenity") if sys.platform.startswith("linux") else None
        if sys.platform.startswith("linux") and zenity_bin and (parent is None or not HAS_TKINTER):
            cmd = [
                zenity_bin,
                "--forms",
                "--title=OpenGuard Kids — Báo chặn nhầm trang web",
                "--text=Điền thông tin trang web cần báo mở:",
                "--add-entry=Tên miền (ví dụ: hocmai.vn):",
                "--add-entry=Lý do cần mở trang web:",
                "--ok-label=Gửi yêu cầu",
                "--cancel-label=Hủy",
                "--width=450",
            ]
            try:
                proc = subprocess.run(cmd, stdout=subprocess.PIPE, text=True)
                if proc.returncode == 0:
                    parts = proc.stdout.strip().split("|")
                    domain = parts[0].strip() if len(parts) > 0 and parts[0].strip() else "hocmai.vn"
                    reason = parts[1].strip() if len(parts) > 1 and parts[1].strip() else "Trang web học tập"
                    if controller and hasattr(controller, "report_unblock_domain"):
                        controller.report_unblock_domain(domain, reason=reason)
            except Exception as e:
                logger.warning("Zenity prompt unblock domain error: %s", e)
            return

        # Tkinter modal prompt if Tkinter available
        if HAS_TKINTER and tk is not None:
            _show_tkinter_unblock_prompt(parent, controller)
            return

        # Fallback default dispatch
        if controller and hasattr(controller, "report_unblock_domain"):
            controller.report_unblock_domain("example.edu.vn", reason="Báo chặn nhầm từ khay hệ thống")

    threading.Thread(target=_worker, daemon=True).start()


def show_transparency_dialog(parent: Any = None, controller: Any = None) -> None:
    """
    Displays the Two-Way Transparency Window (NT5) reflecting parent policies and child rights.
    Uses Zenity --info on Linux Mint and Tkinter window on Windows.
    """
    info = {}
    if controller and hasattr(controller, "get_transparency_info"):
        info = controller.get_transparency_info()

    def _worker():
        zenity_bin = shutil.which("zenity") if sys.platform.startswith("linux") else None
        if sys.platform.startswith("linux") and zenity_bin and (parent is None or not HAS_TKINTER):
            quota = info.get("daily_quota_minutes", 120)
            bedtime = info.get("bed_time", "22:00 - 06:00")
            rights = "\n".join(f"• {r}" for r in info.get("child_rights", []))
            hotline = info.get("hotline", "111 - Cục Trẻ em")
            text = (
                f"QUY TẮC SỬ DỤNG MÁY TÍNH CỦA BẠN (OPENGUARD KIDS)\n\n"
                f"• Hạn mức sử dụng hàng ngày: {quota} phút\n"
                f"• Giờ nghỉ ngơi (Bedtime): {bedtime}\n"
                f"• SafeSearch: Đang bật bảo vệ an toàn\n\n"
                f"4 QUYỀN LỢI CỦA TRẺ EM (NGUYÊN TẮC NT5):\n{rights}\n\n"
                f"ĐƯỜNG DÂY NÓNG TRẺ EM:\n{hotline} (Miễn phí 24/7)"
            )
            cmd = [
                zenity_bin,
                "--info",
                "--title=OpenGuard Kids — Hôm nay em đã dùng gì",
                f"--text={text}",
                "--width=480",
            ]
            try:
                subprocess.run(cmd)
            except Exception as e:
                logger.warning("Zenity transparency dialog error: %s", e)
            return

        if HAS_TKINTER and tk is not None:
            _show_tkinter_transparency(parent, info)

    threading.Thread(target=_worker, daemon=True).start()


def _show_tkinter_extra_time_prompt(parent: Any, controller: Any) -> None:
    """Renders a Tkinter popup dialog for requesting extra time."""
    try:
        top = tk.Toplevel(parent) if parent else tk.Tk()
        top.title("Xin thêm 15 phút học tập")
        top.geometry("380x160")
        top.configure(bg="#1e293b")

        tk.Label(top, text="Nhập lý do xin thêm thời gian:", fg="#ffffff", bg="#1e293b", font=("Arial", 10, "bold")).pack(pady=(12, 6), padx=12, anchor="w")
        ent = tk.Entry(top, font=("Arial", 10), width=36)
        ent.insert(0, "Em cần hoàn thành bài tập")
        ent.pack(pady=4, padx=12)

        def _send():
            reason = ent.get().strip() or "Em cần hoàn thành bài tập"
            if controller and hasattr(controller, "request_extra_time"):
                controller.request_extra_time(15, reason=reason)
            top.destroy()

        btn_box = tk.Frame(top, bg="#1e293b")
        btn_box.pack(pady=12, padx=12, fill="x")
        tk.Button(btn_box, text="Hủy", command=top.destroy, bg="#475569", fg="#ffffff").pack(side="right", padx=(8, 0))
        tk.Button(btn_box, text="Gửi yêu cầu", command=_send, bg="#0284c7", fg="#ffffff", font=("Arial", 9, "bold")).pack(side="right")
    except Exception as e:
        logger.debug("Tkinter extra time prompt failed: %s", e)


def _show_tkinter_unblock_prompt(parent: Any, controller: Any) -> None:
    """Renders a Tkinter popup dialog for reporting a falsely blocked domain."""
    try:
        top = tk.Toplevel(parent) if parent else tk.Tk()
        top.title("Báo chặn nhầm trang web")
        top.geometry("380x210")
        top.configure(bg="#1e293b")

        tk.Label(top, text="Tên miền (domain):", fg="#ffffff", bg="#1e293b", font=("Arial", 9, "bold")).pack(pady=(8, 2), padx=12, anchor="w")
        ent_domain = tk.Entry(top, font=("Arial", 10), width=36)
        ent_domain.insert(0, "hocmai.vn")
        ent_domain.pack(pady=2, padx=12)

        tk.Label(top, text="Lý do cần mở trang web:", fg="#ffffff", bg="#1e293b", font=("Arial", 9, "bold")).pack(pady=(8, 2), padx=12, anchor="w")
        ent_reason = tk.Entry(top, font=("Arial", 10), width=36)
        ent_reason.insert(0, "Phục vụ bài tập trực tuyến")
        ent_reason.pack(pady=2, padx=12)

        def _send():
            domain = ent_domain.get().strip() or "hocmai.vn"
            reason = ent_reason.get().strip() or "Phục vụ học tập"
            if controller and hasattr(controller, "report_unblock_domain"):
                controller.report_unblock_domain(domain, reason=reason)
            top.destroy()

        btn_box = tk.Frame(top, bg="#1e293b")
        btn_box.pack(pady=12, padx=12, fill="x")
        tk.Button(btn_box, text="Hủy", command=top.destroy, bg="#475569", fg="#ffffff").pack(side="right", padx=(8, 0))
        tk.Button(btn_box, text="Gửi báo cáo", command=_send, bg="#0284c7", fg="#ffffff", font=("Arial", 9, "bold")).pack(side="right")
    except Exception as e:
        logger.debug("Tkinter unblock prompt failed: %s", e)


def _show_tkinter_transparency(parent: Any, info: Dict[str, Any]) -> None:
    """Renders a Tkinter window displaying transparency data and child rights."""
    try:
        top = tk.Toplevel(parent) if parent else tk.Tk()
        top.title(info.get("title", "Hôm nay em đã dùng gì"))
        top.geometry("460x320")
        top.configure(bg="#1e293b")

        tk.Label(top, text="📖 QUY TẮC SỬ DỤNG MÁY TÍNH CỦA BẠN", fg="#facc15", bg="#1e293b", font=("Arial", 12, "bold")).pack(pady=(12, 6))
        tk.Label(top, text=f"• Hạn mức hàng ngày: {info.get('daily_quota_minutes', 120)} phút", fg="#ffffff", bg="#1e293b", font=("Arial", 10)).pack(anchor="w", padx=16)
        tk.Label(top, text=f"• Khung giờ nghỉ ngơi: {info.get('bed_time', '22:00 - 06:00')}", fg="#ffffff", bg="#1e293b", font=("Arial", 10)).pack(anchor="w", padx=16)

        tk.Label(top, text="4 QUYỀN LỢI TRẺ EM (NGUYÊN TẮC NT5):", fg="#38bdf8", bg="#1e293b", font=("Arial", 10, "bold")).pack(anchor="w", padx=16, pady=(10, 4))
        for r in info.get("child_rights", []):
            tk.Label(top, text=f"• {r}", fg="#cbd5e1", bg="#1e293b", font=("Arial", 9), wraplength=420, justify="left").pack(anchor="w", padx=20, pady=1)

        tk.Label(top, text=f"Tổng đài Quốc gia: {info.get('hotline', '111 - Cục Trẻ em')}", fg="#f87171", bg="#1e293b", font=("Arial", 9, "italic")).pack(pady=(12, 6))
        tk.Button(top, text="Đã hiểu", command=top.destroy, bg="#0284c7", fg="#ffffff", padx=16, pady=4).pack(pady=(0, 10))
    except Exception as e:
        logger.debug("Tkinter transparency window failed: %s", e)
