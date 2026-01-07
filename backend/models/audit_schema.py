"""
Audit Logging Pydantic Schemas - Phase 8
Data models for comprehensive audit trail system
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


class AuditEventType(str, Enum):
    """Types of audit events tracked in the system"""
    
    # API Events
    API_CALL = "api_call"
    API_ERROR = "api_error"
    
    # Authentication Events
    AUTH_LOGIN = "auth_login"
    AUTH_LOGOUT = "auth_logout"
    AUTH_FAILED = "auth_failed"
    AUTH_TOKEN_REFRESH = "auth_token_refresh"
    AUTH_PASSWORD_CHANGE = "auth_password_change"
    
    # Data Modification Events
    DATA_CREATE = "data_create"
    DATA_UPDATE = "data_update"
    DATA_DELETE = "data_delete"
    DATA_EXPORT = "data_export"
    
    # Security Events
    SECURITY_PERMISSION_DENIED = "security_permission_denied"
    SECURITY_ROLE_CHANGE = "security_role_change"
    SECURITY_SUSPICIOUS_ACTIVITY = "security_suspicious_activity"
    SECURITY_ACCOUNT_LOCKED = "security_account_locked"
    SECURITY_ACCOUNT_UNLOCKED = "security_account_unlocked"
    
    # File Operations
    FILE_UPLOAD = "file_upload"
    FILE_DOWNLOAD = "file_download"
    FILE_DELETE = "file_delete"
    
    # Screening Workflow
    SCREENING_INITIATED = "screening_initiated"
    SCREENING_COMPLETED = "screening_completed"
    ITEM_FLAGGED = "item_flagged"
    ITEM_CLEARED = "item_cleared"
    ITEM_APPROVED = "item_approved"
    ITEM_REJECTED = "item_rejected"
    
    # Report Events
    REPORT_GENERATED = "report_generated"
    REPORT_DOWNLOADED = "report_downloaded"
    REPORT_DELETED = "report_deleted"
    
    # User Management
    USER_CREATED = "user_created"
    USER_UPDATED = "user_updated"
    USER_DELETED = "user_deleted"
    USER_DEACTIVATED = "user_deactivated"
    USER_ACTIVATED = "user_activated"
    
    # Blacklist Management
    BLACKLIST_UPLOADED = "blacklist_uploaded"
    BLACKLIST_UPDATED = "blacklist_updated"
    BLACKLIST_ITEM_ADDED = "blacklist_item_added"
    BLACKLIST_ITEM_REMOVED = "blacklist_item_removed"
    
    # System Events
    SYSTEM_STARTUP = "system_startup"
    SYSTEM_SHUTDOWN = "system_shutdown"
    SYSTEM_ERROR = "system_error"
    SYSTEM_MAINTENANCE = "system_maintenance"
    SCHEDULED_TASK = "scheduled_task"


class AuditSeverity(str, Enum):
    """Severity levels for audit events"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AuditLogEntry(BaseModel):
    """
    Single audit log entry
    Comprehensive tracking of system events
    """
    id: Optional[int] = None
    event_type: AuditEventType
    severity: AuditSeverity = AuditSeverity.LOW
    
    # User context
    user_id: Optional[int] = None
    username: Optional[str] = None
    user_role: Optional[str] = None
    
    # Request context
    endpoint: Optional[str] = None
    http_method: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    
    # Action details
    action: str = Field(..., description="Human-readable action description")
    resource_type: Optional[str] = Field(None, description="Type of resource affected (user, report, etc.)")
    resource_id: Optional[str] = Field(None, description="ID of affected resource")
    
    # Data tracking
    before_state: Optional[Dict[str, Any]] = Field(None, description="State before change")
    after_state: Optional[Dict[str, Any]] = Field(None, description="State after change")
    
    # Additional context
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional event metadata")
    tags: Optional[List[str]] = Field(default_factory=list, description="Tags for categorization")
    
    # Results
    success: bool = True
    error_message: Optional[str] = None
    execution_time_ms: Optional[float] = None
    
    # Timestamps
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "event_type": "auth_login",
                "severity": "low",
                "user_id": 1,
                "username": "admin",
                "user_role": "admin",
                "endpoint": "/api/auth/login",
                "http_method": "POST",
                "ip_address": "192.168.1.100",
                "action": "User logged in successfully",
                "resource_type": "user",
                "resource_id": "1",
                "success": True,
                "timestamp": "2026-01-07T12:00:00Z"
            }
        }


class AuditQueryRequest(BaseModel):
    """Request model for querying audit logs"""
    
    # Date filtering
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    
    # Event filtering
    event_types: Optional[List[AuditEventType]] = None
    severity_levels: Optional[List[AuditSeverity]] = None
    
    # User filtering
    user_id: Optional[int] = None
    username: Optional[str] = None
    user_role: Optional[str] = None
    
    # Resource filtering
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    
    # Request filtering
    endpoint: Optional[str] = None
    http_method: Optional[str] = None
    ip_address: Optional[str] = None
    
    # Status filtering
    success_only: Optional[bool] = None
    failed_only: Optional[bool] = None
    
    # Tags
    tags: Optional[List[str]] = None
    
    # Full-text search
    search_query: Optional[str] = Field(None, description="Search in action or error_message")
    
    # Pagination
    page: int = Field(1, ge=1)
    page_size: int = Field(50, ge=1, le=1000)
    
    # Sorting
    sort_by: str = Field("timestamp", description="Field to sort by")
    sort_desc: bool = Field(True, description="Sort descending (newest first)")


class AuditLogResponse(BaseModel):
    """Response model for audit log queries"""
    logs: List[AuditLogEntry]
    total_count: int
    page: int
    page_size: int
    total_pages: int


class AuditStatsResponse(BaseModel):
    """Response model for audit statistics"""
    
    # Total counts
    total_events: int
    events_by_type: Dict[str, int]
    events_by_severity: Dict[str, int]
    
    # User activity
    most_active_users: List[Dict[str, Any]]
    
    # Time-based stats
    events_by_hour: Dict[str, int]
    events_by_day: Dict[str, int]
    
    # Security stats
    failed_auth_attempts: int
    permission_denials: int
    suspicious_activities: int
    
    # Performance
    avg_execution_time_ms: Optional[float] = None
    slowest_endpoints: List[Dict[str, Any]]
    
    # Error tracking
    error_count: int
    error_rate: float
    most_common_errors: List[Dict[str, Any]]
    
    # Date range
    date_from: datetime
    date_to: datetime


class UserActivitySummary(BaseModel):
    """Summary of user activity"""
    user_id: int
    username: str
    user_role: str
    
    # Activity counts
    total_actions: int
    successful_actions: int
    failed_actions: int
    
    # Event breakdown
    events_by_type: Dict[str, int]
    
    # Time stats
    first_activity: datetime
    last_activity: datetime
    most_active_hour: Optional[str] = None
    
    # Resources accessed
    unique_resources_accessed: int
    resource_types: List[str]
    
    # Security flags
    failed_auth_count: int
    permission_denials: int
    has_suspicious_activity: bool


class SecurityEventSummary(BaseModel):
    """Summary of security events"""
    
    # Failed authentications
    failed_logins: int
    failed_login_ips: List[str]
    failed_login_users: List[str]
    
    # Permission issues
    permission_denials: int
    denied_resources: List[Dict[str, Any]]
    
    # Suspicious activity
    suspicious_events: List[AuditLogEntry]
    suspicious_ips: List[str]
    
    # Account security
    locked_accounts: int
    password_changes: int
    role_changes: int
    
    # Recent alerts
    recent_high_severity: List[AuditLogEntry]
    recent_critical: List[AuditLogEntry]
    
    # Time range
    date_from: datetime
    date_to: datetime


class DataChangeLog(BaseModel):
    """Detailed log of data changes"""
    id: int
    timestamp: datetime
    user_id: int
    username: str
    
    resource_type: str
    resource_id: str
    action: str
    
    fields_changed: List[str]
    before_state: Dict[str, Any]
    after_state: Dict[str, Any]
    
    change_summary: str
    ip_address: str


class AuditRetentionPolicy(BaseModel):
    """Configuration for audit log retention"""
    
    # Retention periods (in days)
    low_severity_days: int = Field(30, description="Days to keep low severity logs")
    medium_severity_days: int = Field(90, description="Days to keep medium severity logs")
    high_severity_days: int = Field(180, description="Days to keep high severity logs")
    critical_severity_days: int = Field(365, description="Days to keep critical severity logs")
    
    # Archive settings
    enable_archival: bool = Field(True, description="Archive old logs instead of deleting")
    archive_location: Optional[str] = Field(None, description="Path to archive location")
    
    # Security events
    keep_security_events: bool = Field(True, description="Never delete security events")
    keep_failed_auth: bool = Field(True, description="Never delete failed auth attempts")
    
    # Compliance
    minimum_retention_days: int = Field(90, description="Minimum retention for compliance")
    
    class Config:
        json_schema_extra = {
            "example": {
                "low_severity_days": 30,
                "medium_severity_days": 90,
                "high_severity_days": 180,
                "critical_severity_days": 365,
                "enable_archival": True,
                "keep_security_events": True,
                "minimum_retention_days": 90
            }
        }


class AuditExportRequest(BaseModel):
    """Request model for exporting audit logs"""
    query: AuditQueryRequest
    format: str = Field("csv", description="Export format: csv, excel, json")
    include_metadata: bool = Field(True, description="Include full metadata in export")
    filename: Optional[str] = None
