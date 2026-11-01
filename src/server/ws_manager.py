"""
OpenGuard Kids — WebSocket Connection Manager & Urgent Command Dispatcher
Provides low-latency (<5s) real-time bidirectional messaging between Parents and Windows Agents.
"""

from __future__ import annotations

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional
from fastapi import WebSocket

logger = logging.getLogger("OpenGuardKids.WebSocket")


class ConnectionManager:
    """
    Manages active WebSocket connections from enrolled devices and parent dashboards.
    """

    def __init__(self):
        # device_id -> active WebSocket
        self.device_connections: Dict[str, WebSocket] = {}
        # parent_id -> list of active WebSockets
        self.parent_connections: Dict[str, List[WebSocket]] = {}
        # Fallback offline command queue: device_id -> list of pending commands
        self.pending_commands: Dict[str, List[Dict[str, Any]]] = {}

    def is_device_online(self, device_id: str) -> bool:
        """Checks if a device has an active WebSocket connection."""
        return device_id in self.device_connections

    async def connect_device(self, device_id: str, websocket: WebSocket) -> None:
        await websocket.accept()
        self.device_connections[device_id] = websocket
        logger.info("Device connected to WebSocket: %s", device_id)

    def disconnect_device(self, device_id: str) -> None:
        self.device_connections.pop(device_id, None)
        logger.info("Device disconnected from WebSocket: %s", device_id)

    async def connect_parent(self, parent_id: str, websocket: WebSocket) -> None:
        await websocket.accept()
        if parent_id not in self.parent_connections:
            self.parent_connections[parent_id] = []
        self.parent_connections[parent_id].append(websocket)
        logger.info("Parent connected to WebSocket: %s", parent_id)

    def disconnect_parent(self, parent_id: str, websocket: WebSocket) -> None:
        if parent_id in self.parent_connections:
            if websocket in self.parent_connections[parent_id]:
                self.parent_connections[parent_id].remove(websocket)
            if not self.parent_connections[parent_id]:
                del self.parent_connections[parent_id]
        logger.info("Parent disconnected from WebSocket: %s", parent_id)

    async def dispatch_urgent_command(
        self,
        device_id: str,
        command_type: str,
        payload: Dict[str, Any] | None = None,
        db_session: Any | None = None,
    ) -> bool:
        """
        Dispatches urgent command ('LOCK_URGENT', 'UNLOCK', 'ADD_TIME') to agent.
        Returns True if sent immediately via WebSocket (< 5s), False if queued for heartbeat.
        If device is offline, persists a PendingCommand record to SQLite database.
        """
        payload = payload or {}
        msg = {
            "type": "URGENT_COMMAND",
            "command": command_type,
            "payload": payload,
        }

        ws = self.device_connections.get(device_id)
        if ws:
            try:
                await ws.send_json(msg)
                logger.info("Dispatched urgent command '%s' to device %s via WebSocket", command_type, device_id)
                return True
            except Exception as e:
                logger.warning("Failed to send WS message to %s, queueing fallback: %s", device_id, e)
                self.disconnect_device(device_id)

        # Fallback: Enqueue for next HTTP heartbeat
        if device_id not in self.pending_commands:
            self.pending_commands[device_id] = []
        self.pending_commands[device_id].append(msg)

        # Persist to SQLite database so commands survive server restart
        if db_session is not None:
            try:
                from src.server.models import PendingCommand
                pending_rec = PendingCommand(
                    device_id=device_id,
                    command_type=command_type,
                    payload_json=json.dumps(payload),
                )
                db_session.add(pending_rec)
                db_session.commit()
                logger.info("Persisted PendingCommand for device %s to SQLite", device_id)
            except Exception as e:
                logger.error("Failed to persist PendingCommand to db: %s", e)
        else:
            try:
                from src.server.database import SessionLocal
                from src.server.models import PendingCommand
                with SessionLocal() as db:
                    pending_rec = PendingCommand(
                        device_id=device_id,
                        command_type=command_type,
                        payload_json=json.dumps(payload),
                    )
                    db.add(pending_rec)
                    db.commit()
            except Exception as e:
                logger.debug("Optional db persistence fallback without db_session skipped: %s", e)

        logger.info("Queued command '%s' for device %s (Heartbeat fallback)", command_type, device_id)
        return False

    def pop_pending_commands(self, device_id: str, db_session: Any | None = None) -> List[Dict[str, Any]]:
        """Retrieves and clears pending commands for a device upon HTTP heartbeat from SQLite and memory."""
        results: List[Dict[str, Any]] = []

        # 1. Drain from SQLite database if db_session is provided
        if db_session is not None:
            try:
                from src.server.models import PendingCommand
                records = (
                    db_session.query(PendingCommand)
                    .filter(PendingCommand.device_id == device_id)
                    .order_by(PendingCommand.id.asc())
                    .all()
                )
                for rec in records:
                    try:
                        p_data = json.loads(rec.payload_json) if rec.payload_json else {}
                    except Exception:
                        p_data = {}
                    results.append({
                        "type": "URGENT_COMMAND",
                        "command": rec.command_type,
                        "payload": p_data,
                    })
                    db_session.delete(rec)
                if records:
                    db_session.commit()
            except Exception as e:
                logger.error("Failed to pop pending commands from SQLite db: %s", e)
        else:
            try:
                from src.server.database import SessionLocal
                from src.server.models import PendingCommand
                with SessionLocal() as db:
                    records = (
                        db.query(PendingCommand)
                        .filter(PendingCommand.device_id == device_id)
                        .order_by(PendingCommand.id.asc())
                        .all()
                    )
                    for rec in records:
                        try:
                            p_data = json.loads(rec.payload_json) if rec.payload_json else {}
                        except Exception:
                            p_data = {}
                        results.append({
                            "type": "URGENT_COMMAND",
                            "command": rec.command_type,
                            "payload": p_data,
                        })
                        db.delete(rec)
                    if records:
                        db.commit()
            except Exception as e:
                logger.debug("Optional db retrieval fallback skipped: %s", e)

        # 2. Drain from in-memory queue
        mem_cmds = self.pending_commands.pop(device_id, [])
        for m in mem_cmds:
            if m not in results:
                results.append(m)

        return results


ws_manager = ConnectionManager()

