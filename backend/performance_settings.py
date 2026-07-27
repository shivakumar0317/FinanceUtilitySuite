from __future__ import annotations
import os
from dataclasses import dataclass

def _bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    return default if value is None else value.strip().lower() in {"1","true","yes","on"}

def _int(name: str, default: int, minimum: int = 0) -> int:
    try:
        value = int(os.getenv(name, str(default)))
    except ValueError:
        value = default
    return max(value, minimum)

@dataclass(frozen=True, slots=True)
class PerformanceSettings:
    cache_enabled: bool
    cache_default_ttl: int
    cache_max_entries: int
    gzip_enabled: bool
    gzip_minimum_size: int
    gzip_compresslevel: int

    slow_request_logging_enabled: bool
    slow_request_threshold_ms: int
def get_performance_settings() -> PerformanceSettings:
    return PerformanceSettings(
        cache_enabled=_bool("CACHE_ENABLED", True),
        cache_default_ttl=_int("CACHE_TTL", 60, 1),
        cache_max_entries=_int("CACHE_MAX_ENTRIES", 1000, 10),
        gzip_enabled=_bool("GZIP_ENABLED", True),
        gzip_minimum_size=_int("GZIP_MINIMUM_SIZE", 1024, 0),
        gzip_compresslevel=min(_int("GZIP_COMPRESSLEVEL", 5, 1), 9),
        slow_request_logging_enabled=_bool("SLOW_REQUEST_LOGGING_ENABLED", True),
        slow_request_threshold_ms=_int("SLOW_REQUEST_THRESHOLD_MS", 500, 1),
    )

