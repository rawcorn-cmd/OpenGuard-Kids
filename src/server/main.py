"""
OpenGuard Kids — Backend Server Entrypoint
Usage:
    python -m src.server.main [--host 127.0.0.1] [--port 8000] [--reload]
"""

from __future__ import annotations

import argparse
import sys
import uvicorn

from src.server.app import app


def main():
    parser = argparse.ArgumentParser(description="OpenGuard Kids Backend Server")
    parser.add_argument("--host", default="127.0.0.1", help="Host interface to bind (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8000, help="Port to listen on (default: 8000)")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload for development")
    args = parser.parse_args()

    print("=" * 70)
    print("  OPENGUARD KIDS — PARENT BACKEND API & DASHBOARD SERVER")
    print(f"  Listening on: http://{args.host}:{args.port}")
    print(f"  Parent Web Dashboard: http://{args.host}:{args.port}/dashboard/1")
    print(f"  API Documentation:    http://{args.host}:{args.port}/docs")
    print("=" * 70)

    uvicorn.run("src.server.app:app", host=args.host, port=args.port, reload=args.reload)


if __name__ == "__main__":
    main()

