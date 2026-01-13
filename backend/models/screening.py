"""
Database models for screening system
Includes: KamcoEntity, BlacklistUpload, ScreeningMatch, DecisionLog
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, ForeignKey, Enum as SQLEnum, JSON
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import enum

from models.database import Base


class EntityType(str, enum.Enum):
    CLIENT = "Client"
    VENDOR = "Vendor"
    STAFF = "Staff"
    BOARD_MEMBER = "Board Member"
    SHAREHOLDER = "Shareholder"
    OTHER = "Other"


class EntityCategory(str, enum.Enum):
    INDIVIDUAL = "Individual"
    CORPORATE = "Corporate"


class MatchConfidence(str, enum.Enum):
    EXACT = "exact"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    POTENTIAL = "potential"


class DecisionStatus(str, enum.Enum):
    PENDING = "pending"
    FLAGGED = "flagged"
    CLEARED = "cleared"
    ESCALATED = "escalated"


class KamcoEntity(Base):
    """
    KAMCO's internal entity database
    Clients, Vendors, Staff, Board Members, Shareholders, etc.
    """
    __tablename__ = "kamco_entities"
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(String(50), unique=True, nullable=False, index=True)
    entity_type = Column(String(50), nullable=False, index=True)  # Client, Vendor, Staff, etc.
    entity_category = Column(String(50), nullable=False)  # Individual or Corporate
    
    # Names
    name_english = Column(String(255), nullable=False, index=True)
    name_arabic = Column(String(255), index=True)
    
    # Identifiers
    civil_id = Column(String(50), index=True)
    passport_number = Column(String(50), index=True)
    national_id = Column(String(50))
    registration_number = Column(String(100))  # For corporate entities
    
    # Personal/Corporate Info
    date_of_birth = Column(String(20))  # Store as string for flexibility
    date_of_incorporation = Column(String(20))  # For corporate
    nationality = Column(String(100))
    secondary_nationality = Column(String(100))
    gender = Column(String(20))
    
    # Contact
    country_of_residence = Column(String(100))
    city = Column(String(100))
    address = Column(Text)
    phone = Column(String(50))
    email = Column(String(255))
    
    # Employment/Business
    occupation = Column(String(255))
    employer = Column(String(255))
    position = Column(String(255))
    industry = Column(String(100))
    business_type = Column(String(100))
    department = Column(String(100))  # For staff
    employee_id = Column(String(50))  # For staff
    hire_date = Column(String(20))  # For staff
    
    # Ownership
    beneficial_owner = Column(String(255))  # For corporate
    shareholding_percentage = Column(String(20))  # For shareholders
    
    # Risk & Status
    account_status = Column(String(50), default="Active")
    risk_level = Column(String(50), default="Low")
    onboarding_date = Column(String(20))
    last_review_date = Column(String(20))
    
    # Notes
    notes = Column(Text)
    
    # Additional data (JSON for flexibility)
    extra_data = Column(JSON, default={})
    
    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    matches = relationship("ScreeningMatch", back_populates="kamco_entity")


class BlacklistUpload(Base):
    """
    Record of uploaded blacklist files
    """
    __tablename__ = "blacklist_uploads"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    file_hash = Column(String(64))  # SHA256 hash for deduplication
    
    # Upload info
    uploaded_by = Column(Integer, ForeignKey("users.id"))
    uploaded_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Stats
    total_entries = Column(Integer, default=0)
    processed_entries = Column(Integer, default=0)
    matched_entries = Column(Integer, default=0)
    new_matches = Column(Integer, default=0)  # Matches not seen before
    re_review_matches = Column(Integer, default=0)  # Matches with previous decisions
    
    # Screening settings used
    threshold_used = Column(Float, default=70.0)
    weights_used = Column(JSON)
    
    # Status
    status = Column(String(50), default="processing")  # processing, completed, failed
    error_message = Column(Text)
    
    # Timestamps
    processing_started_at = Column(DateTime)
    processing_completed_at = Column(DateTime)
    
    # Relationships
    uploader = relationship("User", backref="blacklist_uploads")
    matches = relationship("ScreeningMatch", back_populates="blacklist_upload")


class ScreeningMatch(Base):
    """
    Individual match between blacklist entry and KAMCO entity
    """
    __tablename__ = "screening_matches"
    
    id = Column(Integer, primary_key=True, index=True)
    match_key = Column(String(255), unique=True, nullable=False, index=True)
    
    # References
    blacklist_upload_id = Column(Integer, ForeignKey("blacklist_uploads.id"))
    kamco_entity_id = Column(Integer, ForeignKey("kamco_entities.id"))
    
    # Blacklist entry data (stored for reference)
    blacklist_reference = Column(String(100), index=True)
    blacklist_name_english = Column(String(255))
    blacklist_name_arabic = Column(String(255))
    blacklist_civil_id = Column(String(50))
    blacklist_passport = Column(String(50))
    blacklist_nationality = Column(String(100))
    blacklist_dob = Column(String(20))
    blacklist_list_type = Column(String(100))
    blacklist_list_source = Column(String(100))
    blacklist_risk_level = Column(String(50))
    blacklist_reason = Column(Text)
    blacklist_raw_data = Column(JSON)  # Full blacklist entry data
    
    # Match scores
    overall_score = Column(Float, nullable=False, index=True)
    name_english_score = Column(Float)
    name_arabic_score = Column(Float)
    civil_id_score = Column(Float)
    passport_score = Column(Float)
    dob_score = Column(Float)
    nationality_score = Column(Float)
    
    # Match details
    confidence = Column(String(20), default="potential")  # exact, high, medium, low, potential
    match_reasons = Column(JSON, default=[])
    
    # Current decision
    decision_status = Column(String(20), default="pending", index=True)
    decision_date = Column(DateTime)
    decision_by = Column(Integer, ForeignKey("users.id"))
    decision_notes = Column(Text)
    
    # Re-review tracking
    is_re_review = Column(Boolean, default=False)
    previous_decision = Column(String(20))
    previous_decision_date = Column(DateTime)
    previous_decision_by = Column(Integer, ForeignKey("users.id"))
    previous_notes = Column(Text)
    
    # Timestamps
    screened_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    blacklist_upload = relationship("BlacklistUpload", back_populates="matches")
    kamco_entity = relationship("KamcoEntity", back_populates="matches")
    decision_user = relationship("User", foreign_keys=[decision_by], backref="decisions_made")
    previous_decision_user = relationship("User", foreign_keys=[previous_decision_by])


class DecisionLog(Base):
    """
    Logbook of all decisions made (historical record)
    Never deleted - complete audit trail
    """
    __tablename__ = "decision_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Match reference
    match_id = Column(Integer, ForeignKey("screening_matches.id"))
    match_key = Column(String(255), index=True)
    
    # Entity info (denormalized for historical record)
    kamco_customer_id = Column(String(50), index=True)
    kamco_name = Column(String(255))
    kamco_entity_type = Column(String(50))
    
    # Blacklist info (denormalized)
    blacklist_reference = Column(String(100))
    blacklist_name = Column(String(255))
    blacklist_source = Column(String(100))
    
    # Match details at time of decision
    match_score = Column(Float)
    confidence = Column(String(20))
    
    # Decision details
    decision = Column(String(20), nullable=False, index=True)  # flagged, cleared, escalated
    decision_date = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    decision_by = Column(Integer, ForeignKey("users.id"))
    decision_by_username = Column(String(100))
    decision_by_role = Column(String(50))
    notes = Column(Text)
    
    # Additional context
    escalation_reason = Column(Text)
    final_approval_by = Column(Integer, ForeignKey("users.id"))
    final_approval_date = Column(DateTime)
    
    # Report generated
    report_generated = Column(Boolean, default=False)
    report_path = Column(String(500))
    
    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    match = relationship("ScreeningMatch", backref="decision_logs")
    reviewer = relationship("User", foreign_keys=[decision_by], backref="decision_logs")
    final_approver = relationship("User", foreign_keys=[final_approval_by])
