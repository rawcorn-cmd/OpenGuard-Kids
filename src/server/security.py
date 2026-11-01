"""
OpenGuard Kids — Security & Cryptography Module (Argon2id & Auth)
Implements Requirements:
  - F5: Password hashing using Argon2id (RFC 9106, memory_cost=64MB, time_cost=3)
  - F5: Password complexity (min 10 chars, uppercase, lowercase, digit, symbol)
  - F5: 15-minute brute-force lockout after 5 consecutive failed attempts
Architecture Specification: docs/ARCHITECTURE.md Section 7.2
"""

import time
import re
from typing import Tuple
from argon2 import PasswordHasher, Type
from argon2.exceptions import VerifyMismatchError, InvalidHashError

# Production-grade Argon2id hasher parameters (RFC 9106 recommended)
# time_cost=3, memory_cost=64MB (65536 KB), parallelism=4
ph = PasswordHasher(
    time_cost=3,
    memory_cost=65536,
    parallelism=4,
    hash_len=32,
    type=Type.ID,
)

MAX_FAILED_ATTEMPTS = 5
LOCKOUT_DURATION_SECONDS = 900.0  # 15 minutes


def hash_password(password: str) -> str:
    """Hash password using Argon2id with salt and memory cost."""
    return ph.hash(password)


def verify_password(hashed_password: str, plain_password: str) -> bool:
    """Verify plain password against Argon2id hash."""
    try:
        return ph.verify(hashed_password, plain_password)
    except (VerifyMismatchError, InvalidHashError):
        return False


def validate_password_complexity(password: str) -> Tuple[bool, str]:
    """
    Enforces minimum 10 characters, at least 1 uppercase, 1 lowercase, 1 digit, 1 special char.
    Returns (is_valid, error_message).
    """
    if len(password) < 10:
        return False, "Mật khẩu phải có độ dài tối thiểu 10 ký tự."
    if not re.search(r"[A-Z]", password):
        return False, "Mật khẩu phải chứa ít nhất 1 chữ cái in hoa (A-Z)."
    if not re.search(r"[a-z]", password):
        return False, "Mật khẩu phải chứa ít nhất 1 chữ cái in thường (a-z)."
    if not re.search(r"[0-9]", password):
        return False, "Mật khẩu phải chứa ít nhất 1 chữ số (0-9)."
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False, "Mật khẩu phải chứa ít nhất 1 ký tự đặc biệt (!@#$%^&*...)."
    return True, ""


def check_account_lockout(failed_count: int, locked_until: float) -> Tuple[bool, int]:
    """
    Check if account is currently locked due to too many failed attempts.
    Returns (is_locked, remaining_lockout_seconds).
    """
    now = time.time()
    if locked_until > now:
        remaining = int(locked_until - now)
        return True, remaining
    return False, 0


def record_failed_attempt(current_failed_count: int) -> Tuple[int, float]:
    """
    Increment failed count. If threshold reached, compute lockout deadline.
    Returns (new_failed_count, new_locked_until).
    """
    new_count = current_failed_count + 1
    if new_count >= MAX_FAILED_ATTEMPTS:
        return new_count, time.time() + LOCKOUT_DURATION_SECONDS
    return new_count, 0.0

