"""
OpenGuard Kids — SQLAlchemy Relational Models for Server
Architecture Specification: docs/ARCHITECTURE.md Section 4.1
"""

import time
import uuid
from sqlalchemy import (
    Column,
    String,
    Integer,
    Boolean,
    Float,
    ForeignKey,
    Text,
    Index,
    DateTime,
)
from datetime import datetime, timezone
from sqlalchemy.orm import relationship

from src.server.database import Base


def generate_uuid() -> str:
    return str(uuid.uuid4())


class Parent(Base):
    __tablename__ = "parents"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    failed_login_count = Column(Integer, default=0, nullable=False)
    locked_until = Column(Float, default=0.0, nullable=False)  # Unix timestamp
    created_at = Column(Float, default=time.time, nullable=False)

    children = relationship("Child", back_populates="parent", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="parent", cascade="all, delete-orphan")


class Child(Base):
    __tablename__ = "children"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    parent_id = Column(String(36), ForeignKey("parents.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    age = Column(Integer, nullable=True)
    created_at = Column(Float, default=time.time, nullable=False)

    parent = relationship("Parent", back_populates="children")
    devices = relationship("Device", back_populates="child", cascade="all, delete-orphan")
    policies = relationship("Policy", back_populates="child", cascade="all, delete-orphan")
    events = relationship("Event", back_populates="child", cascade="all, delete-orphan")
    requests = relationship("ChildRequest", back_populates="child", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="child", cascade="all, delete-orphan")


class Device(Base):
    __tablename__ = "devices"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    child_id = Column(String(36), ForeignKey("children.id", ondelete="CASCADE"), nullable=False, index=True)
    pairing_code = Column(String(8), unique=True, nullable=True, index=True)
    pairing_expires_at = Column(Float, default=0.0, nullable=False)
    device_fingerprint = Column(String(64), nullable=True)
    hostname = Column(String(100), default="CHILD-PC", nullable=False)
    is_enrolled = Column(Boolean, default=False, nullable=False)
    last_heartbeat = Column(Float, default=0.0, nullable=False)
    remaining_seconds = Column(Float, default=0.0, nullable=False)
    current_status = Column(String(50), default="ACTIVE", nullable=False)
    is_locked = Column(Boolean, default=False, nullable=False)
    bonus_minutes_today = Column(Integer, default=0, nullable=False)
    device_token = Column(String(128), nullable=True)

    child = relationship("Child", back_populates="devices")
    events = relationship("Event", back_populates="device", cascade="all, delete-orphan")


class Policy(Base):
    __tablename__ = "policies"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    child_id = Column(String(36), ForeignKey("children.id", ondelete="CASCADE"), nullable=False, index=True)
    version = Column(Integer, default=1, nullable=False)
    daily_quota_minutes = Column(Integer, default=120, nullable=False)
    daily_quota_weekend_minutes = Column(Integer, default=120, nullable=False)
    bed_time_start = Column(String(5), default="22:00", nullable=False)  # HH:MM
    bed_time_end = Column(String(5), default="06:00", nullable=False)
    blocklist_json = Column(Text, default="[]", nullable=False)  # JSON array of domains/apps
    whitelist_json = Column(Text, default="[]", nullable=False)
    study_mode = Column(Boolean, default=False, nullable=False)
    safesearch_enabled = Column(Boolean, default=True, nullable=False)
    schedule_matrix_json = Column(Text, default="[]", nullable=False)
    app_blocklist_json = Column(Text, default="[]", nullable=False)
    hmac_signature = Column(String(64), default="", nullable=False)
    updated_at = Column(Float, default=time.time, nullable=False)

    child = relationship("Child", back_populates="policies")

    @property
    def weekend_quota_minutes(self) -> int:
        return self.daily_quota_weekend_minutes

    @weekend_quota_minutes.setter
    def weekend_quota_minutes(self, value: int):
        self.daily_quota_weekend_minutes = value

    @property
    def blocked_apps_json(self) -> str:
        return self.app_blocklist_json

    @blocked_apps_json.setter
    def blocked_apps_json(self, value: str):
        self.app_blocklist_json = value


class Event(Base):
    __tablename__ = "events"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    device_id = Column(String(36), ForeignKey("devices.id", ondelete="CASCADE"), nullable=False, index=True)
    child_id = Column(String(36), ForeignKey("children.id", ondelete="CASCADE"), nullable=False, index=True)
    type = Column(String(50), nullable=False)  # blocked_domain, process_blocked, screen_time, etc.
    subject = Column(String(255), nullable=False)  # domain name or executable path
    duration_sec = Column(Integer, default=0, nullable=False)
    ts = Column(Float, default=time.time, nullable=False, index=True)
    idempotency_key = Column(String(64), unique=True, nullable=False, index=True)

    device = relationship("Device", back_populates="events")
    child = relationship("Child", back_populates="events")

    __table_args__ = (
        Index("idx_events_child_ts", "child_id", "ts"),
    )


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    parent_id = Column(String(36), ForeignKey("parents.id", ondelete="CASCADE"), nullable=False, index=True)
    child_id = Column(String(36), ForeignKey("children.id", ondelete="CASCADE"), nullable=True, index=True)
    action = Column(String(100), nullable=False)
    details = Column(Text, default="", nullable=True)
    old_value = Column(Text, default="", nullable=True)
    new_value = Column(Text, default="", nullable=True)
    ip_address = Column(String(45), nullable=True)
    ts = Column(Float, default=time.time, nullable=False)

    parent = relationship("Parent", back_populates="audit_logs")
    child = relationship("Child", back_populates="audit_logs")


class PendingCommand(Base):
    __tablename__ = "pending_commands"

    id = Column(Integer, primary_key=True, autoincrement=True)
    device_id = Column(String(64), index=True, nullable=False)
    command_type = Column(String(32), nullable=False)
    payload_json = Column(Text, default="{}", nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)



class ChildRequest(Base):
    __tablename__ = "child_requests"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    child_id = Column(String(36), ForeignKey("children.id", ondelete="CASCADE"), nullable=False, index=True)
    type = Column(String(50), nullable=False)  # add_time, unblock_domain
    subject = Column(String(255), nullable=True)
    minutes_requested = Column(Integer, default=15, nullable=False)
    status = Column(String(20), default="PENDING", nullable=False)  # PENDING, APPROVED, REJECTED
    created_at = Column(Float, default=time.time, nullable=False)

    child = relationship("Child", back_populates="requests")


def migrate_device_table(bind_engine=None):
    """Reconciles missing columns in devices table for pre-existing SQLite databases."""
    try:
        from src.server.database import engine
        target = bind_engine or engine
        if target.dialect.name != "sqlite":
            return
        with target.connect() as conn:
            res_device = conn.exec_driver_sql(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='devices'"
            ).fetchone()
            if res_device:
                existing_cols = {
                    row[1]
                    for row in conn.exec_driver_sql("PRAGMA table_info(devices)").fetchall()
                }
                device_columns = {
                    "remaining_seconds": "FLOAT DEFAULT 0.0",
                    "current_status": "VARCHAR(50) DEFAULT 'ACTIVE'",
                    "is_locked": "BOOLEAN DEFAULT 0",
                    "bonus_minutes_today": "INTEGER DEFAULT 0",
                    "device_token": "VARCHAR(128)",
                }
                for col_name, col_def in device_columns.items():
                    if col_name not in existing_cols:
                        conn.exec_driver_sql(f"ALTER TABLE devices ADD COLUMN {col_name} {col_def}")
                conn.commit()
    except Exception:
        pass


migrate_device_table()

