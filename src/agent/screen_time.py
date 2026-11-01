"""
OpenGuard Kids — Screen-Time Tracker & Anti-Tamper Engine
Implements Requirements:
  - F1.1: Daily usage quota & lock upon expiration
  - F1.2: Weekly 7x48 schedule matrix (30-minute granularity)
  - F1.3: Active usage tracking (idle pause > 5 min via user32.GetLastInputInfo; accuracy <= +-30s/hr)
  - F1.4: Advance warnings (10m, 5m, 1m) and 60-second grace period dialog
  - F1.5: Clock rollback anti-tamper detection (>60s backward jump)
Enforces state machine defined in docs/ARCHITECTURE.md.
"""

from __future__ import annotations

import sys
import time
from datetime import datetime, date
from enum import Enum
from typing import Callable, Dict, List, Optional, Any


class ScreenTimeState(str, Enum):
    INITIALIZING = "INITIALIZING"
    ACTIVE_COUNTING = "ACTIVE_COUNTING"
    IDLE_PAUSED = "IDLE_PAUSED"
    WARNING_10M = "WARNING_10M"
    WARNING_5M = "WARNING_5M"
    WARNING_1M = "WARNING_1M"
    GRACE_PERIOD_60S = "GRACE_PERIOD_60S"
    LOCKED_QUOTA = "LOCKED_QUOTA"
    LOCKED_SCHEDULE = "LOCKED_SCHEDULE"
    LOCKED_URGENT = "LOCKED_URGENT"


def get_system_idle_seconds_windows() -> float:
    """
    Retrieves idle seconds on Windows via user32.GetLastInputInfo.
    Returns 0.0 if not on Windows or on error.
    """
    if sys.platform != "win32":
        return 0.0

    try:
        import ctypes

        class LASTINPUTINFO(ctypes.Structure):
            _fields_ = [("cbSize", ctypes.c_uint), ("dwTime", ctypes.c_uint)]

        lii = LASTINPUTINFO()
        lii.cbSize = ctypes.sizeof(LASTINPUTINFO)
        if ctypes.windll.user32.GetLastInputInfo(ctypes.byref(lii)):
            millis = ctypes.windll.kernel32.GetTickCount() - lii.dwTime
            return max(0.0, millis / 1000.0)
    except Exception:
        pass
    return 0.0


class ScreenTimeTracker:
    """
    Core Screen-Time Tracker and Anti-Tamper Engine.
    Evaluated periodically (typically every 10 seconds).
    """

    def __init__(
        self,
        daily_quota_seconds: int = 7200,  # Default: 2 hours
        daily_quota_weekday_seconds: Optional[int] = None,
        daily_quota_weekend_seconds: Optional[int] = None,
        bed_time_start: Optional[str] = None,
        bed_time_end: Optional[str] = None,
        idle_threshold_seconds: int = 300,  # Default: 5 minutes idle pause
        schedule_matrix: Optional[List[List[bool]]] = None,  # 7 days x 48 slots (30m each)
        idle_provider: Optional[Callable[[], float]] = None,
        wall_time_provider: Optional[Callable[[], float]] = None,
        monotonic_time_provider: Optional[Callable[[], float]] = None,
    ):
        self.daily_quota_seconds = daily_quota_seconds
        self.daily_quota_weekday_seconds = daily_quota_weekday_seconds if daily_quota_weekday_seconds is not None else daily_quota_seconds
        self.daily_quota_weekend_seconds = daily_quota_weekend_seconds if daily_quota_weekend_seconds is not None else daily_quota_seconds
        self.bed_time_start = bed_time_start
        self.bed_time_end = bed_time_end
        self.idle_threshold_seconds = idle_threshold_seconds

        # Default schedule: True (allowed) for all 7 days x 48 half-hour slots
        if schedule_matrix is None:
            self.schedule_matrix = [[True for _ in range(48)] for _ in range(7)]
        else:
            self.schedule_matrix = schedule_matrix

        # Providers for platform abstraction and deterministic unit testing
        self._get_idle_seconds = idle_provider or get_system_idle_seconds_windows
        self._get_wall_time = wall_time_provider or time.time
        self._get_monotonic_time = monotonic_time_provider or time.monotonic

        # Initialize internal timestamps
        now_wall = self._get_wall_time()
        now_mono = self._get_monotonic_time()

        self.last_wall_time: float = now_wall
        self.last_monotonic_time: float = now_mono
        self.current_day: date = datetime.fromtimestamp(now_wall).date()

        self.consumed_seconds_today: float = 0.0
        self.bonus_seconds_today: float = 0.0

        self.state: ScreenTimeState = ScreenTimeState.INITIALIZING
        self.urgent_lock: bool = False
        self.tamper_detected: bool = False
        self.grace_period_start_time: Optional[float] = None

        self.alerts: List[Dict[str, Any]] = []

        # Run initial state evaluation
        self.tick()

    def get_quota_today_seconds(self, dt: Optional[datetime] = None) -> float:
        """
        Determines active daily quota in seconds based on weekday vs. weekend.
        """
        if dt is None:
            dt = datetime.fromtimestamp(self._get_wall_time())
        # weekday(): Monday is 0, Sunday is 6
        if dt.weekday() >= 5:
            return float(self.daily_quota_weekend_seconds)
        return float(self.daily_quota_weekday_seconds)

    def is_in_bedtime(self, dt: Optional[datetime] = None) -> bool:
        """
        Checks whether the given datetime falls within the bedtime curfew window.
        Handles curfew windows crossing midnight (e.g., 22:00 -> 06:00).
        """
        if not self.bed_time_start or not self.bed_time_end:
            return False
        if dt is None:
            dt = datetime.fromtimestamp(self._get_wall_time())
        try:
            sh, sm = map(int, self.bed_time_start.split(":"))
            eh, em = map(int, self.bed_time_end.split(":"))
            curr_mins = dt.hour * 60 + dt.minute
            start_mins = sh * 60 + sm
            end_mins = eh * 60 + em
            if start_mins <= end_mins:
                return start_mins <= curr_mins < end_mins
            else:
                return curr_mins >= start_mins or curr_mins < end_mins
        except Exception:
            return False

    def update_policy(self, policy_data: Dict[str, Any]) -> None:
        """
        Dynamically reloads policies (quotas, bedtime curfew, schedule matrix).
        """
        if not policy_data:
            return

        if "daily_quota_minutes" in policy_data and policy_data["daily_quota_minutes"] is not None:
            self.daily_quota_weekday_seconds = int(policy_data["daily_quota_minutes"]) * 60
            self.daily_quota_seconds = self.daily_quota_weekday_seconds

        weekend_mins = policy_data.get("daily_quota_weekend_minutes") or policy_data.get("weekend_quota_minutes")
        if weekend_mins is not None:
            self.daily_quota_weekend_seconds = int(weekend_mins) * 60

        if "bed_time_start" in policy_data and policy_data["bed_time_start"]:
            self.bed_time_start = policy_data["bed_time_start"]

        if "bed_time_end" in policy_data and policy_data["bed_time_end"]:
            self.bed_time_end = policy_data["bed_time_end"]

        if "schedule_matrix" in policy_data and policy_data["schedule_matrix"]:
            matrix = policy_data["schedule_matrix"]
            if isinstance(matrix, list) and len(matrix) == 7:
                self.schedule_matrix = matrix

        # Re-evaluate state immediately
        self.tick()

    def add_bonus_time(self, minutes: int) -> None:
        """
        Adds bonus screen time (in minutes) upon parent approval or agency request.
        """
        if minutes <= 0:
            return
        self.bonus_seconds_today += minutes * 60.0
        # If currently in grace period or locked by quota, clear grace and re-evaluate
        if self.state in (ScreenTimeState.LOCKED_QUOTA, ScreenTimeState.GRACE_PERIOD_60S):
            self.grace_period_start_time = None
        self.tick()

    def set_urgent_lock(self, locked: bool) -> None:
        """
        Sets or clears urgent instant lock ('khóa ngay' command from parent).
        """
        self.urgent_lock = locked
        self.tick()

    def is_schedule_allowed(self, dt: datetime) -> bool:
        """
        Checks whether the given datetime falls into an allowed schedule slot.
        weekday(): 0=Monday ... 6=Sunday
        Slot: 0 to 47 (30 minutes each).
        """
        day_idx = dt.weekday()
        slot_idx = (dt.hour * 60 + dt.minute) // 30
        if 0 <= day_idx < 7 and 0 <= slot_idx < 48:
            return self.schedule_matrix[day_idx][slot_idx]
        return True

    def get_remaining_seconds(self) -> float:
        """
        Calculates remaining quota in seconds. Never returns negative.
        """
        dt = datetime.fromtimestamp(self._get_wall_time())
        total_allowed = self.get_quota_today_seconds(dt) + self.bonus_seconds_today
        return max(0.0, total_allowed - self.consumed_seconds_today)

    def is_locked(self) -> bool:
        """
        Returns True if screen is locked due to quota, schedule, or urgent command.
        """
        return self.state in (
            ScreenTimeState.LOCKED_QUOTA,
            ScreenTimeState.LOCKED_SCHEDULE,
            ScreenTimeState.LOCKED_URGENT,
        )

    def tick(self) -> ScreenTimeState:
        """
        Evaluates active time, idle state, tamper detection, and state machine transitions.
        Should be called every 10 seconds in the main tracking loop.
        """
        current_wall = self._get_wall_time()
        current_mono = self._get_monotonic_time()
        idle_seconds = self._get_idle_seconds()

        dt = datetime.fromtimestamp(current_wall)
        today = dt.date()

        # 1. Midnight auto-reset for new day
        if today != self.current_day:
            self.current_day = today
            self.consumed_seconds_today = 0.0
            self.bonus_seconds_today = 0.0
            self.grace_period_start_time = None

        # 2. Clock Rollback Anti-Tamper Check
        # If wall clock jumped backward by > 60 seconds relative to previous wall time
        delta_wall = current_wall - self.last_wall_time
        delta_mono = max(0.0, current_mono - self.last_monotonic_time)

        if delta_wall < -60.0:
            self.tamper_detected = True
            alert = {
                "type": "quota_warning",
                "subject": "clock_tamper_detected",
                "delta_wall": delta_wall,
                "timestamp": current_wall,
                "message": f"Clock rollback detected: wall clock jumped {delta_wall:.1f}s backward.",
            }
            self.alerts.append(alert)
            # CRITICAL RULE: Consumed quota is NEVER rolled back or decreased.
            self.last_wall_time = current_wall
        else:
            self.last_wall_time = current_wall

        self.last_monotonic_time = current_mono

        # 3. Check Urgent Lock
        if self.urgent_lock:
            self.state = ScreenTimeState.LOCKED_URGENT
            return self.state

        # 4. Check Bedtime Curfew & Schedule Matrix
        if self.is_in_bedtime(dt) or not self.is_schedule_allowed(dt):
            self.state = ScreenTimeState.LOCKED_SCHEDULE
            return self.state

        # 5. Check Quota & Grace Period
        remaining = self.get_remaining_seconds()

        if remaining <= 0.0:
            if self.grace_period_start_time is None:
                # Enter 60-second grace period (Save work dialog)
                self.grace_period_start_time = current_mono
                self.state = ScreenTimeState.GRACE_PERIOD_60S
                return self.state
            else:
                elapsed_grace = current_mono - self.grace_period_start_time
                if elapsed_grace >= 60.0:
                    self.state = ScreenTimeState.LOCKED_QUOTA
                    return self.state
                else:
                    self.state = ScreenTimeState.GRACE_PERIOD_60S
                    return self.state

        # If we had a grace period but now quota is positive (e.g. bonus time added)
        self.grace_period_start_time = None

        # 6. Check Idle State (> 5 minutes / threshold of no input)
        if idle_seconds >= self.idle_threshold_seconds:
            self.state = ScreenTimeState.IDLE_PAUSED
            # Do NOT accumulate screen time while idle
            return self.state

        # 7. Active Usage: User is actively working
        # Accumulate elapsed monotonic time (capped at reasonable interval, e.g. delta_mono)
        if self.state not in (
            ScreenTimeState.INITIALIZING,
            ScreenTimeState.IDLE_PAUSED,
            ScreenTimeState.LOCKED_QUOTA,
            ScreenTimeState.LOCKED_SCHEDULE,
            ScreenTimeState.LOCKED_URGENT,
        ):
            # Accumulate time only if previous state was active/counting
            self.consumed_seconds_today += delta_mono

        # Re-compute remaining after consuming delta_mono
        remaining = self.get_remaining_seconds()

        # 8. Warning Tiers & Active State Transitions
        if remaining <= 0.0:
            self.grace_period_start_time = current_mono
            self.state = ScreenTimeState.GRACE_PERIOD_60S
        elif remaining <= 60.0:
            self.state = ScreenTimeState.WARNING_1M
        elif remaining <= 300.0:
            self.state = ScreenTimeState.WARNING_5M
        elif remaining <= 600.0:
            self.state = ScreenTimeState.WARNING_10M
        else:
            self.state = ScreenTimeState.ACTIVE_COUNTING

        return self.state

    def get_status(self) -> Dict[str, Any]:
        """
        Returns full diagnostic status dictionary for IPC to Tray and Server sync.
        """
        return {
            "state": self.state.value,
            "is_locked": self.is_locked(),
            "remaining_seconds": round(self.get_remaining_seconds(), 1),
            "consumed_seconds_today": round(self.consumed_seconds_today, 1),
            "daily_quota_seconds": int(self.get_quota_today_seconds()),
            "daily_quota_weekday_seconds": self.daily_quota_weekday_seconds,
            "daily_quota_weekend_seconds": self.daily_quota_weekend_seconds,
            "bed_time_start": self.bed_time_start,
            "bed_time_end": self.bed_time_end,
            "bonus_seconds_today": round(self.bonus_seconds_today, 1),
            "tamper_detected": self.tamper_detected,
            "urgent_lock": self.urgent_lock,
            "alerts_count": len(self.alerts),
        }

