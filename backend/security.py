from __future__ import annotations
import logging
from fastapi import FastAPI
from starlette.middleware.trustedhost import TrustedHostMiddleware
from backend.middleware.request_size import RequestSizeLimitMiddleware
from backend.middleware.security_headers import SecurityHeadersMiddleware
from backend.security_settings import get_security_settings

logger = logging.getLogger("finance_utility_suite.security")

def register_security_middleware(app: FastAPI) -> None:
    settings = get_security_settings()
    if settings.security_headers_enabled:
        app.add_middleware(
            SecurityHeadersMiddleware,
            hsts_enabled=settings.hsts_enabled,
            hsts_max_age=settings.hsts_max_age,
        )
    if settings.max_request_size_enabled:
        app.add_middleware(
            RequestSizeLimitMiddleware,
            max_request_size_bytes=settings.max_request_size_mb * 1024 * 1024,
        )
    if settings.trusted_hosts_enabled:
        app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.trusted_hosts)

    logger.info(
        "Security middleware configured | headers=%s | trusted_hosts=%s | max_request_size_mb=%s | hsts=%s",
        settings.security_headers_enabled,
        settings.trusted_hosts if settings.trusted_hosts_enabled else "disabled",
        settings.max_request_size_mb if settings.max_request_size_enabled else "disabled",
        settings.hsts_enabled,
    )
