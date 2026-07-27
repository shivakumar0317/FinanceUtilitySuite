from __future__ import annotations

import logging
from fastapi import FastAPI
from backend.cache.manager import cache_manager
from backend.middleware.slow_request import SlowRequestLoggingMiddleware
from backend.performance_settings import get_performance_settings

logger = logging.getLogger("finance_utility_suite.performance")


def configure_performance_runtime(app: FastAPI) -> None:
    settings = get_performance_settings()
    cache_manager.enabled = settings.cache_enabled
    cache_manager.default_ttl = settings.cache_default_ttl
    cache_manager.max_entries = settings.cache_max_entries

    if settings.slow_request_logging_enabled:
        app.add_middleware(
            SlowRequestLoggingMiddleware,
            threshold_ms=settings.slow_request_threshold_ms,
        )

    logger.info(
        "Application performance configured | cache_enabled=%s | cache_default_ttl=%ss | cache_max_entries=%s | slow_request_logging=%s | slow_request_threshold_ms=%s",
        settings.cache_enabled,
        settings.cache_default_ttl,
        settings.cache_max_entries,
        settings.slow_request_logging_enabled,
        settings.slow_request_threshold_ms,
    )
