"""
User Management API Routes - Phase 10
REST endpoints for user CRUD operations
"""
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from database.connection import get_db
from models.auth import User
from utils.auth import get_current_user, hash_password
from typing import List, Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime

router = APIRouter()


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: str  # screener, checker, finalizer


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: str
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True


@router.get("", response_model=List[UserResponse])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    role: Optional[str] = None,
    is_active: Optional[bool] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get list of users (Finalizer only)
    
    - **skip**: Number of records to skip
    - **limit**: Maximum number of records to return
    - **role**: Filter by role (screener, checker, finalizer)
    - **is_active**: Filter by active status
    """
    # Only finalizers can view all users
    if current_user.role != 'finalizer':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only finalizers can view all users"
        )
    
    query = db.query(User)
    
    if role:
        query = query.filter(User.role == role)
    
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    
    users = query.offset(skip).limit(limit).all()
    
    return users


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get specific user by ID
    
    Users can view their own profile. Finalizers can view any user.
    """
    # Users can view themselves, finalizers can view anyone
    if current_user.id != user_id and current_user.role != 'finalizer':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own profile"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create new user (Finalizer only)
    
    - **username**: Unique username
    - **email**: User email address
    - **password**: User password (will be hashed)
    - **role**: User role (screener, checker, finalizer)
    """
    # Only finalizers can create users
    if current_user.role != 'finalizer':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only finalizers can create users"
        )
    
    # Validate role
    if user_data.role not in ['screener', 'checker', 'finalizer']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid role. Must be: screener, checker, or finalizer"
        )
    
    # Check if username exists
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )
    
    # Check if email exists
    existing_email = db.query(User).filter(User.email == user_data.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists"
        )
    
    # Create new user
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hash_password(user_data.password),
        role=user_data.role,
        is_active=True,
        created_at=datetime.now()
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update user (Finalizer only, or users can update themselves)
    
    - **email**: New email address
    - **role**: New role (Finalizer only)
    - **is_active**: Active status (Finalizer only)
    """
    # Get user to update
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Users can update their own email, finalizers can update anything
    if current_user.id != user_id and current_user.role != 'finalizer':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own profile"
        )
    
    # Only finalizers can change role and active status
    if current_user.role != 'finalizer' and (user_data.role or user_data.is_active is not None):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only finalizers can change role or active status"
        )
    
    # Update fields
    if user_data.email:
        # Check email uniqueness
        existing = db.query(User).filter(
            User.email == user_data.email,
            User.id != user_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already exists"
            )
        user.email = user_data.email
    
    if user_data.role:
        if user_data.role not in ['screener', 'checker', 'finalizer']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid role"
            )
        user.role = user_data.role
    
    if user_data.is_active is not None:
        user.is_active = user_data.is_active
    
    db.commit()
    db.refresh(user)
    
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete user (Finalizer only)
    
    Soft delete by setting is_active to False
    """
    # Only finalizers can delete users
    if current_user.role != 'finalizer':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only finalizers can delete users"
        )
    
    # Get user
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Can't delete yourself
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )
    
    # Soft delete
    user.is_active = False
    db.commit()
    
    return None


@router.get("/stats/summary")
async def get_user_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user statistics (Finalizer only)
    
    Returns counts by role and active status
    """
    # Only finalizers can view stats
    if current_user.role != 'finalizer':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only finalizers can view user statistics"
        )
    
    total_users = db.query(User).count()
    active_users = db.query(User).filter(User.is_active == True).count()
    
    screeners = db.query(User).filter(User.role == 'screener').count()
    checkers = db.query(User).filter(User.role == 'checker').count()
    finalizers = db.query(User).filter(User.role == 'finalizer').count()
    
    return {
        "success": True,
        "statistics": {
            "total_users": total_users,
            "active_users": active_users,
            "inactive_users": total_users - active_users,
            "by_role": {
                "screeners": screeners,
                "checkers": checkers,
                "finalizers": finalizers
            }
        }
    }
