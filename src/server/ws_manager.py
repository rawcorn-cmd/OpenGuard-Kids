"""
OpenGuard Kids — WebSocket Connection Manager & Urgent Command Dispatcher
Provides low-latency (<5s) real-time bidirectional messaging between Parents and Windows Agents.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Dict, List, Any
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
    ) -> bool:
        """
        Dispatches urgent command ('LOCK_URGENT', 'UNLOCK', 'ADD_TIME') to agent.
        Returns True if sent immediately via WebSocket (< 5s), False if queued for heartbeat.
        """
        msg = {
            "type": "URGENT_COMMAND",
            "command": command_type,
            "payload": payload or {},
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
        logger.info("Queued command '%s' for device %s (Heartbeat fallback)", command_type, device_id)
        return False

    def pop_pending_commands(self, device_id: str) -> List[Dict[str, Any]]:
        """Retrieves and clears pending commands for a device upon HTTP heartbeat."""
        return self.pending_commands.pop(device_id, [])


ws_manager = ConnectionManager()

