import time
from collections import defaultdict, deque
from threading import Lock

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from app.core.config import get_settings


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "no-referrer")
        response.headers.setdefault("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
        response.headers.setdefault("Cache-Control", "no-store")
        return response


class RequestSizeLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        settings = get_settings()
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > settings.max_request_body_bytes:
            return JSONResponse({"code": "request_too_large", "message": "Request body is too large"}, status_code=413)
        return await call_next(request)


class SimpleRateLimitMiddleware(BaseHTTPMiddleware):
    _lock = Lock()
    _requests: dict[str, deque[float]] = defaultdict(deque)

    async def dispatch(self, request: Request, call_next) -> Response:
        settings = get_settings()
        now = time.monotonic()
        client = request.client.host if request.client else "unknown"
        key = f"{client}:{request.url.path}"
        with self._lock:
            queue = self._requests[key]
            while queue and now - queue[0] >= settings.rate_limit_window_seconds:
                queue.popleft()
            if len(queue) >= settings.rate_limit_requests:
                return JSONResponse(
                    {"code": "rate_limited", "message": "Too many requests"},
                    status_code=429,
                    headers={"Retry-After": str(settings.rate_limit_window_seconds)},
                )
            queue.append(now)
        return await call_next(request)
