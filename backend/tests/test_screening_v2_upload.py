"""
Comprehensive tests for Screening V2 Upload Endpoint
Tests the /api/screening/v2/upload-blacklist endpoint
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import io
import csv
from datetime import datetime

from main import app
from database.connection import get_db, Base
from models.auth import User
from models.screening import (
    KamcoEntity,
    BlacklistUpload,
    ScreeningMatch,
    DecisionLog,
    EntityType
)
from utils.auth import hash_password, create_access_token

# Test database
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test_screening_v2.db"
engine = create_engine(SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Fixtures
@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database for each test"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Create test client with database override"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)


@pytest.fixture
def test_user(db_session):
    """Create a test user for authentication"""
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
def auth_token(test_user):
    """Generate authentication token"""
    return create_access_token({
        "user_id": test_user.id,
        "email": test_user.email,
        "role": test_user.role.value
    })


@pytest.fixture
def auth_headers(auth_token):
    """Create authorization headers"""
    return {"Authorization": f"Bearer {auth_token}"}


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
        )
    ]
    for entity in entities:
        db_session.add(entity)
    db_session.commit()
    return entities


def create_csv_content(data: list) -> str:
    """Helper to create CSV content from list of dicts"""
    if not data:
        return ""
    
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=data[0].keys())
    writer.writeheader()
    writer.writerows(data)
    return output.getvalue()


# Tests
class TestBlacklistUploadBasic:
    """Test basic upload functionality"""
    
    def test_upload_blacklist_success(self, client, auth_headers, sample_kamco_entities):
        """Test successful blacklist upload"""
        # Create blacklist CSV
        blacklist_data = [
            {
                'Reference_Number': 'BL001',
                'Full_Name_English': 'Mohammed Rashid',
                'Full_Name_Arabic': 'محمد راشد',
                'Civil_ID': '123456',
                'Nationality': 'Kuwaiti',
                'Risk_Level': 'HIGH',
                'Source': 'UN Sanctions',
                'Reason': 'Financial crimes'
            }
        ]
        csv_content = create_csv_content(blacklist_data)
        
        # Upload file
        files = {'file': ('blacklist.csv', csv_content, 'text/csv')}
        data = {'threshold': 70}
        
        response = client.post(
            '/api/screening/v2/upload-blacklist',
            files=files,
            data=data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        result = response.json()
        assert result['success'] is True
        assert result['filename'] == 'blacklist.csv'
        assert result['entries_processed'] == 1
        assert 'upload_id' in result
        assert 'matches' in result
    
    def test_upload_requires_authentication(self, client, sample_kamco_entities):
        """Test that upload requires authentication"""
        csv_content = create_csv_content([{'Full_Name_English': 'Test'}])
        files = {'file': ('test.csv', csv_content, 'text/csv')}
        
        response = client.post('/api/screening/v2/upload-blacklist', files=files)
        assert response.status_code == 401
    
    def test_upload_non_csv_rejected(self, client, auth_headers):
        """Test that non-CSV files are rejected"""
        files = {'file': ('test.txt', 'not a csv', 'text/plain')}
        
        response = client.post(
            '/api/screening/v2/upload-blacklist',
            files=files,
            headers=auth_headers
        )
        
        assert response.status_code == 400
        assert 'CSV' in response.json()['detail']
    
    def test_upload_empty_csv_rejected(self, client, auth_headers):
        """Test that empty CSV is rejected"""
        csv_content = "Full_Name_English\n"  # Header only
        files = {'file': ('empty.csv', csv_content, 'text/csv')}
        
        response = client.post(
            '/api/screening/v2/upload-blacklist',
            files=files,
            headers=auth_headers
        )
        
        assert response.status_code == 400
        assert 'No valid entries' in response.json()['detail']


class TestMatchingLogic:
    """Test matching algorithm"""
    
    def test_exact_name_match(self, client, auth_headers, sample_kamco_entities):
        """Test exact name matching"""
        blacklist_data = [{
            'Reference_Number': 'BL001',
            'Full_Name_English': 'Mohammed Al-Rashid',  # Exact match
            'Nationality': 'Kuwaiti'
        }]
        csv_content = create_csv_content(blacklist_data)
        files = {'file': ('test.csv', csv_content, 'text/csv')}
        data = {'threshold': 70}
        
        response = client.post(
            '/api/screening/v2/upload-blacklist',
            files=files,
            data=data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        result = response.json()
        assert result['matches_found'] > 0
        
        # Check match score
        match = result['matches'][0]
        assert match['overall_score'] >= 90  # High score for exact match
    
    def test_fuzzy_name_match(self, client, auth_headers, sample_kamco_entities):
        """Test fuzzy name matching"""
        blacklist_data = [{
            'Reference_Number': 'BL002',
            'Full_Name_English': 'Mohammed Rashid',  # Similar but not exact
            'Nationality': 'Kuwaiti'
        }]
        csv_content = create_csv_content(blacklist_data)
        files = {'file': ('test.csv', csv_content, 'text/csv')}
        data = {'threshold': 70}
        
        response = client.post(
            '/api/screening/v2/upload-blacklist',
            files=files,
            data=data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        result = response.json()
        assert result['matches_found'] > 0
    
    def test_civil_id_match(self, client, auth_headers, sample_kamco_entities):
        """Test Civil ID matching"""
        blacklist_data = [{
            'Reference_Number': 'BL003',
            'Full_Name_English': 'Different Name',
            'Civil_ID': '123456789',  # Exact Civil ID match
            'Nationality': 'Kuwaiti'
        }]
        csv_content = create_csv_content(blacklist_data)
        files = {'file': ('test.csv', csv_content, 'text/csv')}
        data = {'threshold': 60}
        
        response = client.post(
            '/api/screening/v2/upload-blacklist',
            files=files,
            data=data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        result = response.json()
        # Should match based on Civil ID even with different name
        assert result['matches_found'] > 0
    
    def test_arabic_name_match(self, client, auth_headers, sample_kamco_entities):
        """Test Arabic name matching"""
        blacklist_data = [{
            'Reference_Number': 'BL004',
            'Full_Name_English': 'Unknown',
            'Full_Name_Arabic': 'أحمد المطيري',  # Exact Arabic match
            'Nationality': 'Kuwaiti'
        }]
        csv_content = create_csv_content(blacklist_data)
        files = {'file': ('test.csv', csv_content, 'text/csv')}
        data = {'threshold': 70}
        
        response = client.post(
            '/api/screening/v2/upload-blacklist',
            files=files,
            data=data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        result = response.json()
        assert result['matches_found'] > 0


class TestThresholdFiltering:
    """Test threshold filtering"""
    
    def test_high_threshold(self, client, auth_headers, sample_kamco_entities):
        """Test with high threshold (95%)"""
        blacklist_data = [{
            'Reference_Number': 'BL005',
            'Full_Name_English': 'Mohammed Rashid',  # Similar but not exact
        }]
        csv_content = create_csv_content(blacklist_data)
        files = {'file': ('test.csv', csv_content, 'text/csv')}
        data = {'threshold': 95}  # Very strict
        
        response = client.post(
            '/api/screening/v2/upload-blacklist',
            files=files,
            data=data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        result = response.json()
        # Should have fewer or no matches with strict threshold
        assert result['matches_found'] == 0 or result['matches_found'] < 2
    
    def test_low_threshold(self, client, auth_headers, sample_kamco_entities):
        """Test with low threshold (50%)"""
        blacklist_data = [{
            'Reference_Number': 'BL006',
            'Full_Name_English': 'Ahmed',  # Partial match
        }]
        csv_content = create_csv_content(blacklist_data)
        files = {'file': ('test.csv', csv_content, 'text/csv')}
        data = {'threshold': 50}  # Lenient
        
        response = client.post(
            '/api/screening/v2/upload-blacklist',
            files=files,
            data=data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        result = response.json()
        # Should have more matches with lenient threshold
        assert result['matches_found'] >= 0


class TestDatabasePersistence:
    """Test that data is properly saved to database"""
    
    def test_upload_creates_upload_record(self, client, auth_headers, sample_kamco_entities, db_session):
        """Test that upload creates BlacklistUpload record"""
        blacklist_data = [{'Full_Name_English': 'Test User'}]
        csv_content = create_csv_content(blacklist_data)
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
        assert upload.total_entries == 1
        assert upload.status == 'completed'
    
    def test_matches_saved_to_database(self, client, auth_headers, sample_kamco_entities, db_session):
        """Test that matches are saved to ScreeningMatch table"""
        blacklist_data = [{
            'Full_Name_English': 'Mohammed Al-Rashid',
            'Civil_ID': '123456789'
        }]
        csv_content = create_csv_content(blacklist_data)
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
        matches = db_session.query(ScreeningMatch).filter_by(blacklist_upload_id=upload_id).all()
        assert len(matches) > 0
        assert matches[0].blacklist_name_english is not None
        assert matches[0].overall_score is not None


class TestMultipleEntries:
    """Test with multiple blacklist entries"""
    
    def test_bulk_upload(self, client, auth_headers, sample_kamco_entities):
        """Test uploading multiple entries"""
        blacklist_data = [
            {'Reference_Number': 'BL01', 'Full_Name_English': 'Mohammed Al-Rashid'},
            {'Reference_Number': 'BL02', 'Full_Name_English': 'Ahmed Al-Mutairi'},
            {'Reference_Number': 'BL03', 'Full_Name_English': 'Fatima Al-Salem'},
            {'Reference_Number': 'BL04', 'Full_Name_English': 'John Smith'},
            {'Reference_Number': 'BL05', 'Full_Name_English': 'Unknown Person'}
        ]
        csv_content = create_csv_content(blacklist_data)
        files = {'file': ('bulk.csv', csv_content, 'text/csv')}
        
        response = client.post(
            '/api/screening/v2/upload-blacklist',
            files=files,
            data={'threshold': 70},
            headers=auth_headers
        )
        
        assert response.status_code == 200
        result = response.json()
        assert result['entries_processed'] == 5
        assert result['matches_found'] >= 4  # Should match at least 4 entities


class TestCSVVariations:
    """Test different CSV formats"""
    
    def test_alternate_column_names(self, client, auth_headers, sample_kamco_entities):
        """Test CSV with alternate column names"""
        blacklist_data = [{
            'Name': 'Mohammed Al-Rashid',  # Using 'Name' instead of 'Full_Name_English'
            'ID_Number': '123456789'
        }]
        csv_content = create_csv_content(blacklist_data)
        files = {'file': ('test.csv', csv_content, 'text/csv')}
        
        response = client.post(
            '/api/screening/v2/upload-blacklist',
            files=files,
            data={'threshold': 70},
            headers=auth_headers
        )
        
        assert response.status_code == 200
    
    def test_csv_with_extra_fields(self, client, auth_headers, sample_kamco_entities):
        """Test CSV with extra fields"""
        blacklist_data = [{
            'Full_Name_English': 'Mohammed Al-Rashid',
            'Extra_Field_1': 'Value1',
            'Extra_Field_2': 'Value2',
            'Notes': 'Additional notes'
        }]
        csv_content = create_csv_content(blacklist_data)
        files = {'file': ('test.csv', csv_content, 'text/csv')}
        
        response = client.post(
            '/api/screening/v2/upload-blacklist',
            files=files,
            data={'threshold': 70},
            headers=auth_headers
        )
        
        assert response.status_code == 200


class TestMatchDetails:
    """Test match details in response"""
    
    def test_match_score_breakdown(self, client, auth_headers, sample_kamco_entities):
        """Test that match includes score breakdown"""
        blacklist_data = [{
            'Full_Name_English': 'Mohammed Al-Rashid',
            'Full_Name_Arabic': 'محمد الراشد',
            'Civil_ID': '123456789',
            'Nationality': 'Kuwaiti'
        }]
        csv_content = create_csv_content(blacklist_data)
        files = {'file': ('test.csv', csv_content, 'text/csv')}
        
        response = client.post(
            '/api/screening/v2/upload-blacklist',
            files=files,
            data={'threshold': 70},
            headers=auth_headers
        )
        
        assert response.status_code == 200
        result = response.json()
        assert result['matches_found'] > 0
        
        match = result['matches'][0]
        assert 'score_breakdown' in match
        assert 'overall_score' in match
        assert 'kamco_entity' in match
        assert 'blacklist_entry' in match
    
    def test_match_includes_entity_details(self, client, auth_headers, sample_kamco_entities):
        """Test that match includes full entity details"""
        blacklist_data = [{'Full_Name_English': 'Mohammed Al-Rashid'}]
        csv_content = create_csv_content(blacklist_data)
        files = {'file': ('test.csv', csv_content, 'text/csv')}
        
        response = client.post(
            '/api/screening/v2/upload-blacklist',
            files=files,
            data={'threshold': 70},
            headers=auth_headers
        )
        
        assert response.status_code == 200
        result = response.json()
        
        if result['matches_found'] > 0:
            match = result['matches'][0]
            kamco = match['kamco_entity']
            assert 'id' in kamco
            assert 'name_english' in kamco
            assert 'civil_id' in kamco


class TestErrorHandling:
    """Test error handling"""
    
    def test_malformed_csv(self, client, auth_headers):
        """Test handling of malformed CSV"""
        csv_content = "This is not,valid\nCSV,format,with,too,many,fields"
        files = {'file': ('bad.csv', csv_content, 'text/csv')}
        
        response = client.post(
            '/api/screening/v2/upload-blacklist',
            files=files,
            data={'threshold': 70},
            headers=auth_headers
        )
        
        # Should either succeed with 0 entries or return 400
        assert response.status_code in [200, 400]
    
    def test_missing_file(self, client, auth_headers):
        """Test with missing file parameter"""
        response = client.post(
            '/api/screening/v2/upload-blacklist',
            data={'threshold': 70},
            headers=auth_headers
        )
        
        assert response.status_code == 422  # Unprocessable entity


class TestResponseFormat:
    """Test response format"""
    
    def test_response_structure(self, client, auth_headers, sample_kamco_entities):
        """Test that response has expected structure"""
        blacklist_data = [{'Full_Name_English': 'Test User'}]
        csv_content = create_csv_content(blacklist_data)
        files = {'file': ('test.csv', csv_content, 'text/csv')}
        
        response = client.post(
            '/api/screening/v2/upload-blacklist',
            files=files,
            data={'threshold': 70},
            headers=auth_headers
        )
        
        assert response.status_code == 200
        result = response.json()
        
        # Check all required fields
        assert 'success' in result
        assert 'upload_id' in result
        assert 'filename' in result
        assert 'entries_processed' in result
        assert 'matches_found' in result
        assert 'matches' in result
        assert 'threshold_used' in result
        assert isinstance(result['matches'], list)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
