"""
Audit Service - Phase 8
Core service for comprehensive audit logging
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc, asc
from models.database import AuditLog
from models.auth import User
from models.audit_schema import (
    AuditLogEntry,
    AuditEventType,
    AuditSeverity,
    AuditQueryRequest,
    AuditLogResponse,
    AuditStatsResponse,
    UserActivitySummary,
    SecurityEventSummary,
    DataChangeLog,
    AuditRetentionPolicy
)
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import json
import logging

logger = logging.getLogger(__name__)


class AuditService:
    """
    Central audit logging service
    Handles all audit trail operations
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def _convert_to_pydantic(self, audit_log: AuditLog) -> AuditLogEntry:
        """Convert database model to Pydantic model"""
        return AuditLogEntry(
            id=audit_log.id,
            event_type=AuditEventType(audit_log.event_type),
            severity=AuditSeverity(audit_log.severity),
            user_id=audit_log.user_id,
            username=audit_log.username,
            user_role=audit_log.user_role,
            endpoint=audit_log.endpoint,
            http_method=audit_log.http_method,
            ip_address=audit_log.ip_address,
            user_agent=audit_log.user_agent,
            action=audit_log.action,
            resource_type=audit_log.resource_type,
            resource_id=audit_log.resource_id,
            before_state=json.loads(audit_log.before_state) if audit_log.before_state else None,
            after_state=json.loads(audit_log.after_state) if audit_log.after_state else None,
            metadata=json.loads(audit_log.metadata_json) if audit_log.metadata_json else None,
            tags=json.loads(audit_log.tags) if audit_log.tags else [],
            success=audit_log.success,
            error_message=audit_log.error_message,
            execution_time_ms=audit_log.execution_time_ms,
            timestamp=audit_log.timestamp
        )
    
    def log_event(
        self,
        event_type: AuditEventType,
        action: str,
        user_id: Optional[int] = None,
        username: Optional[str] = None,
        user_role: Optional[str] = None,
        severity: AuditSeverity = AuditSeverity.LOW,
        endpoint: Optional[str] = None,
        http_method: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        before_state: Optional[Dict[str, Any]] = None,
        after_state: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None,
        success: bool = True,
        error_message: Optional[str] = None,
        execution_time_ms: Optional[float] = None
    ) -> Optional[AuditLog]:
        """
        Log an audit event
        
        Args:
            event_type: Type of event
            action: Human-readable description
            ... (other parameters)
            
        Returns:
            Created AuditLog entry or None if failed
        """
        try:
            audit_entry = AuditLog(
                event_type=event_type.value,
                severity=severity.value,
                user_id=user_id,
                username=username,
                user_role=user_role,
                endpoint=endpoint,
                http_method=http_method,
                ip_address=ip_address,
                user_agent=user_agent,
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                before_state=json.dumps(before_state) if before_state else None,
                after_state=json.dumps(after_state) if after_state else None,
                metadata_json=json.dumps(metadata) if metadata else None,
                tags=json.dumps(tags) if tags else None,
                success=success,
                error_message=error_message,
                execution_time_ms=execution_time_ms
            )
            
            self.db.add(audit_entry)
            self.db.commit()
            self.db.refresh(audit_entry)
            
            return audit_entry
            
        except Exception as e:
            logger.error(f"Failed to log audit event: {str(e)}")
            self.db.rollback()
            return None
    
    def log_api_call(
        self,
        endpoint: str,
        http_method: str,
        user_id: Optional[int] = None,
        username: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        success: bool = True,
        error_message: Optional[str] = None,
        execution_time_ms: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[AuditLog]:
        """Log an API call"""
        event_type = AuditEventType.API_ERROR if not success else AuditEventType.API_CALL
        severity = AuditSeverity.MEDIUM if not success else AuditSeverity.LOW
        
        action = f"{http_method} {endpoint}"
        if not success:
            action += f" - FAILED: {error_message}"
        
        return self.log_event(
            event_type=event_type,
            action=action,
            user_id=user_id,
            username=username,
            severity=severity,
            endpoint=endpoint,
            http_method=http_method,
            ip_address=ip_address,
            user_agent=user_agent,
            success=success,
            error_message=error_message,
            execution_time_ms=execution_time_ms,
            metadata=metadata
        )
    
    def log_data_change(
        self,
        resource_type: str,
        resource_id: str,
        action: str,
        user_id: int,
        username: str,
        user_role: str,
        before_state: Optional[Dict[str, Any]] = None,
        after_state: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[AuditLog]:
        """Log a data modification event"""
        # Determine event type based on action
        if "create" in action.lower() or "add" in action.lower():
            event_type = AuditEventType.DATA_CREATE
        elif "update" in action.lower() or "edit" in action.lower():
            event_type = AuditEventType.DATA_UPDATE
        elif "delete" in action.lower() or "remove" in action.lower():
            event_type = AuditEventType.DATA_DELETE
        else:
            event_type = AuditEventType.DATA_UPDATE
        
        # Determine severity based on resource type
        critical_resources = ["user", "blacklist", "role", "permission"]
        severity = AuditSeverity.HIGH if resource_type in critical_resources else AuditSeverity.MEDIUM
        
        return self.log_event(
            event_type=event_type,
            action=action,
            user_id=user_id,
            username=username,
            user_role=user_role,
            severity=severity,
            resource_type=resource_type,
            resource_id=resource_id,
            before_state=before_state,
            after_state=after_state,
            ip_address=ip_address,
            metadata=metadata,
            tags=["data_change", resource_type]
        )
    
    def log_security_event(
        self,
        event_type: AuditEventType,
        action: str,
        user_id: Optional[int] = None,
        username: Optional[str] = None,
        ip_address: Optional[str] = None,
        success: bool = True,
        error_message: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[AuditLog]:
        """Log a security event"""
        # Security events are always at least MEDIUM severity
        if not success or "failed" in action.lower() or "denied" in action.lower():
            severity = AuditSeverity.HIGH
        else:
            severity = AuditSeverity.MEDIUM
        
        return self.log_event(
            event_type=event_type,
            action=action,
            user_id=user_id,
            username=username,
            severity=severity,
            ip_address=ip_address,
            success=success,
            error_message=error_message,
            metadata=metadata,
            tags=["security"]
        )
    
    def log_user_action(
        self,
        event_type: AuditEventType,
        action: str,
        user_id: int,
        username: str,
        user_role: str,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[AuditLog]:
        """Log a user action"""
        return self.log_event(
            event_type=event_type,
            action=action,
            user_id=user_id,
            username=username,
            user_role=user_role,
            resource_type=resource_type,
            resource_id=resource_id,
            metadata=metadata,
            tags=["user_action"]
        )
    
    def query_audit_logs(
        self,
        request: AuditQueryRequest
    ) -> AuditLogResponse:
        """
        Query audit logs with filtering
        
        Args:
            request: Query parameters
            
        Returns:
            Paginated audit log results
        """
        query = self.db.query(AuditLog)
        
        # Date filtering
        if request.date_from:
            query = query.filter(AuditLog.timestamp >= request.date_from)
        if request.date_to:
            query = query.filter(AuditLog.timestamp <= request.date_to)
        
        # Event type filtering
        if request.event_types:
            event_type_values = [et.value for et in request.event_types]
            query = query.filter(AuditLog.event_type.in_(event_type_values))
        
        # Severity filtering
        if request.severity_levels:
            severity_values = [s.value for s in request.severity_levels]
            query = query.filter(AuditLog.severity.in_(severity_values))
        
        # User filtering
        if request.user_id:
            query = query.filter(AuditLog.user_id == request.user_id)
        if request.username:
            query = query.filter(AuditLog.username.ilike(f"%{request.username}%"))
        if request.user_role:
            query = query.filter(AuditLog.user_role == request.user_role)
        
        # Resource filtering
        if request.resource_type:
            query = query.filter(AuditLog.resource_type == request.resource_type)
        if request.resource_id:
            query = query.filter(AuditLog.resource_id == request.resource_id)
        
        # Request filtering
        if request.endpoint:
            query = query.filter(AuditLog.endpoint.ilike(f"%{request.endpoint}%"))
        if request.http_method:
            query = query.filter(AuditLog.http_method == request.http_method)
        if request.ip_address:
            query = query.filter(AuditLog.ip_address == request.ip_address)
        
        # Status filtering
        if request.success_only:
            query = query.filter(AuditLog.success == True)
        if request.failed_only:
            query = query.filter(AuditLog.success == False)
        
        # Tags filtering
        if request.tags:
            for tag in request.tags:
                query = query.filter(AuditLog.tags.like(f'%"{tag}"%'))
        
        # Full-text search
        if request.search_query:
            search_filter = or_(
                AuditLog.action.ilike(f"%{request.search_query}%"),
                AuditLog.error_message.ilike(f"%{request.search_query}%")
            )
            query = query.filter(search_filter)
        
        # Get total count
        total_count = query.count()
        
        # Sorting
        if request.sort_desc:
            query = query.order_by(desc(getattr(AuditLog, request.sort_by)))
        else:
            query = query.order_by(asc(getattr(AuditLog, request.sort_by)))
        
        # Pagination
        offset = (request.page - 1) * request.page_size
        query = query.offset(offset).limit(request.page_size)
        
        # Execute query
        audit_logs = query.all()
        
        # Convert to Pydantic models
        log_entries = [self._convert_to_pydantic(log) for log in audit_logs]
        
        # Calculate total pages
        total_pages = (total_count + request.page_size - 1) // request.page_size
        
        return AuditLogResponse(
            logs=log_entries,
            total_count=total_count,
            page=request.page,
            page_size=request.page_size,
            total_pages=total_pages
        )
    
    def get_user_activity(
        self,
        user_id: int,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None
    ) -> Optional[UserActivitySummary]:
        """
        Get activity summary for a specific user
        
        Args:
            user_id: User ID
            date_from: Start date (optional)
            date_to: End date (optional)
            
        Returns:
            User activity summary
        """
        query = self.db.query(AuditLog).filter(AuditLog.user_id == user_id)
        
        if date_from:
            query = query.filter(AuditLog.timestamp >= date_from)
        if date_to:
            query = query.filter(AuditLog.timestamp <= date_to)
        
        logs = query.all()
        
        if not logs:
            return None
        
        # Get user details
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return None
        
        # Calculate stats
        total_actions = len(logs)
        successful_actions = sum(1 for log in logs if log.success)
        failed_actions = total_actions - successful_actions
        
        # Events by type
        events_by_type = {}
        for log in logs:
            events_by_type[log.event_type] = events_by_type.get(log.event_type, 0) + 1
        
        # Time stats
        first_activity = min(log.timestamp for log in logs)
        last_activity = max(log.timestamp for log in logs)
        
        # Resource stats
        unique_resources = set(
            f"{log.resource_type}:{log.resource_id}"
            for log in logs
            if log.resource_type and log.resource_id
        )
        resource_types = list(set(log.resource_type for log in logs if log.resource_type))
        
        # Security flags
        failed_auth_count = sum(
            1 for log in logs
            if log.event_type == AuditEventType.AUTH_FAILED.value
        )
        permission_denials = sum(
            1 for log in logs
            if log.event_type == AuditEventType.SECURITY_PERMISSION_DENIED.value
        )
        has_suspicious_activity = any(
            log.event_type == AuditEventType.SECURITY_SUSPICIOUS_ACTIVITY.value
            for log in logs
        )
        
        return UserActivitySummary(
            user_id=user_id,
            username=user.username,
            user_role=user.role,
            total_actions=total_actions,
            successful_actions=successful_actions,
            failed_actions=failed_actions,
            events_by_type=events_by_type,
            first_activity=first_activity,
            last_activity=last_activity,
            unique_resources_accessed=len(unique_resources),
            resource_types=resource_types,
            failed_auth_count=failed_auth_count,
            permission_denials=permission_denials,
            has_suspicious_activity=has_suspicious_activity
        )
    
    def get_security_events(
        self,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        limit: int = 100
    ) -> SecurityEventSummary:
        """
        Get summary of security events
        
        Args:
            date_from: Start date
            date_to: End date
            limit: Max events to return
            
        Returns:
            Security event summary
        """
        if not date_from:
            date_from = datetime.utcnow() - timedelta(days=7)
        if not date_to:
            date_to = datetime.utcnow()
        
        # Query security-related events
        security_events = self.db.query(AuditLog).filter(
            and_(
                AuditLog.timestamp >= date_from,
                AuditLog.timestamp <= date_to,
                or_(
                    AuditLog.event_type.like("auth_%"),
                    AuditLog.event_type.like("security_%")
                )
            )
        ).all()
        
        # Failed logins
        failed_login_logs = [
            log for log in security_events
            if log.event_type == AuditEventType.AUTH_FAILED.value
        ]
        failed_logins = len(failed_login_logs)
        failed_login_ips = list(set(log.ip_address for log in failed_login_logs if log.ip_address))
        failed_login_users = list(set(log.username for log in failed_login_logs if log.username))
        
        # Permission denials
        permission_denial_logs = [
            log for log in security_events
            if log.event_type == AuditEventType.SECURITY_PERMISSION_DENIED.value
        ]
        permission_denials = len(permission_denial_logs)
        
        # Suspicious activity
        suspicious_logs = [
            log for log in security_events
            if log.event_type == AuditEventType.SECURITY_SUSPICIOUS_ACTIVITY.value
        ]
        suspicious_ips = list(set(log.ip_address for log in suspicious_logs if log.ip_address))
        
        # High/critical severity events
        high_severity_logs = [
            log for log in security_events
            if log.severity == AuditSeverity.HIGH.value
        ][:limit]
        
        critical_logs = [
            log for log in security_events
            if log.severity == AuditSeverity.CRITICAL.value
        ][:limit]
        
        # Convert to Pydantic
        suspicious_events = [self._convert_to_pydantic(log) for log in suspicious_logs[:limit]]
        recent_high_severity = [self._convert_to_pydantic(log) for log in high_severity_logs]
        recent_critical = [self._convert_to_pydantic(log) for log in critical_logs]
        
        return SecurityEventSummary(
            failed_logins=failed_logins,
            failed_login_ips=failed_login_ips,
            failed_login_users=failed_login_users,
            permission_denials=permission_denials,
            denied_resources=[],
            suspicious_events=suspicious_events,
            suspicious_ips=suspicious_ips,
            locked_accounts=0,
            password_changes=0,
            role_changes=0,
            recent_high_severity=recent_high_severity,
            recent_critical=recent_critical,
            date_from=date_from,
            date_to=date_to
        )
    
    def enforce_retention_policy(
        self,
        policy: AuditRetentionPolicy
    ) -> Dict[str, int]:
        """
        Enforce audit log retention policy
        
        Args:
            policy: Retention policy configuration
            
        Returns:
            Dictionary with deletion counts by severity
        """
        deleted_counts = {
            "low": 0,
            "medium": 0,
            "high": 0,
            "critical": 0
        }
        
        try:
            current_time = datetime.utcnow()
            
            # Delete low severity logs
            if policy.low_severity_days > 0:
                cutoff_date = current_time - timedelta(days=policy.low_severity_days)
                deleted = self.db.query(AuditLog).filter(
                    and_(
                        AuditLog.severity == AuditSeverity.LOW.value,
                        AuditLog.timestamp < cutoff_date
                    )
                ).delete()
                deleted_counts["low"] = deleted
            
            # Delete medium severity logs
            if policy.medium_severity_days > 0:
                cutoff_date = current_time - timedelta(days=policy.medium_severity_days)
                deleted = self.db.query(AuditLog).filter(
                    and_(
                        AuditLog.severity == AuditSeverity.MEDIUM.value,
                        AuditLog.timestamp < cutoff_date
                    )
                ).delete()
                deleted_counts["medium"] = deleted
            
            # Delete high severity logs (unless it's a security event)
            if policy.high_severity_days > 0 and not policy.keep_security_events:
                cutoff_date = current_time - timedelta(days=policy.high_severity_days)
                deleted = self.db.query(AuditLog).filter(
                    and_(
                        AuditLog.severity == AuditSeverity.HIGH.value,
                        AuditLog.timestamp < cutoff_date
                    )
                ).delete()
                deleted_counts["high"] = deleted
            
            self.db.commit()
            
            logger.info(f"Retention policy enforced: {deleted_counts}")
            return deleted_counts
            
        except Exception as e:
            logger.error(f"Failed to enforce retention policy: {str(e)}")
            self.db.rollback()
            return deleted_counts


def get_audit_service(db: Session) -> AuditService:
    """Dependency injection for audit service"""
    return AuditService(db)
