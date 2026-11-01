"""
OpenGuard Kids — Agent Service & Daemon Entrypoint
Usage:
    python -m src.agent.main [--server-url http://127.0.0.1:8000] [--data-dir ./data]
"""

from __future__ import annotations

import argparse
import logging
import sys

from src.agent.service import AgentService
from src.common.constants import DEFAULT_DNS_PORT, DEFAULT_BLOCKPAGE_PORT, DEFAULT_IPC_PORT

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
    datefmt="%H:%M:%S",
)


def main():
    parser = argparse.ArgumentParser(description="OpenGuard Kids Agent Daemon Service")
    parser.add_argument("--server-url", default="http://127.0.0.1:8000", help="Backend cloud server URL")
    parser.add_argument("--device-id", default="DEV-LOCAL-001", help="Device identifier")
    parser.add_argument("--child-id", default="1", help="Child profile identifier")
    parser.add_argument("--data-dir", default=None, help="Directory for local SQLite buffer and tokens")
    parser.add_argument("--dns-port", type=int, default=DEFAULT_DNS_PORT, help="Port for DNS proxy (default: 53)")
    parser.add_argument("--blockpage-port", type=int, default=DEFAULT_BLOCKPAGE_PORT, help="Port for blockpage (default: 8080)")
    parser.add_argument("--ipc-port", type=int, default=DEFAULT_IPC_PORT, help="Port for Tray IPC (default: 8765)")
    parser.add_argument("--quota-mins", type=float, default=120.0, help="Daily screen-time quota in minutes")
    parser.add_argument("--sync-interval", type=float, default=3.0, help="Sync interval with server in seconds")
    args = parser.parse_args()

    print("=" * 70)
    print("  OPENGUARD KIDS — LOCAL ENFORCEMENT AGENT SERVICE (SESSION 0)")
    print(f"  Device ID:         {args.device_id} (Child ID: {args.child_id})")
    print(f"  Backend Sync:      {args.server_url}")
    print(f"  DNS Proxy Port:    {args.dns_port} (UDP)")
    print(f"  Blockpage Server:  http://127.0.0.1:{args.blockpage_port}")
    print(f"  Tray IPC Endpoint: http://127.0.0.1:{args.ipc_port}")
    print(f"  Daily Quota:       {args.quota_mins:.0f} minutes")
    print("=" * 70)

    service = AgentService(
        device_id=args.device_id,
        child_id=args.child_id,
        server_url=args.server_url,
        data_dir=args.data_dir,
        dns_port=args.dns_port,
        blockpage_port=args.blockpage_port,
        ipc_port=args.ipc_port,
        daily_limit_minutes=args.quota_mins,
        sync_interval_seconds=args.sync_interval,
    )
    service.run()


if __name__ == "__main__":
    main()

