"""
OpenGuard Kids — Service-to-Tray IPC Engine (Localhost HTTP with Bearer Token)
Architecture Specification: docs/ARCHITECTURE.md Section 3.1
"""

import os
import json
import secrets
import logging
import threading
from typing import Dict, Any, Optional, Callable
from http.server import HTTPServer, BaseHTTPRequestHandler
import httpx

from src.common.constants import DEFAULT_IPC_HOST, DEFAULT_IPC_PORT, TOKEN_FILE_NAME

logger = logging.getLogger("OGK.IPC")


class IPCHandler(BaseHTTPRequestHandler):
    """HTTP Request Handler with strict Bearer Token authentication."""

    server: "IPCServer"

    def log_message(self, format, *args):
        # Suppress noisy standard HTTP access logs
        return

    def _verify_token(self) -> bool:
        auth_header = self.headers.get("X-OGK-Token")
        if not auth_header or not secrets.compare_digest(auth_header, self.server.secret_token):
            self.send_response(403)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Forbidden: Invalid or missing IPC token"}).encode("utf-8"))
            return False
        return True

    def do_GET(self):
        if not self._verify_token():
            return

        if self.path == "/status":
            status_data = self.server.status_callback() if self.server.status_callback else {
                "status": "RUNNING",
                "remaining_seconds": 3600,
                "policy_version": 1,
            }
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(status_data).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if not self._verify_token():
            return

        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)
        payload = json.loads(body.decode("utf-8")) if body else {}

        if self.path == "/heartbeat":
            self.server.last_tray_heartbeat = payload.get("timestamp", 0)
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "OK"}).encode("utf-8"))

        elif self.path == "/request":
            if self.server.request_callback:
                res = self.server.request_callback(payload)
            else:
                res = {"status": "RECEIVED"}
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(res).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()


class IPCServer(HTTPServer):
    allow_reuse_address = True

    def __init__(
        self,
        host: str = DEFAULT_IPC_HOST,
        port: int = DEFAULT_IPC_PORT,
        token_dir: Optional[str] = None,
        status_callback: Optional[Callable[[], Dict[str, Any]]] = None,
        request_callback: Optional[Callable[[Dict[str, Any]], Dict[str, Any]]] = None,
    ):
        super().__init__((host, port), IPCHandler)
        self.secret_token = secrets.token_hex(32)  # 64 hex characters
        self.status_callback = status_callback
        self.request_callback = request_callback
        self.last_tray_heartbeat = 0.0

        # Persist token to disk with restricted permissions
        self.token_dir = token_dir or os.getcwd()
        self.token_file = os.path.join(self.token_dir, TOKEN_FILE_NAME)
        self._write_token_file()

    def _write_token_file(self):
        os.makedirs(self.token_dir, exist_ok=True)
        with open(self.token_file, "w", encoding="utf-8") as f:
            f.write(self.secret_token)
        try:
            # Set read/write only by owner on Unix-like environments
            os.chmod(self.token_file, 0o600)
        except Exception:
            pass


class IPCManager:
    """Manager to spin up and shut down the IPC Server in a background thread."""

    def __init__(
        self,
        host: str = DEFAULT_IPC_HOST,
        port: int = DEFAULT_IPC_PORT,
        token_dir: Optional[str] = None,
        status_callback: Optional[Callable[[], Dict[str, Any]]] = None,
        request_callback: Optional[Callable[[Dict[str, Any]], Dict[str, Any]]] = None,
    ):
        self.server = IPCServer(
            host=host,
            port=port,
            token_dir=token_dir,
            status_callback=status_callback,
            request_callback=request_callback,
        )
        self._thread: Optional[threading.Thread] = None

    @property
    def secret_token(self) -> str:
        return self.server.secret_token

    @property
    def port(self) -> int:
        return self.server.server_address[1]

    def start(self):
        self._thread = threading.Thread(target=self.server.serve_forever, daemon=True, name="OGK-IPC-Server")
        self._thread.start()
        logger.info(f"IPC Server running on {self.server.server_address}")

    def stop(self):
        # Only invoke shutdown if serve_forever is actually running in another thread to avoid deadlock
        if self._thread and self._thread.is_alive():
            self.server.shutdown()
        self.server.server_close()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2.0)
        # Clean up token file
        if hasattr(self.server, "token_file") and os.path.exists(self.server.token_file):
            try:
                os.remove(self.server.token_file)
            except Exception:
                pass


class IPCClient:
    """Client used by Tray UI (Session 1) to communicate with Service (Session 0)."""

    def __init__(
        self,
        host: str = DEFAULT_IPC_HOST,
        port: int = DEFAULT_IPC_PORT,
        token: Optional[str] = None,
        token_file: Optional[str] = None,
        secret_token: Optional[str] = None,
    ):
        self.base_url = f"http://{host}:{port}"
        self.token_file = token_file or os.path.join(os.getcwd(), TOKEN_FILE_NAME)
        self.token = secret_token or token
        if not self.token and os.path.exists(self.token_file):
            with open(self.token_file, "r", encoding="utf-8") as f:
                self.token = f.read().strip()

    def _reload_token_from_file(self) -> bool:
        """Reloads the token from disk if the Agent Service was restarted."""
        if self.token_file and os.path.exists(self.token_file):
            try:
                with open(self.token_file, "r", encoding="utf-8") as f:
                    disk_token = f.read().strip()
                if disk_token and disk_token != self.token:
                    self.token = disk_token
                    return True
            except Exception:
                pass
        return False

    def _headers(self) -> Dict[str, str]:
        return {"X-OGK-Token": self.token or ""}

    def get_status(self) -> Dict[str, Any]:
        with httpx.Client(timeout=3.0) as client:
            resp = client.get(f"{self.base_url}/status", headers=self._headers())
            if resp.status_code == 403 and self._reload_token_from_file():
                resp = client.get(f"{self.base_url}/status", headers=self._headers())
            resp.raise_for_status()
            return resp.json()

    def send_heartbeat(self, timestamp: float) -> bool:
        with httpx.Client(timeout=3.0) as client:
            resp = client.post(f"{self.base_url}/heartbeat", headers=self._headers(), json={"timestamp": timestamp})
            if resp.status_code == 403 and self._reload_token_from_file():
                resp = client.post(f"{self.base_url}/heartbeat", headers=self._headers(), json={"timestamp": timestamp})
            return resp.status_code == 200

    def send_request(self, req_type: str, minutes: int = 15, subject: str = "") -> Dict[str, Any]:
        return self.send_child_request(req_type, {"minutes": minutes, "subject": subject, "reason": subject})

    def send_child_request(self, req_type: str, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        data = {"type": req_type, "request_type": req_type}
        if payload:
            data.update(payload)
        with httpx.Client(timeout=3.0) as client:
            resp = client.post(
                f"{self.base_url}/request",
                headers=self._headers(),
                json=data,
            )
            if resp.status_code == 403 and self._reload_token_from_file():
                resp = client.post(
                    f"{self.base_url}/request",
                    headers=self._headers(),
                    json=data,
                )
            resp.raise_for_status()
            return resp.json()
