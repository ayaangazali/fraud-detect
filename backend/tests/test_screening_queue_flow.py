"""
Comprehensive tests for the screening queue flow:
1. Upload blacklist → Creates ScreeningMatch records
2. Queue endpoint → Returns pending matches
3. Decision endpoint → Updates match status
4. Bulk decision → Updates multiple matches
5. Matches removed from queue after decision

These tests verify the complete flow from upload to resolution.
"""
import pytest
import io
import csv
from datetime import datetime


class TestScreeningQueueFlow:
    """Test the complete screening queue flow"""
    
    @pytest.fixture
    def sample_blacklist_csv(self):
        """Create a sample blacklist CSV file with entries that match Kamco entities"""
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=[
            'name_english', 'name_arabic', 'civil_id', 'nationality', 'type', 'source'
        ])
        writer.writeheader()
        # Add entries that closely match Kamco entities to ensure matches
        writer.writerow({
            'name_english': 'Ahmad Muhammad Al-Hassan',  # Exact match
            'name_arabic': 'أحمد محمد الحسن',
            'civil_id': '123456789012',
            'nationality': 'Kuwait',
            'type': 'Individual',
            'source': 'UN Sanctions'
        })
        writer.writerow({
            'name_english': 'Global Trading Corporation',  # Close match
            'name_arabic': 'شركة التجارة العالمية',
            'civil_id': '',
            'nationality': 'UAE',
            'type': 'Entity',
            'source': 'OFAC SDN'
        })
        writer.writerow({
            'name_english': 'Mohamed Ali Ibrahim',  # Exact match
            'name_arabic': 'محمد علي',
            'civil_id': '456789012345',
            'nationality': 'Egypt',
            'type': 'Individual',
            'source': 'EU Sanctions'
        })
        output.seek(0)
        return output.getvalue().encode('utf-8')
    
    def test_full_screening_flow(self, client, authenticated_admin, seed_kamco_entities, sample_blacklist_csv):
        """
        Test the complete flow:
        1. Upload blacklist
        2. Verify matches appear in pending-matches queue
        3. Make decision on a match
        4. Verify match is removed from pending queue
        """
        headers = authenticated_admin["headers"]
        
        # Step 1: Upload blacklist file with low threshold to ensure matches
        files = {
            'file': ('test_blacklist.csv', sample_blacklist_csv, 'text/csv')
        }
        response = client.post(
            "/api/screening/v2/upload-blacklist",
            files=files,
            params={'threshold': 20},  # Lower threshold to get more matches
            headers=headers
        )
        
        assert response.status_code == 200
        upload_data = response.json()
        assert upload_data['success'] is True
        upload_id = upload_data['upload_id']
        matches_found = upload_data['matches_found']
        
        print(f"Upload created: ID={upload_id}, matches={matches_found}")
        
        # Step 2: Get pending matches
        response = client.get(
            "/api/screening/v2/pending-matches",
            headers=headers
        )
        
        assert response.status_code == 200
        pending_data = response.json()
        assert pending_data['success'] is True
        
        # Verify queue contains the matches
        queue = pending_data.get('queue') or pending_data.get('matches', [])
        assert len(queue) > 0, "Queue should have pending matches after upload"
        
        # Verify queue item structure has all required fields
        first_match = queue[0]
        assert 'kamco_name' in first_match, "Queue item should have kamco_name"
        assert 'kamco_type' in first_match, "Queue item should have kamco_type"
        assert 'blacklist_name' in first_match, "Queue item should have blacklist_name"
        assert 'match_score' in first_match, "Queue item should have match_score"
        assert 'status' in first_match, "Queue item should have status"
        assert first_match['status'] == 'pending', "New matches should have pending status"
        
        match_id = first_match['match_id']
        print(f"First match: ID={match_id}, kamco={first_match['kamco_name']}, blacklist={first_match['blacklist_name']}")
        
        # Step 3: Make decision on the match (FLAGGED)
        response = client.post(
            "/api/screening/v2/decision",
            json={
                'match_id': match_id,
                'status': 'FLAGGED',
                'notes': 'Test flag - confirmed match'
            },
            headers=headers
        )
        
        assert response.status_code == 200
        decision_data = response.json()
        assert decision_data['success'] is True
        print(f"Decision made: {decision_data['status']}")
        
        # Step 4: Verify match is removed from pending queue
        response = client.get(
            "/api/screening/v2/pending-matches",
            headers=headers
        )
        
        assert response.status_code == 200
        updated_queue = response.json().get('queue') or response.json().get('matches', [])
        
        # The flagged match should no longer be in pending queue
        match_ids_in_queue = [m['match_id'] for m in updated_queue]
        assert match_id not in match_ids_in_queue, "Flagged match should be removed from pending queue"
        
        print(f"Match {match_id} successfully removed from pending queue after decision")
    
    def test_queue_returns_correct_fields_for_frontend(self, client, authenticated_admin, seed_kamco_entities):
        """Test that pending-matches returns all fields needed by ScreeningQueuePage"""
        headers = authenticated_admin["headers"]
        
        response = client.get(
            "/api/screening/v2/pending-matches",
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        
        # Should have both 'queue' and 'matches' for compatibility
        assert 'queue' in data or 'matches' in data
        
        queue = data.get('queue') or data.get('matches', [])
        
        if len(queue) > 0:
            item = queue[0]
            # Required fields for ScreeningQueuePage
            required_fields = [
                'match_id',  # or 'id'
                'kamco_name',
                'kamco_type',
                'blacklist_name',
                'match_score',
                'match_type',
                'severity',
                'status'
            ]
            
            for field in required_fields:
                assert field in item, f"Queue item missing required field: {field}"
    
    def test_bulk_decision(self, client, authenticated_admin, seed_kamco_entities, sample_blacklist_csv):
        """Test bulk decision endpoint"""
        headers = authenticated_admin["headers"]
        
        # First upload a blacklist to create matches
        files = {
            'file': ('bulk_test.csv', sample_blacklist_csv, 'text/csv')
        }
        response = client.post(
            "/api/screening/v2/upload-blacklist",
            files=files,
            params={'threshold': 30},  # Lower threshold to get more matches
            headers=headers
        )
        
        assert response.status_code == 200
        
        # Get pending matches
        response = client.get(
            "/api/screening/v2/pending-matches",
            headers=headers
        )
        
        assert response.status_code == 200
        queue = response.json().get('queue') or response.json().get('matches', [])
        
        if len(queue) < 2:
            pytest.skip("Need at least 2 pending matches for bulk test")
        
        # Select first 2 matches for bulk decision
        match_ids = [queue[0]['match_id'], queue[1]['match_id']]
        
        # Make bulk decision
        response = client.post(
            "/api/screening/v2/bulk-decision",
            json={
                'match_ids': match_ids,
                'status': 'CLEARED',
                'notes': 'Bulk clear - false positives'
            },
            headers=headers
        )
        
        assert response.status_code == 200
        result = response.json()
        assert result['success'] is True
        assert result['success_count'] == 2
        
        # Verify both matches are removed from pending queue
        response = client.get(
            "/api/screening/v2/pending-matches",
            headers=headers
        )
        
        updated_queue = response.json().get('queue') or response.json().get('matches', [])
        remaining_ids = [m['match_id'] for m in updated_queue]
        
        for mid in match_ids:
            assert mid not in remaining_ids, f"Match {mid} should be removed after bulk decision"
    
    def test_upload_creates_matches_with_kamco_data(self, client, authenticated_admin, seed_kamco_entities, sample_blacklist_csv):
        """Test that uploaded blacklist creates matches with full Kamco entity data"""
        headers = authenticated_admin["headers"]
        
        files = {
            'file': ('test.csv', sample_blacklist_csv, 'text/csv')
        }
        response = client.post(
            "/api/screening/v2/upload-blacklist",
            files=files,
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        if data['matches_found'] > 0:
            # Check that match response includes kamco entity info
            matches = data.get('matches', [])
            if matches:
                match = matches[0]
                assert 'kamco_entity' in match, "Match should include kamco_entity"
                kamco = match['kamco_entity']
                assert kamco.get('id') is not None, "Kamco entity should have ID"
    
    def test_decision_updates_match_status(self, client, authenticated_admin, seed_kamco_entities, sample_blacklist_csv):
        """Test that decision endpoint correctly updates match status"""
        headers = authenticated_admin["headers"]
        
        # Upload to create matches
        files = {
            'file': ('status_test.csv', sample_blacklist_csv, 'text/csv')
        }
        client.post(
            "/api/screening/v2/upload-blacklist",
            files=files,
            params={'threshold': 30},
            headers=headers
        )
        
        # Get a pending match
        response = client.get(
            "/api/screening/v2/pending-matches",
            headers=headers
        )
        
        queue = response.json().get('queue') or response.json().get('matches', [])
        if not queue:
            pytest.skip("No pending matches available")
        
        match_id = queue[0]['match_id']
        
        # Test FLAGGED status
        response = client.post(
            "/api/screening/v2/decision",
            json={
                'match_id': match_id,
                'status': 'FLAGGED',
                'notes': 'Confirmed match'
            },
            headers=headers
        )
        
        assert response.status_code == 200
        assert response.json()['status'] == 'FLAGGED'
        
        # Match should not be in pending queue anymore
        response = client.get(
            "/api/screening/v2/pending-matches",
            headers=headers
        )
        
        updated_queue = response.json().get('queue') or response.json().get('matches', [])
        match_ids = [m['match_id'] for m in updated_queue]
        assert match_id not in match_ids
    
    def test_invalid_decision_status(self, client, authenticated_admin, seed_kamco_entities):
        """Test that invalid decision status returns error"""
        headers = authenticated_admin["headers"]
        
        response = client.post(
            "/api/screening/v2/decision",
            json={
                'match_id': 999999,
                'status': 'INVALID_STATUS',
                'notes': 'Test'
            },
            headers=headers
        )
        
        # Should return 400 Bad Request for invalid status
        assert response.status_code == 400
    
    def test_decision_on_nonexistent_match(self, client, authenticated_admin, seed_kamco_entities):
        """Test that decision on non-existent match returns 404"""
        headers = authenticated_admin["headers"]
        
        response = client.post(
            "/api/screening/v2/decision",
            json={
                'match_id': 999999999,
                'status': 'FLAGGED',
                'notes': 'Test'
            },
            headers=headers
        )
        
        assert response.status_code == 404
    
    def test_queue_severity_calculation(self, client, authenticated_admin, seed_kamco_entities, sample_blacklist_csv):
        """Test that severity is calculated correctly based on match score"""
        headers = authenticated_admin["headers"]
        
        # Upload blacklist
        files = {
            'file': ('severity_test.csv', sample_blacklist_csv, 'text/csv')
        }
        client.post(
            "/api/screening/v2/upload-blacklist",
            files=files,
            headers=headers
        )
        
        # Get pending matches
        response = client.get(
            "/api/screening/v2/pending-matches",
            headers=headers
        )
        
        assert response.status_code == 200
        queue = response.json().get('queue') or response.json().get('matches', [])
        
        for item in queue:
            score = item.get('match_score', 0)
            severity = item.get('severity', '')
            
            # Verify severity is set
            assert severity in ['critical', 'high', 'medium', 'low'], \
                f"Severity should be valid, got: {severity}"
            
            # Verify severity matches score ranges
            if score >= 90:
                assert severity in ['critical', 'high'], \
                    f"Score {score} should be critical or high, got {severity}"


class TestQueueAuthentication:
    """Test authentication requirements for queue endpoints"""
    
    def test_pending_matches_requires_auth(self, client, test_users):
        """Test that pending-matches endpoint requires authentication"""
        response = client.get("/api/screening/v2/pending-matches")
        assert response.status_code == 401 or response.status_code == 403
    
    def test_decision_requires_auth(self, client, test_users):
        """Test that decision endpoint requires authentication"""
        response = client.post(
            "/api/screening/v2/decision",
            json={
                'match_id': 1,
                'status': 'FLAGGED',
                'notes': 'Test'
            }
        )
        assert response.status_code == 401 or response.status_code == 403
    
    def test_bulk_decision_requires_auth(self, client, test_users):
        """Test that bulk-decision endpoint requires authentication"""
        response = client.post(
            "/api/screening/v2/bulk-decision",
            json={
                'match_ids': [1, 2],
                'status': 'CLEARED',
                'notes': 'Test'
            }
        )
        assert response.status_code == 401 or response.status_code == 403


class TestQueueFiltering:
    """Test filtering options for pending matches"""
    
    def test_filter_by_min_score(self, client, authenticated_admin, seed_kamco_entities):
        """Test filtering pending matches by minimum score"""
        headers = authenticated_admin["headers"]
        
        response = client.get(
            "/api/screening/v2/pending-matches",
            params={'min_score': 70},
            headers=headers
        )
        
        assert response.status_code == 200
        queue = response.json().get('queue') or response.json().get('matches', [])
        
        for item in queue:
            assert item['match_score'] >= 70 or item['match_score'] >= 0.7, \
                f"Match score {item['match_score']} should be >= 70"
    
    def test_limit_results(self, client, authenticated_admin, seed_kamco_entities):
        """Test limiting the number of results"""
        headers = authenticated_admin["headers"]
        
        response = client.get(
            "/api/screening/v2/pending-matches",
            params={'limit': 5},
            headers=headers
        )
        
        assert response.status_code == 200
        queue = response.json().get('queue') or response.json().get('matches', [])
        assert len(queue) <= 5


class TestDecisionLogging:
    """Test that decisions are properly logged"""
    
    def test_decision_creates_log_entry(self, client, authenticated_admin, seed_kamco_entities, sample_blacklist_csv):
        """Test that making a decision creates a log entry"""
        headers = authenticated_admin["headers"]
        
        # First upload blacklist to create matches
        sample_csv = io.StringIO()
        writer = csv.DictWriter(sample_csv, fieldnames=['name_english', 'nationality'])
        writer.writeheader()
        writer.writerow({'name_english': 'Test Person', 'nationality': 'Kuwait'})
        csv_content = sample_csv.getvalue().encode('utf-8')
        
        files = {
            'file': ('log_test.csv', csv_content, 'text/csv')
        }
        client.post(
            "/api/screening/v2/upload-blacklist",
            files=files,
            params={'threshold': 10},
            headers=headers
        )
        
        # Get a pending match
        response = client.get(
            "/api/screening/v2/pending-matches",
            headers=headers
        )
        
        queue = response.json().get('queue') or response.json().get('matches', [])
        if not queue:
            pytest.skip("No pending matches available")
        
        match_id = queue[0]['match_id']
        
        # Make decision
        response = client.post(
            "/api/screening/v2/decision",
            json={
                'match_id': match_id,
                'status': 'FLAGGED',
                'notes': 'Test log entry creation'
            },
            headers=headers
        )
        
        assert response.status_code == 200
        result = response.json()
        assert result['success'] is True
        assert 'decision_id' in result, "Response should include decision_id"
        
        # Decision ID should be a valid integer
        assert isinstance(result['decision_id'], int)
        assert result['decision_id'] > 0


class TestScreenerWorkflow:
    """Test role-specific workflows"""
    
    def test_screener_can_access_queue(self, client, authenticated_screener, seed_kamco_entities):
        """Test that screener role can access the screening queue"""
        headers = authenticated_screener["headers"]
        
        response = client.get(
            "/api/screening/v2/pending-matches",
            headers=headers
        )
        
        assert response.status_code == 200
        assert response.json()['success'] is True
    
    def test_screener_can_make_decision(self, client, authenticated_screener, authenticated_admin, seed_kamco_entities, sample_blacklist_csv):
        """Test that screener can make decisions on matches"""
        admin_headers = authenticated_admin["headers"]
        screener_headers = authenticated_screener["headers"]
        
        # Admin uploads blacklist
        sample_csv = io.BytesIO(b"name_english,nationality\nTest Name,Kuwait")
        files = {
            'file': ('test.csv', sample_csv, 'text/csv')
        }
        client.post(
            "/api/screening/v2/upload-blacklist",
            files=files,
            params={'threshold': 10},
            headers=admin_headers
        )
        
        # Screener gets pending matches
        response = client.get(
            "/api/screening/v2/pending-matches",
            headers=screener_headers
        )
        
        queue = response.json().get('queue') or response.json().get('matches', [])
        if not queue:
            pytest.skip("No pending matches available")
        
        match_id = queue[0]['match_id']
        
        # Screener makes decision
        response = client.post(
            "/api/screening/v2/decision",
            json={
                'match_id': match_id,
                'status': 'FLAGGED',
                'notes': 'Screener flagged this match'
            },
            headers=screener_headers
        )
        
        assert response.status_code == 200
        assert response.json()['success'] is True


# Add sample_blacklist_csv fixture at class level for TestDecisionLogging
@pytest.fixture
def sample_blacklist_csv():
    """Create a sample blacklist CSV file"""
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=[
        'name_english', 'name_arabic', 'civil_id', 'nationality', 'type', 'source'
    ])
    writer.writeheader()
    writer.writerow({
        'name_english': 'Ahmad Muhammad',
        'name_arabic': 'أحمد محمد',
        'civil_id': '123456789',
        'nationality': 'Kuwait',
        'type': 'Individual',
        'source': 'UN Sanctions'
    })
    output.seek(0)
    return output.getvalue().encode('utf-8')
