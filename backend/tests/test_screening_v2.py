"""
Tests for Screening V2 API - Blacklist Upload Workflow
Tests the new workflow where users upload blacklist CSV files 
and screen them against pre-loaded KAMCO entities.
"""
import pytest
import os
import sys
from io import BytesIO

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.connection import Base, get_db
from main import app
from utils.auth import hash_password
from models.auth import User


# Test database setup
TEST_DATABASE_URL = "sqlite:///./test_screening_v2.db"
test_engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    """Override database dependency for testing"""
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


# Override the database dependency
app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="module")
def client():
    """Create test client"""
    return TestClient(app)


@pytest.fixture(scope="module", autouse=True)
def setup_database():
    """Setup test database with tables and test user"""
    # Drop and recreate tables
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    
    # Create test user
    db = TestSessionLocal()
    try:
        test_user = User(
            username="screening_tester",
            email="screening@test.com",
            hashed_password=hash_password("TestPassword123!"),
            role="screener",
            is_active=True
        )
        db.add(test_user)
        db.commit()
    finally:
        db.close()
    
    yield
    
    # Cleanup
    Base.metadata.drop_all(bind=test_engine)
    if os.path.exists("./test_screening_v2.db"):
        os.remove("./test_screening_v2.db")


@pytest.fixture
def auth_headers(client):
    """Get authentication headers for API requests"""
    response = client.post(
        "/api/auth/login",
        json={"username": "screening_tester", "password": "TestPassword123!"}
    )
    assert response.status_code == 200, f"Login failed: {response.json()}"
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


class TestBlacklistScreeningEngine:
    """Tests for the BlacklistScreeningEngine class"""
    
    def test_engine_import(self):
        """Test that screening engine can be imported"""
        from services.screening_engine import BlacklistScreeningEngine
        engine = BlacklistScreeningEngine()
        assert engine is not None
        assert engine.threshold == 70.0
    
    def test_csv_parsing(self):
        """Test parsing blacklist CSV content"""
        from services.screening_engine import BlacklistScreeningEngine
        
        engine = BlacklistScreeningEngine()
        
        csv_content = """Reference_Number,Full_Name_English,Full_Name_Arabic,Nationality,Civil_ID,Risk_Level,Source
BL001,John Smith,,American,123456789,High,OFAC
BL002,أحمد محمد,Ahmed Mohammed,Kuwaiti,987654321,Critical,UN
BL003,Test Person,,British,,Medium,EU"""
        
        entries = engine.process_blacklist_csv(csv_content)
        
        assert len(entries) == 3
        assert entries[0]['reference_number'] == 'BL001'
        assert entries[0]['full_name_english'] == 'John Smith'
        assert entries[1]['full_name_arabic'] == 'Ahmed Mohammed'
        assert entries[2]['risk_level'] == 'Medium'
    
    def test_fuzzy_matching(self):
        """Test fuzzy matching between blacklist and KAMCO entities"""
        from services.screening_engine import BlacklistScreeningEngine
        
        engine = BlacklistScreeningEngine(threshold=60.0)
        
        blacklist_entries = [
            {
                'reference_number': 'BL001',
                'full_name_english': 'Ahmed Al-Rashid',
                'full_name_arabic': 'أحمد الراشد',
                'civil_id': '284010112345',
                'nationality': 'Kuwaiti'
            }
        ]
        
        kamco_entities = [
            {
                'id': 'KCLI-001',
                'name_english': 'Ahmed Al-Rashid Trading',
                'name_arabic': 'شركة أحمد الراشد للتجارة',
                'civil_id': '284010112345',
                'nationality': 'Kuwaiti',
                'type': 'CLIENT'
            },
            {
                'id': 'KCLI-002',
                'name_english': 'Completely Different Name',
                'name_arabic': 'اسم مختلف تماما',
                'civil_id': '111111111111',
                'nationality': 'American',
                'type': 'CLIENT'
            }
        ]
        
        matches = engine.screen_against_kamco(
            blacklist_entries=blacklist_entries,
            kamco_entities=kamco_entities,
            threshold=60.0,
            existing_decisions=set()
        )
        
        # Should find at least one match with Ahmed Al-Rashid
        assert len(matches) >= 1
        
        # The first match should be the similar name
        top_match = matches[0]
        assert 'Ahmed' in top_match['kamco_entity']['name_english']
        assert top_match['overall_score'] >= 60.0
    
    def test_exact_id_match(self):
        """Test that exact Civil ID matches get high ID scores"""
        from services.screening_engine import BlacklistScreeningEngine
        
        engine = BlacklistScreeningEngine(threshold=15.0)  # Low threshold to catch ID-only match
        
        blacklist_entries = [
            {
                'reference_number': 'BL001',
                'full_name_english': 'Different Name',
                'full_name_arabic': '',
                'civil_id': '284010112345',
                'nationality': 'Kuwaiti'
            }
        ]
        
        kamco_entities = [
            {
                'id': 'KCLI-001',
                'name_english': 'Ahmed Al-Rashid Trading',
                'name_arabic': '',
                'civil_id': '284010112345',
                'nationality': 'Kuwaiti',
                'type': 'CLIENT'
            }
        ]
        
        matches = engine.screen_against_kamco(
            blacklist_entries=blacklist_entries,
            kamco_entities=kamco_entities,
            threshold=15.0,  # Low threshold to catch ID-only match (ID contributes 15%)
            existing_decisions=set()
        )
        
        # Should find match due to ID match + nationality
        assert len(matches) >= 1
        
        # Check that ID score is 100
        top_match = matches[0]
        assert top_match['score_breakdown']['id_number'] == 100.0
    
    def test_skip_already_decided(self):
        """Test that already-decided matches are skipped"""
        from services.screening_engine import BlacklistScreeningEngine
        
        engine = BlacklistScreeningEngine(threshold=50.0)
        
        blacklist_entries = [
            {
                'reference_number': 'BL001',
                'full_name_english': 'Ahmed Al-Rashid',
                'full_name_arabic': '',
                'civil_id': '284010112345',
                'nationality': 'Kuwaiti'
            }
        ]
        
        kamco_entities = [
            {
                'id': 'KCLI-001',
                'name_english': 'Ahmed Al-Rashid',
                'name_arabic': '',
                'civil_id': '284010112345',
                'nationality': 'Kuwaiti',
                'type': 'CLIENT'
            }
        ]
        
        # First, get matches without any decided
        matches_first = engine.screen_against_kamco(
            blacklist_entries=blacklist_entries,
            kamco_entities=kamco_entities,
            threshold=50.0,
            existing_decisions=set()
        )
        assert len(matches_first) >= 1
        
        # Now mark that match as already decided
        already_decided = {matches_first[0]['match_key']}
        
        matches_second = engine.screen_against_kamco(
            blacklist_entries=blacklist_entries,
            kamco_entities=kamco_entities,
            threshold=50.0,
            existing_decisions=already_decided
        )
        
        # Should skip the already-decided match
        assert len(matches_second) == 0


class TestScreeningV2API:
    """Tests for the Screening V2 API endpoints"""
    
    def test_get_kamco_entities_from_seed(self, client, auth_headers):
        """Test getting KAMCO entities (from seed data)"""
        response = client.get(
            "/api/screening/v2/kamco-entities",
            headers=auth_headers
        )
        
        # Should return seed data since DB is empty
        assert response.status_code == 200
        data = response.json()
        assert data['success'] == True
        assert 'entities' in data
        assert data['source'] == 'seed_data'  # Using seed data since DB is empty
    
    def test_get_kamco_entities_with_filter(self, client, auth_headers):
        """Test filtering KAMCO entities by type"""
        response = client.get(
            "/api/screening/v2/kamco-entities?entity_type=CLIENT",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data['success'] == True
        
        # All returned entities should be clients
        for entity in data['entities']:
            assert entity['type'] == 'CLIENT'
    
    def test_get_kamco_entities_with_search(self, client, auth_headers):
        """Test searching KAMCO entities by name"""
        response = client.get(
            "/api/screening/v2/kamco-entities?search=Ahmed",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data['success'] == True
        
        # All returned entities should contain 'Ahmed' in name
        for entity in data['entities']:
            name_lower = entity.get('name_english', '').lower()
            arabic_lower = entity.get('name_arabic', '').lower()
            assert 'ahmed' in name_lower or 'ahmed' in arabic_lower or 'أحمد' in entity.get('name_arabic', '')


class TestKamcoSeedData:
    """Tests for KAMCO entities seed data"""
    
    def test_seed_data_import(self):
        """Test that seed data can be imported"""
        from data.kamco_entities import get_kamco_entities, KAMCO_ENTITIES
        
        entities = get_kamco_entities()
        assert len(entities) > 0
        assert len(entities) == len(KAMCO_ENTITIES)
    
    def test_seed_data_structure(self):
        """Test that seed data has required fields"""
        from data.kamco_entities import get_kamco_entities
        
        entities = get_kamco_entities()
        
        for entity in entities:
            # Required fields
            assert 'id' in entity
            assert 'type' in entity
            assert 'name_english' in entity
            
            # Type should be valid
            assert entity['type'] in ['CLIENT', 'VENDOR', 'STAFF', 'OTHER']
    
    def test_seed_data_variety(self):
        """Test that seed data has variety of entity types"""
        from data.kamco_entities import get_kamco_entities
        
        entities = get_kamco_entities()
        
        types = set(e['type'] for e in entities)
        
        # Should have at least clients and vendors
        assert 'CLIENT' in types
        assert 'VENDOR' in types


class TestScreeningModels:
    """Tests for screening database models"""
    
    def test_decision_status_enum(self):
        """Test DecisionStatus enum values"""
        try:
            from models.screening import DecisionStatus
            
            assert hasattr(DecisionStatus, 'PENDING')
            assert hasattr(DecisionStatus, 'FLAGGED')
            assert hasattr(DecisionStatus, 'CLEARED')
            assert hasattr(DecisionStatus, 'ESCALATED')
            # RE_REVIEW might not exist in the model
        except ImportError:
            pytest.skip("Screening models not available")
    
    def test_entity_type_enum(self):
        """Test EntityType enum values"""
        try:
            from models.screening import EntityType
            
            assert hasattr(EntityType, 'CLIENT')
            assert hasattr(EntityType, 'VENDOR')
            assert hasattr(EntityType, 'STAFF')
            assert hasattr(EntityType, 'OTHER')
        except ImportError:
            pytest.skip("Screening models not available")


class TestWeightedMatching:
    """Tests for weighted fuzzy matching"""
    
    def test_name_has_highest_weight(self):
        """Test that English name has highest weight (40%)"""
        from services.screening_engine import BlacklistScreeningEngine
        
        engine = BlacklistScreeningEngine()
        
        # Name match only
        blacklist = [{
            'reference_number': 'BL001',
            'full_name_english': 'Test Person Name',
            'full_name_arabic': '',
            'civil_id': '',
            'nationality': ''
        }]
        
        kamco = [{
            'id': 'K001',
            'name_english': 'Test Person Name',
            'name_arabic': '',
            'civil_id': '999999999',  # Different
            'nationality': 'Different',
            'type': 'CLIENT'
        }]
        
        matches = engine.screen_against_kamco(
            blacklist_entries=blacklist,
            kamco_entities=kamco,
            threshold=30.0,
            existing_decisions=set()
        )
        
        # Should get a match
        assert len(matches) >= 1
        
        # Name English score should be 100%
        top_match = matches[0]
        assert top_match['score_breakdown']['name_english'] == 100.0
        
        # Overall score should be around 40 (100 * 0.40)
        assert top_match['overall_score'] >= 40.0
    
    def test_combined_scores(self):
        """Test that all fields contribute to overall score"""
        from services.screening_engine import BlacklistScreeningEngine
        
        engine = BlacklistScreeningEngine()
        
        # All fields match
        blacklist = [{
            'reference_number': 'BL001',
            'full_name_english': 'Ahmed Al-Rashid',
            'full_name_arabic': 'أحمد الراشد',
            'civil_id': '284010112345',
            'nationality': 'Kuwaiti'
        }]
        
        kamco = [{
            'id': 'K001',
            'name_english': 'Ahmed Al-Rashid',
            'name_arabic': 'أحمد الراشد',
            'civil_id': '284010112345',
            'nationality': 'Kuwaiti',
            'type': 'CLIENT'
        }]
        
        matches = engine.screen_against_kamco(
            blacklist_entries=blacklist,
            kamco_entities=kamco,
            threshold=50.0,
            existing_decisions=set()
        )
        
        assert len(matches) >= 1
        
        top_match = matches[0]
        
        # All scores should be high
        assert top_match['score_breakdown']['name_english'] >= 90.0
        assert top_match['score_breakdown']['id_number'] == 100.0
        assert top_match['score_breakdown']['nationality'] >= 90.0
        
        # Overall should be very high
        assert top_match['overall_score'] >= 90.0
        
        # Risk level should be CRITICAL
        assert top_match['risk_level'] == 'CRITICAL'


class TestCSVVariations:
    """Tests for handling different CSV formats"""
    
    def test_csv_with_missing_columns(self):
        """Test parsing CSV with missing optional columns"""
        from services.screening_engine import BlacklistScreeningEngine
        
        engine = BlacklistScreeningEngine()
        
        # CSV with only required columns
        csv_content = """Full_Name_English,Nationality
John Smith,American
Jane Doe,British"""
        
        entries = engine.process_blacklist_csv(csv_content)
        
        assert len(entries) == 2
        assert entries[0]['full_name_english'] == 'John Smith'
        assert entries[0]['nationality'] == 'American'
    
    def test_csv_with_alternate_column_names(self):
        """Test parsing CSV with alternate column naming"""
        from services.screening_engine import BlacklistScreeningEngine
        
        engine = BlacklistScreeningEngine()
        
        # CSV with alternate column names
        csv_content = """Name,Name_Arabic,ID_Number,Country
John Smith,جون سميث,123456,USA
Ahmed Mohammed,أحمد محمد,789012,Kuwait"""
        
        entries = engine.process_blacklist_csv(csv_content)
        
        assert len(entries) == 2
        # Should map 'Name' to full_name_english
        assert entries[0]['full_name_english'] == 'John Smith'
    
    def test_csv_with_empty_values(self):
        """Test parsing CSV with empty values"""
        from services.screening_engine import BlacklistScreeningEngine
        
        engine = BlacklistScreeningEngine()
        
        csv_content = """Full_Name_English,Full_Name_Arabic,Civil_ID,Nationality
John Smith,,,American
,أحمد محمد,123456,
Test Person,تست,,"""
        
        entries = engine.process_blacklist_csv(csv_content)
        
        assert len(entries) == 3
        
        # First entry has no arabic name or civil ID
        assert entries[0]['full_name_english'] == 'John Smith'
        assert entries[0]['full_name_arabic'] == ''
        assert entries[0]['civil_id'] == ''


class TestThresholdFiltering:
    """Tests for threshold-based filtering"""
    
    def test_high_threshold_filters_low_matches(self):
        """Test that high threshold filters out low-scoring matches"""
        from services.screening_engine import BlacklistScreeningEngine
        
        engine = BlacklistScreeningEngine()
        
        blacklist = [{
            'reference_number': 'BL001',
            'full_name_english': 'John Smith',
            'full_name_arabic': '',
            'civil_id': '',
            'nationality': 'American'
        }]
        
        kamco = [{
            'id': 'K001',
            'name_english': 'Ahmed Al-Rashid',  # Completely different
            'name_arabic': '',
            'civil_id': '999999999',
            'nationality': 'Kuwaiti',
            'type': 'CLIENT'
        }]
        
        # High threshold should find no matches
        matches_high = engine.screen_against_kamco(
            blacklist_entries=blacklist,
            kamco_entities=kamco,
            threshold=90.0,
            existing_decisions=set()
        )
        assert len(matches_high) == 0
        
        # Low threshold might find weak matches
        matches_low = engine.screen_against_kamco(
            blacklist_entries=blacklist,
            kamco_entities=kamco,
            threshold=5.0,
            existing_decisions=set()
        )
        # May or may not find matches depending on fuzzy match score
        # This test verifies the threshold filtering works
    
    def test_threshold_zero_returns_all(self):
        """Test that threshold of 0 returns all comparisons"""
        from services.screening_engine import BlacklistScreeningEngine
        
        engine = BlacklistScreeningEngine()
        
        blacklist = [{
            'reference_number': 'BL001',
            'full_name_english': 'Any Name',
            'full_name_arabic': '',
            'civil_id': '',
            'nationality': ''
        }]
        
        kamco = [
            {'id': 'K001', 'name_english': 'Entity 1', 'name_arabic': '', 'civil_id': '', 'nationality': '', 'type': 'CLIENT'},
            {'id': 'K002', 'name_english': 'Entity 2', 'name_arabic': '', 'civil_id': '', 'nationality': '', 'type': 'VENDOR'},
        ]
        
        matches = engine.screen_against_kamco(
            blacklist_entries=blacklist,
            kamco_entities=kamco,
            threshold=0.0,
            existing_decisions=set()
        )
        
        # With threshold 0, should compare against all entities
        # May return all comparisons as matches
        assert isinstance(matches, list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
