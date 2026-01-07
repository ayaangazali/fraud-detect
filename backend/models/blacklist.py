"""
Blacklist/Sanctions List Database Model
Phase 4: Excel Parser Enhancement
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Index
from sqlalchemy.sql import func
from models.database import Base


class BlacklistEntry(Base):
    """
    Sanctions/Blacklist entries uploaded via Excel
    Supports Arabic names and Kuwait Government Decree format
    """
    __tablename__ = "blacklist_entries"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Names
    name_arabic = Column(String(500), index=True, nullable=False, 
                        comment="Arabic name from sanctions list")
    name_english = Column(String(500), index=True, 
                         comment="English transliteration if available")
    
    # Identification
    civil_id = Column(String(50), index=True, 
                     comment="Kuwait Civil ID (12-digit)")
    passport_number = Column(String(100), index=True,
                            comment="Passport number if available")
    
    # Entity Information
    entity_type = Column(String(50), 
                        comment="Individual, Corporate, Government, etc.")
    nationality = Column(String(100), 
                        comment="Nationality/country of origin")
    country = Column(String(100), index=True,
                    comment="Country associated with entity")
    
    # Decree/List Information
    decree_number = Column(String(100), index=True,
                          comment="Government decree number (e.g., 99/2025)")
    list_date = Column(String(50),
                      comment="Date added to sanctions list")
    source = Column(String(200), index=True,
                   comment="Source of sanctions (Kuwait Government, OFAC, EU, UN)")
    
    # Classification
    category = Column(String(200),
                     comment="Category (National Security, Terrorism, Fraud, etc.)")
    risk_level = Column(String(50), index=True,
                       comment="Risk level: High, Medium, Low")
    reason = Column(Text,
                   comment="Reason for sanctions/blacklisting")
    
    # Status and Metadata
    status = Column(String(50), default="Active", index=True,
                   comment="Active, Removed, Under Review")
    notes = Column(Text,
                  comment="Additional notes or details")
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(),
                       comment="When record was created in system")
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(),
                       comment="Last update timestamp")
    
    # File tracking
    upload_filename = Column(String(255),
                            comment="Original Excel filename")
    upload_batch_id = Column(String(100), index=True,
                            comment="Batch ID for tracking uploads")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_name_arabic', 'name_arabic'),
        Index('idx_name_english', 'name_english'),
        Index('idx_civil_id', 'civil_id'),
        Index('idx_source_status', 'source', 'status'),
        Index('idx_risk_level', 'risk_level'),
        Index('idx_batch', 'upload_batch_id'),
    )
    
    def __repr__(self):
        return f"<BlacklistEntry(id={self.id}, name_arabic='{self.name_arabic}', civil_id='{self.civil_id}')>"
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            "id": self.id,
            "name_arabic": self.name_arabic,
            "name_english": self.name_english,
            "civil_id": self.civil_id,
            "passport_number": self.passport_number,
            "entity_type": self.entity_type,
            "nationality": self.nationality,
            "country": self.country,
            "decree_number": self.decree_number,
            "list_date": self.list_date,
            "source": self.source,
            "category": self.category,
            "risk_level": self.risk_level,
            "reason": self.reason,
            "status": self.status,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "upload_filename": self.upload_filename,
            "upload_batch_id": self.upload_batch_id
        }
