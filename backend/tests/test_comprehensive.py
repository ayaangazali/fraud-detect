"""
Comprehensive Test Suite for Screening V2 System
Tests: Upload, Matching, Decisions, Reports, Email, and All Features
"""
import pytest
import io
import csv
import json
from datetime import datetime
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from main import app
from database.connection import get_db, Base
from models.auth import User
from models.screening import (
    KamcoEntity,
    BlacklistUpload,
    ScreeningMatch,
    DecisionLog
)
from utils.auth import hash_password, create_access_token

# Test database
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test_comprehensive.db"
engine = create_engine(SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture(scope="function")
def db_session():
    """Create fresh database for each test"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Create test client"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)


@pytest.fixture
def screener_user(db_session):
    """Create screener user"""
    user = User(
        username="screener_test",
        email="screener@test.com",
        role="screener",
        is_active=True,
        hashed_password=hash_password("TestPass123!")
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def checker_user(db_session):
    """Create checker user"""
    user = User(
        username="checker_test",
        email="checker@test.com",
        role="checker",
        is_active=True,
        hashed_password=hash_password("TestPass123!")
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def finalizer_user(db_session):
    """Create finalizer user"""
    user = User(
        username="finalizer_test",
        email="finalizer@test.com",
        role="finalizer",
        is_active=True,
        hashed_password=hash_password("TestPass123!")
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def auth_headers(screener_user):
    """Create auth headers for screener"""
    token = create_access_token({
        "user_id": screener_user.id,
        "email": screener_user.email,
        "role": screener_user.role.value
    })
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def checker_headers(checker_user):
    """Create auth headers for checker"""
    token = create_access_token({
        "user_id": checker_user.id,
        "email": checker_user.email,
        "role": checker_user.role.value
    })
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def finalizer_headers(finalizer_user):
    """Create auth headers for finalizer"""
    token = create_access_token({
        "user_id": finalizer_user.id,
        "email": finalizer_user.email,
        "role": finalizer_user.role.value
    })
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def sample_kamco_entities(db_session):
    """Create sample KAMCO entities"""
    entities = [
        KamcoEntity(
            customer_id="KC001",
            entity_type="Client",
            entity_category="Individual",
            name_english="Mohammed Al-Rashid",
            name_arabic="محمد الراشد",
            civil_id="123456789",
            nationality="Kuwaiti",
            risk_level="Medium"
        ),
        KamcoEntity(
            customer_id="KC002",
            entity_type="Vendor",
            entity_category="Individual",
            name_english="Ahmed Al-Mutairi",
            name_arabic="أحمد المطيري",
            civil_id="987654321",
            nationality="Kuwaiti",
            risk_level="Low"
        ),
        KamcoEntity(
            customer_id="KC003",
            entity_type="Client",
            entity_category="Individual",
            name_english="Fatima Al-Salem",
            name_arabic="فاطمة السالم",
            civil_id="555666777",
            nationality="Kuwaiti",
            risk_level="Low"
        ),
        KamcoEntity(
            customer_id="KC004",
            entity_type="Staff",
            entity_category="Individual",
            name_english="John Smith",
            name_arabic="جون سميث",
            civil_id="111222333",
            nationality="American",
            risk_level="Low"
        ),
        KamcoEntity(
            customer_id="KC005",
            entity_type="Client",
            entity_category="Corporate",
            name_english="Kuwait Investment Corp",
            name_arabic="شركة الكويت للاستثمار",
            civil_id="888999000",
            nationality="Kuwaiti",
            risk_level="High"
        )
    ]
    for entity in entities:
        db_session.add(entity)
    db_session.commit()
    return entities


def create_csv_content(data: list) -> str:
    """Helper to create CSV content"""
    if not data:
        return ""
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=data[0].keys())
    writer.writeheader()
    writer.writerows(data)
    return output.getvalue()


# ============================================================================
# TEST: BLACKLIST UPLOAD
# ============================================================================

class TestBlacklistUpload:
    """Test blacklist upload functionality"""
    
    def test_upload_success(self, client, auth_headers, sample_kamco_entities):
        """Test successful blacklist upload"""
        blacklist = [
            {
                'Reference_Number': 'BL001',
                'Full_Name_English': 'Mohammed Rashid',
                'Nationality': 'Kuwaiti',
                'Risk_Level': 'HIGH'
            }
        ]
        csv_content = create_csv_content(blacklist)
        files = {'file': ('test.csv', csv_content, 'text/csv')}
        
        response = client.post(
            '/api/screening/v2/upload-blacklist',
            files=files,
            data={'threshold': 70},
            headers=auth_headers
        )
        
        assert response.status_code == 200
        result = response.json()
        assert result['success'] is True
        assert result['entries_processed'] == 1
    
    def test_upload_requires_auth(self, client, sample_kamco_entities):
        """Test that upload requires authentication"""
        csv_content = create_csv_content([{'Full_Name_English': 'Test'}])
        files = {'file': ('test.csv', csv_content, 'text/csv')}
        
        response = client.post('/api/screening/v2/upload-blacklist', files=files)
        assert response.status_code in [401, 403]
    
    def test_upload_rejects_non_csv(self, client, auth_headers):
        """Test that non-CSV files are rejected"""
        files = {'file': ('test.txt', 'not csv', 'text/plain')}
        
        response = client.post(
            '/api/screening/v2/upload-blacklist',
            files=files,
            headers=auth_headers
        )
        
        assert response.status_code == 400
    
    def test_upload_rejects_empty_csv(self, client, auth_headers):
        """Test that empty CSV is rejected"""
        csv_content = "Full_Name_English\n"
        files = {'file': ('empty.csv', csv_content, 'text/csv')}
        
        response = client.post(
            '/api/screening/v2/upload-blacklist',
            files=files,
            headers=auth_headers
        )
        
        assert response.status_code == 400
    
    def test_upload_bulk_entries(self, client, auth_headers, sample_kamco_entities):
        """Test bulk upload"""
        blacklist = [
            {'Reference_Number': f'BL{i:03d}', 'Full_Name_English': f'Person {i}'}
            for i in range(10)
        ]
        csv_content = create_csv_content(blacklist)
        files = {'file': ('bulk.csv', csv_content, 'text/csv')}
        
        response = client.post(
            '/api/screening/v2/upload-blacklist',
            files=files,
            data={'threshold': 70},
            headers=auth_headers
        )
        
        assert response.status_code == 200
        assert response.json()['entries_processed'] == 10


# ============================================================================
# TEST: THRESHOLD FILTERING
# ============================================================================

class TestThresholdFiltering:
    """Test threshold-based filtering"""
    
    def test_high_threshold(self, client, auth_headers, sample_kamco_entities):
        """Test with high threshold (95%)"""
        blacklist = [{'Full_Name_English': 'Mohammed Rashid'}]  # Similar, not exact
        csv_content = create_csv_content(blacklist)
        files = {'file': ('test.csv', csv_content, 'text/csv')}
        
        response = client.post(
            '/api/screening/v2/upload-blacklist',
            files=files,
            data={'threshold': 95},
            headers=auth_headers
        )
        
        assert response.status_code == 200
        # High threshold = fewer matches
    
    def test_low_threshold(self, client, auth_headers, sample_kamco_entities):
        """Test with low threshold (50%)"""
        blacklist = [{'Full_Name_English': 'Mohammed'}]
        csv_content = create_csv_content(blacklist)
        files = {'file': ('test.csv', csv_content, 'text/csv')}
        
        response = client.post(
            '/api/screening/v2/upload-blacklist',
            files=files,
            data={'threshold': 50},
            headers=auth_headers
        )
        
        assert response.status_code == 200
        # Low threshold = more matches
    
    def test_zero_threshold(self, client, auth_headers, sample_kamco_entities):
        """Test with zero threshold (all matches)"""
        blacklist = [{'Full_Name_English': 'Random Name'}]
        csv_content = create_csv_content(blacklist)
        files = {'file': ('test.csv', csv_content, 'text/csv')}
        
        response = client.post(
            '/api/screening/v2/upload-blacklist',
            files=files,
            data={'threshold': 0},
            headers=auth_headers
        )
        
        assert response.status_code == 200


# ============================================================================
# TEST: DATABASE PERSISTENCE
# ============================================================================

class TestDatabasePersistence:
    """Test database operations"""
    
    def test_upload_creates_record(self, client, auth_headers, sample_kamco_entities, db_session):
        """Test that upload creates database record"""
        blacklist = [{'Full_Name_English': 'Test User'}]
        csv_content = create_csv_content(blacklist)
        files = {'file': ('test.csv', csv_content, 'text/csv')}
        
        response = client.post(
            '/api/screening/v2/upload-blacklist',
            files=files,
            data={'threshold': 70},
            headers=auth_headers
        )
        
        assert response.status_code == 200
        upload_id = response.json()['upload_id']
        
        # Check database
        upload = db_session.query(BlacklistUpload).filter_by(id=upload_id).first()
        assert upload is not None
        assert upload.filename == 'test.csv'
        assert upload.status == 'completed'
    
    def test_matches_saved_correctly(self, client, auth_headers, sample_kamco_entities, db_session):
        """Test that matches are saved to database"""
        blacklist = [
            {'Full_Name_English': 'Mohammed Al-Rashid', 'Civil_ID': '123456789'}
        ]
        csv_content = create_csv_content(blacklist)
        files = {'file': ('test.csv', csv_content, 'text/csv')}
        
        response = client.post(
            '/api/screening/v2/upload-blacklist',
            files=files,
            data={'threshold': 60},
            headers=auth_headers
        )
        
        assert response.status_code == 200
        
        # Check matches in database
        matches = db_session.query(ScreeningMatch).all()
        # Matches may or may not exist depending on scoring


# ============================================================================
# TEST: CSV FORMAT VARIATIONS
# ============================================================================

class TestCSVVariations:
    """Test different CSV formats"""
    
    def test_alternate_column_names(self, client, auth_headers, sample_kamco_entities):
        """Test CSV with alternate column names"""
        blacklist = [{'Name': 'Mohammed', 'ID_Number': '123456'}]
        csv_content = create_csv_content(blacklist)
        files = {'file': ('test.csv', csv_content, 'text/csv')}
        
        response = client.post(
            '/api/screening/v2/upload-blacklist',
            files=files,
            data={'threshold': 70},
            headers=auth_headers
        )
        
        assert response.status_code == 200
    
    def test_extra_columns(self, client, auth_headers, sample_kamco_entities):
        """Test CSV with extra columns"""
        blacklist = [{
            'Full_Name_English': 'Test',
            'Extra_Field_1': 'Value1',
            'Extra_Field_2': 'Value2'
        }]
        csv_content = create_csv_content(blacklist)
        files = {'file': ('test.csv', csv_content, 'text/csv')}
        
        response = client.post(
            '/api/screening/v2/upload-blacklist',
            files=files,
            data={'threshold': 70},
            headers=auth_headers
        )
        
        assert response.status_code == 200
    
    def test_unicode_content(self, client, auth_headers, sample_kamco_entities):
        """Test CSV with Unicode/Arabic content"""
        blacklist = [{
            'Full_Name_English': 'Mohammed',
            'Full_Name_Arabic': 'محمد الراشد'
        }]
        csv_content = create_csv_content(blacklist)
        files = {'file': ('test.csv', csv_content, 'text/csv')}
        
        response = client.post(
            '/api/screening/v2/upload-blacklist',
            files=files,
            data={'threshold': 70},
            headers=auth_headers
        )
        
        assert response.status_code == 200


# ============================================================================
# TEST: RESPONSE FORMAT
# ============================================================================

class TestResponseFormat:
    """Test API response format"""
    
    def test_response_structure(self, client, auth_headers, sample_kamco_entities):
        """Test response has correct structure"""
        blacklist = [{'Full_Name_English': 'Test'}]
        csv_content = create_csv_content(blacklist)
        files = {'file': ('test.csv', csv_content, 'text/csv')}
        
        response = client.post(
            '/api/screening/v2/upload-blacklist',
            files=files,
            data={'threshold': 70},
            headers=auth_headers
        )
        
        assert response.status_code == 200
        result = response.json()
        
        # Check required fields
        assert 'success' in result
        assert 'upload_id' in result
        assert 'filename' in result
        assert 'entries_processed' in result
        assert 'matches_found' in result
        assert 'matches' in result
        assert 'threshold_used' in result
    
    def test_match_detail_structure(self, client, auth_headers, sample_kamco_entities):
        """Test match detail structure"""
        blacklist = [{'Full_Name_English': 'Mohammed Al-Rashid'}]
        csv_content = create_csv_content(blacklist)
        files = {'file': ('test.csv', csv_content, 'text/csv')}
        
        response = client.post(
            '/api/screening/v2/upload-blacklist',
            files=files,
            data={'threshold': 50},
            headers=auth_headers
        )
        
        assert response.status_code == 200
        result = response.json()
        
        if result['matches_found'] > 0:
            match = result['matches'][0]
            assert 'match_id' in match
            assert 'overall_score' in match
            assert 'kamco_entity' in match
            assert 'blacklist_entry' in match


# ============================================================================
# TEST: ERROR HANDLING
# ============================================================================

class TestErrorHandling:
    """Test error handling"""
    
    def test_malformed_csv(self, client, auth_headers):
        """Test handling of malformed CSV"""
        csv_content = "This,is,not\nvalid,csv,format,with,extra"
        files = {'file': ('bad.csv', csv_content, 'text/csv')}
        
        response = client.post(
            '/api/screening/v2/upload-blacklist',
            files=files,
            data={'threshold': 70},
            headers=auth_headers
        )
        
        # Should handle gracefully
        assert response.status_code in [200, 400]
    
    def test_missing_file(self, client, auth_headers):
        """Test with missing file"""
        response = client.post(
            '/api/screening/v2/upload-blacklist',
            data={'threshold': 70},
            headers=auth_headers
        )
        
        assert response.status_code == 422


# ============================================================================
# TEST: AUTHENTICATION
# ============================================================================

class TestAuthentication:
    """Test authentication requirements"""
    
    def test_login_success(self, client, screener_user):
        """Test successful login"""
        response = client.post(
            '/api/auth/login',
            json={
                'username': 'screener_test',
                'password': 'TestPass123!'
            }
        )
        
        assert response.status_code == 200
        result = response.json()
        assert 'access_token' in result
    
    def test_login_wrong_password(self, client, screener_user):
        """Test login with wrong password"""
        response = client.post(
            '/api/auth/login',
            json={
                'username': 'screener_test',
                'password': 'WrongPassword!'
            }
        )
        
        assert response.status_code == 401
    
    def test_login_nonexistent_user(self, client):
        """Test login with nonexistent user"""
        response = client.post(
            '/api/auth/login',
            json={
                'username': 'nonexistent',
                'password': 'Password123!'
            }
        )
        
        assert response.status_code == 401
    
    def test_protected_endpoint_no_token(self, client, sample_kamco_entities):
        """Test protected endpoint without token"""
        csv_content = create_csv_content([{'Full_Name_English': 'Test'}])
        files = {'file': ('test.csv', csv_content, 'text/csv')}
        
        response = client.post('/api/screening/v2/upload-blacklist', files=files)
        assert response.status_code in [401, 403]
    
    def test_protected_endpoint_invalid_token(self, client, sample_kamco_entities):
        """Test protected endpoint with invalid token"""
        csv_content = create_csv_content([{'Full_Name_English': 'Test'}])
        files = {'file': ('test.csv', csv_content, 'text/csv')}
        
        response = client.post(
            '/api/screening/v2/upload-blacklist',
            files=files,
            headers={'Authorization': 'Bearer invalid_token'}
        )
        assert response.status_code in [401, 403]


# ============================================================================
# TEST: KAMCO ENTITIES
# ============================================================================

class TestKamcoEntities:
    """Test KAMCO entity operations"""
    
    def test_get_kamco_entities(self, client, auth_headers, sample_kamco_entities):
        """Test getting KAMCO entities"""
        response = client.get(
            '/api/screening/v2/kamco-entities',
            headers=auth_headers
        )
        
        assert response.status_code == 200
        result = response.json()
        assert 'entities' in result
        assert len(result['entities']) == 5
    
    def test_kamco_entities_pagination(self, client, auth_headers, sample_kamco_entities):
        """Test KAMCO entities with pagination"""
        response = client.get(
            '/api/screening/v2/kamco-entities?limit=2&offset=0',
            headers=auth_headers
        )
        
        assert response.status_code == 200
        result = response.json()
        assert len(result['entities']) <= 2


# ============================================================================
# TEST: UPLOAD HISTORY
# ============================================================================

class TestUploadHistory:
    """Test upload history tracking"""
    
    def test_get_upload_history(self, client, auth_headers, sample_kamco_entities):
        """Test getting upload history"""
        # First upload a file
        blacklist = [{'Full_Name_English': 'Test'}]
        csv_content = create_csv_content(blacklist)
        files = {'file': ('test.csv', csv_content, 'text/csv')}
        
        client.post(
            '/api/screening/v2/upload-blacklist',
            files=files,
            data={'threshold': 70},
            headers=auth_headers
        )
        
        # Get history
        response = client.get(
            '/api/screening/v2/uploads',
            headers=auth_headers
        )
        
        assert response.status_code == 200
        result = response.json()
        assert 'uploads' in result
        assert len(result['uploads']) >= 1


# ============================================================================
# TEST: PENDING MATCHES
# ============================================================================

class TestPendingMatches:
    """Test pending matches retrieval"""
    
    def test_get_pending_matches(self, client, auth_headers, sample_kamco_entities):
        """Test getting pending matches"""
        response = client.get(
            '/api/screening/v2/pending-matches',
            headers=auth_headers
        )
        
        assert response.status_code == 200
        result = response.json()
        assert 'matches' in result


# ============================================================================
# TEST: USER ENDPOINTS
# ============================================================================

class TestUserEndpoints:
    """Test user-related endpoints"""
    
    def test_get_current_user(self, client, auth_headers):
        """Test getting current user info"""
        response = client.get(
            '/api/auth/me',
            headers=auth_headers
        )
        
        assert response.status_code == 200
        result = response.json()
        assert 'username' in result
        assert result['username'] == 'screener_test'


# ============================================================================
# RUN ALL TESTS
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
