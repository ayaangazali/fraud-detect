"""
Database models and schemas
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

Base = declarative_base()

class KamcoClient(Base):
    __tablename__ = "kamco_clients"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    account_number = Column(String(100))
    date_opened = Column(String(50))
    actor_name = Column(String(255), index=True)  # Representative/Actor field
    country = Column(String(100))
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class KamcoVendor(Base):
    __tablename__ = "kamco_vendors"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    vendor_id = Column(String(100))
    date_registered = Column(String(50))
    actor_name = Column(String(255), index=True)  # Representative/Actor field
    category = Column(String(100))
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class KamcoStaff(Base):
    __tablename__ = "kamco_staff"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    employee_id = Column(String(100))
    department = Column(String(100))
    position = Column(String(100))
    hire_date = Column(String(50))
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class KamcoOther(Base):
    __tablename__ = "kamco_others"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    category = Column(String(100))
    reference_id = Column(String(100))
    description = Column(Text)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Logbook(Base):
    """
    Enhanced Logbook for comprehensive audit trail
    Tracks all decisions and actions with full context
    """
    __tablename__ = "logbook"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Case relationship
    case_id = Column(Integer, ForeignKey("cases.id", ondelete="SET NULL"), nullable=True, index=True)
    
    # Kamco record info
    kamco_name = Column(String(255), nullable=False, index=True)
    kamco_type = Column(String(50), nullable=False, index=True)  # clients, vendors, staff, others
    kamco_id = Column(Integer, nullable=False)
    
    # Blacklist info
    blacklist_name = Column(String(255), nullable=False, index=True)
    blacklist_source = Column(String(255))
    match_score = Column(Float)
    
    # Action tracking
    action_type = Column(String(50), nullable=False, index=True)  # scan, flag, clear, approve, reject, override, recheck
    previous_status = Column(String(50))
    new_status = Column(String(50))
    
    # User tracking
    reviewed_by_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    approved_by_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    
    # Legacy fields (backward compatibility)
    reviewed_by = Column(String(100))  # Will be deprecated
    
    # Decision details
    decision = Column(String(50), index=True)  # cleared, flagged, pending
    notes = Column(Text)
    
    # Performance metrics
    time_spent_seconds = Column(Integer)  # Time spent on review
    compliance_score = Column(Integer)  # 1-100 compliance score
    
    # Escalation tracking
    requires_escalation = Column(Boolean, default=False, nullable=False)
    escalation_notes = Column(Text)
    
    # Full audit trail
    ip_address = Column(String(50))
    user_agent = Column(String(500))
    
    # Timestamps
    reviewed_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    case = relationship("Case")
    reviewed_by_user = relationship("User", foreign_keys=[reviewed_by_id])
    approved_by_user = relationship("User", foreign_keys=[approved_by_id])
    
    # Composite indexes
    __table_args__ = (
        Index('idx_case_action', 'case_id', 'action_type'),
        Index('idx_user_action', 'reviewed_by_id', 'action_type'),
        Index('idx_type_decision', 'kamco_type', 'decision'),
        Index('idx_date_action', 'reviewed_at', 'action_type'),
    )
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "case_id": self.case_id,
            "kamco_name": self.kamco_name,
            "kamco_type": self.kamco_type,
            "kamco_id": self.kamco_id,
            "blacklist_name": self.blacklist_name,
            "blacklist_source": self.blacklist_source,
            "match_score": self.match_score,
            "action_type": self.action_type,
            "previous_status": self.previous_status,
            "new_status": self.new_status,
            "reviewed_by_id": self.reviewed_by_id,
            "approved_by_id": self.approved_by_id,
            "decision": self.decision,
            "notes": self.notes,
            "time_spent_seconds": self.time_spent_seconds,
            "compliance_score": self.compliance_score,
            "requires_escalation": self.requires_escalation,
            "escalation_notes": self.escalation_notes,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "reviewed_at": self.reviewed_at.isoformat() if self.reviewed_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

class InReviewQueue(Base):
    """
    Enhanced In-Review Queue for compliance screening workflow
    Tracks items that need review with full metadata and case linkage
    """
    __tablename__ = "in_review_queue"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Case relationship
    case_id = Column(Integer, ForeignKey("cases.id", ondelete="CASCADE"), nullable=True, index=True)
    
    # Kamco record info
    kamco_name = Column(String(255), nullable=False)
    kamco_type = Column(String(50), nullable=False, index=True)  # clients, vendors, staff, others
    kamco_id = Column(Integer, nullable=False)
    
    # Blacklist match info
    blacklist_name = Column(String(255), nullable=False)
    blacklist_source = Column(String(255))
    match_score = Column(Float, nullable=False)
    
    # Actor field (for clients/vendors)
    actor_name = Column(String(255))
    actor_match_score = Column(Float)
    
    # Enhanced matching metadata (JSON string)
    match_metadata = Column(Text)  # JSON: {algorithm, confidence_level, individual_scores, match_reasons}
    
    # Risk assessment
    risk_score = Column(Integer, nullable=False, default=5, index=True)  # 1-10 scale
    requires_checker_review = Column(Boolean, default=False, nullable=False)
    escalation_reason = Column(Text)
    
    # Assignment and review tracking
    screener_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    assigned_at = Column(DateTime(timezone=True), nullable=True)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Status tracking
    status = Column(String(50), default="pending", nullable=False, index=True)  # pending, in_progress, flagged, cleared
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    
    # Relationships
    case = relationship("Case")
    screener = relationship("User", foreign_keys=[screener_id])
    
    # Add composite indexes for common queries
    __table_args__ = (
        Index('idx_case_status', 'case_id', 'status'),
        Index('idx_screener_status', 'screener_id', 'status'),
        Index('idx_risk_type', 'risk_score', 'kamco_type'),
    )
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "case_id": self.case_id,
            "kamco_name": self.kamco_name,
            "kamco_type": self.kamco_type,
            "kamco_id": self.kamco_id,
            "blacklist_name": self.blacklist_name,
            "blacklist_source": self.blacklist_source,
            "match_score": self.match_score,
            "actor_name": self.actor_name,
            "actor_match_score": self.actor_match_score,
            "match_metadata": self.match_metadata,
            "risk_score": self.risk_score,
            "requires_checker_review": self.requires_checker_review,
            "escalation_reason": self.escalation_reason,
            "screener_id": self.screener_id,
            "assigned_at": self.assigned_at.isoformat() if self.assigned_at else None,
            "reviewed_at": self.reviewed_at.isoformat() if self.reviewed_at else None,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

class FlaggedItem(Base):
    """
    Enhanced Flagged Items for multi-stage compliance workflow
    Tracks flagged items through checker and finalizer review
    """
    __tablename__ = "flagged_items"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Case relationship
    case_id = Column(Integer, ForeignKey("cases.id", ondelete="CASCADE"), nullable=True, index=True)
    
    # Kamco record info
    kamco_name = Column(String(255), nullable=False)
    kamco_type = Column(String(50), nullable=False, index=True)
    kamco_id = Column(Integer, nullable=False)
    
    # Blacklist match info
    blacklist_name = Column(String(255), nullable=False)
    blacklist_source = Column(String(255))
    match_score = Column(Float)
    
    # Flag details
    flag_reason = Column(Text, nullable=False)
    flag_reason_category = Column(String(50), nullable=False, index=True)  # match_confirmed, suspicious_activity, high_risk, regulatory
    severity = Column(String(20), nullable=False, default="medium", index=True)  # low, medium, high, critical
    
    # Workflow tracking
    flagged_by_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    checker_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    finalizer_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    
    # Compliance tracking
    requires_compliance_approval = Column(Boolean, default=False, nullable=False)
    compliance_notes = Column(Text)
    
    # Status and resolution
    status = Column(String(50), default="pending", nullable=False, index=True)  # pending, checker_review, awaiting_final, approved, rejected, overridden
    resolution_type = Column(String(50))  # cleared, flagged, pending, escalated
    
    # Timestamps
    flagged_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    checker_assigned_at = Column(DateTime(timezone=True), nullable=True)
    checker_reviewed_at = Column(DateTime(timezone=True), nullable=True)
    finalizer_reviewed_at = Column(DateTime(timezone=True), nullable=True)
    escalated_at = Column(DateTime(timezone=True))
    resolved_at = Column(DateTime(timezone=True))
    reviewed_at = Column(DateTime(timezone=True))
    resolution_date = Column(DateTime(timezone=True), nullable=True)
    
    # Additional notes and tracking
    checker_notes = Column(Text, nullable=True)
    finalizer_notes = Column(Text, nullable=True)
    escalation_level = Column(String(50), nullable=True)  # management, executive, legal
    
    # Legacy fields (for backward compatibility)
    flagged_by = Column(String(100))  # Will be deprecated in favor of flagged_by_id
    reviewed_by = Column(String(100))  # Will be deprecated
    review_notes = Column(Text)
    
    # Relationships
    case = relationship("Case")
    flagged_by_user = relationship("User", foreign_keys=[flagged_by_id])
    checker_user = relationship("User", foreign_keys=[checker_id])
    finalizer_user = relationship("User", foreign_keys=[finalizer_id])
    
    # Composite indexes
    __table_args__ = (
        Index('idx_case_status_flagged', 'case_id', 'status'),
        Index('idx_severity_status', 'severity', 'status'),
        Index('idx_checker_status', 'checker_id', 'status'),
        Index('idx_category_severity', 'flag_reason_category', 'severity'),
    )
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "case_id": self.case_id,
            "kamco_name": self.kamco_name,
            "kamco_type": self.kamco_type,
            "kamco_id": self.kamco_id,
            "blacklist_name": self.blacklist_name,
            "blacklist_source": self.blacklist_source,
            "match_score": self.match_score,
            "flag_reason": self.flag_reason,
            "flag_reason_category": self.flag_reason_category,
            "severity": self.severity,
            "flagged_by_id": self.flagged_by_id,
            "checker_id": self.checker_id,
            "finalizer_id": self.finalizer_id,
            "requires_compliance_approval": self.requires_compliance_approval,
            "compliance_notes": self.compliance_notes,
            "status": self.status,
            "resolution_type": self.resolution_type,
            "flagged_at": self.flagged_at.isoformat() if self.flagged_at else None,
            "escalated_at": self.escalated_at.isoformat() if self.escalated_at else None,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "reviewed_at": self.reviewed_at.isoformat() if self.reviewed_at else None
        }
