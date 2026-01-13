"""
Authentication Routes
User registration, login, token refresh, logout endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, Field, validator
from datetime import datetime, timedelta, timezone
from typing import Optional
import re

from database.connection import get_db
from models.auth import User, RefreshToken, UserRole
from utils.auth import (
    hash_password,
    authenticate_user,
    create_access_token,
    create_refresh_token,
    verify_refresh_token,
    get_current_active_user,
    security
)
from utils.audit_service import AuditService
from models.audit_schema import AuditEventType, AuditSeverity
from utils.security import login_rate_limiter, sanitize_username

router = APIRouter()

# ============================================================================
# Request/Response Models
# ============================================================================

class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    role: UserRole = UserRole.SCREENER
    
    @validator('password')
    def validate_password_strength(cls, v):
        """Validate password complexity"""
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        return v
    
    @validator('username')
    def validate_username(cls, v):
        """Validate username format"""
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('Username can only contain letters, numbers, hyphens, and underscores')
        return v


class LoginRequest(BaseModel):
    username: str
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds
    user: dict


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: str
    is_active: bool
    created_at: str
    last_login: Optional[str] = None


class MessageResponse(BaseModel):
    message: str
    success: bool = True


# ============================================================================
# Endpoints
# ============================================================================

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """
    Register a new user
    
    - **username**: Unique username (3-50 chars, alphanumeric + _ -)
    - **email**: Valid email address (must be unique)
    - **password**: Strong password (min 8 chars, uppercase, lowercase, digit)
    - **role**: User role (screener, checker, finalizer) - defaults to screener
    
    Returns user details (without password)
    """
    audit_service = AuditService(db)
    
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        # Log failed registration attempt
        audit_service.log_security_event(
            event_type=AuditEventType.USER_CREATED,
            action=f"Failed user registration attempt for email: {request.email} (email already exists)",
            username=request.username,
            success=False,
            error_message="Email already registered"
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Check if username already exists
    existing_username = db.query(User).filter(User.username == request.username).first()
    if existing_username:
        # Log failed registration attempt
        audit_service.log_security_event(
            event_type=AuditEventType.USER_CREATED,
            action=f"Failed user registration attempt for username: {request.username} (username taken)",
            username=request.username,
            success=False,
            error_message="Username already taken"
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    # Create new user
    hashed_pwd = hash_password(request.password)
    new_user = User(
        username=request.username,
        email=request.email,
        hashed_password=hashed_pwd,
        role=request.role,
        is_active=True
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Log successful registration
    audit_service.log_security_event(
        event_type=AuditEventType.USER_CREATED,
        action=f"New user registered: {new_user.username} (role: {new_user.role.value})",
        user_id=new_user.id,
        username=new_user.username,
        success=True,
        metadata={"email": new_user.email, "role": new_user.role.value}
    )
    
    return UserResponse(
        id=new_user.id,
        username=new_user.username,
        email=new_user.email,
        role=new_user.role.value,
        is_active=new_user.is_active,
        created_at=new_user.created_at.isoformat() if new_user.created_at else "",
        last_login=None
    )


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest, req: Request, db: Session = Depends(get_db)):
    """
    Login with username and password
    
    - **username**: User username
    - **password**: User password
    
    Returns access token (15 min), refresh token (7 days), and user info
    """
    audit_service = AuditService(db)
    ip_address = req.client.host if req.client else "Unknown"
    
    # Sanitize username to prevent injection attacks
    sanitized_username = sanitize_username(request.username)
    
    # Check rate limiting
    if login_rate_limiter.is_locked(sanitized_username):
        lockout_time = login_rate_limiter.get_lockout_time_remaining(sanitized_username)
        audit_service.log_security_event(
            event_type=AuditEventType.AUTH_FAILED,
            action=f"Rate limit exceeded for username: {sanitized_username}",
            username=sanitized_username,
            ip_address=ip_address,
            success=False,
            error_message=f"Account temporarily locked due to too many failed attempts"
        )
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Too many failed login attempts. Account locked for {lockout_time} seconds. Please try again later."
        )
    
    # Authenticate user
    user = authenticate_user(db, sanitized_username, request.password)
    
    if not user:
        # Record failed attempt for rate limiting
        login_rate_limiter.record_failed_attempt(sanitized_username)
        remaining = login_rate_limiter.get_remaining_attempts(sanitized_username)
        
        # Log failed login attempt
        audit_service.log_security_event(
            event_type=AuditEventType.AUTH_FAILED,
            action=f"Failed login attempt for username: {sanitized_username} ({remaining} attempts remaining)",
            username=sanitized_username,
            ip_address=ip_address,
            success=False,
            error_message="Incorrect username or password"
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Incorrect username or password. {remaining} attempts remaining before account lockout.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        # Log inactive account access attempt
        audit_service.log_security_event(
            event_type=AuditEventType.AUTH_FAILED,
            action=f"Login attempt with inactive account: {user.username}",
            user_id=user.id,
            username=user.username,
            ip_address=ip_address,
            success=False,
            error_message="User account is inactive"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    # Update last login
    user.last_login = datetime.now(timezone.utc)
    db.commit()
    
    # Reset rate limiter on successful login
    login_rate_limiter.reset_attempts(sanitized_username)
    
    # Create tokens
    token_data = {
        "user_id": user.id,
        "email": user.email,
        "role": user.role.value
    }
    
    access_token = create_access_token(token_data)
    refresh_token_str = create_refresh_token({"user_id": user.id})
    
    # Save refresh token to database
    refresh_token = RefreshToken(
        user_id=user.id,
        token=refresh_token_str,
        expires_at=datetime.now(timezone.utc) + timedelta(days=7)
    )
    db.add(refresh_token)
    db.commit()
    
    # Log successful login
    audit_service.log_security_event(
        event_type=AuditEventType.AUTH_LOGIN,
        action=f"User logged in: {user.username}",
        user_id=user.id,
        username=user.username,
        ip_address=ip_address,
        success=True,
        metadata={"email": user.email, "role": user.role.value}
    )
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token_str,
        token_type="bearer",
        expires_in=15 * 60,  # 15 minutes in seconds
        user=user.to_dict()
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(request: RefreshRequest, db: Session = Depends(get_db)):
    """
    Refresh access token using refresh token
    
    - **refresh_token**: Valid refresh token
    
    Returns new access token and refresh token
    """
    # Verify refresh token
    user = verify_refresh_token(request.refresh_token, db)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    # Revoke old refresh token
    old_token = db.query(RefreshToken).filter(
        RefreshToken.token == request.refresh_token
    ).first()
    if old_token:
        old_token.is_revoked = True
    
    # Create new tokens
    token_data = {
        "user_id": user.id,
        "email": user.email,
        "role": user.role.value
    }
    
    access_token = create_access_token(token_data)
    refresh_token_str = create_refresh_token({"user_id": user.id})
    
    # Save new refresh token
    new_refresh_token = RefreshToken(
        user_id=user.id,
        token=refresh_token_str,
        expires_at=datetime.now(timezone.utc) + timedelta(days=7)
    )
    db.add(new_refresh_token)
    db.commit()
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token_str,
        token_type="bearer",
        expires_in=15 * 60,
        user=user.to_dict()
    )


@router.post("/logout", response_model=MessageResponse)
async def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Logout user by revoking all refresh tokens
    
    Requires valid access token in Authorization header
    """
    audit_service = AuditService(db)
    
    # Revoke all user's refresh tokens
    db.query(RefreshToken).filter(
        RefreshToken.user_id == current_user.id,
        RefreshToken.is_revoked == False
    ).update({"is_revoked": True})
    
    db.commit()
    
    # Log logout
    audit_service.log_security_event(
        event_type=AuditEventType.AUTH_LOGOUT,
        action=f"User logged out: {current_user.username}",
        user_id=current_user.id,
        username=current_user.username,
        success=True,
        metadata={"role": current_user.role.value}
    )
    
    return MessageResponse(
        message="Successfully logged out",
        success=True
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current authenticated user information
    
    Requires valid access token in Authorization header
    """
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        role=current_user.role.value,
        is_active=current_user.is_active,
        created_at=current_user.created_at.isoformat() if current_user.created_at else "",
        last_login=current_user.last_login.isoformat() if current_user.last_login else None
    )


@router.get("/users")
async def list_users(
    role: Optional[str] = None,
    is_active: Optional[bool] = None,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    List all users (requires authentication)
    
    - **role**: Filter by role (screener, checker, finalizer)
    - **is_active**: Filter by active status
    - **limit**: Maximum number of users to return
    """
    try:
        query = db.query(User)
        
        if role:
            query = query.filter(User.role == role)
        
        if is_active is not None:
            query = query.filter(User.is_active == is_active)
        
        users = query.order_by(User.created_at.desc()).limit(limit).all()
        
        user_list = []
        for user in users:
            user_list.append({
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role.value,
                'is_active': user.is_active,
                'created_at': user.created_at.isoformat() if user.created_at else None,
                'last_login': user.last_login.isoformat() if user.last_login else None
            })
        
        return {
            'success': True,
            'users': user_list,
            'count': len(user_list)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list users: {str(e)}"
        )
