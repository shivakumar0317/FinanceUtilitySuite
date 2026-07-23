from __future__ import annotations
from collections import OrderedDict
from copy import deepcopy
from dataclasses import dataclass
from threading import RLock
from time import monotonic
from typing import Any, Hashable

@dataclass(slots=True)
class CacheEntry:
    value: Any
    expires_at: float

class TTLCache:
    def __init__(self, *, enabled: bool=True, default_ttl: int=60, max_entries: int=1000) -> None:
        self.enabled = enabled
        self.default_ttl = max(default_ttl, 1)
        self.max_entries = max(max_entries, 10)
        self._items: OrderedDict[Hashable, CacheEntry] = OrderedDict()
        self._lock = RLock()
        self._hits = self._misses = self._sets = self._evictions = 0

    def get(self, key: Hashable, default: Any=None) -> Any:
        if not self.enabled:
            self._misses += 1
            return default
        now = monotonic()
        with self._lock:
            entry = self._items.get(key)
            if entry is None or entry.expires_at <= now:
                self._items.pop(key, None)
                self._misses += 1
                return default
            self._items.move_to_end(key)
            self._hits += 1
            return deepcopy(entry.value)

    def set(self, key: Hashable, value: Any, ttl: int|None=None) -> None:
        if not self.enabled:
            return
        with self._lock:
            self._items[key] = CacheEntry(deepcopy(value), monotonic()+max(ttl or self.default_ttl, 1))
            self._items.move_to_end(key)
            self._sets += 1
            while len(self._items) > self.max_entries:
                self._items.popitem(last=False)
                self._evictions += 1

    def delete(self, key: Hashable) -> bool:
        with self._lock:
            return self._items.pop(key, None) is not None

    def invalidate_prefix(self, prefix: str) -> int:
        with self._lock:
            keys = [k for k in self._items if isinstance(k, str) and k.startswith(prefix)]
            for key in keys:
                self._items.pop(key, None)
            return len(keys)

    def clear(self) -> None:
        with self._lock:
            self._items.clear()

    def stats(self) -> dict[str, int|bool]:
        with self._lock:
            return {
                "enabled": self.enabled,
                "entries": len(self._items),
                "max_entries": self.max_entries,
                "default_ttl": self.default_ttl,
                "hits": self._hits,
                "misses": self._misses,
                "sets": self._sets,
                "evictions": self._evictions,
            }

_cache: TTLCache|None = None
_cache_lock = RLock()

def configure_cache(*, enabled: bool, default_ttl: int, max_entries: int) -> TTLCache:
    global _cache
    with _cache_lock:
        _cache = TTLCache(enabled=enabled, default_ttl=default_ttl, max_entries=max_entries)
        return _cache

def get_cache() -> TTLCache:
    global _cache
    with _cache_lock:
        if _cache is None:
            _cache = TTLCache()
        return _cache
