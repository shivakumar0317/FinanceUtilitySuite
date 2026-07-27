from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from backend.cache.manager import cache_manager


router = APIRouter(prefix="/performance", tags=["Performance"])


@router.get("/cache/stats")
async def get_cache_stats():
    return {
        "success": True,
        "cache": await cache_manager.stats(),
    }


@router.post("/cache/clear")
async def clear_cache():
    cleared = await cache_manager.clear()

    return {
        "success": True,
        "message": "Cache cleared.",
        "cleared_entries": cleared,
    }


@router.delete("/cache/prefix/{prefix}")
async def invalidate_cache_prefix(prefix: str):
    prefix = prefix.strip()

    if not prefix:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cache prefix is required.",
        )

    count = await cache_manager.invalidate_prefix(prefix)

    return {
        "success": True,
        "message": "Cache prefix invalidated.",
        "prefix": prefix,
        "invalidated_entries": count,
    }
