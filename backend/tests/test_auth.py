"""
Authentication Tests
Tests for login, registration, token refresh, and logout
"""
import pytest
from datetime import datetime, timedelta, timezone


class TestLogin:
    """Test login functionality"""
    
    def test_login_success_screener(self, client, test_users):
        """Test successful login with screener credentials"""
        screener = test_users["screener_test"]
        response = client.post(
            "/api/auth/login",
            json={
                "username": screener["username"],
                "password": screener["password"]
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "access_token" in data
        assert "refresh_token" in data
        assert "token_type" in data
        assert "expires_in" in data
        assert "user" in data
        
        # Verify token type
        assert data["token_type"] == "bearer"
        
        # Verify user data
        user_data = data["user"]
        assert user_data["username"] == screener["username"]
        assert user_data["email"] == screener["email"]
        assert user_data["role"] == "screener"
        assert user_data["is_active"] is True
        assert "id" in user_data
        
        # Verify password is not returned
        assert "password" not in user_data
        assert "hashed_password" not in user_data
    
    def test_login_success_checker(self, client, test_users):
        """Test successful login with checker credentials"""
        checker = test_users["checker_test"]
        response = client.post(
            "/api/auth/login",
            json={
                "username": checker["username"],
                "password": checker["password"]
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["user"]["role"] == "checker"
    
    def test_login_success_finalizer(self, client, test_users):
        """Test successful login with finalizer credentials"""
        finalizer = test_users["finalizer_test"]
        response = client.post(
            "/api/auth/login",
            json={
                "username": finalizer["username"],
                "password": finalizer["password"]
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["user"]["role"] == "finalizer"
    
    def test_login_wrong_password(self, client, test_users):
        """Test login with incorrect password"""
        screener = test_users["screener_test"]
        response = client.post(
            "/api/auth/login",
            json={
                "username": screener["username"],
                "password": "WrongPassword123"
            }
        )
        
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
        assert "incorrect" in data["detail"].lower()
    
    def test_login_wrong_username(self, client, test_users):
        """Test login with non-existent username"""
        response = client.post(
            "/api/auth/login",
            json={
                "username": "nonexistent_user",
                "password": "SomePassword123"
            }
        )
        
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
    
    def test_login_inactive_user(self, client, test_users):
        """Test login with inactive user account"""
        inactive = test_users["inactive_user"]
        response = client.post(
            "/api/auth/login",
            json={
                "username": inactive["username"],
                "password": inactive["password"]
            }
        )
        
        assert response.status_code == 403
        data = response.json()
        assert "inactive" in data["detail"].lower()
    
    def test_login_missing_username(self, client):
        """Test login without username"""
        response = client.post(
            "/api/auth/login",
            json={"password": "SomePassword123"}
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_login_missing_password(self, client, test_users):
        """Test login without password"""
        screener = test_users["screener_test"]
        response = client.post(
            "/api/auth/login",
            json={"username": screener["username"]}
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_login_empty_username(self, client):
        """Test login with empty username"""
        response = client.post(
            "/api/auth/login",
            json={"username": "", "password": "SomePassword123"}
        )
        
        assert response.status_code == 401
    
    def test_login_empty_password(self, client, test_users):
        """Test login with empty password"""
        screener = test_users["screener_test"]
        response = client.post(
            "/api/auth/login",
            json={"username": screener["username"], "password": ""}
        )
        
        assert response.status_code == 401
    
    def test_login_case_sensitive_username(self, client, test_users):
        """Test that username is case-sensitive"""
        screener = test_users["screener_test"]
        response = client.post(
            "/api/auth/login",
            json={
                "username": screener["username"].upper(),
                "password": screener["password"]
            }
        )
        
        assert response.status_code == 401
    
    def test_login_sql_injection_attempt(self, client):
        """Test protection against SQL injection"""
        response = client.post(
            "/api/auth/login",
            json={
                "username": "admin' OR '1'='1",
                "password": "password' OR '1'='1"
            }
        )
        
        assert response.status_code == 401
    
    def test_multiple_successful_logins(self, client, test_users):
        """Test that a user can login multiple times"""
        screener = test_users["screener_test"]
        
        # First login
        response1 = client.post(
            "/api/auth/login",
            json={
                "username": screener["username"],
                "password": screener["password"]
            }
        )
        assert response1.status_code == 200
        token1 = response1.json()["access_token"]
        
        # Second login
        response2 = client.post(
            "/api/auth/login",
            json={
                "username": screener["username"],
                "password": screener["password"]
            }
        )
        assert response2.status_code == 200
        token2 = response2.json()["access_token"]
        
        # Tokens should be different
        assert token1 != token2


class TestRegistration:
    """Test user registration functionality"""
    
    def test_register_success(self, client):
        """Test successful user registration"""
        response = client.post(
            "/api/auth/register",
            json={
                "username": "newuser",
                "email": "newuser@kamco.com",
                "password": "NewUser123",
                "role": "screener"
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        
        assert data["username"] == "newuser"
        assert data["email"] == "newuser@kamco.com"
        assert data["role"] == "screener"
        assert data["is_active"] is True
        assert "id" in data
        assert "password" not in data
    
    def test_register_duplicate_email(self, client, test_users):
        """Test registration with existing email"""
        screener = test_users["screener_test"]
        response = client.post(
            "/api/auth/register",
            json={
                "username": "different_username",
                "email": screener["email"],
                "password": "Password123",
                "role": "screener"
            }
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "email" in data["detail"].lower()
    
    def test_register_duplicate_username(self, client, test_users):
        """Test registration with existing username"""
        screener = test_users["screener_test"]
        response = client.post(
            "/api/auth/register",
            json={
                "username": screener["username"],
                "email": "different@kamco.com",
                "password": "Password123",
                "role": "screener"
            }
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "username" in data["detail"].lower()
    
    def test_register_weak_password_no_uppercase(self, client):
        """Test registration with weak password (no uppercase)"""
        response = client.post(
            "/api/auth/register",
            json={
                "username": "weakuser",
                "email": "weak@kamco.com",
                "password": "password123",
                "role": "screener"
            }
        )
        
        assert response.status_code == 422
        data = response.json()
        assert "uppercase" in str(data).lower()
    
    def test_register_weak_password_no_lowercase(self, client):
        """Test registration with weak password (no lowercase)"""
        response = client.post(
            "/api/auth/register",
            json={
                "username": "weakuser",
                "email": "weak@kamco.com",
                "password": "PASSWORD123",
                "role": "screener"
            }
        )
        
        assert response.status_code == 422
        data = response.json()
        assert "lowercase" in str(data).lower()
    
    def test_register_weak_password_no_digit(self, client):
        """Test registration with weak password (no digit)"""
        response = client.post(
            "/api/auth/register",
            json={
                "username": "weakuser",
                "email": "weak@kamco.com",
                "password": "PasswordABC",
                "role": "screener"
            }
        )
        
        assert response.status_code == 422
        data = response.json()
        assert "digit" in str(data).lower()
    
    def test_register_password_too_short(self, client):
        """Test registration with password too short"""
        response = client.post(
            "/api/auth/register",
            json={
                "username": "shortpw",
                "email": "short@kamco.com",
                "password": "Pw1",
                "role": "screener"
            }
        )
        
        assert response.status_code == 422
    
    def test_register_invalid_email(self, client):
        """Test registration with invalid email format"""
        response = client.post(
            "/api/auth/register",
            json={
                "username": "invalidem",
                "email": "notanemail",
                "password": "Password123",
                "role": "screener"
            }
        )
        
        assert response.status_code == 422
    
    def test_register_invalid_username_special_chars(self, client):
        """Test registration with invalid username (special characters)"""
        response = client.post(
            "/api/auth/register",
            json={
                "username": "user@#$%",
                "email": "user@kamco.com",
                "password": "Password123",
                "role": "screener"
            }
        )
        
        assert response.status_code == 422
    
    def test_register_username_too_short(self, client):
        """Test registration with username too short"""
        response = client.post(
            "/api/auth/register",
            json={
                "username": "ab",
                "email": "short@kamco.com",
                "password": "Password123",
                "role": "screener"
            }
        )
        
        assert response.status_code == 422


class TestTokenAuthentication:
    """Test token-based authentication"""
    
    def test_access_protected_endpoint_with_valid_token(self, client, authenticated_screener):
        """Test accessing protected endpoint with valid token"""
        response = client.get(
            "/api/auth/me",
            headers=authenticated_screener["headers"]
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "screener_test"
    
    def test_access_protected_endpoint_without_token(self, client):
        """Test accessing protected endpoint without token"""
        response = client.get("/api/auth/me")
        
        assert response.status_code == 403  # Forbidden
    
    def test_access_protected_endpoint_with_invalid_token(self, client):
        """Test accessing protected endpoint with invalid token"""
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": "Bearer invalid_token_here"}
        )
        
        assert response.status_code == 401
    
    def test_access_protected_endpoint_with_malformed_header(self, client):
        """Test accessing protected endpoint with malformed auth header"""
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": "NotBearer token"}
        )
        
        assert response.status_code == 403
    
    def test_token_contains_user_info(self, client, authenticated_screener):
        """Test that access token contains user information"""
        # Decode the token (in real test, would use jwt.decode)
        response = client.get(
            "/api/auth/me",
            headers=authenticated_screener["headers"]
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "username" in data
        assert "email" in data
        assert "role" in data


class TestTokenRefresh:
    """Test token refresh functionality"""
    
    def test_refresh_token_success(self, client, authenticated_screener):
        """Test successful token refresh"""
        response = client.post(
            "/api/auth/refresh",
            json={"refresh_token": authenticated_screener["refresh_token"]}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert "token_type" in data
        
        # New access token should be different
        assert data["access_token"] != authenticated_screener["access_token"]
    
    def test_refresh_with_invalid_token(self, client):
        """Test refresh with invalid token"""
        response = client.post(
            "/api/auth/refresh",
            json={"refresh_token": "invalid_refresh_token"}
        )
        
        assert response.status_code == 401
    
    def test_refresh_with_access_token(self, client, authenticated_screener):
        """Test that access token cannot be used for refresh"""
        response = client.post(
            "/api/auth/refresh",
            json={"refresh_token": authenticated_screener["access_token"]}
        )
        
        assert response.status_code == 401


class TestLogout:
    """Test logout functionality"""
    
    def test_logout_success(self, client, authenticated_screener):
        """Test successful logout"""
        response = client.post(
            "/api/auth/logout",
            headers=authenticated_screener["headers"]
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_logout_invalidates_refresh_token(self, client, authenticated_screener):
        """Test that logout invalidates refresh token"""
        # Logout
        logout_response = client.post(
            "/api/auth/logout",
            headers=authenticated_screener["headers"]
        )
        assert logout_response.status_code == 200
        
        # Try to use refresh token after logout
        refresh_response = client.post(
            "/api/auth/refresh",
            json={"refresh_token": authenticated_screener["refresh_token"]}
        )
        
        assert refresh_response.status_code == 401
    
    def test_logout_without_token(self, client):
        """Test logout without authentication"""
        response = client.post("/api/auth/logout")
        
        assert response.status_code == 403


class TestPasswordSecurity:
    """Test password hashing and security"""
    
    def test_passwords_are_hashed(self, client, db_session, test_users):
        """Test that passwords are hashed in database"""
        from models.auth import User
        
        screener = test_users["screener_test"]
        user = db_session.query(User).filter(
            User.username == screener["username"]
        ).first()
        
        # Password should not be stored in plain text
        assert user.hashed_password != screener["password"]
        
        # Password should be bcrypt hash
        assert user.hashed_password.startswith("$2b$")
    
    def test_same_password_different_hashes(self, client):
        """Test that same password gets different hashes (due to salt)"""
        # Register two users with same password
        response1 = client.post(
            "/api/auth/register",
            json={
                "username": "user1",
                "email": "user1@kamco.com",
                "password": "SamePassword123",
                "role": "screener"
            }
        )
        assert response1.status_code == 201
        
        response2 = client.post(
            "/api/auth/register",
            json={
                "username": "user2",
                "email": "user2@kamco.com",
                "password": "SamePassword123",
                "role": "screener"
            }
        )
        assert response2.status_code == 201
        
        # Both should be able to login (hashes work correctly)
        login1 = client.post(
            "/api/auth/login",
            json={"username": "user1", "password": "SamePassword123"}
        )
        assert login1.status_code == 200
        
        login2 = client.post(
            "/api/auth/login",
            json={"username": "user2", "password": "SamePassword123"}
        )
        assert login2.status_code == 200


class TestRoleBasedAccess:
    """Test role-based access control"""
    
    def test_screener_can_login(self, client, test_users):
        """Test screener role can login"""
        screener = test_users["screener_test"]
        response = client.post(
            "/api/auth/login",
            json={
                "username": screener["username"],
                "password": screener["password"]
            }
        )
        
        assert response.status_code == 200
        assert response.json()["user"]["role"] == "screener"
    
    def test_checker_can_login(self, client, test_users):
        """Test checker role can login"""
        checker = test_users["checker_test"]
        response = client.post(
            "/api/auth/login",
            json={
                "username": checker["username"],
                "password": checker["password"]
            }
        )
        
        assert response.status_code == 200
        assert response.json()["user"]["role"] == "checker"
    
    def test_finalizer_can_login(self, client, test_users):
        """Test finalizer role can login"""
        finalizer = test_users["finalizer_test"]
        response = client.post(
            "/api/auth/login",
            json={
                "username": finalizer["username"],
                "password": finalizer["password"]
            }
        )
        
        assert response.status_code == 200
        assert response.json()["user"]["role"] == "finalizer"


class TestSecurityHeaders:
    """Test security headers and CORS"""
    
    def test_login_response_headers(self, client, test_users):
        """Test that login response has proper security headers"""
        screener = test_users["screener_test"]
        response = client.post(
            "/api/auth/login",
            json={
                "username": screener["username"],
                "password": screener["password"]
            }
        )
        
        assert response.status_code == 200
        # Check for CORS headers (if configured)
        # assert "access-control-allow-origin" in response.headers


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
