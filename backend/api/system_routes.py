from __future__ import annotations

import os
import platform
import shutil
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter

import fastapi
import sqlalchemy
from fastapi import APIRouter, HTTPException, status
from sqlalchemy import text

from backend.config import get_settings
from backend.database import SessionLocal


router = APIRouter(tags=["System"])
settings = get_settings()
_started_at = time.monotonic()


def _utc_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def _format_uptime(seconds: float) -> str:
    total_seconds = max(0, int(seconds))
    days, remainder = divmod(total_seconds, 86_400)
    hours, remainder = divmod(remainder, 3_600)
    minutes, seconds = divmod(remainder, 60)

    parts: list[str] = []
    if days:
        parts.append(f"{days}d")
    if hours or days:
        parts.append(f"{hours}h")
    if minutes or hours or days:
        parts.append(f"{minutes}m")
    parts.append(f"{seconds}s")
    return " ".join(parts)


@router.get("/health")
def health_check() -> dict:
    """Lightweight liveness endpoint used by Docker."""
    return {
        "status": "healthy",
        "application": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
        "uptime": _format_uptime(time.monotonic() - _started_at),
        "timestamp": _utc_timestamp(),
    }


@router.get("/health/db")
def database_health() -> dict:
    """Verify that a database connection can execute a lightweight query."""
    started = perf_counter()

    try:
        with SessionLocal() as db:
            db.execute(text("SELECT 1"))
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "status": "unhealthy",
                "database": "disconnected",
                "message": str(exc),
                "timestamp": _utc_timestamp(),
            },
        ) from exc

    return {
        "status": "healthy",
        "database": "connected",
        "latency_ms": round((perf_counter() - started) * 1000, 2),
        "timestamp": _utc_timestamp(),
    }


@router.get("/health/storage")
def storage_health() -> dict:
    """Check that the upload directory exists and is writable."""
    upload_directory = Path(settings.upload_dir).expanduser()
    test_file = upload_directory / ".healthcheck"

    try:
        upload_directory.mkdir(parents=True, exist_ok=True)
        test_file.write_text("ok", encoding="utf-8")
        test_file.unlink(missing_ok=True)
        usage = shutil.disk_usage(upload_directory)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "status": "unhealthy",
                "storage": "unavailable",
                "path": str(upload_directory),
                "message": str(exc),
                "timestamp": _utc_timestamp(),
            },
        ) from exc

    return {
        "status": "healthy",
        "storage": "writable",
        "path": str(upload_directory),
        "free_bytes": usage.free,
        "total_bytes": usage.total,
        "free_gb": round(usage.free / (1024**3), 2),
        "timestamp": _utc_timestamp(),
    }


@router.get("/version")
def version_info() -> dict:
    return {
        "application": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
        "timestamp": _utc_timestamp(),
    }


@router.get("/system")
def system_info() -> dict:
    """Return non-sensitive runtime diagnostics."""
    database_engine = settings.database_url.split(":", 1)[0]

    return {
        "application": {
            "name": settings.app_name,
            "version": settings.app_version,
            "environment": settings.environment,
            "debug": settings.debug,
            "uptime": _format_uptime(time.monotonic() - _started_at),
        },
        "runtime": {
            "python": platform.python_version(),
            "fastapi": fastapi.__version__,
            "sqlalchemy": sqlalchemy.__version__,
            "platform": platform.platform(),
            "processor": platform.processor() or "unknown",
            "pid": os.getpid(),
            "executable": sys.executable,
        },
        "database": {
            "engine": database_engine,
        },
        "storage": {
            "upload_dir": settings.upload_dir,
        },
        "timestamp": _utc_timestamp(),
    }
