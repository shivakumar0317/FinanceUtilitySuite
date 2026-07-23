from __future__ import annotations
import os
from dataclasses import dataclass

def _bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    return default if value is None else value.strip().lower() in {"1", "true", "yes", "on"}

def _int(name: str, default: int, minimum: int = 1) -> int:
    try:
        value = int(os.getenv(name, str(default)))
    except ValueError:
        value = default
    return max(value, minimum)

def _list(name: str, default: list[str]) -> list[str]:
    value = os.getenv(name)
    if not value:
        return default
    items = [item.strip() for item in value.split(",") if item.strip()]
    return items or default

@dataclass(frozen=True, slots=True)
class SecuritySettings:
    security_headers_enabled: bool
    trusted_hosts_enabled: bool
    trusted_hosts: list[str]
    max_request_size_enabled: bool
    max_request_size_mb: int
    hsts_enabled: bool
    hsts_max_age: int

def get_security_settings() -> SecuritySettings:
    return SecuritySettings(
        security_headers_enabled=_bool("SECURITY_HEADERS_ENABLED", True),
        trusted_hosts_enabled=_bool("TRUSTED_HOSTS_ENABLED", True),
        trusted_hosts=_list("TRUSTED_HOSTS", ["localhost", "127.0.0.1", "finance_backend", "testserver"]),
        max_request_size_enabled=_bool("MAX_REQUEST_SIZE_ENABLED", True),
        max_request_size_mb=_int("MAX_REQUEST_SIZE_MB", 10),
        hsts_enabled=_bool("HSTS_ENABLED", False),
        hsts_max_age=_int("HSTS_MAX_AGE", 31536000),
    )
