"""
OpenGuard Kids — Process Monitor & SHA-256 Hash Scanner
Enforces application control by process name and binary SHA-256 cryptographic hash (F2.1 & F2.2).
Detects and blocks prohibited applications even when renamed (e.g. game.exe renamed to notepad.exe).
"""

from __future__ import annotations

import hashlib
import logging
import os
import sys
import threading
import time
from typing import Callable, Dict, List, Optional, Set, Tuple

import psutil

logger = logging.getLogger("OpenGuardKids.ProcessMonitor")

# Essential system processes that must NEVER be terminated
PROTECTED_SYSTEM_PROCESSES = {
    "system", "system idle process", "smss.exe", "csrss.exe", "wininit.exe",
    "services.exe", "lsass.exe", "svchost.exe", "winlogon.exe", "explorer.exe",
    "taskhostw.exe", "dwm.exe", "python.exe", "python3.exe", "pythonw.exe",
    "openguardkids.exe", "ogk_service.exe", "ogk_tray.exe",
    # Linux system binaries for test environment portability
    "init", "systemd", "bash", "sh", "pytest", "python3.12", "python3.11",
}


def compute_file_sha256(filepath: str, chunk_size: int = 65536) -> Optional[str]:
    """
    Computes the SHA-256 hexadecimal hash of a binary file.
    Returns None if file cannot be read.
    """
    if not os.path.isfile(filepath):
        return None

    sha256 = hashlib.sha256()
    try:
        with open(filepath, "rb") as f:
            while chunk := f.read(chunk_size):
                sha256.update(chunk)
        return sha256.hexdigest().lower()
    except (PermissionError, FileNotFoundError, OSError):
        return None


class ProcessMonitor:
    """
    Monitors running processes, checks names and binary SHA-256 hashes against policy,
    terminates blocked applications, and emits explanatory events (F2.1, F2.2).
    """

    def __init__(
        self,
        scan_interval_seconds: float = 2.0,
        on_process_blocked: Optional[Callable[[Dict[str, Any]], None]] = None,
    ):
        self.scan_interval_seconds = scan_interval_seconds
        self.on_process_blocked = on_process_blocked

        self._lock = threading.Lock()
        self.blocked_names: Set[str] = set()
        self.blocked_hashes: Set[str] = set()
        self.allowed_names: Set[str] = set()
        self.allowed_hashes: Set[str] = set()
        self.study_mode: bool = False

        # In-memory Hash Cache: (filepath, mtime, size) -> sha256
        # Eliminates repeated disk I/O on every 2-second scan loop
        self._hash_cache: Dict[Tuple[str, float, int], str] = {}

        self.is_running = False
        self._thread: Optional[threading.Thread] = None

    def add_blocked_names(self, names: List[str]) -> None:
        with self._lock:
            for name in names:
                self.blocked_names.add(name.strip().lower())

    def add_blocked_hashes(self, hashes: List[str]) -> None:
        with self._lock:
            for h in hashes:
                self.blocked_hashes.add(h.strip().lower())

    def set_study_mode(self, enabled: bool, allowed_names: Optional[List[str]] = None, allowed_hashes: Optional[List[str]] = None) -> None:
        with self._lock:
            self.study_mode = enabled
            if allowed_names is not None:
                self.allowed_names = {n.strip().lower() for n in allowed_names}
            if allowed_hashes is not None:
                self.allowed_hashes = {h.strip().lower() for h in allowed_hashes}

    def get_file_hash_cached(self, filepath: str) -> Optional[str]:
        """
        Retrieves or calculates the SHA-256 hash using an mtime/size cache.
        """
        try:
            stat = os.stat(filepath)
            cache_key = (filepath, stat.st_mtime, stat.st_size)
            if cache_key in self._hash_cache:
                return self._hash_cache[cache_key]

            sha256 = compute_file_sha256(filepath)
            if sha256:
                self._hash_cache[cache_key] = sha256
            return sha256
        except (OSError, PermissionError):
            return None

    def evaluate_process(self, proc: psutil.Process) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Evaluates whether a single process should be blocked.
        Returns: (should_block, reason, file_sha256)
        """
        try:
            name = proc.name().lower()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return False, None, None

        # Ignore protected system processes
        if name in PROTECTED_SYSTEM_PROCESSES:
            return False, None, None

        exe_path: Optional[str] = None
        try:
            exe_path = proc.exe()
        except (psutil.NoSuchProcess, psutil.AccessDenied, OSError):
            pass

        file_hash: Optional[str] = None
        if exe_path:
            file_hash = self.get_file_hash_cached(exe_path)

        with self._lock:
            # 1. Check blocked hash first (F2.1: detects renamed binaries like game.exe -> notepad.exe)
            if file_hash and file_hash in self.blocked_hashes:
                return True, f"Mã băm SHA-256 ({file_hash[:8]}...) nằm trong danh sách cấm.", file_hash

            # 2. Check blocked process name
            if name in self.blocked_names:
                return True, f"Ứng dụng '{name}' nằm trong danh mục hạn chế.", file_hash

            # 3. Check Study Mode (White-list only)
            if self.study_mode:
                is_name_allowed = name in self.allowed_names
                is_hash_allowed = bool(file_hash and file_hash in self.allowed_hashes)
                if not (is_name_allowed or is_hash_allowed):
                    return True, "Chế độ học tập đang bật: chỉ cho phép các ứng dụng học tập được phê duyệt.", file_hash

        return False, None, file_hash

    def scan_and_enforce_once(self) -> List[Dict[str, Any]]:
        """
        Performs a single scan iteration across all running processes.
        Terminates prohibited processes and returns a list of action reports.
        """
        blocked_actions: List[Dict[str, Any]] = []

        for proc in psutil.process_iter(["pid", "name"]):
            try:
                should_block, reason, file_hash = self.evaluate_process(proc)
                if should_block:
                    pid = proc.pid
                    proc_name = proc.name()

                    # Terminate process (F2.2)
                    try:
                        proc.terminate()
                        # Give process a brief grace to terminate gracefully before kill
                        proc.wait(timeout=0.2)
                    except (psutil.TimeoutExpired, psutil.AccessDenied):
                        try:
                            proc.kill()
                        except Exception:
                            pass
                    except psutil.NoSuchProcess:
                        pass

                    action = {
                        "pid": pid,
                        "name": proc_name,
                        "hash": file_hash,
                        "reason": reason,
                        "timestamp": time.time(),
                    }
                    blocked_actions.append(action)
                    logger.warning("Terminated blocked process [PID %d] %s: %s", pid, proc_name, reason)

                    if self.on_process_blocked:
                        self.on_process_blocked(action)

            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
            except Exception as e:
                logger.error("Error evaluating process: %s", e)
                continue

        return blocked_actions

    def _run_loop(self) -> None:
        while self.is_running:
            self.scan_and_enforce_once()
            time.sleep(self.scan_interval_seconds)

    def start(self) -> None:
        if self.is_running:
            return
        self.is_running = True
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
        logger.info("ProcessMonitor started with scan interval %.1fs", self.scan_interval_seconds)

    def stop(self) -> None:
        if not self.is_running:
            return
        self.is_running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.0)
        logger.info("ProcessMonitor stopped.")

