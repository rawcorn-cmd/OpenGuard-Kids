"""
OpenGuard Kids — Desktop Tray UI Application Entrypoint
Usage:
    python -m src.tray.main [--token-dir ./data] [--ipc-port 8765]
"""

from __future__ import annotations

import argparse
import os
import sys
import time
import signal
import logging

from src.agent.ipc import IPCClient
from src.tray.app import TrayAppController
from src.common.constants import DEFAULT_IPC_HOST, DEFAULT_IPC_PORT, TOKEN_FILE_NAME

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [TrayUI] %(message)s",
    datefmt="%H:%M:%S",
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)
logger = logging.getLogger("OGK.TrayMain")


def default_ui_display(event_type: str, data: dict):
    """Console UI visualizer for cross-platform demonstration."""
    if event_type == "STATUS_UPDATE":
        rem = data.get("remaining_seconds", 0)
        status = data.get("status") or data.get("state", "UNKNOWN")
        sys.stdout.write(f"\r[Tray State] Status: {status:<15} | Còn lại: {rem/60:05.1f} phút  ")
        sys.stdout.flush()
    elif event_type == "BONUS_TIME_ADDED":
        print(f"\n✨ [CỘNG THÊM GIỜ] {data.get('title')}: {data.get('message')}")
    elif event_type == "WARNING_TOAST":
        print(f"\n🔔 [CẢNH BÁO THỜI GIAN] {data.get('title')}: {data.get('message')}")
    elif event_type in ("GRACE_PERIOD", "GRACE_PERIOD_DIALOG"):
        print(f"\n⏳ [60 GIÂY ÂN HẠN] {data.get('title')}: {data.get('message')}")
    elif event_type in ("LOCK_OVERLAY", "LOCK_SCREEN"):
        print(f"\n🔒 [MÀN HÌNH KHÓA] {data.get('title')}: {data.get('message')}")
    elif event_type in ("UNLOCK", "UNLOCK_SCREEN"):
        print(f"\n🔓 [MỞ KHÓA] {data.get('message')}")
    elif event_type == "CONNECTION_LOST":
        print(f"\n⚠️ [MẤT KẾT NỐI SERVICE] {data.get('message')}")


def main():
    parser = argparse.ArgumentParser(description="OpenGuard Kids Desktop Tray UI")
    parser.add_argument("--ipc-host", default=DEFAULT_IPC_HOST, help="IPC server host")
    parser.add_argument("--ipc-port", type=int, default=DEFAULT_IPC_PORT, help="IPC server port")
    parser.add_argument("--token-dir", default=None, help="Directory containing ipc_secret.token")
    parser.add_argument("--token", default=None, help="Explicit 64-hex IPC secret token")
    args = parser.parse_args()

    token_dir = args.token_dir or os.getcwd()
    secret_token = args.token

    if not secret_token:
        token_path = os.path.join(token_dir, TOKEN_FILE_NAME)
        if os.path.isfile(token_path):
            with open(token_path, "r", encoding="utf-8") as f:
                secret_token = f.read().strip()
        else:
            print(f"Error: Token file not found at {token_path}. Is the Agent Service running?")
            sys.exit(1)

    print("=" * 70)
    print("  OPENGUARD KIDS — DESKTOP TRAY UI INTERFACE (SESSION 1)")
    print(f"  Connected to IPC: http://{args.ipc_host}:{args.ipc_port}")
    print(f"  Token Preview:    {secret_token[:8]}...{secret_token[-8:]}")
    print("=" * 70)

    client = IPCClient(host=args.ipc_host, port=args.ipc_port, secret_token=secret_token)
    controller = TrayAppController(ipc_client=client, ui_notifier=default_ui_display)

    controller.start()

    def _sig_handler(sig, frame):
        print("\nStopping Tray UI...")
        controller.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, _sig_handler)
    signal.signal(signal.SIGTERM, _sig_handler)

    try:
        while True:
            time.sleep(0.5)
    except KeyboardInterrupt:
        controller.stop()


if __name__ == "__main__":
    main()

