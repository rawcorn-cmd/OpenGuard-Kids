"""
OpenGuard Kids — Pydantic Schemas for Server API
"""

from __future__ import annotations

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict, Field, model_validator


class ParentRegisterRequest(BaseModel):
    email: str = Field(..., pattern=r"^[^@]+@[^@]+\.[^@]+$", description="Valid email address")
    password: str = Field(..., min_length=10, description="Argon2id compliant password")


class ParentLoginRequest(BaseModel):
    email: str = Field(..., pattern=r"^[^@]+@[^@]+\.[^@]+$")
    password: str


class ParentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    email: str
    created_at: float


class ChildCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    age: Optional[int] = Field(None, ge=1, le=18)


class ChildResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    parent_id: str
    name: str
    age: Optional[int] = None
    created_at: float


class PairingCodeResponse(BaseModel):
    child_id: str
    pairing_code: str
    expires_at: float
    ttl_seconds: int = 600


class DeviceEnrollRequest(BaseModel):
    pairing_code: str = Field(..., min_length=8, max_length=8)
    hostname: str = Field("CHILD-PC", max_length=100)
    device_fingerprint: Optional[str] = Field(None, max_length=64)


class DeviceEnrollResponse(BaseModel):
    device_id: str
    child_id: str
    device_token: str
    status: str = "ENROLLED"


class PolicyUpdateRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")

    daily_quota_minutes: Optional[int] = Field(None, ge=15, le=1440)
    daily_quota_weekend_minutes: Optional[int] = Field(None, ge=15, le=1440)
    weekend_quota_minutes: Optional[int] = Field(None, ge=15, le=1440)
    bed_time_start: Optional[str] = Field(None, pattern=r"^\d{2}:\d{2}$")
    bed_time_end: Optional[str] = Field(None, pattern=r"^\d{2}:\d{2}$")
    blocklist: Optional[List[str]] = None
    whitelist: Optional[List[str]] = None
    study_mode: Optional[bool] = None
    safesearch_enabled: Optional[bool] = None
    blocked_apps: Optional[List[Dict[str, Any]]] = None
    schedule_matrix: Optional[List[List[bool]]] = None

    @model_validator(mode="before")
    @classmethod
    def reconcile_weekend_quota(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if "weekend_quota_minutes" in data and "daily_quota_weekend_minutes" not in data:
                data["daily_quota_weekend_minutes"] = data["weekend_quota_minutes"]
            elif "daily_quota_weekend_minutes" in data and "weekend_quota_minutes" not in data:
                data["weekend_quota_minutes"] = data["daily_quota_weekend_minutes"]
        return data


class PolicyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="ignore")

    id: Optional[str] = None
    child_id: str
    version: int
    daily_quota_minutes: int
    daily_quota_weekend_minutes: int = 120
    weekend_quota_minutes: int = 120
    bed_time_start: str
    bed_time_end: str
    study_mode: bool
    safesearch_enabled: bool = True
    blocklist: List[str] = []
    whitelist: List[str] = []
    blocked_apps: List[Dict[str, Any]] = []
    schedule_matrix: List[List[bool]] = []
    hmac_signature: str = ""
    signature: str = ""
    updated_at: float


class DomainRuleRequest(BaseModel):
    domain: str = Field(..., min_length=3, max_length=255)
    list_type: str = Field("blacklist", description="'whitelist' or 'blacklist'")


class AppHashRuleRequest(BaseModel):
    name: Optional[str] = Field("app.exe", max_length=255)
    sha256: str = Field(..., pattern=r"^[a-fA-F0-9]{64}$", description="64-char hex SHA-256 hash")


class AuditLogItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="ignore")

    id: str
    parent_id: str
    child_id: Optional[str] = None
    action: str
    details: Optional[str] = ""
    old_value: Optional[str] = ""
    new_value: Optional[str] = ""
    ip_address: Optional[str] = None
    ts: float



class EventItemSchema(BaseModel):
    """Strict 7-field privacy-preserving schema per NT2 & F5."""
    id: Optional[str] = None
    device_id: str
    child_id: str
    type: str = Field(..., description="blocked_domain, process_blocked, screen_time, quota_warning")
    subject: str = Field(..., description="domain name or app executable")
    duration_sec: int = Field(0, ge=0)
    ts: float
    idempotency_key: str = Field(..., min_length=8, max_length=128)


class EventBatchIngestRequest(BaseModel):
    events: List[EventItemSchema]


class EventBatchIngestResponse(BaseModel):
    ingested_count: int
    acknowledged_keys: List[str]
    status: str = "SUCCESS"


class HeartbeatRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")

    device_id: str
    screen_time_remaining: Optional[float] = None
    remaining_seconds: Optional[float] = None
    child_id: Optional[Any] = None
    status: str = "ACTIVE"
    is_locked: Optional[bool] = None

    @model_validator(mode="before")
    @classmethod
    def normalize_fields(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if "screen_time_remaining" not in data and "remaining_seconds" in data:
                data["screen_time_remaining"] = data["remaining_seconds"]
            elif "remaining_seconds" not in data and "screen_time_remaining" in data:
                data["remaining_seconds"] = data["screen_time_remaining"]
            if data.get("screen_time_remaining") is None and data.get("remaining_seconds") is None:
                data["screen_time_remaining"] = 0.0
                data["remaining_seconds"] = 0.0
            elif data.get("screen_time_remaining") is None:
                data["screen_time_remaining"] = data.get("remaining_seconds")
            elif data.get("remaining_seconds") is None:
                data["remaining_seconds"] = data.get("screen_time_remaining")
        return data


class HeartbeatResponse(BaseModel):
    server_time: float
    pending_commands: List[Dict[str, Any]] = []
    policy_version: int = 1
