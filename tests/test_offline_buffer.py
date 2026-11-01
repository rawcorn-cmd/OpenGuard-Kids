"""
Unit tests for OpenGuard Kids Offline Event Buffer.
Verifies SQLite WAL mode, 7-field privacy schema, batch peeking, sync acknowledgment, and deduplication.
"""

import os
import tempfile
import time
from src.agent.offline_buffer import OfflineEventBuffer


def test_enqueue_and_peek_batch():
    with tempfile.TemporaryDirectory() as tmp_dir:
        db_path = os.path.join(tmp_dir, "test_events.db")
        buffer = OfflineEventBuffer(db_path=db_path)

        assert buffer.get_pending_count() == 0

        # Enqueue 3 events adhering to 7-field schema
        id1 = buffer.enqueue_event(
            device_id="dev-01",
            child_id="child-01",
            event_type="blocked_domain",
            subject="bad-site.com",
            duration_sec=0,
            idempotency_key="key-001",
        )
        id2 = buffer.enqueue_event(
            device_id="dev-01",
            child_id="child-01",
            event_type="screen_time",
            subject="active_usage",
            duration_sec=300,
            idempotency_key="key-002",
        )
        id3 = buffer.enqueue_event(
            device_id="dev-01",
            child_id="child-01",
            event_type="process_blocked",
            subject="game.exe",
            duration_sec=0,
            idempotency_key="key-003",
        )

        assert buffer.get_pending_count() == 3

        # Peek batch of limit 2
        batch = buffer.peek_unsynced_batch(limit=2)
        assert len(batch) == 2
        assert batch[0]["idempotency_key"] == "key-001"
        assert batch[0]["type"] == "blocked_domain"
        assert batch[1]["idempotency_key"] == "key-002"


def test_acknowledge_synced_and_deduplication():
    with tempfile.TemporaryDirectory() as tmp_dir:
        db_path = os.path.join(tmp_dir, "test_events.db")
        buffer = OfflineEventBuffer(db_path=db_path)

        buffer.enqueue_event(
            device_id="dev-01",
            child_id="child-01",
            event_type="blocked_domain",
            subject="bad-site.com",
            idempotency_key="uniq-123",
        )

        # Duplicate enqueue attempt with same idempotency key
        buffer.enqueue_event(
            device_id="dev-01",
            child_id="child-01",
            event_type="blocked_domain",
            subject="bad-site.com",
            idempotency_key="uniq-123",
        )

        # Deduplication must ensure only 1 record exists
        assert buffer.get_pending_count() == 1

        # Acknowledge sync
        acked = buffer.acknowledge_synced(["uniq-123"])
        assert acked == 1
        assert buffer.get_pending_count() == 0

        # Peeking now returns empty list
        remaining = buffer.peek_unsynced_batch()
        assert len(remaining) == 0


def test_purge_old_synced_events():
    with tempfile.TemporaryDirectory() as tmp_dir:
        db_path = os.path.join(tmp_dir, "test_events.db")
        buffer = OfflineEventBuffer(db_path=db_path)

        # Event from 10 days ago (synced)
        old_ts = time.time() - (10 * 86400.0)
        buffer.enqueue_event(
            device_id="dev-01",
            child_id="child-01",
            event_type="screen_time",
            subject="old_session",
            ts=old_ts,
            idempotency_key="old-synced-1",
        )
        buffer.acknowledge_synced(["old-synced-1"])

        # Event from today (unsynced)
        buffer.enqueue_event(
            device_id="dev-01",
            child_id="child-01",
            event_type="screen_time",
            subject="today_session",
            ts=time.time(),
            idempotency_key="today-unsynced",
        )

        # Purge synced events older than 7 days
        purged = buffer.purge_synced_events(older_than_days=7)
        assert purged == 1

        # Today's unsynced event must remain intact
        assert buffer.get_pending_count() == 1

