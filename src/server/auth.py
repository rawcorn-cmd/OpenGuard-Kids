"""
OpenGuard Kids — Authentication & Authorization Dependency Module
Implements Requirements:
  - F5: Session management (HttpOnly, SameSite=Lax, 12h TTL)
  - F5: Query-level ownership checks preventing IDOR (cross-tenant access)
"""

from __future__ import annotations

import secrets
import time
from typing import Dict, Optional

from fastapi import Depends, HTTPException, Header, Request, status
from sqlalchemy.orm import Session

from src.server.database import get_db
from src.server.models import Parent

# In-memory session store: session_token -> (parent_id, expires_at)
# In production, this can also be backed by an SQLite sessions table.
SESSION_STORE: Dict[str, tuple[str, float]] = {}
SESSION_TTL_SECONDS = 12 * 3600  # 12 hours


def create_parent_session(parent_id: str) -> str:
    """Creates a new cryptographically secure session token."""
    token = secrets.token_hex(32)
    expires_at = time.time() + SESSION_TTL_SECONDS
    SESSION_STORE[token] = (parent_id, expires_at)
    return token


def invalidate_parent_session(token: str) -> None:
    """Removes a session token upon logout."""
    SESSION_STORE.pop(token, None)


def get_current_parent(
    request: Request,
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db),
) -> Parent:
    """
    Extracts and authenticates the current parent via either:
    1. Cookie: `session_token`
    2. Header: `Authorization: Bearer <token>`
    """
    token = None

    # Check Bearer header
    if authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ", 1)[1].strip()

    # Fallback to Cookie
    if not token:
        token = request.cookies.get("session_token")

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Yêu cầu xác thực. Vui lòng đăng nhập.",
        )

    session_data = SESSION_STORE.get(token)
    if not session_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Phiên đăng nhập không hợp lệ hoặc đã hết hạn.",
        )

    parent_id, expires_at = session_data
    if time.time() > expires_at:
        SESSION_STORE.pop(token, None)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại.",
        )

    parent = db.query(Parent).filter(Parent.id == parent_id).first()
    if not parent:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tài khoản phụ huynh không tồn tại.",
        )

    return parent

