"""
OpenGuard Kids — Desktop Tray State Listener
Monitors Windows Service status via loopback IPC, sends heartbeat every 10s,
and dispatches UI warning events (10m, 5m, 1m, 60s grace, Lock).
Enforces Anti-Abuse Rule (NT1, F5): alerts or shuts down if connection to service is lost > 15s.
"""

from __future__ import annotations

import logging
import threading
import time
from typing import Callable, Dict, Optional, Any

from src.agent.ipc import IPCClient

logger = logging.getLogger("OGK.TrayListener")


class StateListener:
    """
    Background worker for the Tray UI process.
    Polls the Windows Service via IPC, sends heartbeats, and dispatches UI notifications.
    """

    def __init__(
        self,
        ipc_client: IPCClient,
        poll_interval_seconds: float = 2.0,
        on_status_update: Optional[Callable[[Dict[str, Any]], None]] = None,
        on_warning: Optional[Callable[[str, float], None]] = None,
        on_grace_period: Optional[Callable[[float], None]] = None,
        on_lock: Optional[Callable[[str], None]] = None,
        on_unlock: Optional[Callable[[], None]] = None,
        on_connection_lost: Optional[Callable[[], None]] = None,
    ):
        self.client = ipc_client
        self.poll_interval = poll_interval_seconds

        # Callback hooks for UI actions
        self.on_status_update = on_status_update
        self.on_warning = on_warning
        self.on_grace_period = on_grace_period
        self.on_lock = on_lock
        self.on_unlock = on_unlock
        self.on_connection_lost = on_connection_lost

        # Tracking state
        self.is_running = False
        self._thread: Optional[threading.Thread] = None

        self.last_state: Optional[str] = None
        self.last_is_locked: bool = False
        self.warnings_fired: set[str] = set()

        self.last_successful_contact: float = time.time()
        self.connection_lost: bool = False

    def poll_once(self) -> Optional[Dict[str, Any]]:
        """
        Executes a single polling iteration.
        Returns status dictionary or None on failure.
        """
        now = time.time()
        try:
            status = self.client.get_status()
            # Send periodic heartbeat
            self.client.send_heartbeat(now)

            self.last_successful_contact = now
            if self.connection_lost:
                self.connection_lost = False
                logger.info("Reconnected to OGK Service.")

            current_state = status.get("state") or status.get("status", "UNKNOWN")
            is_locked = status.get("is_locked", False)
            remaining = status.get("remaining_seconds", 0.0)

            # 1. State change notifications
            if self.on_status_update:
                self.on_status_update(status)

            # 2. Warning Tiers (10m, 5m, 1m)
            if current_state == "WARNING_10M" and "10M" not in self.warnings_fired:
                self.warnings_fired.add("10M")
                if self.on_warning:
                    self.on_warning("10M", remaining)
            elif current_state == "WARNING_5M" and "5M" not in self.warnings_fired:
                self.warnings_fired.add("5M")
                if self.on_warning:
                    self.on_warning("5M", remaining)
            elif current_state == "WARNING_1M" and "1M" not in self.warnings_fired:
                self.warnings_fired.add("1M")
                if self.on_warning:
                    self.on_warning("1M", remaining)
            elif current_state == "ACTIVE_COUNTING":
                # Clear warning flags if time was added / reset
                self.warnings_fired.clear()

            # 3. 60-second Grace Period
            if current_state == "GRACE_PERIOD_60S" and self.last_state != "GRACE_PERIOD_60S":
                if self.on_grace_period:
                    self.on_grace_period(remaining)

            # 4. Lock / Unlock transitions
            if is_locked and not self.last_is_locked:
                self.last_is_locked = True
                if self.on_lock:
                    self.on_lock(current_state)
            elif not is_locked and self.last_is_locked:
                self.last_is_locked = False
                if self.on_unlock:
                    self.on_unlock()

            self.last_state = current_state
            return status

        except Exception as e:
            # Check if lost connection exceeded 15-second anti-abuse threshold
            elapsed_since_contact = now - self.last_successful_contact
            if elapsed_since_contact > 15.0 and not self.connection_lost:
                self.connection_lost = True
                logger.error("Lost connection to Service for > 15 seconds. Triggering anti-abuse safeguard.")
                if self.on_connection_lost:
                    self.on_connection_lost()
            return None

    def _run_loop(self) -> None:
        while self.is_running:
            self.poll_once()
            time.sleep(self.poll_interval)

    def start(self) -> None:
        if self.is_running:
            return
        self.is_running = True
        self._thread = threading.Thread(target=self._run_loop, daemon=True, name="OGK-Tray-Listener")
        self._thread.start()
        logger.info("StateListener started.")

    def stop(self) -> None:
        if not self.is_running:
            return
        self.is_running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.0)
        logger.info("StateListener stopped.")

