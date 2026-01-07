"""
Email Notification Models
Email queue and template management for automated notifications
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database.connection import Base
import enum

class EmailType(str, enum.Enum):
    """Types of email notifications"""
    FLAG_CREATED = "flag_created"
    CHECKER_ASSIGNED = "checker_assigned"
    APPROVAL_REQUIRED = "approval_required"
    RECHECK_REQUESTED = "recheck_requested"
    CASE_CLOSED = "case_closed"
    DAILY_SUMMARY = "daily_summary"
    ESCALATION = "escalation"
    OVERRIDE = "override"

class EmailStatus(str, enum.Enum):
    """Email sending status"""
    PENDING = "pending"
    SENDING = "sending"
    SENT = "sent"
    FAILED = "failed"
    CANCELLED = "cancelled"

class EmailNotification(Base):
    """
    Email Notification Queue
    Stores pending and sent emails for audit trail
    """
    __tablename__ = "email_notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Recipient
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    to_email = Column(String(255), nullable=False, index=True)
    
    # Email content
    email_type = Column(SQLEnum(EmailType), nullable=False, index=True)
    subject = Column(String(500), nullable=False)
    body = Column(Text, nullable=False)
    
    # Status tracking
    status = Column(SQLEnum(EmailStatus), nullable=False, default=EmailStatus.PENDING, index=True)
    
    # Metadata (JSON string for extra context) - renamed to avoid SQLAlchemy conflict
    email_metadata = Column(Text)  # JSON: {case_id, case_number, priority, etc.}
    
    # Error tracking
    error_message = Column(Text)
    retry_count = Column(Integer, default=0, nullable=False)
    max_retries = Column(Integer, default=3, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    sent_at = Column(DateTime(timezone=True))
    failed_at = Column(DateTime(timezone=True))
    next_retry_at = Column(DateTime(timezone=True))
    
    # Relationships
    user = relationship("User")
    
    def __repr__(self):
        return f"<EmailNotification(id={self.id}, type='{self.email_type.value}', status='{self.status.value}', to='{self.to_email}')>"
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "to_email": self.to_email,
            "email_type": self.email_type.value,
            "subject": self.subject,
            "body": self.body,
            "status": self.status.value,
            "metadata": self.email_metadata,
            "error_message": self.error_message,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "sent_at": self.sent_at.isoformat() if self.sent_at else None,
            "failed_at": self.failed_at.isoformat() if self.failed_at else None,
            "next_retry_at": self.next_retry_at.isoformat() if self.next_retry_at else None
        }
    
    def can_retry(self) -> bool:
        """Check if email can be retried"""
        return self.retry_count < self.max_retries and self.status == EmailStatus.FAILED

class EmailTemplate(Base):
    """
    Email Templates
    Reusable email templates with variable substitution
    """
    __tablename__ = "email_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Template identification
    template_name = Column(String(100), unique=True, nullable=False, index=True)
    email_type = Column(SQLEnum(EmailType), nullable=False, index=True)
    
    # Template content (supports Jinja2 variables)
    subject_template = Column(String(500), nullable=False)
    body_template = Column(Text, nullable=False)
    
    # Template metadata
    description = Column(Text)
    variables = Column(Text)  # JSON array of required variables
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<EmailTemplate(id={self.id}, name='{self.template_name}', type='{self.email_type.value}')>"
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "template_name": self.template_name,
            "email_type": self.email_type.value,
            "subject_template": self.subject_template,
            "body_template": self.body_template,
            "description": self.description,
            "variables": self.variables,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
