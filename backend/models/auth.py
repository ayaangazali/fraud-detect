"""
Authentication Models
User and RefreshToken models for JWT-based authentication
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database.connection import Base
import enum

class UserRole(str, enum.Enum):
    """User roles for role-based access control"""
    SCREENER = "screener"
    CHECKER = "checker"
    FINALIZER = "finalizer"

class User(Base):
    """
    User model for authentication and authorization
    
    Roles:
        - screener: Can upload blacklists, scan, flag items
        - checker: Can review flagged items, approve or send back for recheck
        - finalizer: Can give final approval, override decisions, generate reports
    """
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(SQLEnum(UserRole), nullable=False, default=UserRole.SCREENER)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}', role='{self.role.value}')>"
    
    def to_dict(self):
        """Convert user to dictionary (exclude password)"""
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "role": self.role.value,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None
        }

class RefreshToken(Base):
    """
    Refresh token model for JWT token refresh mechanism
    Allows users to get new access tokens without re-authenticating
    """
    __tablename__ = "refresh_tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    token = Column(String(500), unique=True, nullable=False, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    is_revoked = Column(Boolean, default=False, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="refresh_tokens")
    
    def __repr__(self):
        return f"<RefreshToken(id={self.id}, user_id={self.user_id}, expires_at='{self.expires_at}', revoked={self.is_revoked})>"
    
    def is_valid(self):
        """Check if token is still valid (not expired and not revoked)"""
        from datetime import datetime, timezone
        return not self.is_revoked and self.expires_at > datetime.now(timezone.utc)
