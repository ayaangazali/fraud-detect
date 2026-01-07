"""
Case Management Models
Case tracking and notes for compliance screening workflow
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database.connection import Base
import enum
from datetime import datetime

class CaseStatus(str, enum.Enum):
    """Case status stages in the compliance workflow"""
    OPEN = "open"                    # Initial state after scan
    IN_REVIEW = "in_review"          # Screener reviewing matches
    FLAGGED = "flagged"              # Flagged by screener, awaiting checker
    CHECKER_REVIEW = "checker_review" # Checker reviewing flag
    AWAITING_FINAL = "awaiting_final" # Awaiting finalizer approval
    CLEARED = "cleared"              # Cleared/approved
    CLOSED = "closed"                # Case closed
    REJECTED = "rejected"            # Rejected/dismissed

class CasePriority(str, enum.Enum):
    """Case priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class NoteType(str, enum.Enum):
    """Type of case note"""
    COMMENT = "comment"              # User comment
    SYSTEM = "system"                # System-generated note
    STATUS_CHANGE = "status_change"  # Status transition log
    ESCALATION = "escalation"        # Escalation note
    DECISION = "decision"            # Decision note

class Case(Base):
    """
    Case model for tracking compliance screening cases
    Each case represents a screening workflow from scan to resolution
    """
    __tablename__ = "cases"
    
    id = Column(Integer, primary_key=True, index=True)
    case_number = Column(String(50), unique=True, nullable=False, index=True)  # CASE-YYYY-XXXX
    status = Column(SQLEnum(CaseStatus), nullable=False, default=CaseStatus.OPEN, index=True)
    priority = Column(SQLEnum(CasePriority), nullable=False, default=CasePriority.MEDIUM, index=True)
    
    # User relationships
    created_by_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    assigned_to_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    
    # Case details
    title = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    closed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    notes = relationship("CaseNote", back_populates="case", cascade="all, delete-orphan")
    created_by = relationship("User", foreign_keys=[created_by_id])
    assigned_to = relationship("User", foreign_keys=[assigned_to_id])
    
    def __repr__(self):
        return f"<Case(id={self.id}, case_number='{self.case_number}', status='{self.status.value}', priority='{self.priority.value}')>"
    
    def to_dict(self):
        """Convert case to dictionary"""
        return {
            "id": self.id,
            "case_number": self.case_number,
            "status": self.status.value,
            "priority": self.priority.value,
            "title": self.title,
            "description": self.description,
            "created_by_id": self.created_by_id,
            "assigned_to_id": self.assigned_to_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "closed_at": self.closed_at.isoformat() if self.closed_at else None
        }
    
    @staticmethod
    def generate_case_number(year: int = None, sequence: int = None) -> str:
        """
        Generate case number in format CASE-YYYY-XXXX
        
        Args:
            year: Year for case number (default: current year)
            sequence: Sequence number (default: auto-increment)
            
        Returns:
            Case number string
        """
        if year is None:
            year = datetime.now().year
        
        if sequence is None:
            # This will be handled by the database query to get max sequence
            sequence = 1
        
        return f"CASE-{year}-{sequence:04d}"

class CaseNote(Base):
    """
    Case notes model for tracking comments and system logs
    Each note is attached to a case and created by a user
    """
    __tablename__ = "case_notes"
    
    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("cases.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    
    note = Column(Text, nullable=False)
    note_type = Column(SQLEnum(NoteType), nullable=False, default=NoteType.COMMENT, index=True)
    
    # Additional metadata (renamed from 'metadata' to avoid SQLAlchemy conflict)
    note_metadata = Column(Text, nullable=True)  # JSON string for extra data
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    
    # Relationships
    case = relationship("Case", back_populates="notes")
    user = relationship("User")
    
    def __repr__(self):
        return f"<CaseNote(id={self.id}, case_id={self.case_id}, type='{self.note_type.value}', created_at='{self.created_at}')>"
    
    def to_dict(self):
        """Convert case note to dictionary"""
        return {
            "id": self.id,
            "case_id": self.case_id,
            "user_id": self.user_id,
            "note": self.note,
            "note_type": self.note_type.value,
            "metadata": self.note_metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
