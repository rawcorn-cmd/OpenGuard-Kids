"""
Unit tests for OpenGuard Kids Screen-Time Tracker & Anti-Tamper Engine.
Verifies idle detection, clock rollback detection, schedule matrix, warning states, and accuracy benchmark.
"""

from datetime import datetime
from src.agent.screen_time import ScreenTimeTracker, ScreenTimeState


class MockEnvironment:
    """Simulates wall clock, monotonic clock, and user idle seconds."""

    def __init__(self, start_wall: float = 1700000000.0):
        self.wall = start_wall
        self.mono = 1000.0
        self.idle = 0.0

    def get_wall(self) -> float:
        return self.wall

    def get_mono(self) -> float:
        return self.mono

    def get_idle(self) -> float:
        return self.idle

    def advance(self, seconds: float, idle_seconds: float = 0.0):
        self.wall += seconds
        self.mono += seconds
        self.idle = idle_seconds


def test_initial_state_and_active_counting():
    env = MockEnvironment()
    # 2 hours daily quota (7200 seconds)
    tracker = ScreenTimeTracker(
        daily_quota_seconds=7200,
        idle_threshold_seconds=300,
        idle_provider=env.get_idle,
        wall_time_provider=env.get_wall,
        monotonic_time_provider=env.get_mono,
    )

    assert tracker.state == ScreenTimeState.ACTIVE_COUNTING
    assert tracker.get_remaining_seconds() == 7200.0

    # Advance 100 seconds with active input (idle=0)
    env.advance(100.0, idle_seconds=0.0)
    tracker.tick()

    assert tracker.state == ScreenTimeState.ACTIVE_COUNTING
    assert tracker.consumed_seconds_today == 100.0
    assert tracker.get_remaining_seconds() == 7100.0
    assert not tracker.is_locked()


def test_idle_pause_does_not_consume_quota():
    env = MockEnvironment()
    tracker = ScreenTimeTracker(
        daily_quota_seconds=3600,
        idle_threshold_seconds=300,
        idle_provider=env.get_idle,
        wall_time_provider=env.get_wall,
        monotonic_time_provider=env.get_mono,
    )

    # Active for 60 seconds
    env.advance(60.0, idle_seconds=0.0)
    tracker.tick()
    assert tracker.consumed_seconds_today == 60.0

    # User steps away: idle = 301 seconds (> 300s threshold)
    env.advance(600.0, idle_seconds=301.0)
    state = tracker.tick()

    assert state == ScreenTimeState.IDLE_PAUSED
    # Quota must NOT have been consumed during this 600s idle period!
    assert tracker.consumed_seconds_today == 60.0
    assert tracker.get_remaining_seconds() == 3540.0

    # User returns: idle drops to 2 seconds
    env.advance(10.0, idle_seconds=2.0)
    tracker.tick()
    assert tracker.state == ScreenTimeState.ACTIVE_COUNTING


def test_warning_tiers_and_grace_period():
    env = MockEnvironment()
    # 700 seconds quota
    tracker = ScreenTimeTracker(
        daily_quota_seconds=700,
        idle_threshold_seconds=300,
        idle_provider=env.get_idle,
        wall_time_provider=env.get_wall,
        monotonic_time_provider=env.get_mono,
    )

    # 1. Quota remaining: 700 -> ACTIVE_COUNTING
    assert tracker.state == ScreenTimeState.ACTIVE_COUNTING

    # 2. Advance 150s -> remaining = 550s (<= 600s / 10 min) -> WARNING_10M
    env.advance(150.0, idle_seconds=0.0)
    assert tracker.tick() == ScreenTimeState.WARNING_10M

    # 3. Advance 300s -> remaining = 250s (<= 300s / 5 min) -> WARNING_5M
    env.advance(300.0, idle_seconds=0.0)
    assert tracker.tick() == ScreenTimeState.WARNING_5M

    # 4. Advance 200s -> remaining = 50s (<= 60s / 1 min) -> WARNING_1M
    env.advance(200.0, idle_seconds=0.0)
    assert tracker.tick() == ScreenTimeState.WARNING_1M

    # 5. Advance 50s -> remaining = 0s -> GRACE_PERIOD_60S (child has 60s to save work)
    env.advance(50.0, idle_seconds=0.0)
    assert tracker.tick() == ScreenTimeState.GRACE_PERIOD_60S
    assert not tracker.is_locked()  # Grace period allows saving work before hard lock

    # 6. Advance 30s into grace period -> still in GRACE_PERIOD_60S
    env.advance(30.0, idle_seconds=0.0)
    assert tracker.tick() == ScreenTimeState.GRACE_PERIOD_60S

    # 7. Advance 35s more (total 65s > 60s grace) -> LOCKED_QUOTA
    env.advance(35.0, idle_seconds=0.0)
    assert tracker.tick() == ScreenTimeState.LOCKED_QUOTA
    assert tracker.is_locked()


def test_clock_rollback_anti_tamper():
    env = MockEnvironment(start_wall=1700000000.0)
    tracker = ScreenTimeTracker(
        daily_quota_seconds=3600,
        idle_provider=env.get_idle,
        wall_time_provider=env.get_wall,
        monotonic_time_provider=env.get_mono,
    )

    # Consume 600 seconds
    env.advance(600.0, idle_seconds=0.0)
    tracker.tick()
    assert tracker.consumed_seconds_today == 600.0
    assert not tracker.tamper_detected

    # Child changes Windows system clock backward by 2 hours (-7200 seconds)
    env.wall -= 7200.0
    env.mono += 10.0  # Monotonic clock always moves forward!
    tracker.tick()

    # Verify tamper detected!
    assert tracker.tamper_detected
    assert len(tracker.alerts) >= 1
    assert tracker.alerts[0]["subject"] == "clock_tamper_detected"

    # Consumed quota must NEVER be rolled back!
    assert tracker.consumed_seconds_today >= 600.0


def test_schedule_matrix_blocking():
    env = MockEnvironment()
    # Schedule matrix: all allowed EXCEPT Monday 14:00 - 14:30 (slot 28)
    matrix = [[True for _ in range(48)] for _ in range(7)]
    matrix[0][28] = False  # Monday slot 28 is blocked

    # Set mock environment to a Monday at 13:50 (allowed)
    # 2026-10-26 was a Monday.
    dt_allowed = datetime(2026, 10, 26, 13, 50, 0)
    env.wall = dt_allowed.timestamp()

    tracker = ScreenTimeTracker(
        daily_quota_seconds=3600,
        schedule_matrix=matrix,
        idle_provider=env.get_idle,
        wall_time_provider=env.get_wall,
        monotonic_time_provider=env.get_mono,
    )

    assert tracker.state == ScreenTimeState.ACTIVE_COUNTING

    # Advance 15 minutes to 14:05 (enters slot 28 -> blocked!)
    env.advance(15 * 60.0, idle_seconds=0.0)
    state = tracker.tick()

    assert state == ScreenTimeState.LOCKED_SCHEDULE
    assert tracker.is_locked()


def test_urgent_lock_and_bonus_time():
    env = MockEnvironment()
    tracker = ScreenTimeTracker(
        daily_quota_seconds=1800,
        idle_provider=env.get_idle,
        wall_time_provider=env.get_wall,
        monotonic_time_provider=env.get_mono,
    )

    # Urgent lock from parent WebSocket
    tracker.set_urgent_lock(True)
    assert tracker.state == ScreenTimeState.LOCKED_URGENT
    assert tracker.is_locked()

    # Unlock
    tracker.set_urgent_lock(False)
    assert tracker.state == ScreenTimeState.ACTIVE_COUNTING

    # Run down quota to lock (advance 1800s)
    env.advance(1800.0, idle_seconds=0.0)
    tracker.tick()
    # Advance 65s into grace period to trigger lock
    env.advance(65.0, idle_seconds=0.0)
    tracker.tick()
    assert tracker.state == ScreenTimeState.LOCKED_QUOTA

    # Parent grants 15 minutes bonus time ("cộng 15 phút")
    tracker.add_bonus_time(15)
    assert not tracker.is_locked()
    assert tracker.state == ScreenTimeState.ACTIVE_COUNTING
    assert tracker.bonus_seconds_today == 900.0


def test_benchmark_hourly_accuracy():
    """
    Accuracy benchmark: Verify drift is <= +-30s per hour (3600 seconds)
    per requirements in docs/ARCHITECTURE.md.
    """
    env = MockEnvironment()
    tracker = ScreenTimeTracker(
        daily_quota_seconds=7200,
        idle_provider=env.get_idle,
        wall_time_provider=env.get_wall,
        monotonic_time_provider=env.get_mono,
    )

    # Simulate 360 ticks of 10 seconds each (1 hour total)
    for _ in range(360):
        env.advance(10.0, idle_seconds=0.0)
        tracker.tick()

    expected_consumed = 3600.0
    actual_consumed = tracker.consumed_seconds_today
    drift = abs(actual_consumed - expected_consumed)

    assert drift <= 30.0, f"Screen time drift {drift}s exceeded +/-30s tolerance!"
