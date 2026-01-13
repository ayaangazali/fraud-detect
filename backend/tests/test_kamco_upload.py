"""
Comprehensive Tests for Kamco Upload System
Ensures the system never fails with proper error handling
"""
import pytest
import asyncio
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app
from database.connection import Base, get_db
from models.auth import User
from utils.auth import hash_password

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_kamco.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


# Test Data
SAMPLE_CSV_CONTENT = """Customer_ID,Name_English,Name_Arabic,Entity_Type,Entity_Category,ID_Number,Registration_Date,Contact_Person,Type_Individual_Corporate,Nationality,Country_of_Origin,Industry_Sector,Risk_Level,Account_Status,Phone,Email,Address,Notes
KCLI-TEST-001,Test Client One,عميل تجريبي واحد,Client,Individual,TEST123,2020-01-01,Test Person,Individual,Kuwaiti,Kuwait,Finance,Medium,Active,+965-1234-5678,test@email.com,"Test Address",Test notes
KVEN-TEST-001,Test Vendor One,بائع تجريبي واحد,Vendor,Corporate,TEST456,2021-02-15,Vendor Person,Corporate,Kuwaiti,Kuwait,IT,Low,Active,+965-9876-5432,vendor@email.com,"Vendor Address",Vendor notes
KSTA-TEST-001,Test Staff One,موظف تجريبي واحد,Staff,Individual,EMP001,2019-06-20,Staff Person,Individual,Kuwaiti,Kuwait,HR,N/A,Active,+965-5555-5555,staff@email.com,"Staff Address",Staff notes
KOTH-TEST-001,Test Other One,آخر تجريبي واحد,Other,Government,GOV001,2018-12-25,Other Person,Corporate,N/A,Kuwait,Government,N/A,Active,+965-7777-7777,other@email.com,"Other Address",Other notes"""

INVALID_CSV_MISSING_REQUIRED = """Customer_ID,Name_English
KCLI-TEST-002,Test Client Two"""

INVALID_CSV_WRONG_ENTITY_TYPE = """Customer_ID,Name_English,Name_Arabic,Entity_Type
KCLI-TEST-003,Test Client Three,عميل تجريبي ثلاثة,InvalidType"""

MALFORMED_CSV = """Customer_ID,Name_English,Entity_Type
KCLI-TEST-004,"Unclosed quote,Client"""


class TestKamcoUploadSystem:
    """Comprehensive test suite for Kamco upload system"""
    
    @classmethod
    def setup_class(cls):
        """Setup test database and test user"""
        # Remove old test database if it exists
        if os.path.exists("test_kamco.db"):
            os.remove("test_kamco.db")
        
        # Create all tables fresh
        Base.metadata.create_all(bind=engine)
        
        # Create test user
        db = TestingSessionLocal()
        try:
            test_user = User(
                username="test_screener",
                email="test@kamco.com",
                hashed_password=hash_password("Test123!"),
                role="screener",
                is_active=True
            )
            db.add(test_user)
            db.commit()
        except Exception as e:
            db.rollback()
            print(f"Warning: Could not create test user: {e}")
        finally:
            db.close()
    
    @classmethod
    def teardown_class(cls):
        """Cleanup test database"""
        Base.metadata.drop_all(bind=engine)
        if os.path.exists("test_kamco.db"):
            try:
                os.remove("test_kamco.db")
            except Exception as e:
                print(f"Warning: Could not remove test database: {e}")
    
    def get_auth_token(self):
        """Get authentication token for tests"""
        response = client.post(
            "/api/auth/login",
            json={"username": "test_screener", "password": "Test123!"}
        )
        assert response.status_code == 200
        return response.json()["access_token"]
    
    # ========================================================================
    # TEST 1: Valid CSV Upload
    # ========================================================================
    def test_upload_valid_csv(self):
        """Test uploading a valid CSV file"""
        token = self.get_auth_token()
        
        response = client.post(
            "/api/upload/kamco-entities",
            files={"file": ("test_entities.csv", SAMPLE_CSV_CONTENT, "text/csv")},
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert data["data"]["summary"]["stored_entities"] == 4
        assert data["data"]["summary"]["by_type"]["clients"] == 1
        assert data["data"]["summary"]["by_type"]["vendors"] == 1
        assert data["data"]["summary"]["by_type"]["staff"] == 1
        assert data["data"]["summary"]["by_type"]["others"] == 1
    
    # ========================================================================
    # TEST 2: Invalid File Type
    # ========================================================================
    def test_upload_invalid_file_type(self):
        """Test uploading non-CSV file"""
        token = self.get_auth_token()
        
        response = client.post(
            "/api/upload/kamco-entities",
            files={"file": ("test.txt", "Not a CSV", "text/plain")},
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 400
        assert "Invalid file type" in response.json()["detail"]
    
    # ========================================================================
    # TEST 3: Missing Required Columns
    # ========================================================================
    def test_upload_missing_required_columns(self):
        """Test uploading CSV with missing required columns"""
        token = self.get_auth_token()
        
        response = client.post(
            "/api/upload/kamco-entities",
            files={"file": ("invalid.csv", INVALID_CSV_MISSING_REQUIRED, "text/csv")},
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "Missing required columns" in str(data["detail"])
    
    # ========================================================================
    # TEST 4: Invalid Entity Type
    # ========================================================================
    def test_upload_invalid_entity_type(self):
        """Test uploading CSV with invalid entity type"""
        token = self.get_auth_token()
        
        response = client.post(
            "/api/upload/kamco-entities",
            files={"file": ("invalid_type.csv", INVALID_CSV_WRONG_ENTITY_TYPE, "text/csv")},
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # Should still succeed but with validation errors
        assert response.status_code in [200, 400]
        if response.status_code == 200:
            data = response.json()
            assert len(data["data"]["errors"]) > 0
    
    # ========================================================================
    # TEST 5: Duplicate Upload Prevention
    # ========================================================================
    def test_duplicate_upload_prevention(self):
        """Test that duplicate entities are skipped"""
        token = self.get_auth_token()
        
        # Upload first time
        response1 = client.post(
            "/api/upload/kamco-entities",
            files={"file": ("entities1.csv", SAMPLE_CSV_CONTENT, "text/csv")},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response1.status_code == 200
        
        # Upload again with same data
        response2 = client.post(
            "/api/upload/kamco-entities",
            files={"file": ("entities2.csv", SAMPLE_CSV_CONTENT, "text/csv")},
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response2.status_code == 200
        data = response2.json()
        # Should have errors about duplicates
        assert len(data["data"]["errors"]) > 0
        assert any("already exists" in error for error in data["data"]["errors"])
    
    # ========================================================================
    # TEST 6: Empty CSV File
    # ========================================================================
    def test_upload_empty_csv(self):
        """Test uploading empty CSV file"""
        token = self.get_auth_token()
        
        empty_csv = "Customer_ID,Name_English,Name_Arabic,Entity_Type\n"
        
        response = client.post(
            "/api/upload/kamco-entities",
            files={"file": ("empty.csv", empty_csv, "text/csv")},
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 400
        assert "No valid entities" in response.json()["detail"]["message"]
    
    # ========================================================================
    # TEST 7: Unauthenticated Access
    # ========================================================================
    def test_upload_without_authentication(self):
        """Test uploading without authentication token"""
        response = client.post(
            "/api/upload/kamco-entities",
            files={"file": ("test.csv", SAMPLE_CSV_CONTENT, "text/csv")}
        )
        
        assert response.status_code == 403  # Forbidden
    
    # ========================================================================
    # TEST 8: Get Summary Endpoint
    # ========================================================================
    def test_get_summary(self):
        """Test getting Kamco entities summary"""
        token = self.get_auth_token()
        
        response = client.get(
            "/api/upload/kamco-entities/summary",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "total" in data["data"]
        assert "clients" in data["data"]
    
    # ========================================================================
    # TEST 9: UTF-8 with BOM
    # ========================================================================
    def test_upload_utf8_bom(self):
        """Test uploading CSV with UTF-8 BOM"""
        token = self.get_auth_token()
        
        # Add BOM to content
        bom_content = b'\xef\xbb\xbf' + SAMPLE_CSV_CONTENT.encode('utf-8')
        
        response = client.post(
            "/api/upload/kamco-entities",
            files={"file": ("bom_test.csv", bom_content, "text/csv")},
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # Should handle BOM correctly
        assert response.status_code == 200
    
    # ========================================================================
    # TEST 10: Large File Handling
    # ========================================================================
    def test_upload_large_file(self):
        """Test uploading large CSV file (stress test)"""
        token = self.get_auth_token()
        
        # Generate 100 rows
        header = "Customer_ID,Name_English,Name_Arabic,Entity_Type,Entity_Category,ID_Number,Registration_Date,Contact_Person,Type_Individual_Corporate,Nationality,Country_of_Origin,Industry_Sector,Risk_Level,Account_Status,Phone,Email,Address,Notes\n"
        rows = []
        for i in range(100):
            rows.append(f"KCLI-LARGE-{i:03d},Client {i},عميل {i},Client,Individual,ID{i},2020-01-01,Person {i},Individual,Kuwaiti,Kuwait,Finance,Medium,Active,+965-{i:04d}-0000,client{i}@test.com,Address {i},Notes {i}")
        
        large_csv = header + "\n".join(rows)
        
        response = client.post(
            "/api/upload/kamco-entities",
            files={"file": ("large.csv", large_csv, "text/csv")},
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["summary"]["stored_entities"] > 0


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
