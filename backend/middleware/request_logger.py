from __future__ import annotations

import logging
from time import perf_counter

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger("finance_utility_suite.request")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        started = perf_counter()
        response = await call_next(request)

        logger.info(
            "%s %s | status=%s | duration_ms=%.2f | client=%s | request_id=%s",
            request.method,
            request.url.path,
            response.status_code,
            (perf_counter() - started) * 1000,
            request.client.host if request.client else "unknown",
            getattr(request.state, "request_id", "unknown"),
        )
        return response
