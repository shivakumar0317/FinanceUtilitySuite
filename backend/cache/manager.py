from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class CacheEntry:
    value: Any
    expires_at: float
    created_at: float


class CacheManager:
    """Process-local asynchronous TTL cache with bounded storage and metrics."""

    def __init__(self, *, enabled: bool = True, default_ttl: int = 60, max_entries: int = 1000) -> None:
        self.enabled = enabled
        self.default_ttl = max(int(default_ttl), 1)
        self.max_entries = max(int(max_entries), 10)
        self._entries: dict[str, CacheEntry] = {}
        self._lock = asyncio.Lock()
        self._hits = 0
        self._misses = 0
        self._sets = 0
        self._evictions = 0
        self._invalidations = 0

    async def get(self, key: str) -> Any | None:
        if not self.enabled:
            self._misses += 1
            return None
        now = time.monotonic()
        async with self._lock:
            entry = self._entries.get(key)
            if entry is None:
                self._misses += 1
                return None
            if entry.expires_at <= now:
                self._entries.pop(key, None)
                self._misses += 1
                self._evictions += 1
                return None
            self._hits += 1
            return entry.value

    async def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        if not self.enabled:
            return
        ttl_seconds = max(int(ttl or self.default_ttl), 1)
        now = time.monotonic()
        async with self._lock:
            if len(self._entries) >= self.max_entries and key not in self._entries:
                oldest_key = min(self._entries, key=lambda item: self._entries[item].created_at)
                self._entries.pop(oldest_key, None)
                self._evictions += 1
            self._entries[key] = CacheEntry(value=value, expires_at=now + ttl_seconds, created_at=now)
            self._sets += 1

    async def delete(self, key: str) -> bool:
        async with self._lock:
            existed = key in self._entries
            self._entries.pop(key, None)
            if existed:
                self._invalidations += 1
            return existed

    async def invalidate_prefix(self, prefix: str) -> int:
        async with self._lock:
            keys = [key for key in self._entries if key.startswith(prefix)]
            for key in keys:
                self._entries.pop(key, None)
            self._invalidations += len(keys)
            return len(keys)

    async def clear(self) -> int:
        async with self._lock:
            count = len(self._entries)
            self._entries.clear()
            self._invalidations += count
            return count

    async def cleanup_expired(self) -> int:
        now = time.monotonic()
        async with self._lock:
            expired = [key for key, entry in self._entries.items() if entry.expires_at <= now]
            for key in expired:
                self._entries.pop(key, None)
            self._evictions += len(expired)
            return len(expired)

    async def stats(self) -> dict[str, int | float | bool]:
        await self.cleanup_expired()
        total_lookups = self._hits + self._misses
        hit_ratio = self._hits / total_lookups if total_lookups else 0.0
        async with self._lock:
            active_entries = len(self._entries)
        return {
            "enabled": self.enabled,
            "active_entries": active_entries,
            "max_entries": self.max_entries,
            "hits": self._hits,
            "misses": self._misses,
            "sets": self._sets,
            "evictions": self._evictions,
            "invalidations": self._invalidations,
            "total_lookups": total_lookups,
            "hit_ratio": round(hit_ratio, 4),
            "default_ttl_seconds": self.default_ttl,
        }


cache_manager = CacheManager()
