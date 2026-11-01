"""
Unit tests for OpenGuard Kids Process Monitor & SHA-256 Hash Scanner (F2.1 & F2.2).
Verifies process name filtering, binary SHA-256 hash matching, renamed binary detection,
study mode whitelist, and process termination with callback notification.
"""

import hashlib
import os
import subprocess
import sys
import tempfile
import time
import psutil

from src.agent.process_monitor import (
    ProcessMonitor,
    compute_file_sha256,
)


def test_compute_file_sha256_and_caching():
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(b"OpenGuard Kids Test Binary Payload 12345")
        tmp_path = tmp.name

    try:
        # Calculate expected hash
        expected_hash = hashlib.sha256(b"OpenGuard Kids Test Binary Payload 12345").hexdigest().lower()
        actual_hash = compute_file_sha256(tmp_path)
        assert actual_hash == expected_hash

        # Test cached retrieval
        monitor = ProcessMonitor()
        cached_hash = monitor.get_file_hash_cached(tmp_path)
        assert cached_hash == expected_hash
        assert (tmp_path, os.stat(tmp_path).st_mtime, os.stat(tmp_path).st_size) in monitor._hash_cache
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


def test_process_name_blocking():
    monitor = ProcessMonitor()
    monitor.add_blocked_names(["discord.exe", "steam.exe", "bad_game.exe"])

    # Mock process class
    class MockProcess:
        def __init__(self, name: str, exe_path: str = ""):
            self._name = name
            self._exe = exe_path

        def name(self):
            return self._name

        def exe(self):
            return self._exe

    # Blocked by name
    mock_bad = MockProcess("steam.exe")
    should_block, reason, _ = monitor.evaluate_process(mock_bad)  # type: ignore
    assert should_block is True
    assert "steam.exe" in reason

    # Permitted application
    mock_good = MockProcess("word.exe")
    should_block_good, _, _ = monitor.evaluate_process(mock_good)  # type: ignore
    assert should_block_good is False


def test_renamed_binary_sha256_detection():
    """
    CRITICAL ACCEPTANCE TEST (F2.1):
    Renaming a prohibited binary (e.g. game.exe -> notepad.exe) is STILL detected
    and blocked by comparing the binary's SHA-256 hash.
    """
    with tempfile.NamedTemporaryFile(delete=False, suffix=".exe") as tmp:
        # Simulate binary content of a prohibited game
        game_bytes = b"PROHIBITED_GAME_BINARY_SIGNATURE_XYZ_999"
        tmp.write(game_bytes)
        game_exe_path = tmp.name

    try:
        game_hash = hashlib.sha256(game_bytes).hexdigest().lower()

        monitor = ProcessMonitor()
        # Parent configured policy to block this game's hash
        monitor.add_blocked_hashes([game_hash])

        # Child renamed the binary to 'notepad.exe' to deceive the system
        class MockRenamedProcess:
            def name(self):
                return "notepad.exe"  # Renamed!

            def exe(self):
                return game_exe_path

        renamed_proc = MockRenamedProcess()
        should_block, reason, detected_hash = monitor.evaluate_process(renamed_proc)  # type: ignore

        # Verification: Must be caught by hash!
        assert should_block is True
        assert detected_hash == game_hash
        assert "Mã băm SHA-256" in reason
    finally:
        if os.path.exists(game_exe_path):
            os.remove(game_exe_path)


def test_study_mode_whitelist():
    monitor = ProcessMonitor()
    monitor.set_study_mode(enabled=True, allowed_names=["winword.exe", "excel.exe", "zoom.exe"])

    class MockApp:
        def __init__(self, name):
            self._name = name

        def name(self):
            return self._name

        def exe(self):
            return ""

    # Zoom is whitelisted -> allowed
    zoom_proc = MockApp("zoom.exe")
    should_block_zoom, _, _ = monitor.evaluate_process(zoom_proc)  # type: ignore
    assert should_block_zoom is False

    # Calculator is not whitelisted during study mode -> blocked!
    calc_proc = MockApp("calculator.exe")
    should_block_calc, reason, _ = monitor.evaluate_process(calc_proc)  # type: ignore
    assert should_block_calc is True
    assert "Chế độ học tập" in reason


def test_process_termination_and_event_callback():
    """
    ACCEPTANCE TEST (F2.2):
    Terminates running prohibited process and fires event callback with details.
    """
    captured_events = []

    def on_blocked(action):
        captured_events.append(action)

    monitor = ProcessMonitor(on_process_blocked=on_blocked)

    # Spawn a dummy background process with a unique command line
    dummy_code = "import time; time.sleep(15)"
    proc = subprocess.Popen([sys.executable, "-c", dummy_code])
    pid = proc.pid

    try:
        # Give process a moment to spin up
        time.sleep(0.3)
        assert psutil.pid_exists(pid)

        # Mock evaluate_process specifically for this PID in monitor
        original_evaluate = monitor.evaluate_process

        def mock_eval(p):
            if p.pid == pid:
                return True, "Ứng dụng cấm thử nghiệm", "mock_hash_1234"
            return original_evaluate(p)

        monitor.evaluate_process = mock_eval  # type: ignore

        # Run enforcement
        actions = monitor.scan_and_enforce_once()

        # Check action was recorded
        matching_actions = [a for a in actions if a["pid"] == pid]
        assert len(matching_actions) == 1
        assert matching_actions[0]["reason"] == "Ứng dụng cấm thử nghiệm"

        # Check callback was called
        assert len(captured_events) >= 1
        assert any(e["pid"] == pid for e in captured_events)

        # Verify process was terminated!
        time.sleep(0.3)
        assert not psutil.pid_exists(pid)

    finally:
        # Clean up if still exists
        try:
            if psutil.pid_exists(pid):
                proc.kill()
        except Exception:
            pass

