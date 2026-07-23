from __future__ import annotations

import logging
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from starlette import status
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger("finance_utility_suite.exception")


def _request_id(request: Request) -> str:
    return getattr(request.state, "request_id", "unknown")


def _response(request: Request, status_code: int, code: str, message: str, details: Any = None) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "success": False,
            "request_id": _request_id(request),
            "error": {"code": code, "message": message, "details": details},
        },
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    detail = exc.detail
    message = str(detail.get("message") or detail.get("detail") or "Request failed.") if isinstance(detail, dict) else str(detail)
    return _response(request, exc.status_code, f"HTTP_{exc.status_code}", message, detail if isinstance(detail, dict) else None)


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    details = [
        {
            "field": ".".join(str(part) for part in item.get("loc", [])),
            "message": item.get("msg"),
            "type": item.get("type"),
        }
        for item in exc.errors()
    ]
    return _response(
        request,
        status.HTTP_422_UNPROCESSABLE_ENTITY,
        "VALIDATION_ERROR",
        "The request contains invalid or missing data.",
        details,
    )


async def database_exception_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    logger.exception("Database error | request_id=%s", _request_id(request), exc_info=exc)
    return _response(
        request,
        status.HTTP_503_SERVICE_UNAVAILABLE,
        "DATABASE_ERROR",
        "The database operation could not be completed.",
    )


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled error | request_id=%s", _request_id(request), exc_info=exc)
    return _response(
        request,
        status.HTTP_500_INTERNAL_SERVER_ERROR,
        "INTERNAL_SERVER_ERROR",
        "An unexpected error occurred.",
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(SQLAlchemyError, database_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)
