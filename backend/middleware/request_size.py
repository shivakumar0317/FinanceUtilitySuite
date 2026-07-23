from __future__ import annotations
from starlette import status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

class RequestSizeLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, *, max_request_size_bytes: int) -> None:
        super().__init__(app)
        self.max_request_size_bytes = max(max_request_size_bytes, 1)

    async def dispatch(self, request: Request, call_next) -> Response:
        content_length = request.headers.get("content-length")
        if content_length:
            try:
                declared_size = int(content_length)
            except ValueError:
                declared_size = 0
            if declared_size > self.max_request_size_bytes:
                return JSONResponse(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    content={
                        "success": False,
                        "request_id": getattr(request.state, "request_id", "unknown"),
                        "error": {
                            "code": "REQUEST_TOO_LARGE",
                            "message": "The request body exceeds the allowed size.",
                            "details": {
                                "maximum_bytes": self.max_request_size_bytes,
                                "declared_bytes": declared_size,
                            },
                        },
                    },
                )
        return await call_next(request)
