"""
OpenGuard Kids — Tray UI Dialogs & User Notifications
Provides Polite Warning Toasts (10m, 5m, 1m), 60s Grace Period Dialog (D1),
Lock Screen Overlay, Request Time Dialog (NT4), and Transparency Screen (NT5).
"""

from __future__ import annotations

import logging
from typing import Callable, Optional, Dict, Any

logger = logging.getLogger("OGK.TrayDialogs")


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
            "hotline": "Tổng đài Quốc gia Bảo vệ Trẻ em: 111",
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

