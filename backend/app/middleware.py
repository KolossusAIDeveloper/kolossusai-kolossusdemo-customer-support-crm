from fastapi import Request
from fastapi.responses import JSONResponse
import time


# Simple rate limiter as a dependency instead of middleware to avoid BaseHTTPMiddleware compatibility issues
_requests: dict = {}


def check_rate_limit(request: Request, calls: int = 200, period: int = 60) -> bool:
    client_ip = request.client.host if request.client else "unknown"
    now = time.time()
    window_start = now - period

    if client_ip not in _requests:
        _requests[client_ip] = []

    _requests[client_ip] = [t for t in _requests[client_ip] if t > window_start]

    if len(_requests[client_ip]) >= calls:
        return False

    _requests[client_ip].append(now)
    return True
