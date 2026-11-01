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
)
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

    child = relationship("Child", back_populates="devices")
    events = relationship("Event", back_populates="device", cascade="all, delete-orphan")


class Policy(Base):
    __tablename__ = "policies"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    child_id = Column(String(36), ForeignKey("children.id", ondelete="CASCADE"), nullable=False, index=True)
    version = Column(Integer, default=1, nullable=False)
    daily_quota_minutes = Column(Integer, default=120, nullable=False)
    bed_time_start = Column(String(5), default="22:00", nullable=False)  # HH:MM
    bed_time_end = Column(String(5), default="06:00", nullable=False)
    blocklist_json = Column(Text, default="[]", nullable=False)  # JSON array of domains/apps
    whitelist_json = Column(Text, default="[]", nullable=False)
    study_mode = Column(Boolean, default=False, nullable=False)
    updated_at = Column(Float, default=time.time, nullable=False)

    child = relationship("Child", back_populates="policies")


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
    action = Column(String(100), nullable=False)
    ip_address = Column(String(45), nullable=True)
    ts = Column(Float, default=time.time, nullable=False)

    parent = relationship("Parent", back_populates="audit_logs")


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

