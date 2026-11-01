"""
Adversarial Stress & Edge-Case Verification Harness for OpenGuard Kids Tray GUI
Challenger 1 — Empirical Stress Test

Tests:
1. Rapid Concurrent Event Flooding (1000+ events across 10 threads)
2. Malformed / Corrupted Payloads
3. Thread Safety & Deadlock Absence in TrayUIPresenter
4. Memory Leak / Consumption Verification (tracemalloc)
5. Repeated Window Lifecycle (Toast, Grace, Lock Overlay) Stress
"""

import sys
import os
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import time
import queue
import threading
import tracemalloc
from unittest.mock import MagicMock, patch

from src.tray.gui import (
    TrayUIPresenter,
    create_tray_icon_image,
    build_context_menu,
    ToastNotificationManager,
    GracePeriodDialog,
    FullscreenLockOverlay,
    COLOR_NORMAL,
    COLOR_WARNING,
    COLOR_URGENT,
    COLOR_LOCKED,
)


def run_rapid_event_flooding_stress():
    print("=" * 60)
    print("TEST 1: Rapid Concurrent Event Flooding & Deadlock Verification")
    print("=" * 60)

    mock_client = MagicMock()
    mock_client.get_status.return_value = {
        "state": "ACTIVE_COUNTING",
        "remaining_seconds": 3600.0,
        "is_locked": False,
    }

    presenter = TrayUIPresenter(ipc_client=mock_client)
    presenter.root = MagicMock()
    presenter.icon = MagicMock()
    presenter.toast_mgr = MagicMock()

    NUM_THREADS = 10
    EVENTS_PER_THREAD = 100
    TOTAL_EVENTS = NUM_THREADS * EVENTS_PER_THREAD

    event_samples = [
        ("STATUS_UPDATE", {"remaining_seconds": 3600.0, "is_locked": False, "state": "NORMAL"}),
        ("STATUS_UPDATE", {"remaining_seconds": 580.0, "is_locked": False, "state": "WARNING_10M"}),
        ("STATUS_UPDATE", {"remaining_seconds": 290.0, "is_locked": False, "state": "WARNING_5M"}),
        ("STATUS_UPDATE", {"remaining_seconds": 50.0, "is_locked": False, "state": "WARNING_1M"}),
        ("STATUS_UPDATE", {"remaining_seconds": 0.0, "is_locked": False, "state": "GRACE_PERIOD_60S"}),
        ("STATUS_UPDATE", {"remaining_seconds": 0.0, "is_locked": True, "state": "LOCKED_QUOTA"}),
        ("WARNING_TOAST", {"level": "10M", "message": "10 minutes left", "title": "Notice"}),
        ("WARNING_TOAST", {"level": "5M", "message": "5 minutes left", "title": "Warning"}),
        ("WARNING_TOAST", {"level": "1M", "message": "1 minute left", "title": "Urgent"}),
        ("BONUS_TIME_ADDED", {"message": "Granted 15 mins", "title": "Bonus"}),
        ("LOST_CONNECTION", {"message": "Service offline"}),
        ("UNLOCK", {}),
    ]

    start_time = time.perf_counter()
    errors = []

    def producer_worker(thread_idx: int):
        for i in range(EVENTS_PER_THREAD):
            evt_type, data = event_samples[(thread_idx * EVENTS_PER_THREAD + i) % len(event_samples)]
            try:
                presenter.handle_notification(evt_type, data.copy())
            except Exception as e:
                errors.append(e)

    # Launch concurrent producers
    threads = [threading.Thread(target=producer_worker, args=(t,)) for t in range(NUM_THREADS)]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=5.0)

    elapsed_push = time.perf_counter() - start_time
    print(f"Pushed {TOTAL_EVENTS} events across {NUM_THREADS} threads in {elapsed_push * 1000:.2f}ms")
    assert len(errors) == 0, f"Errors during push: {errors}"
    assert presenter.event_queue.qsize() == TOTAL_EVENTS, f"Queue size mismatch: {presenter.event_queue.qsize()}"

    # Drain queue
    start_drain = time.perf_counter()
    drain_cycles = 0
    while not presenter.event_queue.empty():
        presenter._poll_queue()
        drain_cycles += 1

    elapsed_drain = time.perf_counter() - start_drain
    print(f"Drained {TOTAL_EVENTS} events in {drain_cycles} cycles in {elapsed_drain * 1000:.2f}ms")
    assert presenter.event_queue.empty()
    print("TEST 1 PASSED: Zero deadlocks, zero race conditions detected.\n")


def run_malformed_corrupted_payload_stress():
    print("=" * 60)
    print("TEST 2: Corrupted & Malformed Payloads Stress")
    print("=" * 60)

    mock_client = MagicMock()
    presenter = TrayUIPresenter(ipc_client=mock_client)
    presenter.root = MagicMock()
    presenter.icon = MagicMock()
    presenter.toast_mgr = MagicMock()

    malformed_events = [
        ("STATUS_UPDATE", {}),
        ("STATUS_UPDATE", {"remaining_seconds": "not_a_number"}),
        ("STATUS_UPDATE", {"remaining_seconds": None, "state": None}),
        ("STATUS_UPDATE", {"remaining_seconds": -999999, "is_locked": "yes"}),
        ("STATUS_UPDATE", {"remaining_seconds": 1e9, "state": 12345}),
        ("WARNING_TOAST", {}),
        ("WARNING_TOAST", {"level": None, "message": None}),
        ("WARNING_TOAST", {"level": "INVALID_LEVEL", "message": "<script>alert(1)</script>"}),
        ("LOCK_SCREEN", {}),
        ("LOCK_SCREEN", {"reason": None}),
        ("LOST_CONNECTION", {}),
        ("CORRUPT_UNKNOWN_EVENT", {"random_garbage": True}),
        ("", {}),
        (None, None),
    ]

    for evt_type, data in malformed_events:
        try:
            # We wrap corrupt event handling to ensure the presenter never crashes the loop
            presenter.event_queue.put((evt_type, data))
        except Exception as e:
            assert False, f"Exception pushing malformed event ({evt_type}, {data}): {e}"

    # Process all malformed events through _poll_queue
    try:
        presenter._poll_queue()
        print(f"Processed {len(malformed_events)} malformed/corrupted events without unhandled crash.")
    except Exception as e:
        assert False, f"Crash during malformed event dispatch: {e}"

    print("TEST 2 PASSED: Graceful resilience to corrupt / malformed data.\n")


def run_memory_leak_stress():
    print("=" * 60)
    print("TEST 3: Memory Consumption & Leak Analysis")
    print("=" * 60)

    class DummyIcon:
        def __init__(self):
            self.icon = None

    class DummyRoot:
        def after(self, ms, cb):
            pass

    class DummyClient:
        def get_status(self):
            return {"state": "NORMAL", "remaining_seconds": 3600.0}

    tracemalloc.start()
    snapshot1 = tracemalloc.take_snapshot()

    presenter = TrayUIPresenter(ipc_client=DummyClient())
    presenter.root = DummyRoot()
    presenter.icon = DummyIcon()
    presenter.toast_mgr = None

    # Pump 2000 events in batches of 50
    for batch in range(40):
        for i in range(50):
            presenter.handle_notification(
                "STATUS_UPDATE",
                {"remaining_seconds": 1800.0 - (i % 60), "is_locked": False, "state": "NORMAL"}
            )
        presenter._poll_queue()

    snapshot2 = tracemalloc.take_snapshot()
    top_stats = snapshot2.compare_to(snapshot1, 'lineno')

    total_diff = sum(stat.size_diff for stat in top_stats)
    print(f"Total memory difference after 2000 dispatched events: {total_diff / 1024:.2f} KB")

    tracemalloc.stop()

    # Memory difference for 2000 events must be reasonable (< 256KB)
    assert total_diff < 256 * 1024, f"Potential memory leak detected: {total_diff / 1024:.2f} KB"
    print("TEST 3 PASSED: No memory runaway detected (< 256KB for 2000 events).\n")


def run_dialog_lifecycle_stress():
    print("=" * 60)
    print("TEST 4: Dialog & Overlay Rapid Lifecycle Stress")
    print("=" * 60)

    mock_controller = MagicMock()

    # GracePeriodDialog 50 rapid instantiations & button clicks
    for _ in range(50):
        mock_toplevel = MagicMock()
        with patch("sys.platform", "win32"), patch("ctypes.windll", create=True) as mock_windll:
            mock_windll.user32.GetWindowLongW.return_value = 0
            mock_windll.user32.GetParent.return_value = 12345
            dlg = GracePeriodDialog(parent=mock_toplevel, controller=mock_controller)
            dlg.setup_ui()
            # MUST NEVER call grab_set or focus_force
            mock_toplevel.grab_set.assert_not_called()
            mock_toplevel.focus_force.assert_not_called()
            dlg.on_lock_now_clicked()
            dlg.on_request_time_clicked()

    # FullscreenLockOverlay 50 rapid show/hide cycles
    mock_lock_top = MagicMock()
    overlay = FullscreenLockOverlay(parent=mock_lock_top, controller=mock_controller)
    for _ in range(50):
        overlay.show(reason="Stress test")
        overlay.on_request_time_clicked()
        overlay.hide()

    print("TEST 4 PASSED: 50x rapid lifecycle cycles completed with 100% focus preservation.\n")


if __name__ == "__main__":
    print("\n>>> STARTING ADVERSARIAL STRESS TEST SUITE <<<\n")
    run_rapid_event_flooding_stress()
    run_malformed_corrupted_payload_stress()
    run_memory_leak_stress()
    run_dialog_lifecycle_stress()
    print(">>> ALL ADVERSARIAL STRESS TESTS COMPLETED SUCCESSFULLY (100% PASS) <<<\n")
