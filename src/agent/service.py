"""
OpenGuard Kids — Master Agent Service & Daemon Orchestrator
Architecture Specification: docs/ARCHITECTURE.md Section 2 & docs/components/01_windows_service_session0.md

Ties together all agent subsystem engines:
  1. ScreenTimeTracker (Quota, 7x48 Schedule, Idle Pause, Clock Rollback Anti-tamper)
  2. DNSProxy (UDP Port 53, SafeSearch CNAME, Canary Domain, Blocklist redirection)
  3. LocalBlockPageServer (HTTP 127.0.0.1:8080, Polite educational notice, Hotline 111)
  4. ProcessMonitor (psutil scanner, binary SHA-256 matching, anti-rename enforcement)
  5. OfflineEventBuffer (SQLite WAL persistent queue, 7-field privacy schema)
  6. IPCManager (Localhost HTTP 127.0.0.1:8765, 64-hex token authentication)
  7. Background Sync Engine (Periodic heartbeat, batch event flushing, WebSocket real-time hub)
"""

from __future__ import annotations

import os
import sys
import time
import json
import signal
import logging
import threading
from typing import Dict, List, Optional, Any, Callable
import httpx

from src.common.constants import (
    DEFAULT_DNS_HOST,
    DEFAULT_DNS_PORT,
    DEFAULT_BLOCKPAGE_HOST,
    DEFAULT_BLOCKPAGE_PORT,
    DEFAULT_IPC_HOST,
    DEFAULT_IPC_PORT,
    DEFAULT_UPSTREAM_DNS,
    DEFAULT_UPSTREAM_PORT,
)
from src.agent.screen_time import ScreenTimeTracker, ScreenTimeState
from src.agent.dns_proxy import DNSProxy
from src.agent.blockpage import LocalBlockPageServer
from src.agent.process_monitor import ProcessMonitor
from src.agent.offline_buffer import OfflineEventBuffer
from src.agent.ipc import IPCManager

logger = logging.getLogger("OGK.AgentService")


class AgentService:
    """
    Unified Orchestrator running as a Windows Service (Session 0)
    or cross-platform daemon process.
    """

    def __init__(
        self,
        device_id: str = "DEV-LOCAL-001",
        child_id: str = "1",
        server_url: Optional[str] = "http://127.0.0.1:8000",
        data_dir: Optional[str] = None,
        dns_port: int = DEFAULT_DNS_PORT,
        blockpage_port: int = DEFAULT_BLOCKPAGE_PORT,
        ipc_port: int = DEFAULT_IPC_PORT,
        daily_limit_minutes: float = 120.0,
        sync_interval_seconds: float = 3.0,
    ):
        self.device_id = device_id
        self.child_id = child_id
        self.server_url = server_url.rstrip("/") if server_url else None
        self.data_dir = data_dir or os.getcwd()
        self.sync_interval_seconds = sync_interval_seconds

        # 1. Initialize SQLite Offline Event Buffer
        db_path = os.path.join(self.data_dir, "offline_events.db")
        self.buffer = OfflineEventBuffer(db_path=db_path)

        # 2. Initialize Screen-Time Tracker & State Machine
        self.tracker = ScreenTimeTracker(
            daily_quota_seconds=int(daily_limit_minutes * 60),
            idle_threshold_seconds=300,
        )

        # Restore accumulated daily screen-time from offline buffer across restart/reboot
        self._last_enqueued_consumed: float = 0.0
        try:
            today_consumed = self.buffer.get_today_screen_time_seconds()
            if today_consumed > 0.0:
                logger.info(f"Restoring consumed screen time today from local buffer: {today_consumed:.1f}s")
                self.tracker.consumed_seconds_today = float(today_consumed)
                self._last_enqueued_consumed = float(today_consumed)
                self.tracker.tick()
        except Exception as e:
            logger.warning(f"Could not restore consumed screen time from local buffer: {e}")

        # 3. Initialize DNS Proxy Engine
        self.dns_proxy = DNSProxy(
            listen_host=DEFAULT_DNS_HOST,
            listen_port=dns_port,
            upstream_host=DEFAULT_UPSTREAM_DNS,
            upstream_port=DEFAULT_UPSTREAM_PORT,
            blockpage_ip=DEFAULT_BLOCKPAGE_HOST,
            on_blocked_callback=self._on_dns_domain_blocked,
        )

        # 4. Initialize Local Educational Blockpage Server
        self.blockpage = LocalBlockPageServer(
            host=DEFAULT_BLOCKPAGE_HOST,
            port=blockpage_port,
            on_unblock_request=self._on_blockpage_child_request,
        )

        # 5. Initialize Process Monitor & SHA-256 Scanner
        self.process_monitor = ProcessMonitor(
            scan_interval_seconds=2.0,
            on_process_blocked=self._on_process_blocked,
        )

        # 6. Initialize Service-to-Tray IPC Server
        self.ipc_manager = IPCManager(
            host=DEFAULT_IPC_HOST,
            port=ipc_port,
            token_dir=self.data_dir,
            status_callback=self.get_status_payload,
            request_callback=self.handle_ipc_child_request,
        )

        # Service lifecycle controls
        self.is_running = False
        self._stop_event = threading.Event()
        self._threads: List[threading.Thread] = []
        self.device_token: str = f"ogk_dev_{self.device_id}"

    # -------------------------------------------------------------------------
    # Callbacks & Event Enqueueing
    # -------------------------------------------------------------------------

    def _on_dns_domain_blocked(self, domain: str, reason: str) -> None:
        logger.info(f"DNS Blocked: {domain} ({reason})")
        self.buffer.enqueue_event(
            device_id=self.device_id,
            child_id=self.child_id,
            event_type="dns_blocked",
            subject=domain,
        )

    def _on_process_blocked(self, event_data: Dict[str, Any]) -> None:
        pname = event_data.get("process_name", "unknown")
        logger.info(f"Process Blocked: {pname} ({event_data.get('reason')})")
        self.buffer.enqueue_event(
            device_id=self.device_id,
            child_id=self.child_id,
            event_type="process_blocked",
            subject=pname,
        )

    def _on_blockpage_child_request(self, domain: str, reason: str) -> None:
        logger.info(f"Child Unblock Request submitted for: {domain}")
        self.buffer.enqueue_event(
            device_id=self.device_id,
            child_id=self.child_id,
            event_type="unblock_request",
            subject=domain,
        )

    def _on_screen_time_warning(self, tier: str, remaining_seconds: float) -> None:
        logger.warning(f"Screen-Time Warning: {tier} (Remaining: {remaining_seconds:.0f}s)")

    def _on_screen_time_grace_period(self) -> None:
        logger.warning("Screen-Time 60-Second Grace Period Triggered!")
        self.buffer.enqueue_event(
            device_id=self.device_id,
            child_id=self.child_id,
            event_type="screen_time_grace",
            subject="60s_grace",
        )

    def _on_screen_time_lock(self, reason: str) -> None:
        logger.warning(f"Screen Locked: {reason}")
        self.buffer.enqueue_event(
            device_id=self.device_id,
            child_id=self.child_id,
            event_type="screen_locked",
            subject=reason,
        )

    def _on_screen_time_unlock(self) -> None:
        logger.info("Screen Unlocked.")
        self.buffer.enqueue_event(
            device_id=self.device_id,
            child_id=self.child_id,
            event_type="screen_unlocked",
            subject="parent_unlock",
        )

    # -------------------------------------------------------------------------
    # IPC Status & Request Handlers
    # -------------------------------------------------------------------------

    def get_status_payload(self) -> Dict[str, Any]:
        """Provides real-time state for Tray UI status polling."""
        return {
            "status": self.tracker.state.value,
            "state": self.tracker.state.value,
            "remaining_seconds": self.tracker.get_remaining_seconds(),
            "consumed_seconds": self.tracker.consumed_seconds_today,
            "daily_quota_seconds": self.tracker.daily_quota_seconds,
            "is_locked": self.tracker.is_locked(),
            "lock_reason": (
                "LOCKED_URGENT" if self.tracker.urgent_lock else (
                    "LOCKED_SCHEDULE" if self.tracker.state == ScreenTimeState.LOCKED_SCHEDULE else (
                        "LOCKED_QUOTA" if self.tracker.state == ScreenTimeState.LOCKED_QUOTA else None
                    )
                )
            ),
            "study_mode": self.dns_proxy.study_mode,
            "timestamp": time.time(),
        }

    def handle_ipc_child_request(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handles child agency actions submitted from Tray UI."""
        req_type = payload.get("type") or payload.get("request_type")
        if req_type in ("ADD_TIME", "MORE_TIME", "REQUEST_MORE_TIME"):
            mins = int(payload.get("minutes", 15))
            reason = payload.get("reason") or payload.get("subject") or "Xin thêm thời gian học tập"
            self.buffer.enqueue_event(
                device_id=self.device_id,
                child_id=self.child_id,
                event_type="time_extension_request",
                subject=reason,
                duration_sec=mins * 60,
            )
            return {"status": "SUCCESS", "message": f"Yêu cầu xin thêm {mins} phút đã được gửi tới phụ huynh."}

        elif req_type in ("UNBLOCK_DOMAIN", "UNBLOCK_REQUEST"):
            domain = payload.get("domain") or payload.get("subject", "")
            self.buffer.enqueue_event(
                device_id=self.device_id,
                child_id=self.child_id,
                event_type="unblock_request",
                subject=domain,
            )
            return {"status": "SUCCESS", "message": f"Đã gửi báo cáo xem xét tên miền {domain}."}

        return {"status": "UNKNOWN_REQUEST"}

    # -------------------------------------------------------------------------
    # Background Workers & Sync
    # -------------------------------------------------------------------------

    def _flush_active_screen_time_to_buffer(self, min_seconds: float = 1.0) -> None:
        """Enqueues accumulated active usage as a screen_time event."""
        curr_consumed = self.tracker.consumed_seconds_today
        if curr_consumed < self._last_enqueued_consumed:
            # Midnight reset occurred
            self._last_enqueued_consumed = 0.0

        elapsed = curr_consumed - self._last_enqueued_consumed
        if elapsed >= min_seconds:
            dur = int(elapsed)
            if dur > 0:
                self.buffer.enqueue_event(
                    device_id=self.device_id,
                    child_id=self.child_id,
                    event_type="screen_time",
                    subject="active_usage",
                    duration_sec=dur,
                )
                self._last_enqueued_consumed += dur

    def _screen_time_worker(self) -> None:
        """Main active screen-time tracking loop running at 1.0 Hz."""
        while not self._stop_event.is_set():
            try:
                prev_state = self.tracker.state
                curr_state = self.tracker.tick()

                curr_consumed = self.tracker.consumed_seconds_today
                if curr_consumed < self._last_enqueued_consumed:
                    self._last_enqueued_consumed = 0.0

                elapsed_active = curr_consumed - self._last_enqueued_consumed
                state_changed = (curr_state != prev_state)

                # Periodically (>= 15s) or on state change (>= 1s), enqueue screen_time event
                if (elapsed_active >= 15.0) or (state_changed and elapsed_active >= 1.0):
                    self._flush_active_screen_time_to_buffer(min_seconds=1.0)

            except Exception as e:
                logger.error(f"Error in screen-time tick loop: {e}", exc_info=True)
            self._stop_event.wait(1.0)

    def _sync_worker(self) -> None:
        """Periodic background sync to cloud/backend server."""
        while not self._stop_event.is_set():
            if self.server_url:
                try:
                    self._perform_heartbeat_and_flush()
                except Exception as e:
                    logger.debug(f"Sync attempt skipped or failed (offline resilience): {e}")

            self._stop_event.wait(self.sync_interval_seconds)

    def _websocket_worker(self) -> None:
        """Persistent WebSocket client connecting to /ws/v1/agent/{device_id}."""
        if not self.server_url:
            return

        from websockets.sync.client import connect as ws_connect

        base = self.server_url.rstrip("/")
        if base.startswith("https://"):
            ws_url = "wss://" + base[8:] + f"/ws/v1/agent/{self.device_id}"
        elif base.startswith("http://"):
            ws_url = "ws://" + base[7:] + f"/ws/v1/agent/{self.device_id}"
        else:
            ws_url = f"ws://{base}/ws/v1/agent/{self.device_id}"

        last_ping_time = 0.0

        while not self._stop_event.is_set():
            try:
                logger.info(f"Connecting to agent WebSocket at {ws_url}...")
                with ws_connect(ws_url, open_timeout=4.0) as ws:
                    logger.info(f"Connected to agent WebSocket at {ws_url}")
                    # Send initial handshake ping
                    try:
                        ws.send(json.dumps({
                            "type": "hello",
                            "device_id": self.device_id,
                            "child_id": str(self.child_id),
                            "status": self.tracker.state.value,
                            "remaining_seconds": self.tracker.get_remaining_seconds(),
                        }))
                    except Exception:
                        pass

                    while not self._stop_event.is_set():
                        now = time.time()
                        if now - last_ping_time >= 10.0:
                            try:
                                ws.send(json.dumps({
                                    "type": "ping",
                                    "device_id": self.device_id,
                                    "status": self.tracker.state.value,
                                    "remaining_seconds": self.tracker.get_remaining_seconds(),
                                    "timestamp": now,
                                }))
                                last_ping_time = now
                            except Exception:
                                break

                        try:
                            msg_str = ws.recv(timeout=1.0)
                            if msg_str:
                                try:
                                    cmd_data = json.loads(msg_str)
                                    logger.info(f"WebSocket received command: {cmd_data}")
                                    self._apply_server_command(cmd_data)
                                except Exception as json_err:
                                    logger.warning(f"Error parsing WebSocket message: {json_err}")
                        except TimeoutError:
                            continue
                        except Exception:
                            break
            except Exception as conn_err:
                logger.debug(f"WebSocket connection error: {conn_err}")

            # Reconnection backoff: check stop_event every 0.2s
            for _ in range(10):
                if self._stop_event.is_set():
                    break
                time.sleep(0.2)

    def _perform_heartbeat_and_flush(self) -> None:
        if not self.server_url:
            return

        # Ensure latest active usage is flushed to offline buffer before sync
        self._flush_active_screen_time_to_buffer(min_seconds=1.0)

        with httpx.Client(timeout=4.0) as client:
            # 1. Send periodic heartbeat
            hb_payload = {
                "device_id": self.device_id,
                "child_id": str(self.child_id),
                "status": self.tracker.state.value,
                "screen_time_remaining": self.tracker.get_remaining_seconds(),
                "remaining_seconds": self.tracker.get_remaining_seconds(),
                "is_locked": self.tracker.is_locked(),
            }
            try:
                hb_res = client.post(f"{self.server_url}/api/v1/heartbeat", json=hb_payload)
                if hb_res.status_code == 200:
                    data = hb_res.json()
                    # Check for urgent commands queued during offline fallback
                    commands = data.get("pending_commands", [])
                    for cmd in commands:
                        self._apply_server_command(cmd)
            except Exception:
                pass

            # 2. Flush offline buffer batch
            batch = self.buffer.peek_unsynced_batch(limit=50)
            if batch:
                events_payload = [
                    {
                        "id": row["id"],
                        "device_id": row["device_id"],
                        "child_id": str(row["child_id"]),
                        "type": row["type"],
                        "subject": row["subject"],
                        "duration_sec": row.get("duration_sec", 0),
                        "ts": row["ts"],
                        "idempotency_key": row["idempotency_key"],
                    }
                    for row in batch
                ]
                try:
                    sync_res = client.post(
                        f"{self.server_url}/api/v1/events/batch",
                        json={"events": events_payload},
                    )
                    if sync_res.status_code in (200, 201):
                        synced_keys = [row["idempotency_key"] for row in batch]
                        self.buffer.acknowledge_synced(synced_keys)
                        logger.info(f"Successfully synced batch of {len(synced_keys)} events to server.")
                except Exception:
                    pass

    def _apply_server_command(self, cmd: Dict[str, Any]) -> None:
        """Applies real-time commands from parent."""
        cmd_type = cmd.get("command") or cmd.get("type")
        payload = cmd.get("payload", {})
        logger.info(f"Applying server command: {cmd_type} -> {payload}")

        if cmd_type == "LOCK_URGENT":
            self.tracker.set_urgent_lock(True)
            logger.info("🔒 [LOCK_URGENT] Nhận lệnh KHÓA KHẨN CẤP từ phụ huynh!")

        elif cmd_type == "UNLOCK":
            self.tracker.set_urgent_lock(False)
            logger.info("🔓 [UNLOCK] Nhận lệnh MỞ KHÓA từ phụ huynh!")

        elif cmd_type == "ADD_TIME":
            bonus_minutes = int(payload.get("minutes", 15))
            self.tracker.add_bonus_time(bonus_minutes)
            rem = self.tracker.get_remaining_seconds()
            logger.info(f"✨ [ADD_TIME] Đã cộng thêm {bonus_minutes} phút! Thời gian còn lại: {rem/60:.1f} phút.")

        elif cmd_type == "POLICY_UPDATE":
            logger.info("📋 [POLICY_UPDATE] Nhận thông báo cập nhật chính sách từ phụ huynh!")
            self._fetch_and_apply_policy(payload.get("policy"))

        elif cmd_type in ("PURGE_DATA", "PURGE_LOCAL_CACHE"):
            child_id_to_purge = str(payload.get("child_id", self.child_id))
            purged = self.buffer.purge_child_events(child_id_to_purge)
            logger.info(f"🗑️ [PURGE_DATA] Đã xóa {purged} bản ghi sự kiện theo lệnh phụ huynh.")

    def _fetch_and_apply_policy(self, embedded_policy: Optional[Dict[str, Any]] = None) -> None:
        """Fetches or applies latest policy across ScreenTimeTracker, DNSProxy, and ProcessMonitor."""
        policy_data = embedded_policy
        if not policy_data and self.server_url:
            headers = {"Authorization": f"Bearer {self.device_token}"}
            try:
                with httpx.Client(timeout=4.0) as client:
                    res = client.get(
                        f"{self.server_url}/api/v1/devices/{self.device_id}/policy",
                        headers=headers,
                    )
                    if res.status_code == 200:
                        policy_data = res.json()
            except Exception as e:
                logger.error(f"Error fetching policy from server: {e}")

        if not policy_data:
            return

        logger.info(f"Applying policy update: v{policy_data.get('version', 'unknown')}")

        # 1. Update ScreenTimeTracker
        self.tracker.update_policy(policy_data)

        # 2. Update DNSProxy
        blocklist = policy_data.get("blocklist") or []
        whitelist = policy_data.get("whitelist") or []
        study_mode = bool(policy_data.get("study_mode", False))
        with self.dns_proxy._lock:
            self.dns_proxy.blocklist = {d.strip().lower().rstrip(".") for d in blocklist}
            self.dns_proxy.whitelist = {d.strip().lower().rstrip(".") for d in whitelist}
            self.dns_proxy.study_mode = study_mode

        # 3. Update ProcessMonitor
        blocked_apps = policy_data.get("blocked_apps") or []
        app_names = []
        app_hashes = []
        for item in blocked_apps:
            if isinstance(item, dict):
                if item.get("name"):
                    app_names.append(item["name"])
                if item.get("sha256"):
                    app_hashes.append(item["sha256"])
            elif isinstance(item, str):
                if len(item) == 64:
                    app_hashes.append(item)
                else:
                    app_names.append(item)
        with self.process_monitor._lock:
            self.process_monitor.blocked_names = {n.strip().lower() for n in app_names}
            self.process_monitor.blocked_hashes = {h.strip().lower() for h in app_hashes}
            self.process_monitor.study_mode = study_mode

        logger.info("Policy successfully applied to ScreenTimeTracker, DNSProxy, and ProcessMonitor.")

    # -------------------------------------------------------------------------
    # Lifecycle Controls
    # -------------------------------------------------------------------------

    def start(self) -> None:
        """Starts all engines and worker threads."""
        if self.is_running:
            return

        logger.info("Starting OpenGuard Kids Agent Service...")
        self.is_running = True
        self._stop_event.clear()

        # 1. Start DNS Proxy
        try:
            self.dns_proxy.start()
        except Exception as e:
            logger.warning(f"Could not bind DNS port 53 (requires root/admin or alternative port): {e}")

        # 2. Start Blockpage Server
        try:
            self.blockpage.start()
        except Exception as e:
            logger.warning(f"Could not start blockpage server: {e}")

        # 3. Start Process Monitor
        try:
            self.process_monitor.start()
        except Exception as e:
            logger.warning(f"Could not start process monitor: {e}")

        # 4. Start Local IPC Manager
        self.ipc_manager.start()

        # Ensure latest consumed screen-time is refreshed prior to thread startup
        try:
            today_consumed = self.buffer.get_today_screen_time_seconds()
            if today_consumed > self.tracker.consumed_seconds_today:
                self.tracker.consumed_seconds_today = float(today_consumed)
                self._last_enqueued_consumed = float(today_consumed)
                self.tracker.tick()
        except Exception as e:
            logger.warning(f"Could not refresh consumed screen time from local buffer: {e}")

        # 5. Start Background Workers
        t_tracker = threading.Thread(target=self._screen_time_worker, name="OGK-ScreenTimeWorker", daemon=True)
        t_sync = threading.Thread(target=self._sync_worker, name="OGK-SyncWorker", daemon=True)
        t_tracker.start()
        t_sync.start()
        self._threads.extend([t_tracker, t_sync])

        if self.server_url:
            t_ws = threading.Thread(target=self._websocket_worker, name="OGK-WebSocketWorker", daemon=True)
            t_ws.start()
            self._threads.append(t_ws)

        logger.info("OpenGuard Kids Agent Service is fully operational.")

    def stop(self) -> None:
        """Gracefully shuts down all components."""
        was_running = self.is_running
        self.is_running = False
        self._stop_event.set()

        logger.info("Stopping OpenGuard Kids Agent Service...")

        if was_running:
            # Flush any remaining accumulated active screen-time to buffer
            try:
                self._flush_active_screen_time_to_buffer(min_seconds=1.0)
            except Exception:
                pass

        # Always stop IPC manager to close listening socket and avoid port leaks,
        # even if start() was not called or service was already stopped
        try:
            if hasattr(self, "ipc_manager") and self.ipc_manager:
                self.ipc_manager.stop()
        except Exception:
            pass

        if not was_running:
            return

        # Stop engines in reverse order
        try:
            self.process_monitor.stop()
        except Exception:
            pass

        try:
            self.blockpage.stop()
        except Exception:
            pass

        try:
            self.dns_proxy.stop()
        except Exception:
            pass

        for t in self._threads:
            t.join(timeout=1.5)
        self._threads.clear()

        logger.info("OpenGuard Kids Agent Service stopped successfully.")

    def run(self) -> None:
        """Blocking run loop with signal handling for standalone/daemon mode."""
        self.start()

        def _signal_handler(sig, frame):
            logger.info("Termination signal received. Exiting...")
            self.stop()
            sys.exit(0)

        try:
            signal.signal(signal.SIGINT, _signal_handler)
            signal.signal(signal.SIGTERM, _signal_handler)
        except Exception:
            pass

        while self.is_running:
            time.sleep(0.5)


# -----------------------------------------------------------------------------
# Optional Windows Service Framework Integration
# -----------------------------------------------------------------------------
if sys.platform == "win32":
    try:
        import win32serviceutil
        import win32service
        import win32event

        class OpenGuardKidsWindowsService(win32serviceutil.ServiceFramework):
            _svc_name_ = "OpenGuardKidsService"
            _svc_display_name_ = "OpenGuard Kids Parental Protection Service"
            _svc_description_ = "Windows Service bảo vệ thời gian và nội dung sử dụng máy tính của trẻ em (OpenGuard Kids)."

            def __init__(self, args):
                super().__init__(args)
                self.stop_event = win32event.CreateEvent(None, 0, 0, None)
                self.agent_service = AgentService()

            def SvcStop(self):
                self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
                win32event.SetEvent(self.stop_event)
                self.agent_service.stop()

            def SvcDoRun(self):
                self.agent_service.start()
                while self.agent_service.is_running:
                    rc = win32event.WaitForSingleObject(self.stop_event, 1000)
                    if rc == win32event.WAIT_OBJECT_0:
                        break
    except ImportError:
        pass
