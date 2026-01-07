"""
Report Generation Models
Report management and scheduling for compliance reporting
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Date, ForeignKey, Boolean, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database.connection import Base
import enum

class ReportType(str, enum.Enum):
    """Types of reports"""
    CASE_SUMMARY = "case_summary"              # Individual case report (PDF)
    CUMULATIVE_DAILY = "cumulative_daily"      # Daily statistics (Excel)
    CUMULATIVE_MONTHLY = "cumulative_monthly"  # Monthly analytics (Excel)
    AUDIT_LOG = "audit_log"                    # Audit trail export (Excel)
    USER_PERFORMANCE = "user_performance"      # User performance metrics
    HIGH_RISK = "high_risk"                    # High-risk items report

class ReportStatus(str, enum.Enum):
    """Report generation status"""
    PENDING = "pending"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class ScheduleType(str, enum.Enum):
    """Report schedule frequency"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"

class Report(Base):
    """
    Report model for tracking generated reports
    Stores metadata and file paths for all generated reports
    """
    __tablename__ = "reports"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Report identification
    report_type = Column(SQLEnum(ReportType), nullable=False, index=True)
    report_number = Column(String(50), unique=True, nullable=False, index=True)  # REP-YYYY-XXXX
    
    # User who generated the report
    generated_by_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    
    # Date range for report
    date_from = Column(Date, nullable=True, index=True)
    date_to = Column(Date, nullable=True, index=True)
    
    # Filter criteria (JSON string)
    filters = Column(Text)  # JSON: {entity_types, priorities, statuses, users, etc.}
    
    # File information
    file_path = Column(String(500), nullable=True)  # Path to generated file
    file_name = Column(String(255), nullable=True)
    file_size = Column(Integer, nullable=True)  # Size in bytes
    file_format = Column(String(10), nullable=True)  # pdf, xlsx, csv
    
    # Status tracking
    status = Column(SQLEnum(ReportStatus), nullable=False, default=ReportStatus.PENDING, index=True)
    error_message = Column(Text)
    
    # Report metadata (JSON string) - renamed to avoid SQLAlchemy conflict
    report_metadata = Column(Text)  # JSON: {total_cases, flagged_count, cleared_count, etc.}
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    expires_at = Column(DateTime(timezone=True))  # Optional expiration for cleanup
    
    # Relationships
    generated_by = relationship("User")
    
    def __repr__(self):
        return f"<Report(id={self.id}, number='{self.report_number}', type='{self.report_type.value}', status='{self.status.value}')>"
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "report_type": self.report_type.value,
            "report_number": self.report_number,
            "generated_by_id": self.generated_by_id,
            "date_from": self.date_from.isoformat() if self.date_from else None,
            "date_to": self.date_to.isoformat() if self.date_to else None,
            "filters": self.filters,
            "file_path": self.file_path,
            "file_name": self.file_name,
            "file_size": self.file_size,
            "file_format": self.file_format,
            "status": self.status.value,
            "error_message": self.error_message,
            "metadata": self.report_metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None
        }

class ReportSchedule(Base):
    """
    Report Schedule model for recurring reports
    Automates report generation based on schedule
    """
    __tablename__ = "report_schedules"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Owner
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Schedule configuration
    schedule_name = Column(String(255), nullable=False)
    schedule_type = Column(SQLEnum(ScheduleType), nullable=False, index=True)
    report_type = Column(SQLEnum(ReportType), nullable=False)
    
    # Report configuration (JSON string)
    report_config = Column(Text, nullable=False)  # JSON: {filters, recipients, format, etc.}
    
    # Email configuration
    send_email = Column(Boolean, default=True, nullable=False)
    email_recipients = Column(Text)  # JSON array of email addresses
    
    # Schedule status
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    
    # Execution tracking
    last_run = Column(DateTime(timezone=True))
    last_status = Column(String(50))  # success, failed
    last_error = Column(Text)
    
    next_run = Column(DateTime(timezone=True), index=True)
    run_count = Column(Integer, default=0, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User")
    
    def __repr__(self):
        return f"<ReportSchedule(id={self.id}, name='{self.schedule_name}', type='{self.schedule_type.value}', active={self.is_active})>"
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "schedule_name": self.schedule_name,
            "schedule_type": self.schedule_type.value,
            "report_type": self.report_type.value,
            "report_config": self.report_config,
            "send_email": self.send_email,
            "email_recipients": self.email_recipients,
            "is_active": self.is_active,
            "last_run": self.last_run.isoformat() if self.last_run else None,
            "last_status": self.last_status,
            "last_error": self.last_error,
            "next_run": self.next_run.isoformat() if self.next_run else None,
            "run_count": self.run_count,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
