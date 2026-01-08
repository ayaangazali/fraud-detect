"""
Audit Log API Routes - Phase 8
REST endpoints for querying and analyzing audit logs
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from database.connection import get_db
from models.auth import User
from models.audit_schema import (
    AuditQueryRequest,
    AuditLogResponse,
    AuditStatsResponse,
    UserActivitySummary,
    SecurityEventSummary,
    AuditRetentionPolicy,
    AuditEventType,
    AuditSeverity
)
from utils.auth import get_current_user
from utils.audit_service import get_audit_service
from datetime import datetime, timedelta
from typing import List, Optional
import logging
import csv
import os

router = APIRouter()
logger = logging.getLogger(__name__)


def require_admin(current_user: User = Depends(get_current_user)):
    """Require admin role for audit access"""
    if current_user.role not in ["admin", "finalizer"]:
        raise HTTPException(
            status_code=403,
            detail="Only administrators can access audit logs"
        )
    return current_user


@router.get("/logs", response_model=AuditLogResponse)
async def query_audit_logs(
    date_from: Optional[datetime] = Query(None, description="Start date"),
    date_to: Optional[datetime] = Query(None, description="End date"),
    event_types: Optional[List[str]] = Query(None, description="Filter by event types"),
    severity_levels: Optional[List[str]] = Query(None, description="Filter by severity"),
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    resource_type: Optional[str] = Query(None, description="Filter by resource type"),
    search_query: Optional[str] = Query(None, description="Search query"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Page size"),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Query audit logs with filtering (GET endpoint for easy frontend access)
    
    - **date_from**: Start date (optional)
    - **date_to**: End date (optional)
    - **event_types**: Filter by event types
    - **severity_levels**: Filter by severity
    - **user_id**: Filter by user
    - **resource_type**: Filter by resource
    - **search_query**: Full-text search
    - **page**: Page number (default 1)
    - **page_size**: Results per page (default 50)
    """
    try:
        from models.audit_schema import AuditQueryRequest
        
        # Build request object from query params
        request = AuditQueryRequest(
            date_from=date_from,
            date_to=date_to,
            event_types=event_types,
            severity_levels=severity_levels,
            user_id=user_id,
            resource_type=resource_type,
            search_query=search_query,
            page=page,
            page_size=page_size
        )
        
        audit_service = get_audit_service(db)
        result = audit_service.query_audit_logs(request)
        
        logger.info(
            f"Admin {current_user.username} queried audit logs: "
            f"{result.total_count} results"
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error querying audit logs: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/user/{user_id}", response_model=UserActivitySummary)
async def get_user_activity(
    user_id: int,
    date_from: Optional[datetime] = Query(None, description="Start date"),
    date_to: Optional[datetime] = Query(None, description="End date"),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Get activity summary for a specific user
    
    Returns:
    - Total actions
    - Success/failure counts
    - Event breakdown
    - Security flags
    - Time stats
    """
    try:
        audit_service = get_audit_service(db)
        
        if not date_from:
            date_from = datetime.utcnow() - timedelta(days=30)
        if not date_to:
            date_to = datetime.utcnow()
        
        summary = audit_service.get_user_activity(user_id, date_from, date_to)
        
        if not summary:
            raise HTTPException(
                status_code=404,
                detail=f"No activity found for user {user_id}"
            )
        
        logger.info(
            f"Admin {current_user.username} retrieved activity for user {user_id}"
        )
        
        return summary
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving user activity: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/security", response_model=SecurityEventSummary)
async def get_security_events(
    date_from: Optional[datetime] = Query(None, description="Start date"),
    date_to: Optional[datetime] = Query(None, description="End date"),
    limit: int = Query(100, ge=1, le=1000, description="Max events to return"),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Get summary of security events
    
    Returns:
    - Failed login attempts
    - Permission denials
    - Suspicious activities
    - Recent high/critical events
    """
    try:
        audit_service = get_audit_service(db)
        
        if not date_from:
            date_from = datetime.utcnow() - timedelta(days=7)
        if not date_to:
            date_to = datetime.utcnow()
        
        summary = audit_service.get_security_events(date_from, date_to, limit)
        
        logger.info(
            f"Admin {current_user.username} retrieved security events summary"
        )
        
        return summary
        
    except Exception as e:
        logger.error(f"Error retrieving security events: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Alias endpoint for tests
@router.get("/security-events", response_model=SecurityEventSummary)
async def get_security_events_alias(
    date_from: Optional[datetime] = Query(None, description="Start date"),
    date_to: Optional[datetime] = Query(None, description="End date"),
    limit: int = Query(100, ge=1, le=1000, description="Max events to return"),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Alias for /security endpoint"""
    return await get_security_events(date_from, date_to, limit, current_user, db)


# Alias endpoint for user activity without user_id (returns all activity)
@router.get("/user-activity")
async def get_all_user_activity(
    date_from: Optional[datetime] = Query(None, description="Start date"),
    date_to: Optional[datetime] = Query(None, description="End date"),
    limit: int = Query(100, ge=1, le=1000, description="Max activities to return"),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Get recent user activity across all users
    """
    try:
        from sqlalchemy import func
        from models.database import AuditLog
        
        if not date_from:
            date_from = datetime.utcnow() - timedelta(days=7)
        if not date_to:
            date_to = datetime.utcnow()
        
        # Get recent activities grouped by user
        activities_query = db.query(
            AuditLog.username,
            AuditLog.user_role,
            func.count(AuditLog.id).label('total_actions'),
            func.max(AuditLog.timestamp).label('last_activity')
        ).filter(
            AuditLog.timestamp >= date_from,
            AuditLog.timestamp <= date_to,
            AuditLog.username.isnot(None)
        ).group_by(
            AuditLog.username,
            AuditLog.user_role
        ).order_by(
            func.max(AuditLog.timestamp).desc()
        ).limit(limit).all()
        
        activities = [
            {
                "username": row.username,
                "role": row.user_role,
                "total_actions": row.total_actions,
                "last_activity": row.last_activity.isoformat() if row.last_activity else None
            }
            for row in activities_query
        ]
        
        logger.info(
            f"Admin {current_user.username} retrieved user activity summary"
        )
        
        return {
            "success": True,
            "date_from": date_from.isoformat(),
            "date_to": date_to.isoformat(),
            "activities": activities,
            "count": len(activities)
        }
        
    except Exception as e:
        logger.error(f"Error retrieving user activity: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_audit_stats(
    date_from: Optional[datetime] = Query(None, description="Start date"),
    date_to: Optional[datetime] = Query(None, description="End date"),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Get audit statistics
    
    Returns:
    - Event counts by type
    - Most active users
    - Error rates
    - Performance metrics
    """
    try:
        from sqlalchemy import func
        from models.database import AuditLog
        
        if not date_from:
            date_from = datetime.utcnow() - timedelta(days=30)
        if not date_to:
            date_to = datetime.utcnow()
        
        # Total events
        total_events = db.query(func.count(AuditLog.id)).filter(
            AuditLog.timestamp >= date_from,
            AuditLog.timestamp <= date_to
        ).scalar()
        
        # Events by type
        events_by_type_query = db.query(
            AuditLog.event_type,
            func.count(AuditLog.id).label('count')
        ).filter(
            AuditLog.timestamp >= date_from,
            AuditLog.timestamp <= date_to
        ).group_by(AuditLog.event_type).all()
        
        events_by_type = {row.event_type: row.count for row in events_by_type_query}
        
        # Events by severity
        events_by_severity_query = db.query(
            AuditLog.severity,
            func.count(AuditLog.id).label('count')
        ).filter(
            AuditLog.timestamp >= date_from,
            AuditLog.timestamp <= date_to
        ).group_by(AuditLog.severity).all()
        
        events_by_severity = {row.severity: row.count for row in events_by_severity_query}
        
        # Most active users
        most_active_users_query = db.query(
            AuditLog.username,
            AuditLog.user_role,
            func.count(AuditLog.id).label('count')
        ).filter(
            AuditLog.timestamp >= date_from,
            AuditLog.timestamp <= date_to,
            AuditLog.username.isnot(None)
        ).group_by(AuditLog.username, AuditLog.user_role).order_by(
            func.count(AuditLog.id).desc()
        ).limit(10).all()
        
        most_active_users = [
            {"username": row.username, "role": row.user_role, "actions": row.count}
            for row in most_active_users_query
        ]
        
        # Error count
        error_count = db.query(func.count(AuditLog.id)).filter(
            AuditLog.timestamp >= date_from,
            AuditLog.timestamp <= date_to,
            AuditLog.success == False
        ).scalar()
        
        error_rate = (error_count / total_events * 100) if total_events > 0 else 0.0
        
        # Performance metrics
        avg_execution_time = db.query(
            func.avg(AuditLog.execution_time_ms)
        ).filter(
            AuditLog.timestamp >= date_from,
            AuditLog.timestamp <= date_to,
            AuditLog.execution_time_ms.isnot(None)
        ).scalar()
        
        # Slowest endpoints
        slowest_endpoints_query = db.query(
            AuditLog.endpoint,
            func.avg(AuditLog.execution_time_ms).label('avg_time'),
            func.count(AuditLog.id).label('count')
        ).filter(
            AuditLog.timestamp >= date_from,
            AuditLog.timestamp <= date_to,
            AuditLog.endpoint.isnot(None),
            AuditLog.execution_time_ms.isnot(None)
        ).group_by(AuditLog.endpoint).order_by(
            func.avg(AuditLog.execution_time_ms).desc()
        ).limit(10).all()
        
        slowest_endpoints = [
            {"endpoint": row.endpoint, "avg_time_ms": float(row.avg_time), "calls": row.count}
            for row in slowest_endpoints_query
        ]
        
        # Security stats
        failed_auth_attempts = db.query(func.count(AuditLog.id)).filter(
            AuditLog.timestamp >= date_from,
            AuditLog.timestamp <= date_to,
            AuditLog.event_type == AuditEventType.AUTH_FAILED.value
        ).scalar()
        
        permission_denials = db.query(func.count(AuditLog.id)).filter(
            AuditLog.timestamp >= date_from,
            AuditLog.timestamp <= date_to,
            AuditLog.event_type == AuditEventType.SECURITY_PERMISSION_DENIED.value
        ).scalar()
        
        suspicious_activities = db.query(func.count(AuditLog.id)).filter(
            AuditLog.timestamp >= date_from,
            AuditLog.timestamp <= date_to,
            AuditLog.event_type == AuditEventType.SECURITY_SUSPICIOUS_ACTIVITY.value
        ).scalar()
        
        logger.info(
            f"Admin {current_user.username} retrieved audit statistics"
        )
        
        return {
            "total_events": total_events,
            "events_by_type": events_by_type,
            "events_by_severity": events_by_severity,
            "most_active_users": most_active_users,
            "events_by_hour": {},  # TODO: Implement
            "events_by_day": {},   # TODO: Implement
            "failed_auth_attempts": failed_auth_attempts,
            "permission_denials": permission_denials,
            "suspicious_activities": suspicious_activities,
            "avg_execution_time_ms": float(avg_execution_time) if avg_execution_time else None,
            "slowest_endpoints": slowest_endpoints,
            "error_count": error_count,
            "error_rate": round(error_rate, 2),
            "most_common_errors": [],  # TODO: Implement
            "date_from": date_from,
            "date_to": date_to
        }
        
    except Exception as e:
        logger.error(f"Error retrieving audit stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/retention/enforce")
async def enforce_retention_policy(
    policy: AuditRetentionPolicy,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Enforce audit log retention policy
    
    Deletes old logs based on severity and retention days
    (Admin only)
    """
    try:
        audit_service = get_audit_service(db)
        deleted_counts = audit_service.enforce_retention_policy(policy)
        
        logger.info(
            f"Admin {current_user.username} enforced retention policy: {deleted_counts}"
        )
        
        return {
            "success": True,
            "message": "Retention policy enforced successfully",
            "deleted_counts": deleted_counts
        }
        
    except Exception as e:
        logger.error(f"Error enforcing retention policy: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/export/csv")
async def export_audit_logs_csv(
    date_from: Optional[datetime] = Query(None),
    date_to: Optional[datetime] = Query(None),
    event_type: Optional[str] = Query(None),
    user_id: Optional[int] = Query(None),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Export audit logs to CSV file
    
    Downloads a CSV file with filtered audit logs
    """
    try:
        audit_service = get_audit_service(db)
        
        # Build query request
        query_request = AuditQueryRequest(
            date_from=date_from,
            date_to=date_to,
            event_types=[AuditEventType(event_type)] if event_type else None,
            user_id=user_id,
            page=1,
            page_size=10000  # Large page size for export
        )
        
        result = audit_service.query_audit_logs(query_request)
        
        # Create CSV file
        filename = f"audit_logs_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
        filepath = os.path.join("reports", filename)
        
        # Ensure reports directory exists
        os.makedirs("reports", exist_ok=True)
        
        # Write CSV
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = [
                'id', 'timestamp', 'event_type', 'severity',
                'username', 'user_role', 'action',
                'endpoint', 'http_method', 'ip_address',
                'resource_type', 'resource_id', 'success', 'error_message'
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for log in result.logs:
                writer.writerow({
                    'id': log.id,
                    'timestamp': log.timestamp.isoformat(),
                    'event_type': log.event_type.value,
                    'severity': log.severity.value,
                    'username': log.username or '',
                    'user_role': log.user_role or '',
                    'action': log.action,
                    'endpoint': log.endpoint or '',
                    'http_method': log.http_method or '',
                    'ip_address': log.ip_address or '',
                    'resource_type': log.resource_type or '',
                    'resource_id': log.resource_id or '',
                    'success': log.success,
                    'error_message': log.error_message or ''
                })
        
        logger.info(
            f"Admin {current_user.username} exported {result.total_count} audit logs to CSV"
        )
        
        return FileResponse(
            path=filepath,
            filename=filename,
            media_type="text/csv"
        )
        
    except Exception as e:
        logger.error(f"Error exporting audit logs: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/recent")
async def get_recent_logs(
    limit: int = Query(100, ge=1, le=1000),
    severity: Optional[str] = Query(None, description="Filter by severity"),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Get most recent audit logs
    Quick view for monitoring
    """
    try:
        audit_service = get_audit_service(db)
        
        query_request = AuditQueryRequest(
            severity_levels=[AuditSeverity(severity)] if severity else None,
            page=1,
            page_size=limit,
            sort_by="timestamp",
            sort_desc=True
        )
        
        result = audit_service.query_audit_logs(query_request)
        
        return result
        
    except Exception as e:
        logger.error(f"Error retrieving recent logs: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
