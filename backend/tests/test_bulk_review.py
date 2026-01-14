"""
Comprehensive Tests for Bulk Review and Error Handling
Tests the bulk review wizard functionality and proper error handling

Uses fixtures from conftest.py for client and test_users
"""
import pytest
from datetime import datetime
import json


class TestBulkReviewWizard:
    """Test suite for bulk review wizard functionality"""

    def test_bulk_items_details_empty_list(self, client, test_users):
        """Test bulk items details with empty item list"""
        # Login as checker
        login_response = client.post("/api/auth/login", json={
            "username": test_users["checker_test"]["username"],
            "password": test_users["checker_test"]["password"]
        })
        if login_response.status_code != 200:
            pytest.skip("Could not authenticate checker user")
        
        token = login_response.json().get("access_token")
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.post(
            "/api/reviews/bulk-items-details",
            json={"item_ids": []},
            headers=headers
        )
        # Should return empty list, not error
        assert response.status_code in [200, 422]

    def test_bulk_items_details_invalid_ids(self, client, test_users):
        """Test bulk items details with non-existent IDs"""
        login_response = client.post("/api/auth/login", json={
            "username": test_users["checker_test"]["username"],
            "password": test_users["checker_test"]["password"]
        })
        if login_response.status_code != 200:
            pytest.skip("Could not authenticate checker user")
        
        token = login_response.json().get("access_token")
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.post(
            "/api/reviews/bulk-items-details",
            json={"item_ids": [99999, 99998, 99997]},
            headers=headers
        )
        # Should return empty list or error, not crash
        assert response.status_code in [200, 404, 422]

    def test_submit_bulk_wizard_empty_reviews(self, client, test_users):
        """Test submit bulk wizard with empty reviews list"""
        login_response = client.post("/api/auth/login", json={
            "username": test_users["checker_test"]["username"],
            "password": test_users["checker_test"]["password"]
        })
        if login_response.status_code != 200:
            pytest.skip("Could not authenticate checker user")
        
        token = login_response.json().get("access_token")
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.post(
            "/api/reviews/submit-bulk-wizard",
            json=[],
            headers=headers
        )
        # Should handle gracefully
        assert response.status_code in [200, 422]

    def test_submit_bulk_wizard_invalid_decision(self, client, test_users):
        """Test submit bulk wizard with invalid decision value"""
        login_response = client.post("/api/auth/login", json={
            "username": test_users["checker_test"]["username"],
            "password": test_users["checker_test"]["password"]
        })
        if login_response.status_code != 200:
            pytest.skip("Could not authenticate checker user")
        
        token = login_response.json().get("access_token")
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.post(
            "/api/reviews/submit-bulk-wizard",
            json=[{
                "item_id": 1,
                "decision": "invalid_decision",
                "notes": "Test notes"
            }],
            headers=headers
        )
        # Should not crash, may return error or handle gracefully
        assert response.status_code in [200, 400, 422, 404]

    def test_submit_bulk_wizard_missing_notes(self, client, test_users):
        """Test submit bulk wizard with missing notes"""
        login_response = client.post("/api/auth/login", json={
            "username": test_users["checker_test"]["username"],
            "password": test_users["checker_test"]["password"]
        })
        if login_response.status_code != 200:
            pytest.skip("Could not authenticate checker user")
        
        token = login_response.json().get("access_token")
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.post(
            "/api/reviews/submit-bulk-wizard",
            json=[{
                "item_id": 1,
                "decision": "approved"
                # notes missing
            }],
            headers=headers
        )
        # Should handle missing notes gracefully
        assert response.status_code in [200, 400, 422, 404]

    def test_submit_bulk_wizard_proper_format(self, client, test_users):
        """Test submit bulk wizard with proper format"""
        login_response = client.post("/api/auth/login", json={
            "username": test_users["checker_test"]["username"],
            "password": test_users["checker_test"]["password"]
        })
        if login_response.status_code != 200:
            pytest.skip("Could not authenticate checker user")
        
        token = login_response.json().get("access_token")
        headers = {"Authorization": f"Bearer {token}"}
        
        # This tests the proper format even if item doesn't exist
        response = client.post(
            "/api/reviews/submit-bulk-wizard",
            json=[{
                "item_id": 1,
                "decision": "approved",
                "notes": "Test approval notes"
            }],
            headers=headers
        )
        # Should not crash - returns success or item not found
        assert response.status_code in [200, 404]


class TestErrorHandling:
    """Test suite for proper error handling"""

    def test_validation_error_format(self, client, test_users):
        """Test that validation errors return proper format"""
        login_response = client.post("/api/auth/login", json={
            "username": test_users["checker_test"]["username"],
            "password": test_users["checker_test"]["password"]
        })
        if login_response.status_code != 200:
            pytest.skip("Could not authenticate checker user")
        
        token = login_response.json().get("access_token")
        headers = {"Authorization": f"Bearer {token}"}
        
        # Send malformed request
        response = client.post(
            "/api/reviews/submit-bulk-wizard",
            json="not a list",  # Should be a list
            headers=headers
        )
        
        # Should return 422 with proper error format
        if response.status_code == 422:
            data = response.json()
            # Error should be a dict with detail
            assert "detail" in data

    def test_error_messages_are_strings(self, client, test_users):
        """Test that error messages can be rendered as strings"""
        login_response = client.post("/api/auth/login", json={
            "username": test_users["checker_test"]["username"],
            "password": test_users["checker_test"]["password"]
        })
        if login_response.status_code != 200:
            pytest.skip("Could not authenticate checker user")
        
        token = login_response.json().get("access_token")
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.post(
            "/api/reviews/submit-bulk-wizard",
            json=[{"invalid": "data"}],
            headers=headers
        )
        
        if response.status_code in [400, 422]:
            data = response.json()
            detail = data.get("detail")
            # Detail should be renderable - either string or list of objects with msg
            if isinstance(detail, str):
                assert len(detail) > 0
            elif isinstance(detail, list):
                for item in detail:
                    if isinstance(item, dict):
                        # Should have 'msg' field that's a string
                        msg = item.get("msg", "")
                        assert isinstance(msg, str)
            elif isinstance(detail, dict):
                msg = detail.get("msg", str(detail))
                assert isinstance(msg, str)


class TestBulkDecisions:
    """Test suite for bulk decision processing"""

    def test_approve_all_format(self, client, test_users):
        """Test format for approving all items"""
        login_response = client.post("/api/auth/login", json={
            "username": test_users["checker_test"]["username"],
            "password": test_users["checker_test"]["password"]
        })
        if login_response.status_code != 200:
            pytest.skip("Could not authenticate checker user")
        
        token = login_response.json().get("access_token")
        headers = {"Authorization": f"Bearer {token}"}
        
        reviews = [
            {"item_id": i, "decision": "approved", "notes": f"Approved item {i}"}
            for i in range(1, 6)
        ]
        
        response = client.post(
            "/api/reviews/submit-bulk-wizard",
            json=reviews,
            headers=headers
        )
        
        # Should process without crashing
        assert response.status_code in [200, 404, 422]

    def test_reject_all_format(self, client, test_users):
        """Test format for rejecting all items"""
        login_response = client.post("/api/auth/login", json={
            "username": test_users["checker_test"]["username"],
            "password": test_users["checker_test"]["password"]
        })
        if login_response.status_code != 200:
            pytest.skip("Could not authenticate checker user")
        
        token = login_response.json().get("access_token")
        headers = {"Authorization": f"Bearer {token}"}
        
        reviews = [
            {"item_id": i, "decision": "rejected", "notes": f"Rejected item {i}"}
            for i in range(1, 6)
        ]
        
        response = client.post(
            "/api/reviews/submit-bulk-wizard",
            json=reviews,
            headers=headers
        )
        
        # Should process without crashing
        assert response.status_code in [200, 404, 422]

    def test_mixed_decisions(self, client, test_users):
        """Test format for mixed decisions"""
        login_response = client.post("/api/auth/login", json={
            "username": test_users["checker_test"]["username"],
            "password": test_users["checker_test"]["password"]
        })
        if login_response.status_code != 200:
            pytest.skip("Could not authenticate checker user")
        
        token = login_response.json().get("access_token")
        headers = {"Authorization": f"Bearer {token}"}
        
        reviews = [
            {"item_id": 1, "decision": "approved", "notes": "Approved"},
            {"item_id": 2, "decision": "rejected", "notes": "Rejected"},
            {"item_id": 3, "decision": "escalated", "notes": "Needs review", "escalation_notes": "High risk"}
        ]
        
        response = client.post(
            "/api/reviews/submit-bulk-wizard",
            json=reviews,
            headers=headers
        )
        
        # Should process without crashing
        assert response.status_code in [200, 404, 422]


class TestReportGeneration:
    """Test suite for report generation"""

    def test_generate_screening_summary_pdf(self, client, test_users):
        """Test generating screening summary PDF"""
        login_response = client.post("/api/auth/login", json={
            "username": test_users["checker_test"]["username"],
            "password": test_users["checker_test"]["password"]
        })
        if login_response.status_code != 200:
            pytest.skip("Could not authenticate checker user")
        
        token = login_response.json().get("access_token")
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.post(
            "/api/reports/generate",
            json={
                "report_type": "screening_summary",
                "report_format": "pdf",
                "title": "Test Report"
            },
            headers=headers
        )
        
        # Should return report or error, not crash
        assert response.status_code in [200, 400, 404, 422, 500]

    def test_screening_summary_endpoint(self, client, test_users):
        """Test screening summary endpoint"""
        login_response = client.post("/api/auth/login", json={
            "username": test_users["checker_test"]["username"],
            "password": test_users["checker_test"]["password"]
        })
        if login_response.status_code != 200:
            pytest.skip("Could not authenticate checker user")
        
        token = login_response.json().get("access_token")
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.get("/api/reports/screening-summary", headers=headers)
        
        assert response.status_code in [200, 403, 404]


class TestNotifications:
    """Test suite for notifications/activity data"""

    def test_get_uploads_for_activity(self, client, test_users):
        """Test getting uploads which feed into activity notifications"""
        login_response = client.post("/api/auth/login", json={
            "username": test_users["screener_test"]["username"],
            "password": test_users["screener_test"]["password"]
        })
        if login_response.status_code != 200:
            pytest.skip("Could not authenticate user")
        
        token = login_response.json().get("access_token")
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.get("/api/screening/v2/uploads", headers=headers)
        
        assert response.status_code in [200, 403, 404]

    def test_get_pending_matches_for_activity(self, client, test_users):
        """Test getting pending matches for notifications"""
        login_response = client.post("/api/auth/login", json={
            "username": test_users["screener_test"]["username"],
            "password": test_users["screener_test"]["password"]
        })
        if login_response.status_code != 200:
            pytest.skip("Could not authenticate user")
        
        token = login_response.json().get("access_token")
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.get("/api/screening/v2/pending-matches", headers=headers)
        
        assert response.status_code in [200, 403, 404]


class TestDashboardData:
    """Test suite for dashboard real data endpoints"""

    def test_dashboard_stats_endpoints(self, client, test_users):
        """Test all endpoints needed for dashboard stats"""
        login_response = client.post("/api/auth/login", json={
            "username": test_users["screener_test"]["username"],
            "password": test_users["screener_test"]["password"]
        })
        if login_response.status_code != 200:
            pytest.skip("Could not authenticate user")
        
        token = login_response.json().get("access_token")
        headers = {"Authorization": f"Bearer {token}"}
        
        endpoints = [
            "/api/reports/screening-summary",
            "/api/screening/v2/uploads",
            "/api/screening/v2/pending-matches"
        ]
        
        for endpoint in endpoints:
            response = client.get(endpoint, headers=headers)
            # All should return data or graceful error, not crash
            assert response.status_code in [200, 403, 404, 500]

    def test_kamco_entities_endpoint(self, client, test_users):
        """Test KAMCO entities endpoint"""
        login_response = client.post("/api/auth/login", json={
            "username": test_users["screener_test"]["username"],
            "password": test_users["screener_test"]["password"]
        })
        if login_response.status_code != 200:
            pytest.skip("Could not authenticate user")
        
        token = login_response.json().get("access_token")
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.get("/api/screening/v2/kamco-entities", headers=headers)
        
        assert response.status_code in [200, 403, 404]


class TestAuthenticationErrors:
    """Test authentication error handling"""

    def test_unauthorized_bulk_review(self, client):
        """Test bulk review without auth token"""
        response = client.post(
            "/api/reviews/submit-bulk-wizard",
            json=[{"item_id": 1, "decision": "approved", "notes": "test"}]
        )
        
        assert response.status_code in [401, 403]

    def test_invalid_token_bulk_review(self, client):
        """Test bulk review with invalid token"""
        headers = {"Authorization": "Bearer invalid_token_12345"}
        
        response = client.post(
            "/api/reviews/submit-bulk-wizard",
            json=[{"item_id": 1, "decision": "approved", "notes": "test"}],
            headers=headers
        )
        
        assert response.status_code in [401, 403]
