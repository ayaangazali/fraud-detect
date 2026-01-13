"""
Security Enhancements for Authentication System
Additional security layers and rate limiting
"""
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict, Optional
import threading


class RateLimiter:
    """Rate limiter to prevent brute force attacks"""
    
    def __init__(self, max_attempts: int = 5, lockout_duration: int = 300):
        """
        Initialize rate limiter
        
        Args:
            max_attempts: Maximum failed attempts before lockout
            lockout_duration: Lockout duration in seconds (default 5 minutes)
        """
        self.max_attempts = max_attempts
        self.lockout_duration = lockout_duration
        self.attempts: Dict[str, list] = defaultdict(list)
        self.lock = threading.Lock()
    
    def is_locked(self, identifier: str) -> bool:
        """
        Check if identifier is currently locked out
        
        Args:
            identifier: Username or IP address
            
        Returns:
            True if locked out, False otherwise
        """
        with self.lock:
            if identifier not in self.attempts:
                return False
            
            # Clean up old attempts
            cutoff_time = datetime.now() - timedelta(seconds=self.lockout_duration)
            self.attempts[identifier] = [
                attempt for attempt in self.attempts[identifier]
                if attempt > cutoff_time
            ]
            
            return len(self.attempts[identifier]) >= self.max_attempts
    
    def record_failed_attempt(self, identifier: str):
        """
        Record a failed login attempt
        
        Args:
            identifier: Username or IP address
        """
        with self.lock:
            self.attempts[identifier].append(datetime.now())
    
    def reset_attempts(self, identifier: str):
        """
        Reset failed attempts (on successful login)
        
        Args:
            identifier: Username or IP address
        """
        with self.lock:
            if identifier in self.attempts:
                del self.attempts[identifier]
    
    def get_remaining_attempts(self, identifier: str) -> int:
        """
        Get remaining login attempts before lockout
        
        Args:
            identifier: Username or IP address
            
        Returns:
            Number of remaining attempts
        """
        with self.lock:
            if identifier not in self.attempts:
                return self.max_attempts
            
            # Clean up old attempts
            cutoff_time = datetime.now() - timedelta(seconds=self.lockout_duration)
            self.attempts[identifier] = [
                attempt for attempt in self.attempts[identifier]
                if attempt > cutoff_time
            ]
            
            return max(0, self.max_attempts - len(self.attempts[identifier]))
    
    def get_lockout_time_remaining(self, identifier: str) -> Optional[int]:
        """
        Get remaining lockout time in seconds
        
        Args:
            identifier: Username or IP address
            
        Returns:
            Seconds remaining in lockout, or None if not locked out
        """
        with self.lock:
            if not self.is_locked(identifier):
                return None
            
            if identifier not in self.attempts or not self.attempts[identifier]:
                return None
            
            # Get the oldest attempt
            oldest_attempt = min(self.attempts[identifier])
            lockout_end = oldest_attempt + timedelta(seconds=self.lockout_duration)
            remaining = (lockout_end - datetime.now()).total_seconds()
            
            return max(0, int(remaining))


# Global rate limiter instance
login_rate_limiter = RateLimiter(max_attempts=5, lockout_duration=300)


def check_password_strength(password: str) -> tuple[bool, str]:
    """
    Check password strength beyond basic validation
    
    Args:
        password: Password to check
        
    Returns:
        Tuple of (is_strong, message)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if len(password) > 128:
        return False, "Password must not exceed 128 characters"
    
    if not any(c.isupper() for c in password):
        return False, "Password must contain at least one uppercase letter"
    
    if not any(c.islower() for c in password):
        return False, "Password must contain at least one lowercase letter"
    
    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one digit"
    
    # Check for common weak passwords
    common_passwords = [
        "Password123", "Admin123", "Welcome123", "Qwerty123",
        "123456789", "Abc123456", "Password1", "Test123"
    ]
    
    if password in common_passwords:
        return False, "Password is too common. Please choose a stronger password"
    
    # Check for sequential characters
    if "123" in password or "abc" in password.lower():
        return False, "Password should not contain sequential characters"
    
    return True, "Password is strong"


def sanitize_username(username: str) -> str:
    """
    Sanitize username to prevent injection attacks
    
    Args:
        username: Raw username input
        
    Returns:
        Sanitized username
    """
    # Remove any potential SQL injection characters
    dangerous_chars = ["'", '"', ";", "--", "/*", "*/", "xp_", "sp_", "DROP", "SELECT", "INSERT", "UPDATE", "DELETE"]
    
    sanitized = username
    for char in dangerous_chars:
        sanitized = sanitized.replace(char, "")
    
    return sanitized.strip()


def validate_session_token(token: str) -> bool:
    """
    Validate session token format
    
    Args:
        token: JWT token string
        
    Returns:
        True if token format is valid, False otherwise
    """
    if not token or not isinstance(token, str):
        return False
    
    # JWT tokens have 3 parts separated by dots
    parts = token.split(".")
    if len(parts) != 3:
        return False
    
    # Each part should be base64url encoded
    for part in parts:
        if not part or not all(c in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_=" for c in part):
            return False
    
    return True


def log_security_event(event_type: str, username: str, ip_address: str, success: bool, details: str = ""):
    """
    Log security-related events for audit trail
    
    Args:
        event_type: Type of event (LOGIN, LOGOUT, PASSWORD_CHANGE, etc.)
        username: Username involved
        ip_address: IP address of request
        success: Whether the action was successful
        details: Additional details
    """
    timestamp = datetime.now().isoformat()
    status = "SUCCESS" if success else "FAILED"
    
    log_entry = f"[{timestamp}] {event_type} {status} - User: {username}, IP: {ip_address}"
    if details:
        log_entry += f" - {details}"
    
    # Log to file (in production, use proper logging framework)
    try:
        with open("logs/security.log", "a") as f:
            f.write(log_entry + "\n")
    except:
        pass  # Fail silently if logging fails
    
    print(log_entry)
