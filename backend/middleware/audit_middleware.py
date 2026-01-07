"""
Audit Middleware - Phase 8
Automatic logging of all API requests/responses
"""
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from sqlalchemy.orm import Session
from database.connection import SessionLocal
from utils.audit_service import AuditService
from models.audit_schema import AuditEventType, AuditSeverity
from typing import Optional
import time
import logging
import json

logger = logging.getLogger(__name__)


class AuditMiddleware(BaseHTTPMiddleware):
    """
    Middleware to automatically log all API requests
    Captures request/response metadata for audit trail
    """
    
    def __init__(self, app: ASGIApp, excluded_paths: list = None):
        super().__init__(app)
        # Paths to exclude from audit logging (e.g., health checks, static files)
        self.excluded_paths = excluded_paths or [
            "/health",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/favicon.ico",
            "/static"
        ]
    
    async def dispatch(self, request: Request, call_next):
        """
        Process each request and log to audit trail
        
        Args:
            request: FastAPI request
            call_next: Next middleware/endpoint
            
        Returns:
            Response from endpoint
        """
        # Skip excluded paths
        if any(request.url.path.startswith(path) for path in self.excluded_paths):
            return await call_next(request)
        
        # Start timing
        start_time = time.time()
        
        # Extract request details
        method = request.method
        path = request.url.path
        ip_address = self._get_client_ip(request)
        user_agent = request.headers.get("user-agent", "Unknown")
        
        # Extract user info from request state (set by auth middleware)
        user_id = None
        username = None
        user_role = None
        
        if hasattr(request.state, "user"):
            user = request.state.user
            user_id = getattr(user, "id", None)
            username = getattr(user, "username", None)
            user_role = getattr(user, "role", None)
        
        # Process request
        response = None
        error_message = None
        success = True
        
        try:
            response = await call_next(request)
            success = response.status_code < 400
            
            if not success:
                error_message = f"HTTP {response.status_code}"
            
        except Exception as e:
            success = False
            error_message = str(e)
            logger.error(f"Error processing request {method} {path}: {error_message}")
            raise
        
        finally:
            # Calculate execution time
            execution_time_ms = (time.time() - start_time) * 1000
            
            # Log to audit trail (async to avoid blocking)
            try:
                self._log_request(
                    method=method,
                    path=path,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    user_id=user_id,
                    username=username,
                    user_role=user_role,
                    success=success,
                    error_message=error_message,
                    execution_time_ms=execution_time_ms,
                    status_code=response.status_code if response else 500
                )
            except Exception as log_error:
                logger.error(f"Failed to log audit entry: {str(log_error)}")
        
        return response
    
    def _get_client_ip(self, request: Request) -> str:
        """
        Extract client IP address from request
        Handles proxies and load balancers
        """
        # Check X-Forwarded-For header (for proxies)
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            # Take the first IP in the chain
            return forwarded_for.split(",")[0].strip()
        
        # Check X-Real-IP header
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip
        
        # Fall back to direct client IP
        if request.client:
            return request.client.host
        
        return "Unknown"
    
    def _log_request(
        self,
        method: str,
        path: str,
        ip_address: str,
        user_agent: str,
        user_id: Optional[int],
        username: Optional[str],
        user_role: Optional[str],
        success: bool,
        error_message: Optional[str],
        execution_time_ms: float,
        status_code: int
    ):
        """
        Log request to audit trail
        Uses a new database session to avoid conflicts
        """
        db = SessionLocal()
        try:
            audit_service = AuditService(db)
            
            # Create metadata
            metadata = {
                "status_code": status_code,
                "execution_time_ms": execution_time_ms
            }
            
            # Determine severity based on status
            if status_code >= 500:
                severity = AuditSeverity.HIGH
            elif status_code >= 400:
                severity = AuditSeverity.MEDIUM
            else:
                severity = AuditSeverity.LOW
            
            # Log the API call
            audit_service.log_event(
                event_type=AuditEventType.API_ERROR if not success else AuditEventType.API_CALL,
                action=f"{method} {path}",
                user_id=user_id,
                username=username,
                user_role=user_role,
                severity=severity,
                endpoint=path,
                http_method=method,
                ip_address=ip_address,
                user_agent=user_agent,
                success=success,
                error_message=error_message,
                execution_time_ms=execution_time_ms,
                metadata=metadata
            )
            
        except Exception as e:
            logger.error(f"Failed to log request to audit trail: {str(e)}")
        finally:
            db.close()


class RequestIdMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add unique request ID to each request
    Useful for tracing and debugging
    """
    
    async def dispatch(self, request: Request, call_next):
        import uuid
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        
        return response


def setup_audit_middleware(app):
    """
    Setup audit middleware on FastAPI app
    
    Args:
        app: FastAPI application
    """
    # Add request ID middleware first
    app.add_middleware(RequestIdMiddleware)
    
    # Add audit middleware
    app.add_middleware(
        AuditMiddleware,
        excluded_paths=[
            "/health",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/favicon.ico",
            "/static"
        ]
    )
    
    logger.info("Audit middleware configured successfully")
