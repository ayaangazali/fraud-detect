"""
Phase 5 Test Suite - Fuzzy Matching & Deduplication (SIMPLIFIED)
Tests for enhanced fuzzy matcher, Civil ID matching (no format validation), deduplication, and screening

Note: Civil IDs are random unique numbers - no format validation, only exact matching
"""
import sys
import os
from datetime import datetime

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from database.connection import get_db, engine
from models.blacklist import BlacklistEntry
from models.database import KamcoClient, KamcoVendor, KamcoStaff, KamcoOther
from utils.fuzzy_matcher_enhanced import FuzzyMatcherEnhanced
from utils.civil_id_validator import CivilIDValidator
from utils.deduplication import DeduplicationSystem


class TestRunner:
    """Test runner with result tracking"""
    
    def __init__(self):
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.test_results = []
    
    def run_test(self, test_name, test_func):
        """Run a single test"""
        self.total_tests += 1
        print(f"\n{'='*80}")
        print(f"TEST {self.total_tests}: {test_name}")
        print(f"{'='*80}")
        
        try:
            test_func()
            print(f"✅ PASSED: {test_name}")
            self.passed_tests += 1
            self.test_results.append({'test': test_name, 'status': 'PASSED', 'error': None})
        except AssertionError as e:
            print(f"❌ FAILED: {test_name}")
            print(f"Error: {str(e)}")
            self.failed_tests += 1
            self.test_results.append({'test': test_name, 'status': 'FAILED', 'error': str(e)})
        except Exception as e:
            print(f"💥 ERROR: {test_name}")
            print(f"Error: {str(e)}")
            self.failed_tests += 1
            self.test_results.append({'test': test_name, 'status': 'ERROR', 'error': str(e)})
    
    def print_summary(self):
        """Print test summary"""
        print(f"\n{'='*80}")
        print("TEST SUMMARY")
        print(f"{'='*80}")
        print(f"Total Tests: {self.total_tests}")
        print(f"✅ Passed: {self.passed_tests}")
        print(f"❌ Failed: {self.failed_tests}")
        print(f"Success Rate: {(self.passed_tests/self.total_tests)*100:.1f}%")
        
        if self.failed_tests > 0:
            print(f"\n{'='*80}")
            print("FAILED TESTS:")
            print(f"{'='*80}")
            for result in self.test_results:
                if result['status'] != 'PASSED':
                    print(f"\n❌ {result['test']}")
                    print(f"   {result['error']}")


# Test Suite

def test_arabic_normalization():
    """Test Arabic text normalization"""
    matcher = FuzzyMatcherEnhanced()
    
    # Test diacritic removal
    text_with_diacritics = "أَحْمَدُ خَالِدٍ العُتَيْبِي"
    normalized = matcher.normalize_arabic_text(text_with_diacritics)
    
    # Should not contain diacritics
    diacritics = ['َ', 'ً', 'ُ', 'ٌ', 'ِ', 'ٍ', 'ْ', 'ّ', 'ـ']
    for diacritic in diacritics:
        assert diacritic not in normalized, f"Diacritic {diacritic} should be removed"
    
    print(f"Original: {text_with_diacritics}")
    print(f"Normalized: {normalized}")
    
    # Test Alef normalization
    alef_variations = ['إبراهيم', 'أحمد', 'آدم', 'ابراهيم']
    for name in alef_variations:
        normalized = matcher.normalize_arabic_text(name)
        assert 'ا' in normalized, f"Alef should be normalized in {name}"
        print(f"{name} → {normalized}")


def test_fuzzy_matching_accuracy():
    """Test fuzzy matching with exact and similar names"""
    matcher = FuzzyMatcherEnhanced()
    
    # Test exact match
    result = matcher.match_names("أحمد خالد العتيبي", "أحمد خالد العتيبي")
    print(f"\nExact match score: {result['match_score']}")
    assert result['match_score'] >= 95, "Exact match should be >= 95%"
    assert result['risk_level'] in ['EXACT', 'CRITICAL'], "Should be EXACT or CRITICAL risk"
    
    # Test high similarity (different word order)
    result = matcher.match_names("محمد علي أحمد", "أحمد علي محمد")
    print(f"Word order variation score: {result['match_score']}")
    assert result['match_score'] >= 80, "Word order variation should match well"
    
    # Test moderate similarity (typo)
    result = matcher.match_names("سعيد محمد الرشيد", "سعيد محمد الرشيدي")
    print(f"Typo variation score: {result['match_score']}")
    assert result['match_score'] >= 70, "Minor typo should still match"
    
    # Test low similarity (different names)
    result = matcher.match_names("أحمد خالد العتيبي", "فاطمة محمد الخالد")
    print(f"Different names score: {result['match_score']}")
    assert result['match_score'] < 70, "Different names should not match"


def test_fuzzy_matching_with_diacritics():
    """Test fuzzy matching works with and without diacritics"""
    matcher = FuzzyMatcherEnhanced()
    
    name1 = "أَحْمَدُ خَالِدٍ"
    name2 = "احمد خالد"
    
    result = matcher.match_names(name1, name2)
    print(f"\nMatch score (with vs without diacritics): {result['match_score']}")
    assert result['match_score'] >= 95, "Names with/without diacritics should match exactly"
    
    print(f"Normalized 1: {result['normalized_name1']}")
    print(f"Normalized 2: {result['normalized_name2']}")


def test_multiple_algorithms():
    """Test that multiple algorithms are used"""
    matcher = FuzzyMatcherEnhanced()
    
    result = matcher.match_names(
        "محمد علي أحمد السالم",
        "أحمد علي محمد السالم",
        use_multiple_algorithms=True
    )
    
    print(f"\nAlgorithms used: {result['algorithms_used']}")
    assert len(result['algorithms_used']) > 1, "Should use multiple algorithms"
    assert 'token_set_ratio' in result['algorithms_used'], "Should include token_set_ratio"
    
    for algo, score in result['algorithms_used'].items():
        print(f"  {algo}: {score}")


def test_batch_matching():
    """Test batch matching multiple names"""
    matcher = FuzzyMatcherEnhanced()
    
    queries = ["أحمد خالد", "محمد علي", "فاطمة سعيد"]
    candidates = [
        {"name": "أحمد خالد العتيبي", "id": 1},
        {"name": "محمد علي الرشيد", "id": 2},
        {"name": "سارة محمد", "id": 3}
    ]
    
    results = matcher.batch_match(queries, candidates, min_score=70)
    
    print(f"\nBatch results:")
    total_matches = sum(len(matches) for matches in results.values())
    print(f"Total matches found: {total_matches}")
    
    for query, matches in results.items():
        print(f"Query '{query}': {len(matches)} matches")
        for match in matches:
            print(f"  - {match['name']} (Score: {match['match_score']})")
    
    assert total_matches >= 2, "Should find at least 2 matches"


def test_civil_id_validation():
    """Test Civil ID validation (no format requirements - just non-empty)"""
    validator = CivilIDValidator()
    
    # Valid Civil IDs (any non-empty string after normalization)
    valid_ids = [
        "272081412355",
        "ABC-123-DEF",
        "ID2024001",
        "12345",
        "USER_ID_123"
    ]
    
    print("\nValidating various Civil IDs:")
    for civil_id in valid_ids:
        result = validator.validate_civil_id(civil_id)
        normalized = result.get('normalized')
        print(f"  '{civil_id}' → '{normalized}': valid={result['valid']}")
        assert result['valid'], f"{civil_id} should be valid"
        assert normalized is not None, "Should have normalized value"
        assert normalized != "", "Normalized value should not be empty"
    
    # Invalid Civil IDs (empty after normalization)
    invalid_ids = ["", "   ", "---"]
    
    print("\nValidating empty/invalid Civil IDs:")
    for civil_id in invalid_ids:
        result = validator.validate_civil_id(civil_id)
        print(f"  '{civil_id}': valid={result['valid']}, error={result.get('error')}")
        assert not result['valid'], f"'{civil_id}' should be invalid"


def test_civil_id_normalization():
    """Test Civil ID normalization removes separators"""
    validator = CivilIDValidator()
    
    test_cases = [
        ("208-141235-512", "208141235512"),
        ("208 141235 512", "208141235512"),
        ("208.141235.512", "208141235512"),
        ("208141235512", "208141235512"),
        ("  208141235512  ", "208141235512"),
        ("ABC-DEF-123", "ABCDEF123"),
        ("ID_2024_001", "ID2024001")
    ]
    
    print("\nNormalization tests:")
    for input_id, expected in test_cases:
        normalized = validator.normalize_civil_id(input_id)
        print(f"{input_id:20s} → {normalized}")
        assert normalized == expected, f"Should normalize to {expected}"


def test_civil_id_extraction():
    """Test Civil ID info extraction"""
    validator = CivilIDValidator()
    
    civil_id = "272081412355"
    info = validator.extract_info(civil_id)
    
    print(f"\nExtracted info from {civil_id}:")
    for key, value in info.items():
        print(f"  {key}: {value}")
    
    assert info is not None, "Should extract info"
    assert 'civil_id' in info, "Should have civil_id field"
    assert info['civil_id'] == "272081412355", "Should match normalized ID"


def test_civil_id_matching():
    """Test Civil ID exact matching"""
    validator = CivilIDValidator()
    
    # Exact match
    result = validator.match_civil_ids("272081412355", "272081412355")
    print(f"\nExact match: {result}")
    assert result['match'], "Same Civil IDs should match"
    assert result['confidence'] == 'EXACT', "Should have EXACT confidence"
    
    # Different Civil IDs
    result = validator.match_civil_ids("272081412355", "ABC123DEF456")
    print(f"Different IDs: {result}")
    assert not result['match'], "Different Civil IDs should not match"
    
    # With formatting (separators removed)
    result = validator.match_civil_ids("272-081412-355", "272081412355")
    print(f"Format variation: {result}")
    assert result['match'], "Should match despite different formats"


def test_civil_id_duplicates():
    """Test finding duplicates in a list"""
    validator = CivilIDValidator()
    
    civil_ids = [
        "272081412355",
        "ABC-123-DEF",
        "272-081412-355",  # Duplicate of first
        "ID2024001",
        "ABC123DEF"        # Duplicate of second
    ]
    
    duplicates = validator.find_duplicates(civil_ids)
    
    print(f"\nDuplicates found: {len(duplicates)}")
    for civil_id, indices in duplicates.items():
        print(f"  {civil_id}: positions {indices}")
    
    assert len(duplicates) >= 2, "Should find at least 2 sets of duplicates"
    assert "272081412355" in duplicates, "Should find first duplicate"
    assert "ABC123DEF" in duplicates, "Should find second duplicate"


def test_database_connectivity(db: Session):
    """Test database connection and data availability"""
    
    # Check blacklist entries
    blacklist_count = db.query(BlacklistEntry).count()
    print(f"\nBlacklist entries in database: {blacklist_count}")
    assert blacklist_count > 0, "Database should have blacklist entries"
    
    # Check Kamco entities
    clients_count = db.query(KamcoClient).count()
    vendors_count = db.query(KamcoVendor).count()
    staff_count = db.query(KamcoStaff).count()
    others_count = db.query(KamcoOther).count()
    
    print(f"Kamco Clients: {clients_count}")
    print(f"Kamco Vendors: {vendors_count}")
    print(f"Kamco Staff: {staff_count}")
    print(f"Kamco Others: {others_count}")
    
    total_entities = clients_count + vendors_count + staff_count + others_count
    assert total_entities > 0, "Database should have Kamco entities"
    
    print(f"Total Kamco entities: {total_entities}")


def test_deduplication_civil_id(db: Session):
    """Test Civil ID duplicate detection in database"""
    dedup = DeduplicationSystem(db)
    
    # Get an existing entry with Civil ID
    existing_entry = db.query(BlacklistEntry).filter(
        BlacklistEntry.civil_id.isnot(None),
        BlacklistEntry.civil_id != ""
    ).first()
    
    if existing_entry:
        print(f"\nChecking duplicate for Civil ID: {existing_entry.civil_id}")
        duplicate = dedup.check_civil_id_duplicate(existing_entry.civil_id)
        
        assert duplicate is not None, "Should find duplicate in database"
        assert duplicate.id == existing_entry.id, "Should match the same entry"
        print(f"✅ Found duplicate: {duplicate.name_arabic} (ID: {duplicate.id})")
    else:
        print("\n⚠️  No Civil IDs in database to test with")


def test_deduplication_name(db: Session):
    """Test name duplicate detection in database"""
    dedup = DeduplicationSystem(db)
    
    # Get an existing entry
    existing_entry = db.query(BlacklistEntry).filter(
        BlacklistEntry.status == "Active"
    ).first()
    
    if existing_entry:
        print(f"\nChecking name duplicates for: {existing_entry.name_arabic}")
        duplicates = dedup.check_name_duplicate(
            existing_entry.name_arabic,
            existing_entry.name_english
        )
        
        assert len(duplicates) >= 1, "Should find at least itself as duplicate"
        
        # Should find exact match with high score
        exact_match = next((d for d in duplicates if d['entry'].id == existing_entry.id), None)
        assert exact_match is not None, "Should find exact match"
        assert exact_match['match_score'] >= 95, "Exact match should have score >= 95"
        
        print(f"Found {len(duplicates)} potential name duplicates:")
        for dup in duplicates[:3]:
            print(f"  - {dup['entry'].name_arabic} (Score: {dup['match_score']}, Risk: {dup['risk_level']})")
    else:
        print("\n⚠️  No entries in database to test with")


def test_deduplication_comprehensive(db: Session):
    """Test comprehensive duplicate check"""
    dedup = DeduplicationSystem(db)
    
    # Get an existing entry
    existing_entry = db.query(BlacklistEntry).filter(
        BlacklistEntry.status == "Active"
    ).first()
    
    if existing_entry:
        print(f"\nRunning comprehensive duplicate check:")
        print(f"  Name: {existing_entry.name_arabic}")
        print(f"  Civil ID: {existing_entry.civil_id}")
        print(f"  Decree: {existing_entry.decree_number}")
        
        result = dedup.check_for_duplicates(
            name_arabic=existing_entry.name_arabic,
            civil_id=existing_entry.civil_id,
            name_english=existing_entry.name_english,
            decree_number=existing_entry.decree_number,
            source=existing_entry.source
        )
        
        print(f"\nResults:")
        print(f"  Has duplicates: {result['has_duplicates']}")
        print(f"  Duplicate types: {result['duplicate_types']}")
        print(f"  Recommendation: {result['recommendation']}")
        print(f"  Message: {result['message']}")
        
        assert result['has_duplicates'], "Should detect duplicates"
        assert result['recommendation'] in ['PROCEED', 'WARN', 'REJECT', 'MERGE'], "Should have valid recommendation"
    else:
        print("\n⚠️  No entries in database to test with")


def test_end_to_end_screening(db: Session):
    """Test end-to-end screening workflow"""
    matcher = FuzzyMatcherEnhanced()
    validator = CivilIDValidator()
    
    # Get sample Kamco client
    client = db.query(KamcoClient).first()
    
    if not client:
        print("\n⚠️  No Kamco clients to test with")
        return
    
    # Get all blacklist entries
    blacklist_entries = db.query(BlacklistEntry).filter(
        BlacklistEntry.status == "Active"
    ).all()
    
    if not blacklist_entries:
        print("\n⚠️  No blacklist entries to test with")
        return
    
    print(f"\n🔍 Screening client: {client.name}")
    print(f"   Against {len(blacklist_entries)} blacklist entries")
    
    matches = []
    
    for bl_entry in blacklist_entries:
        # Check Civil ID (if client has civil_id field)
        civil_id_match = False
        client_civil_id = getattr(client, 'civil_id', None)
        if client_civil_id and bl_entry.civil_id:
            match_result = validator.match_civil_ids(client_civil_id, bl_entry.civil_id)
            civil_id_match = match_result['match']
        
        # Check name
        name_match = matcher.match_names(client.name, bl_entry.name_arabic)
        
        if civil_id_match or name_match['match_score'] >= 70:
            matches.append({
                'blacklist_entry': bl_entry.name_arabic,
                'civil_id_match': civil_id_match,
                'name_score': name_match['match_score'],
                'risk_level': name_match['risk_level']
            })
    
    print(f"\n✅ Screening complete: {len(matches)} matches found")
    
    for match in matches[:5]:
        print(f"   - {match['blacklist_entry']}")
        print(f"     Civil ID match: {match['civil_id_match']}")
        print(f"     Name score: {match['name_score']}")
        print(f"     Risk level: {match['risk_level']}")


# Main execution

def main():
    """Run all tests"""
    print("="*80)
    print("PHASE 5 TEST SUITE - FUZZY MATCHING & DEDUPLICATION (SIMPLIFIED)")
    print("Note: Civil IDs are random unique numbers - no format validation")
    print("="*80)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    runner = TestRunner()
    
    # Get database session
    db = next(get_db())
    
    # Run tests
    runner.run_test("Test 1: Arabic text normalization", test_arabic_normalization)
    runner.run_test("Test 2: Fuzzy matching accuracy", test_fuzzy_matching_accuracy)
    runner.run_test("Test 3: Fuzzy matching with diacritics", test_fuzzy_matching_with_diacritics)
    runner.run_test("Test 4: Multiple algorithms", test_multiple_algorithms)
    runner.run_test("Test 5: Batch matching", test_batch_matching)
    runner.run_test("Test 6: Civil ID validation (no format)", test_civil_id_validation)
    runner.run_test("Test 7: Civil ID normalization", test_civil_id_normalization)
    runner.run_test("Test 8: Civil ID extraction", test_civil_id_extraction)
    runner.run_test("Test 9: Civil ID matching", test_civil_id_matching)
    runner.run_test("Test 10: Civil ID duplicate detection", test_civil_id_duplicates)
    runner.run_test("Test 11: Database connectivity", lambda: test_database_connectivity(db))
    runner.run_test("Test 12: Deduplication - Civil ID", lambda: test_deduplication_civil_id(db))
    runner.run_test("Test 13: Deduplication - Name", lambda: test_deduplication_name(db))
    runner.run_test("Test 14: Deduplication - Comprehensive", lambda: test_deduplication_comprehensive(db))
    runner.run_test("Test 15: End-to-end screening", lambda: test_end_to_end_screening(db))
    
    # Print summary
    runner.print_summary()
    
    # Close database
    db.close()
    
    print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Return exit code
    return 0 if runner.failed_tests == 0 else 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
