"""
OpenGuard Kids — Offline Event Buffer
Persists enforcement events locally in SQLite WAL mode when the agent is offline.
Enforces the strict 7-field privacy schema (NT2 / F5) without spyware or screen captures.
"""

from __future__ import annotations

import os
import sqlite3
import time
import uuid
from typing import Dict, List, Optional, Any

DEFAULT_LOCAL_DATA_DIR = os.path.join(
    os.getenv("ProgramData", os.path.expanduser("~")),
    "OpenGuardKids",
)


class OfflineEventBuffer:
    """
    Manages local persistent event queue for network outage resilience.
    Uses SQLite WAL mode to avoid database corruption on abrupt power loss.
    """

    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            os.makedirs(DEFAULT_LOCAL_DATA_DIR, exist_ok=True)
            self.db_path = os.path.join(DEFAULT_LOCAL_DATA_DIR, "offline_events.db")
        else:
            self.db_path = db_path
            os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)

        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=5.0)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        return conn

    def _init_db(self) -> None:
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS local_events (
                    id TEXT PRIMARY KEY,
                    device_id TEXT NOT NULL,
                    child_id TEXT NOT NULL,
                    type TEXT NOT NULL,
                    subject TEXT NOT NULL,
                    duration_sec INTEGER NOT NULL DEFAULT 0,
                    ts REAL NOT NULL,
                    idempotency_key TEXT UNIQUE NOT NULL,
                    synced INTEGER NOT NULL DEFAULT 0
                );
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_local_events_synced ON local_events(synced, ts);")
            conn.commit()

    def enqueue_event(
        self,
        device_id: str,
        child_id: str,
        event_type: str,
        subject: str,
        duration_sec: int = 0,
        ts: Optional[float] = None,
        idempotency_key: Optional[str] = None,
    ) -> str:
        """
        Enqueues an event adhering strictly to the 7-field schema.
        Returns the generated event ID.
        """
        event_id = str(uuid.uuid4())
        timestamp = ts or time.time()
        key = idempotency_key or f"{device_id}_{event_type}_{subject}_{int(timestamp * 1000)}"

        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT OR IGNORE INTO local_events 
                (id, device_id, child_id, type, subject, duration_sec, ts, idempotency_key, synced)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0)
                """,
                (event_id, device_id, child_id, event_type, subject, duration_sec, timestamp, key),
            )
            conn.commit()

        return event_id

    def peek_unsynced_batch(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Retrieves the oldest unsynced events up to the specified limit.
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                """
                SELECT id, device_id, child_id, type, subject, duration_sec, ts, idempotency_key
                FROM local_events
                WHERE synced = 0
                ORDER BY ts ASC
                LIMIT ?
                """,
                (limit,),
            )
            rows = cursor.fetchall()
            return [dict(r) for r in rows]

    def acknowledge_synced(self, idempotency_keys: List[str]) -> int:
        """
        Marks events as successfully synced to the central server.
        """
        if not idempotency_keys:
            return 0

        with self._get_connection() as conn:
            placeholders = ",".join("?" for _ in idempotency_keys)
            cursor = conn.execute(
                f"UPDATE local_events SET synced = 1 WHERE idempotency_key IN ({placeholders})",
                idempotency_keys,
            )
            conn.commit()
            return cursor.rowcount

    def purge_synced_events(self, older_than_days: int = 7) -> int:
        """
        Deletes already-synced events older than N days to prevent infinite local disk growth.
        """
        cutoff_ts = time.time() - (older_than_days * 86400.0)
        with self._get_connection() as conn:
            cursor = conn.execute(
                "DELETE FROM local_events WHERE synced = 1 AND ts < ?",
                (cutoff_ts,),
            )
            conn.commit()
            return cursor.rowcount

    def get_pending_count(self) -> int:
        with self._get_connection() as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM local_events WHERE synced = 0")
            return cursor.fetchone()[0]

    def purge_child_events(self, child_id: Any) -> int:
        """
        F3.4: Atomic Dual Deletion handler on agent local SQLite cache.
        Purges all locally stored events belonging to a specific child upon receiving
        the PURGE_LOCAL_CACHE command from the parent via WebSocket.
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                "DELETE FROM local_events WHERE child_id = ?",
                (str(child_id),),
            )
            conn.commit()
            return cursor.rowcount


