"""
Audit Decorators - Phase 8
Function decorators for automatic audit logging
"""
from functools import wraps
from typing import Callable, Optional, Dict, Any
from database.connection import SessionLocal
from utils.audit_service import AuditService
from models.audit_schema import AuditEventType, AuditSeverity
import inspect
import logging

logger = logging.getLogger(__name__)


def audit_action(
    event_type: AuditEventType,
    action_template: str,
    severity: AuditSeverity = AuditSeverity.MEDIUM,
    resource_type: Optional[str] = None,
    capture_args: bool = False,
    capture_result: bool = False
):
    """
    Decorator to audit a function call
    
    Usage:
        @audit_action(
            event_type=AuditEventType.BLACKLIST_UPLOADED,
            action_template="Blacklist file uploaded: {filename}",
            severity=AuditSeverity.HIGH,
            resource_type="blacklist",
            capture_args=True
        )
        def upload_blacklist(filename: str, user_id: int):
            ...
    
    Args:
        event_type: Type of audit event
        action_template: String template for action description (can use {arg_name} placeholders)
        severity: Event severity level
        resource_type: Type of resource being acted upon
        capture_args: Whether to capture function arguments in metadata
        capture_result: Whether to capture function result in metadata
    """
    def decorator(func: Callable):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            return await _execute_with_audit(
                func, args, kwargs,
                event_type, action_template, severity, resource_type,
                capture_args, capture_result, is_async=True
            )
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            return _execute_with_audit(
                func, args, kwargs,
                event_type, action_template, severity, resource_type,
                capture_args, capture_result, is_async=False
            )
        
        # Return appropriate wrapper based on function type
        if inspect.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


async def _execute_with_audit(
    func: Callable,
    args: tuple,
    kwargs: dict,
    event_type: AuditEventType,
    action_template: str,
    severity: AuditSeverity,
    resource_type: Optional[str],
    capture_args: bool,
    capture_result: bool,
    is_async: bool
):
    """Execute function with audit logging"""
    import time
    start_time = time.time()
    
    # Extract function signature
    sig = inspect.signature(func)
    bound_args = sig.bind(*args, **kwargs)
    bound_args.apply_defaults()
    
    # Extract user context from arguments
    user_id = bound_args.arguments.get("user_id") or \
              bound_args.arguments.get("current_user_id")
    username = bound_args.arguments.get("username")
    user_role = bound_args.arguments.get("user_role")
    
    # If we have a user object, extract from it
    current_user = bound_args.arguments.get("current_user")
    if current_user:
        user_id = getattr(current_user, "id", user_id)
        username = getattr(current_user, "username", username)
        user_role = getattr(current_user, "role", user_role)
    
    # Extract resource ID if provided
    resource_id = bound_args.arguments.get("resource_id") or \
                  bound_args.arguments.get("id") or \
                  bound_args.arguments.get("item_id")
    
    # Format action string with arguments
    try:
        action = action_template.format(**bound_args.arguments)
    except (KeyError, ValueError):
        action = action_template
    
    # Prepare metadata
    metadata = {}
    if capture_args:
        # Capture function arguments (sanitize sensitive data)
        safe_args = {
            k: v for k, v in bound_args.arguments.items()
            if not k.lower() in ["password", "token", "secret", "key"]
        }
        metadata["args"] = str(safe_args)
    
    metadata["function"] = func.__name__
    metadata["module"] = func.__module__
    
    # Execute function
    result = None
    success = True
    error_message = None
    
    try:
        if is_async:
            result = await func(*args, **kwargs)
        else:
            result = func(*args, **kwargs)
        
        if capture_result:
            # Sanitize result (don't capture large objects)
            if result is not None and len(str(result)) < 1000:
                metadata["result"] = str(result)
    
    except Exception as e:
        success = False
        error_message = str(e)
        logger.error(f"Error in audited function {func.__name__}: {error_message}")
        raise
    
    finally:
        # Calculate execution time
        execution_time_ms = (time.time() - start_time) * 1000
        
        # Log to audit trail
        try:
            db = SessionLocal()
            try:
                audit_service = AuditService(db)
                audit_service.log_event(
                    event_type=event_type,
                    action=action,
                    user_id=user_id,
                    username=username,
                    user_role=user_role,
                    severity=severity,
                    resource_type=resource_type,
                    resource_id=str(resource_id) if resource_id else None,
                    success=success,
                    error_message=error_message,
                    execution_time_ms=execution_time_ms,
                    metadata=metadata,
                    tags=["function_call", func.__name__]
                )
            finally:
                db.close()
        except Exception as log_error:
            logger.error(f"Failed to log audit entry: {str(log_error)}")
    
    return result


def audit_data_change(
    resource_type: str,
    action_template: str,
    severity: AuditSeverity = AuditSeverity.MEDIUM,
    capture_before: bool = True,
    capture_after: bool = True
):
    """
    Decorator to audit data modification operations
    
    Usage:
        @audit_data_change(
            resource_type="user",
            action_template="Updated user {username}",
            capture_before=True,
            capture_after=True
        )
        def update_user(user_id: int, data: dict, current_user):
            ...
    
    Args:
        resource_type: Type of resource being modified
        action_template: String template for action
        severity: Event severity
        capture_before: Capture state before modification
        capture_after: Capture state after modification
    """
    def decorator(func: Callable):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            return await _execute_data_change_audit(
                func, args, kwargs,
                resource_type, action_template, severity,
                capture_before, capture_after, is_async=True
            )
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            return _execute_data_change_audit(
                func, args, kwargs,
                resource_type, action_template, severity,
                capture_before, capture_after, is_async=False
            )
        
        if inspect.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


async def _execute_data_change_audit(
    func: Callable,
    args: tuple,
    kwargs: dict,
    resource_type: str,
    action_template: str,
    severity: AuditSeverity,
    capture_before: bool,
    capture_after: bool,
    is_async: bool
):
    """Execute data change with audit logging"""
    # Extract arguments
    sig = inspect.signature(func)
    bound_args = sig.bind(*args, **kwargs)
    bound_args.apply_defaults()
    
    # Extract user context
    user_id = bound_args.arguments.get("user_id")
    username = bound_args.arguments.get("username")
    user_role = bound_args.arguments.get("user_role")
    
    current_user = bound_args.arguments.get("current_user")
    if current_user:
        user_id = getattr(current_user, "id", user_id)
        username = getattr(current_user, "username", username)
        user_role = getattr(current_user, "role", user_role)
    
    # Extract resource ID
    resource_id = bound_args.arguments.get("resource_id") or \
                  bound_args.arguments.get("id") or \
                  bound_args.arguments.get("user_id") or \
                  bound_args.arguments.get("item_id")
    
    # Format action
    try:
        action = action_template.format(**bound_args.arguments)
    except (KeyError, ValueError):
        action = action_template
    
    # Capture before state (if applicable)
    before_state = None
    if capture_before and "before_data" in bound_args.arguments:
        before_state = bound_args.arguments["before_data"]
    
    # Execute function
    result = None
    success = True
    error_message = None
    after_state = None
    
    try:
        if is_async:
            result = await func(*args, **kwargs)
        else:
            result = func(*args, **kwargs)
        
        # Capture after state
        if capture_after:
            if hasattr(result, "to_dict"):
                after_state = result.to_dict()
            elif isinstance(result, dict):
                after_state = result
    
    except Exception as e:
        success = False
        error_message = str(e)
        raise
    
    finally:
        # Log to audit
        try:
            db = SessionLocal()
            try:
                audit_service = AuditService(db)
                audit_service.log_data_change(
                    resource_type=resource_type,
                    resource_id=str(resource_id) if resource_id else None,
                    action=action,
                    user_id=user_id or 0,
                    username=username or "Unknown",
                    user_role=user_role or "Unknown",
                    before_state=before_state,
                    after_state=after_state,
                    metadata={
                        "function": func.__name__,
                        "success": success,
                        "error": error_message
                    }
                )
            finally:
                db.close()
        except Exception as log_error:
            logger.error(f"Failed to log data change: {str(log_error)}")
    
    return result


def audit_security(
    event_type: AuditEventType,
    action_template: str,
    severity: AuditSeverity = AuditSeverity.HIGH
):
    """
    Decorator to audit security-related operations
    Always logs with at least HIGH severity
    
    Usage:
        @audit_security(
            event_type=AuditEventType.SECURITY_ROLE_CHANGE,
            action_template="Changed role for user {username} to {new_role}"
        )
        def change_user_role(username: str, new_role: str, current_user):
            ...
    """
    # Security events always HIGH or CRITICAL
    if severity not in [AuditSeverity.HIGH, AuditSeverity.CRITICAL]:
        severity = AuditSeverity.HIGH
    
    return audit_action(
        event_type=event_type,
        action_template=action_template,
        severity=severity,
        resource_type="security",
        capture_args=True,
        capture_result=False
    )


# Convenience decorators for common operations

def audit_file_upload(filename_param: str = "filename"):
    """Decorator for file upload operations"""
    return audit_action(
        event_type=AuditEventType.FILE_UPLOAD,
        action_template=f"File uploaded: {{{filename_param}}}",
        severity=AuditSeverity.MEDIUM,
        resource_type="file",
        capture_args=True
    )


def audit_report_generation(report_type_param: str = "report_type"):
    """Decorator for report generation operations"""
    return audit_action(
        event_type=AuditEventType.REPORT_GENERATED,
        action_template=f"Report generated: {{{report_type_param}}}",
        severity=AuditSeverity.LOW,
        resource_type="report",
        capture_args=True
    )


def audit_blacklist_operation(operation: str):
    """Decorator for blacklist operations"""
    return audit_action(
        event_type=AuditEventType.BLACKLIST_UPDATED,
        action_template=f"Blacklist {operation}",
        severity=AuditSeverity.HIGH,
        resource_type="blacklist",
        capture_args=True
    )


def audit_user_management(operation: str):
    """Decorator for user management operations"""
    event_map = {
        "create": AuditEventType.USER_CREATED,
        "update": AuditEventType.USER_UPDATED,
        "delete": AuditEventType.USER_DELETED,
        "activate": AuditEventType.USER_ACTIVATED,
        "deactivate": AuditEventType.USER_DEACTIVATED
    }
    
    event_type = event_map.get(operation, AuditEventType.USER_UPDATED)
    
    return audit_action(
        event_type=event_type,
        action_template=f"User {operation}d: {{username}}",
        severity=AuditSeverity.HIGH,
        resource_type="user",
        capture_args=True
    )
