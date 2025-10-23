"""
Security middleware for the Medical Text Classification API.
"""
import logging
import os
import time
from collections import defaultdict
from datetime import datetime, timezone
from typing import Dict, List, Optional

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from src.api.security import log_security_event, security_config

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware to prevent abuse."""
    
    def __init__(self, app, requests_per_window: Optional[int] = None, window_seconds: Optional[int] = None):
        super().__init__(app)
        self.requests_per_window = requests_per_window or security_config.RATE_LIMIT_REQUESTS
        self.window_seconds = window_seconds or security_config.RATE_LIMIT_WINDOW
        self.client_requests: Dict[str, list] = defaultdict(list)
    
    def _get_client_id(self, request: Request) -> str:
        """Get client identifier for rate limiting."""
        # Use X-Forwarded-For if behind proxy, otherwise use client IP
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        return request.client.host if request.client else "unknown"
    
    def _clean_old_requests(self, client_id: str, current_time: float):
        """Remove old requests outside the time window."""
        cutoff_time = current_time - self.window_seconds
        self.client_requests[client_id] = [
            req_time for req_time in self.client_requests[client_id]
            if req_time > cutoff_time
        ]
    
    def _is_rate_limited(self, client_id: str, current_time: float) -> bool:
        """Check if client is rate limited."""
        self._clean_old_requests(client_id, current_time)
        return len(self.client_requests[client_id]) >= self.requests_per_window
    
    async def dispatch(self, request: Request, call_next):
        """Process request with rate limiting."""
        # Skip rate limiting for health checks and OPTIONS requests
        if request.url.path in ["/health", "/metrics"] or request.method == "OPTIONS":
            return await call_next(request)

        # Skip rate limiting completely in test environment
        if os.getenv('TESTING', 'false').lower() in ['true', '1']:
            return await call_next(request)

        client_id = self._get_client_id(request)
        current_time = time.time()

        if self._is_rate_limited(client_id, current_time):
            # Log rate limit violation
            log_security_event(
                "rate_limit_exceeded",
                {
                    "client_id": client_id,
                    "requests_in_window": len(self.client_requests[client_id]),
                    "limit": self.requests_per_window,
                    "window_seconds": self.window_seconds
                },
                request
            )

            return JSONResponse(
                status_code=429,
                content={
                    "error": "Rate limit exceeded",
                    "detail": f"Maximum {self.requests_per_window} requests per {self.window_seconds} seconds",
                    "retry_after": self.window_seconds
                },
                headers={"Retry-After": str(self.window_seconds)}
            )

        # Record this request
        self.client_requests[client_id].append(current_time)

        return await call_next(request)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware to add security headers."""
    
    async def dispatch(self, request: Request, call_next):
        """Add security headers to response."""
        response = await call_next(request)
        
        if security_config.ENABLE_SECURITY_HEADERS:
            # Store existing CORS headers to preserve them
            existing_cors_headers = {}
            for header_name in ["access-control-allow-origin", "access-control-allow-methods", 
                               "access-control-allow-headers", "access-control-expose-headers",
                               "access-control-allow-credentials"]:
                if header_name in response.headers:
                    existing_cors_headers[header_name] = response.headers[header_name]
            
            # Prevent clickjacking
            response.headers["X-Frame-Options"] = "DENY"
            
            # Prevent MIME type sniffing
            response.headers["X-Content-Type-Options"] = "nosniff"
            
            # Enable XSS protection
            response.headers["X-XSS-Protection"] = "1; mode=block"
            
            # Strict transport security (HTTPS only)
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
            
            # Content Security Policy
            response.headers["Content-Security-Policy"] = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data:; "
                "font-src 'self'; "
                "connect-src 'self'; "
                "frame-ancestors 'none'"
            )
            
            # Referrer Policy
            response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
            
            # Permissions Policy
            response.headers["Permissions-Policy"] = (
                "geolocation=(), "
                "microphone=(), "
                "camera=(), "
                "payment=(), "
                "usb=(), "
                "magnetometer=(), "
                "gyroscope=(), "
                "speaker=()"
            )
            
            # Restore CORS headers
            for header_name, header_value in existing_cors_headers.items():
                response.headers[header_name] = header_value
        
        return response


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for comprehensive request logging."""
    
    async def dispatch(self, request: Request, call_next):
        """Log request details for security monitoring."""
        start_time = time.time()
        
        # Log request details
        if security_config.LOG_REQUESTS:
            client_ip = request.client.host if request.client else "unknown"
            user_agent = request.headers.get("user-agent", "unknown")
            
            log_data = {
                "method": request.method,
                "path": str(request.url.path),
                "query_params": str(request.query_params),
                "client_ip": client_ip,
                "user_agent": user_agent,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            # Log headers (excluding sensitive ones)
            sensitive_headers = {"authorization", "x-api-key", "cookie"}
            headers = {
                k: v for k, v in request.headers.items()
                if k.lower() not in sensitive_headers
            }
            log_data["headers"] = headers
            
            logger.info(f"Request: {log_data}")
        
        # Process request
        try:
            response = await call_next(request)
            
            # Log response details
            if security_config.LOG_REQUESTS:
                duration = time.time() - start_time
                logger.info(f"Response: status={response.status_code}, duration={duration:.3f}s")
            
            return response
            
        except Exception as e:
            # Log errors
            duration = time.time() - start_time
            logger.error(f"Request failed: {str(e)}, duration={duration:.3f}s")
            raise


class TrustedHostMiddleware(BaseHTTPMiddleware):
    """Middleware to validate Host header against allowed hosts."""
    
    def __init__(self, app, allowed_hosts: Optional[List[str]] = None):
        super().__init__(app)
        self.allowed_hosts = allowed_hosts or security_config.ALLOWED_HOSTS
    
    async def dispatch(self, request: Request, call_next):
        """Validate Host header."""
        # Skip host validation for OPTIONS requests and in test environment
        if request.method == "OPTIONS" or os.getenv('TESTING', 'false').lower() in ['true', '1']:
            return await call_next(request)

        if "*" in self.allowed_hosts:
            return await call_next(request)

        host = request.headers.get("host", "").split(":")[0]  # Remove port

        if host not in self.allowed_hosts:
            log_security_event(
                "invalid_host_header",
                {
                    "host": host,
                    "allowed_hosts": self.allowed_hosts
                },
                request
            )

            return JSONResponse(
                status_code=400,
                content={
                    "error": "Invalid Host header",
                    "detail": "The Host header is not allowed"
                }
            )

        return await call_next(request)


class InputSanitizationMiddleware(BaseHTTPMiddleware):
    """Middleware for input sanitization and validation."""
    
    async def dispatch(self, request: Request, call_next):
        """Sanitize and validate inputs."""
        # Check for suspicious patterns in URL
        suspicious_patterns = [
            "../", "..\\", "<script", "javascript:", "data:", "vbscript:",
            "onload=", "onerror=", "onclick=", "eval(", "expression(",
            "union select", "drop table", "insert into", "delete from"
        ]
        
        path_lower = request.url.path.lower()
        query_lower = str(request.query_params).lower()
        
        for pattern in suspicious_patterns:
            if pattern in path_lower or pattern in query_lower:
                log_security_event(
                    "suspicious_input_detected",
                    {
                        "pattern": pattern,
                        "path": request.url.path,
                        "query_params": str(request.query_params)
                    },
                    request
                )
                
                return JSONResponse(
                    status_code=400,
                    content={
                        "error": "Invalid input detected",
                        "detail": "Request contains potentially malicious content"
                    }
                )
        
        return await call_next(request)
