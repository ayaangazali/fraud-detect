"""
Password Utility Tests
Tests for password hashing and verification
"""
import pytest
from utils.auth import hash_password, verify_password


class TestPasswordHashing:
    """Test password hashing functionality"""
    
    def test_hash_password_returns_string(self):
        """Test that hash_password returns a string"""
        password = "TestPassword123"
        hashed = hash_password(password)
        
        assert isinstance(hashed, str)
        assert len(hashed) > 0
    
    def test_hash_password_is_bcrypt_format(self):
        """Test that hashed password is in bcrypt format"""
        password = "TestPassword123"
        hashed = hash_password(password)
        
        # Bcrypt hashes start with $2b$
        assert hashed.startswith("$2b$")
    
    def test_hash_password_different_each_time(self):
        """Test that same password produces different hashes (salt)"""
        password = "TestPassword123"
        hash1 = hash_password(password)
        hash2 = hash_password(password)
        
        assert hash1 != hash2
    
    def test_verify_password_correct(self):
        """Test password verification with correct password"""
        password = "TestPassword123"
        hashed = hash_password(password)
        
        assert verify_password(password, hashed) is True
    
    def test_verify_password_incorrect(self):
        """Test password verification with incorrect password"""
        password = "TestPassword123"
        hashed = hash_password(password)
        
        assert verify_password("WrongPassword", hashed) is False
    
    def test_verify_password_case_sensitive(self):
        """Test that password verification is case-sensitive"""
        password = "TestPassword123"
        hashed = hash_password(password)
        
        assert verify_password("testpassword123", hashed) is False
        assert verify_password("TESTPASSWORD123", hashed) is False
    
    def test_hash_password_with_special_characters(self):
        """Test hashing password with special characters"""
        password = "P@ssw0rd!#$%"
        hashed = hash_password(password)
        
        assert verify_password(password, hashed) is True
    
    def test_hash_password_with_unicode(self):
        """Test hashing password with unicode characters"""
        password = "Pāsswörd123"
        hashed = hash_password(password)
        
        assert verify_password(password, hashed) is True
    
    def test_hash_empty_string(self):
        """Test hashing empty string"""
        password = ""
        hashed = hash_password(password)
        
        assert isinstance(hashed, str)
        assert verify_password("", hashed) is True
    
    def test_hash_very_long_password(self):
        """Test hashing very long password"""
        password = "a" * 1000
        hashed = hash_password(password)
        
        assert verify_password(password, hashed) is True


class TestTokenGeneration:
    """Test JWT token generation"""
    
    def test_create_access_token(self):
        """Test access token creation"""
        from utils.auth import create_access_token
        
        token_data = {
            "user_id": 1,
            "email": "test@kamco.com",
            "role": "screener"
        }
        
        token = create_access_token(token_data)
        
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_create_refresh_token(self):
        """Test refresh token creation"""
        from utils.auth import create_refresh_token
        
        token_data = {"user_id": 1}
        token = create_refresh_token(token_data)
        
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_decode_valid_token(self):
        """Test decoding valid token"""
        from utils.auth import create_access_token, decode_token
        
        token_data = {
            "user_id": 1,
            "email": "test@kamco.com",
            "role": "screener"
        }
        
        token = create_access_token(token_data)
        decoded = decode_token(token)
        
        assert decoded["user_id"] == 1
        assert decoded["email"] == "test@kamco.com"
        assert decoded["role"] == "screener"
        assert decoded["type"] == "access"
    
    def test_decode_invalid_token(self):
        """Test decoding invalid token raises exception"""
        from utils.auth import decode_token
        from fastapi import HTTPException
        
        with pytest.raises(HTTPException) as exc_info:
            decode_token("invalid_token_string")
        
        assert exc_info.value.status_code == 401
    
    def test_tokens_are_different(self):
        """Test that different calls produce different tokens"""
        from utils.auth import create_access_token
        
        token_data = {"user_id": 1}
        token1 = create_access_token(token_data)
        token2 = create_access_token(token_data)
        
        # Tokens should be different due to timestamp
        assert token1 != token2


class TestAuthenticateUser:
    """Test user authentication function"""
    
    def test_authenticate_user_success(self, db_session, test_users):
        """Test successful user authentication"""
        from utils.auth import authenticate_user
        
        screener = test_users["screener_test"]
        user = authenticate_user(
            db_session,
            screener["username"],
            screener["password"]
        )
        
        assert user is not None
        assert user.username == screener["username"]
        assert user.email == screener["email"]
    
    def test_authenticate_user_wrong_password(self, db_session, test_users):
        """Test authentication with wrong password"""
        from utils.auth import authenticate_user
        
        screener = test_users["screener_test"]
        user = authenticate_user(
            db_session,
            screener["username"],
            "WrongPassword123"
        )
        
        assert user is None
    
    def test_authenticate_user_wrong_username(self, db_session):
        """Test authentication with non-existent username"""
        from utils.auth import authenticate_user
        
        user = authenticate_user(
            db_session,
            "nonexistent_user",
            "SomePassword123"
        )
        
        assert user is None
    
    def test_authenticate_user_empty_credentials(self, db_session):
        """Test authentication with empty credentials"""
        from utils.auth import authenticate_user
        
        user = authenticate_user(db_session, "", "")
        assert user is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
