"""
Unit Tests for Server Database (SQLite WAL) and Security (Argon2id & Lockout)
"""

import time
import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from src.server.database import set_sqlite_pragma, Base
from src.server.models import Parent, Child, Device, Policy, Event
from src.server.security import (
    hash_password,
    verify_password,
    validate_password_complexity,
    check_account_lockout,
    record_failed_attempt,
    MAX_FAILED_ATTEMPTS,
)


@pytest.fixture
def test_db():
    """Create an in-memory SQLite database configured with WAL and Foreign Keys."""
    engine = create_engine("sqlite:///:memory:")
    # Register SQLite pragmas
    from sqlalchemy import event
    event.listen(engine, "connect", set_sqlite_pragma)

    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    db = Session()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)


def test_sqlite_wal_and_foreign_keys_pragma(test_db):
    """Verify that foreign keys are enabled."""
    res_fk = test_db.execute(text("PRAGMA foreign_keys;")).scalar()
    assert res_fk == 1, "Foreign keys pragma must be active (1)"


def test_argon2id_password_hashing():
    """Verify Argon2id produces valid hash and verifies correctly."""
    plain = "SuperSecret@2026"
    hashed = hash_password(plain)

    assert hashed.startswith("$argon2id$"), "Hash must use Argon2id format"
    assert verify_password(hashed, plain) is True
    assert verify_password(hashed, "WrongPassword@2026") is False


def test_password_complexity_validator():
    """Verify minimum 10 chars, uppercase, lowercase, digit, and symbol."""
    # Valid
    valid, _ = validate_password_complexity("ValidPass@123")
    assert valid is True

    # Too short (<10)
    valid, err = validate_password_complexity("Short@1")
    assert valid is False
    assert "tối thiểu 10 ký tự" in err

    # Missing uppercase
    valid, err = validate_password_complexity("nouppercase@123")
    assert valid is False
    assert "in hoa" in err

    # Missing special character
    valid, err = validate_password_complexity("NoSpecialChar123")
    assert valid is False
    assert "ký tự đặc biệt" in err


def test_brute_force_lockout_after_five_attempts():
    """Account must lock for 15 minutes after 5 consecutive failed attempts."""
    failed_count = 0
    locked_until = 0.0

    # Attempts 1 to 4: not locked
    for _ in range(4):
        failed_count, locked_until = record_failed_attempt(failed_count)
        is_locked, _ = check_account_lockout(failed_count, locked_until)
        assert is_locked is False

    # 5th attempt: must lock
    failed_count, locked_until = record_failed_attempt(failed_count)
    assert failed_count == MAX_FAILED_ATTEMPTS
    assert locked_until > time.time()

    is_locked, remaining_sec = check_account_lockout(failed_count, locked_until)
    assert is_locked is True
    assert 850 < remaining_sec <= 900


def test_models_relational_cascade_deletion(test_db):
    """Deleting a Parent must cascade delete Children, Devices, Policies, and Events."""
    # 1. Create Parent
    parent = Parent(
        email="parent@test.com",
        hashed_password=hash_password("ParentPass@2026"),
    )
    test_db.add(parent)
    test_db.commit()

    # 2. Create Child
    child = Child(parent_id=parent.id, name="Test Child", age=10)
    test_db.add(child)
    test_db.commit()

    # 3. Create Device & Policy
    device = Device(child_id=child.id, hostname="CHILD-LAPTOP", is_enrolled=True)
    policy = Policy(child_id=child.id, version=1, daily_quota_minutes=90)
    test_db.add_all([device, policy])
    test_db.commit()

    # 4. Create Event
    event = Event(
        device_id=device.id,
        child_id=child.id,
        type="blocked_domain",
        subject="badsite.com",
        idempotency_key="unique-test-key-1",
    )
    test_db.add(event)
    test_db.commit()

    # Verify presence
    assert test_db.query(Child).count() == 1
    assert test_db.query(Device).count() == 1
    assert test_db.query(Event).count() == 1

    # 5. Delete Parent -> Cascade should purge everything
    test_db.delete(parent)
    test_db.commit()

    assert test_db.query(Parent).count() == 0
    assert test_db.query(Child).count() == 0
    assert test_db.query(Device).count() == 0
    assert test_db.query(Policy).count() == 0
    assert test_db.query(Event).count() == 0

