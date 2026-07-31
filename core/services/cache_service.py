"""RMS v2.0.1 - Smart JSON cache service."""
from __future__ import annotations
import json, os, threading
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

class CacheService:
    DEFAULT_CACHE_PATH = Path(__file__).resolve().parents[1] / "cache" / "stock_master.json"
    _lock = threading.RLock()

    def __init__(self, cache_path: str | Path | None = None, ttl_days: int = 7):
        self.cache_path = Path(cache_path or self.DEFAULT_CACHE_PATH)
        self.ttl = timedelta(days=max(int(ttl_days), 0))
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)

    def get(self, symbol: str) -> dict[str, Any] | None:
        record = self.get_any(symbol)
        return None if record is None or self.is_stale(record) else record

    def get_any(self, symbol: str) -> dict[str, Any] | None:
        with self._lock:
            value = self._read_all().get(self._key(symbol))
        return dict(value) if isinstance(value, dict) else None

    def set(self, symbol: str, record: dict[str, Any]) -> None:
        self.set_many({symbol: record})

    def set_many(self, records: dict[str, dict[str, Any]]) -> None:
        if not records:
            return
        stamp = datetime.now(timezone.utc).isoformat()
        with self._lock:
            data = self._read_all()
            for symbol, record in records.items():
                payload = dict(record)
                payload["symbol"] = self._key(symbol)
                payload["cached_at"] = stamp
                data[self._key(symbol)] = payload
            self._write_all(data)

    def clear(self) -> None:
        with self._lock:
            self._write_all({})

    def is_stale(self, record: dict[str, Any]) -> bool:
        if self.ttl.total_seconds() <= 0 or not record.get("cached_at"):
            return True
        try:
            timestamp = datetime.fromisoformat(str(record["cached_at"]))
            if timestamp.tzinfo is None:
                timestamp = timestamp.replace(tzinfo=timezone.utc)
        except (TypeError, ValueError):
            return True
        return datetime.now(timezone.utc) - timestamp > self.ttl

    def stats(self) -> dict[str, int]:
        data = self._read_all()
        fresh = sum(1 for r in data.values() if isinstance(r, dict) and not self.is_stale(r))
        return {"records": len(data), "fresh": fresh, "stale": len(data) - fresh}

    def _read_all(self) -> dict[str, Any]:
        if not self.cache_path.exists():
            return {}
        try:
            with self.cache_path.open("r", encoding="utf-8") as handle:
                data = json.load(handle)
            return data if isinstance(data, dict) else {}
        except (OSError, json.JSONDecodeError):
            return {}

    def _write_all(self, data: dict[str, Any]) -> None:
        temp = self.cache_path.with_suffix(self.cache_path.suffix + ".tmp")
        with temp.open("w", encoding="utf-8") as handle:
            json.dump(data, handle, indent=2, ensure_ascii=False, default=str)
        os.replace(temp, self.cache_path)

    @staticmethod
    def _key(symbol: str) -> str:
        value = str(symbol or "").strip().upper().removesuffix(".NS").removesuffix(".BO")
        if not value:
            raise ValueError("Cache symbol cannot be empty.")
        return value
