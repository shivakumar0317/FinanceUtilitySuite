from __future__ import annotations

import logging
import time

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


logger = logging.getLogger("finance_utility_suite.slow_request")


class SlowRequestLoggingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, *, threshold_ms: float = 500.0) -> None:
        super().__init__(app)
        self.threshold_ms = max(float(threshold_ms), 1.0)

    async def dispatch(self, request: Request, call_next) -> Response:
        started = time.perf_counter()
        response = await call_next(request)
        elapsed_ms = (time.perf_counter() - started) * 1000

        if elapsed_ms >= self.threshold_ms:
            logger.warning(
                (
                    "Slow request | method=%s | path=%s | status=%s "
                    "| elapsed_ms=%.2f | request_id=%s"
                ),
                request.method,
                request.url.path,
                response.status_code,
                elapsed_ms,
                getattr(request.state, "request_id", "unknown"),
            )

        return response
