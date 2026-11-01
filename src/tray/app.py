"""
OpenGuard Kids — Desktop Tray UI Application Controller
Runs in User Desktop Session (Session 1+).
Orchestrates Tray icon, status countdown, warning toasts (10m, 5m, 1m),
grace period prompt (60s), lock screen, and child agency actions (NT4/NT5).
"""

from __future__ import annotations

import logging
from typing import Callable, Dict, Optional, Any, List

from src.agent.ipc import IPCClient
from src.tray.state_listener import StateListener
from src.tray.dialogs import NotificationModel

logger = logging.getLogger("OGK.TrayApp")


class TrayAppController:
    """
    Main controller for the user-facing desktop tray application.
    Decoupled from graphics toolkit for robust testing and cross-platform compatibility.
    """

    def __init__(
        self,
        ipc_client: IPCClient,
        ui_notifier: Optional[Callable[[str, Dict[str, Any]], None]] = None,
    ):
        self.ipc_client = ipc_client
        self.ui_notifier = ui_notifier

        self.current_status: Dict[str, Any] = {}
        self.active_view: str = "NORMAL"  # NORMAL, WARNING_TOAST, GRACE_PERIOD, LOCKED, LOST_CONNECTION
        self.notification_history: List[Dict[str, Any]] = []

        # Initialize StateListener
        self.listener = StateListener(
            ipc_client=self.ipc_client,
            poll_interval_seconds=1.0,
            on_status_update=self._handle_status_update,
            on_warning=self._handle_warning,
            on_grace_period=self._handle_grace_period,
            on_lock=self._handle_lock,
            on_unlock=self._handle_unlock,
            on_connection_lost=self._handle_connection_lost,
        )

    def start(self) -> None:
        self.listener.start()
        logger.info("TrayAppController started.")

    def stop(self) -> None:
        self.listener.stop()
        logger.info("TrayAppController stopped.")

    def _notify_ui(self, event_type: str, data: Dict[str, Any]) -> None:
        self.notification_history.append({"type": event_type, "data": data})
        if self.ui_notifier:
            self.ui_notifier(event_type, data)

    def _handle_status_update(self, status: Dict[str, Any]) -> None:
        self.current_status = status

    def _handle_warning(self, level: str, remaining_seconds: float) -> None:
        msg = NotificationModel.format_warning_message(level, remaining_seconds)
        self.active_view = "WARNING_TOAST"
        self._notify_ui("WARNING_TOAST", msg)
        logger.info("Displayed warning toast: %s", msg["title"])

    def _handle_grace_period(self, remaining_seconds: float) -> None:
        msg = NotificationModel.format_grace_period_message()
        self.active_view = "GRACE_PERIOD"
        self._notify_ui("GRACE_PERIOD_DIALOG", msg)
        logger.warning("Displayed 60s Grace Period dialog.")

    def _handle_lock(self, lock_state: str) -> None:
        msg = NotificationModel.format_lock_screen_info(lock_state)
        self.active_view = "LOCKED"
        self._notify_ui("LOCK_SCREEN", msg)
        logger.warning("Activated Lock Screen overlay: %s", lock_state)

    def _handle_unlock(self) -> None:
        self.active_view = "NORMAL"
        self._notify_ui("UNLOCK_SCREEN", {"message": "Màn hình đã được mở khóa."})
        logger.info("Deactivated Lock Screen overlay.")

    def _handle_connection_lost(self) -> None:
        self.active_view = "LOST_CONNECTION"
        msg = {
            "title": "Mất kết nối với Dịch vụ Bảo vệ",
            "message": "Không nhận được tín hiệu từ Windows Service. Tuân thủ nguyên tắc NT1, ứng dụng sẽ tự động kích hoạt bảo vệ an toàn.",
        }
        self._notify_ui("LOST_CONNECTION_ALERT", msg)

    # ==========================================
    # Child Agency Actions (NT4 / NT5)
    # ==========================================

    def request_extra_time(self, minutes: int = 15, reason: str = "") -> Dict[str, Any]:
        """
        Sends an agency request from the child to the parent for additional time.
        """
        try:
            res = self.ipc_client.send_request(
                req_type="ADD_TIME",
                minutes=minutes,
                subject=reason or "Yêu cầu thêm thời gian học tập",
            )
            return {"status": "SUCCESS", "message": "Yêu cầu đã được gửi tới Cha/Mẹ.", "data": res}
        except Exception as e:
            return {"status": "ERROR", "message": f"Không thể gửi yêu cầu: {e}"}

    def report_unblock_domain(self, domain: str, reason: str = "") -> Dict[str, Any]:
        """
        Sends a false positive or study domain unblock request.
        """
        try:
            res = self.ipc_client.send_request(
                req_type="UNBLOCK_DOMAIN",
                minutes=0,
                subject=f"{domain}: {reason or 'Cần mở trang web phục vụ học tập'}",
            )
            return {"status": "SUCCESS", "message": "Yêu cầu mở trang đã được gửi.", "data": res}
        except Exception as e:
            return {"status": "ERROR", "message": f"Không thể gửi yêu cầu: {e}"}

    def get_transparency_info(self) -> Dict[str, Any]:
        """
        Retrieves transparency policy info for the child (NT5).
        """
        policy = self.current_status.get("policy", {})
        return NotificationModel.format_transparency_info(policy)

