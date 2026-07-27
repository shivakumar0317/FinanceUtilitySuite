from __future__ import annotations

import functools
import hashlib
import inspect
import json
from collections.abc import Callable
from typing import Any

from backend.cache.manager import cache_manager


def _normalize(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _normalize(item) for key, item in sorted(value.items())}
    if isinstance(value, (list, tuple, set)):
        return [_normalize(item) for item in value]
    if hasattr(value, "model_dump"):
        return value.model_dump()
    if hasattr(value, "__dict__"):
        return {
            key: _normalize(item)
            for key, item in vars(value).items()
            if not key.startswith("_")
        }
    return value


def build_cache_key(namespace: str, args: tuple[Any, ...], kwargs: dict[str, Any]) -> str:
    payload = {
        "args": _normalize(args),
        "kwargs": _normalize(kwargs),
    }

    raw = json.dumps(payload, sort_keys=True, default=str, separators=(",", ":"))
    digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    return f"{namespace}:{digest}"


def cached(*, namespace: str, ttl: int | None = None) -> Callable:
    """Cache async or sync function results without changing its public signature."""

    def decorator(func: Callable) -> Callable:
        is_async = inspect.iscoroutinefunction(func)

        if is_async:
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                key = build_cache_key(namespace, args, kwargs)
                cached_value = await cache_manager.get(key)

                if cached_value is not None:
                    return cached_value

                value = await func(*args, **kwargs)
                await cache_manager.set(key, value, ttl)
                return value

            return async_wrapper

        @functools.wraps(func)
        async def sync_wrapper(*args, **kwargs):
            key = build_cache_key(namespace, args, kwargs)
            cached_value = await cache_manager.get(key)

            if cached_value is not None:
                return cached_value

            value = func(*args, **kwargs)
            await cache_manager.set(key, value, ttl)
            return value

        return sync_wrapper

    return decorator
