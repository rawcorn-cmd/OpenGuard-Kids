"""
OpenGuard Kids — Database Engine Setup (SQLite with WAL Mode)
Architecture Specification: docs/ARCHITECTURE.md Section 4
"""

import os
from sqlalchemy import create_engine, event
from sqlalchemy.orm import declarative_base, sessionmaker, scoped_session

# Default database directory and path
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data")
os.makedirs(DATA_DIR, exist_ok=True)
DEFAULT_DB_PATH = os.path.join(DATA_DIR, "server.db")

DATABASE_URL = os.getenv("OGK_DATABASE_URL", f"sqlite:///{DEFAULT_DB_PATH}")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False,
)

# Enforce SQLite WAL (Write-Ahead Logging) and Foreign Keys on every connection
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL;")
    cursor.execute("PRAGMA foreign_keys=ON;")
    cursor.execute("PRAGMA synchronous=NORMAL;")
    cursor.close()

SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
Base = declarative_base()


def get_db():
    """Dependency for FastAPI route handlers."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def migrate_db(bind_engine=None):
    """
    Automatically reconciles SQLite schema for pre-existing tables.
    Adds missing columns to 'policies' and 'audit_logs' with safe defaults.
    """
    target = bind_engine or engine
    if target.dialect.name != "sqlite":
        return

    with target.connect() as conn:
        # 1. Reconcile policies table
        res_policies = conn.exec_driver_sql(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='policies'"
        ).fetchone()
        if res_policies:
            existing_cols = {
                row[1]
                for row in conn.exec_driver_sql("PRAGMA table_info(policies)").fetchall()
            }
            policy_columns = {
                "daily_quota_weekend_minutes": "INTEGER DEFAULT 120",
                "safesearch_enabled": "BOOLEAN DEFAULT 1",
                "schedule_matrix_json": "TEXT DEFAULT '[]'",
                "app_blocklist_json": "TEXT DEFAULT '[]'",
                "hmac_signature": "VARCHAR DEFAULT ''",
            }
            for col_name, col_def in policy_columns.items():
                if col_name not in existing_cols:
                    conn.exec_driver_sql(f"ALTER TABLE policies ADD COLUMN {col_name} {col_def}")

        # 2. Reconcile audit_logs table
        res_audit = conn.exec_driver_sql(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='audit_logs'"
        ).fetchone()
        if res_audit:
            existing_audit_cols = {
                row[1]
                for row in conn.exec_driver_sql("PRAGMA table_info(audit_logs)").fetchall()
            }
            audit_columns = {
                "child_id": "VARCHAR(36)",
                "details": "TEXT DEFAULT ''",
                "old_value": "TEXT DEFAULT ''",
                "new_value": "TEXT DEFAULT ''",
            }
            for col_name, col_def in audit_columns.items():
                if col_name not in existing_audit_cols:
                    conn.exec_driver_sql(f"ALTER TABLE audit_logs ADD COLUMN {col_name} {col_def}")

        conn.commit()


def init_db(bind_engine=None):
    """Initializes tables in the database and automatically reconciles schemas."""
    target = bind_engine or engine
    Base.metadata.create_all(bind=target)
    migrate_db(target)
