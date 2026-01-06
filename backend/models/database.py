"""
Database models and schemas
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

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
    __tablename__ = "logbook"
    
    id = Column(Integer, primary_key=True, index=True)
    kamco_name = Column(String(255), nullable=False, index=True)
    kamco_type = Column(String(50), nullable=False)  # clients, vendors, staff, others
    kamco_id = Column(Integer, nullable=False)
    blacklist_name = Column(String(255), nullable=False, index=True)
    blacklist_source = Column(String(255))
    match_score = Column(Float)
    reviewed_by = Column(String(100))
    reviewed_at = Column(DateTime(timezone=True), server_default=func.now())
    decision = Column(String(50))  # cleared, flagged
    notes = Column(Text)

class InReviewQueue(Base):
    __tablename__ = "in_review_queue"
    
    id = Column(Integer, primary_key=True, index=True)
    kamco_name = Column(String(255), nullable=False)
    kamco_type = Column(String(50), nullable=False)
    kamco_id = Column(Integer, nullable=False)
    blacklist_name = Column(String(255), nullable=False)
    blacklist_source = Column(String(255))
    match_score = Column(Float, nullable=False)
    actor_name = Column(String(255))  # Only for clients/vendors
    actor_match_score = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class FlaggedItem(Base):
    __tablename__ = "flagged_items"
    
    id = Column(Integer, primary_key=True, index=True)
    kamco_name = Column(String(255), nullable=False)
    kamco_type = Column(String(50), nullable=False)
    kamco_id = Column(Integer, nullable=False)
    blacklist_name = Column(String(255), nullable=False)
    blacklist_source = Column(String(255))
    match_score = Column(Float)
    flag_reason = Column(Text, nullable=False)
    flagged_by = Column(String(100), nullable=False)
    flagged_at = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(String(50), default="pending")  # pending, approved, recheck, overridden
    reviewed_by = Column(String(100))
    reviewed_at = Column(DateTime(timezone=True))
    review_notes = Column(Text)
