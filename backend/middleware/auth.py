"""
Role-Based Access Control Middleware
Provides role-based authorization decorators and dependencies
"""
from fastapi import Depends, HTTPException, status
from functools import wraps
from typing import List

from models.auth import User, UserRole
from utils.auth import get_current_active_user


def require_roles(allowed_roles: List[UserRole]):
    """
    Dependency factory to require specific roles
    
    Args:
        allowed_roles: List of allowed UserRole enums
        
    Returns:
        Dependency function that checks user role
        
    Example:
        @router.get("/admin")
        async def admin_route(user: User = Depends(require_roles([UserRole.FINALIZER]))):
            ...
    """
    async def role_checker(current_user: User = Depends(get_current_active_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required role(s): {[role.value for role in allowed_roles]}. Your role: {current_user.role.value}"
            )
        return current_user
    
    return role_checker


# ============================================================================
# Role-Specific Dependencies
# ============================================================================

async def require_screener(current_user: User = Depends(get_current_active_user)) -> User:
    """
    Dependency to require screener role
    Screeners can: upload blacklists, run scans, flag items, undo flags
    
    Usage:
        @router.post("/scan")
        async def scan(user: User = Depends(require_screener)):
            ...
    """
    if current_user.role != UserRole.SCREENER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied. Screener role required. Your role: {current_user.role.value}"
        )
    return current_user


async def require_checker(current_user: User = Depends(get_current_active_user)) -> User:
    """
    Dependency to require checker role
    Checkers can: review flagged items, approve flags, request rechecks, assign items
    
    Usage:
        @router.post("/checker/approve")
        async def approve(user: User = Depends(require_checker)):
            ...
    """
    if current_user.role != UserRole.CHECKER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied. Checker role required. Your role: {current_user.role.value}"
        )
    return current_user


async def require_finalizer(current_user: User = Depends(get_current_active_user)) -> User:
    """
    Dependency to require finalizer role
    Finalizers can: give final approval, override decisions, generate reports, view audit logs
    
    Usage:
        @router.post("/finalizer/approve")
        async def final_approve(user: User = Depends(require_finalizer)):
            ...
    """
    if current_user.role != UserRole.FINALIZER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied. Finalizer role required. Your role: {current_user.role.value}"
        )
    return current_user


async def require_checker_or_finalizer(current_user: User = Depends(get_current_active_user)) -> User:
    """
    Dependency to require checker OR finalizer role
    Useful for endpoints accessible to both supervisory roles
    
    Usage:
        @router.get("/flagged-items")
        async def get_flagged(user: User = Depends(require_checker_or_finalizer)):
            ...
    """
    if current_user.role not in [UserRole.CHECKER, UserRole.FINALIZER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied. Checker or Finalizer role required. Your role: {current_user.role.value}"
        )
    return current_user


async def require_screener_or_checker(current_user: User = Depends(get_current_active_user)) -> User:
    """
    Dependency to require screener OR checker role
    Useful for endpoints accessible to operational roles
    
    Usage:
        @router.get("/in-review")
        async def get_in_review(user: User = Depends(require_screener_or_checker)):
            ...
    """
    if current_user.role not in [UserRole.SCREENER, UserRole.CHECKER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied. Screener or Checker role required. Your role: {current_user.role.value}"
        )
    return current_user


# ============================================================================
# Helper Functions
# ============================================================================

def check_permission(user: User, required_role: UserRole) -> bool:
    """
    Check if user has required role permission
    
    Args:
        user: User object
        required_role: Required role
        
    Returns:
        True if user has permission, False otherwise
    """
    return user.role == required_role


def check_any_permission(user: User, required_roles: List[UserRole]) -> bool:
    """
    Check if user has any of the required roles
    
    Args:
        user: User object
        required_roles: List of required roles
        
    Returns:
        True if user has any of the roles, False otherwise
    """
    return user.role in required_roles


def get_role_hierarchy() -> dict:
    """
    Get role hierarchy (higher levels can access lower level features)
    
    Returns:
        Dictionary mapping roles to their access levels
    """
    return {
        UserRole.SCREENER: 1,
        UserRole.CHECKER: 2,
        UserRole.FINALIZER: 3
    }


def has_higher_or_equal_role(user: User, required_role: UserRole) -> bool:
    """
    Check if user has higher or equal role in hierarchy
    
    Args:
        user: User object
        required_role: Required role
        
    Returns:
        True if user role is higher or equal, False otherwise
    """
    hierarchy = get_role_hierarchy()
    return hierarchy.get(user.role, 0) >= hierarchy.get(required_role, 0)
