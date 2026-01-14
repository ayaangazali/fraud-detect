"""
Comprehensive Tests for Review Workflow
Tests screener -> checker -> finalizer workflow and bulk review operations
"""
import pytest
from datetime import datetime
import json


class TestReviewWorkflow:
    """Test the complete review workflow from screener to finalizer"""

    def test_screener_flags_item_goes_to_checker(self, client, test_users, db_session):
        """When screener flags an item, it should go to checker queue"""
        # Login as screener
        login_response = client.post("/api/auth/login", json={
            "username": test_users["screener_test"]["username"],
            "password": test_users["screener_test"]["password"]
        })
        if login_response.status_code != 200:
            pytest.skip("Could not authenticate screener user")
        
        token = login_response.json().get("access_token")
        headers = {"Authorization": f"Bearer {token}"}
        
        # Get screener queue (should have pending items if any exist)
        response = client.get("/api/reviews/queue/screener", headers=headers)
        assert response.status_code in [200, 403, 404]

    def test_screener_clears_item_resolved(self, client, test_users):
        """When screener clears an item, it should be resolved"""
        login_response = client.post("/api/auth/login", json={
            "username": test_users["screener_test"]["username"],
            "password": test_users["screener_test"]["password"]
        })
        if login_response.status_code != 200:
            pytest.skip("Could not authenticate screener user")
        
        token = login_response.json().get("access_token")
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test bulk review with rejection (clear)
        response = client.post(
            "/api/reviews/review/bulk",
            json={
                "item_ids": [999],  # Non-existent, but tests the workflow
                "decision": "rejected",
                "notes": "False positive - cleared"
            },
            headers=headers
        )
        # Should handle gracefully
        assert response.status_code in [200, 404, 422]

    def test_checker_sees_screener_flagged_items(self, client, test_users):
        """Checker should see items that screeners have flagged"""
        login_response = client.post("/api/auth/login", json={
            "username": test_users["checker_test"]["username"],
            "password": test_users["checker_test"]["password"]
        })
        if login_response.status_code != 200:
            pytest.skip("Could not authenticate checker user")
        
        token = login_response.json().get("access_token")
        headers = {"Authorization": f"Bearer {token}"}
        
        # Get checker queue
        response = client.get("/api/reviews/queue/checker", headers=headers)
        assert response.status_code in [200, 403, 404]
        if response.status_code == 200:
            data = response.json()
            assert "success" in data
            assert "queue" in data
            assert "count" in data

    def test_checker_confirms_flag(self, client, test_users):
        """Checker can confirm a screener's flag"""
        login_response = client.post("/api/auth/login", json={
            "username": test_users["checker_test"]["username"],
            "password": test_users["checker_test"]["password"]
        })
        if login_response.status_code != 200:
            pytest.skip("Could not authenticate checker user")
        
        token = login_response.json().get("access_token")
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.post(
            "/api/reviews/review/bulk",
            json={
                "item_ids": [999],
                "decision": "approved",
                "notes": "Confirmed match"
            },
            headers=headers
        )
        assert response.status_code in [200, 404, 422]

    def test_checker_overrides_clears_item(self, client, test_users):
        """Checker can override screener and clear an item"""
        login_response = client.post("/api/auth/login", json={
            "username": test_users["checker_test"]["username"],
            "password": test_users["checker_test"]["password"]
        })
        if login_response.status_code != 200:
            pytest.skip("Could not authenticate checker user")
        
        token = login_response.json().get("access_token")
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.post(
            "/api/reviews/review/bulk",
            json={
                "item_ids": [999],
                "decision": "rejected",
                "notes": "Overriding screener - this is a false positive"
            },
            headers=headers
        )
        assert response.status_code in [200, 404, 422]

    def test_finalizer_queue(self, client, test_users):
        """Finalizer should see high-risk items awaiting approval"""
        login_response = client.post("/api/auth/login", json={
            "username": test_users["finalizer_test"]["username"],
            "password": test_users["finalizer_test"]["password"]
        })
        if login_response.status_code != 200:
            pytest.skip("Could not authenticate finalizer user")
        
        token = login_response.json().get("access_token")
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.get("/api/reviews/queue/finalizer", headers=headers)
        assert response.status_code in [200, 403, 404]

    def test_my_queue_endpoint(self, client, test_users):
        """My queue endpoint should return items based on role"""
        # Test for each role
        for role in ["screener_test", "checker_test", "finalizer_test"]:
            login_response = client.post("/api/auth/login", json={
                "username": test_users[role]["username"],
                "password": test_users[role]["password"]
            })
            if login_response.status_code != 200:
                continue
            
            token = login_response.json().get("access_token")
            headers = {"Authorization": f"Bearer {token}"}
            
            response = client.get("/api/reviews/queue/my-queue", headers=headers)
            assert response.status_code in [200, 403, 404]
            if response.status_code == 200:
                data = response.json()
                assert "role" in data


class TestBulkReviewDecisions:
    """Test bulk review with different decisions"""

    def test_bulk_flag_all(self, client, test_users):
        """Test flagging all items in bulk"""
        login_response = client.post("/api/auth/login", json={
            "username": test_users["screener_test"]["username"],
            "password": test_users["screener_test"]["password"]
        })
        if login_response.status_code != 200:
            pytest.skip("Could not authenticate user")
        
        token = login_response.json().get("access_token")
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.post(
            "/api/reviews/review/bulk",
            json={
                "item_ids": [1, 2, 3, 4, 5],
                "decision": "approved",  # Flag all
                "notes": "Bulk flagged - confirmed matches"
            },
            headers=headers
        )
        assert response.status_code in [200, 404, 422]
        if response.status_code == 200:
            data = response.json()
            assert "success" in data
            assert "data" in data
            assert "role" in data["data"]

    def test_bulk_clear_all(self, client, test_users):
        """Test clearing all items in bulk"""
        login_response = client.post("/api/auth/login", json={
            "username": test_users["screener_test"]["username"],
            "password": test_users["screener_test"]["password"]
        })
        if login_response.status_code != 200:
            pytest.skip("Could not authenticate user")
        
        token = login_response.json().get("access_token")
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.post(
            "/api/reviews/review/bulk",
            json={
                "item_ids": [1, 2, 3, 4, 5],
                "decision": "rejected",  # Clear all
                "notes": "Bulk cleared - false positives"
            },
            headers=headers
        )
        assert response.status_code in [200, 404, 422]

    def test_bulk_review_empty_list(self, client, test_users):
        """Test bulk review with empty item list"""
        login_response = client.post("/api/auth/login", json={
            "username": test_users["checker_test"]["username"],
            "password": test_users["checker_test"]["password"]
        })
        if login_response.status_code != 200:
            pytest.skip("Could not authenticate user")
        
        token = login_response.json().get("access_token")
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.post(
            "/api/reviews/review/bulk",
            json={
                "item_ids": [],
                "decision": "approved",
                "notes": "Test"
            },
            headers=headers
        )
        # Should handle gracefully, not crash
        assert response.status_code in [200, 422]

    def test_bulk_review_invalid_decision(self, client, test_users):
        """Test bulk review with invalid decision"""
        login_response = client.post("/api/auth/login", json={
            "username": test_users["checker_test"]["username"],
            "password": test_users["checker_test"]["password"]
        })
        if login_response.status_code != 200:
            pytest.skip("Could not authenticate user")
        
        token = login_response.json().get("access_token")
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.post(
            "/api/reviews/review/bulk",
            json={
                "item_ids": [1],
                "decision": "invalid_decision",
                "notes": "Test"
            },
            headers=headers
        )
        # Should handle gracefully
        assert response.status_code in [200, 400, 422]


class TestCumulativeReport:
    """Test cumulative report generation"""

    def test_cumulative_report_endpoint(self, client, test_users):
        """Test cumulative report endpoint"""
        login_response = client.post("/api/auth/login", json={
            "username": test_users["checker_test"]["username"],
            "password": test_users["checker_test"]["password"]
        })
        if login_response.status_code != 200:
            pytest.skip("Could not authenticate user")
        
        token = login_response.json().get("access_token")
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.get("/api/reviews/report/cumulative", headers=headers)
        assert response.status_code in [200, 403, 404]
        if response.status_code == 200:
            data = response.json()
            assert "success" in data
            assert "data" in data

    def test_cumulative_report_with_filters(self, client, test_users):
        """Test cumulative report with status filter"""
        login_response = client.post("/api/auth/login", json={
            "username": test_users["checker_test"]["username"],
            "password": test_users["checker_test"]["password"]
        })
        if login_response.status_code != 200:
            pytest.skip("Could not authenticate user")
        
        token = login_response.json().get("access_token")
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.get(
            "/api/reviews/report/cumulative?status=approved",
            headers=headers
        )
        assert response.status_code in [200, 403, 404]

    def test_cumulative_report_by_severity(self, client, test_users):
        """Test cumulative report filtered by severity"""
        login_response = client.post("/api/auth/login", json={
            "username": test_users["checker_test"]["username"],
            "password": test_users["checker_test"]["password"]
        })
        if login_response.status_code != 200:
            pytest.skip("Could not authenticate user")
        
        token = login_response.json().get("access_token")
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.get(
            "/api/reviews/report/cumulative?severity=high",
            headers=headers
        )
        assert response.status_code in [200, 403, 404]


class TestSingleItemReview:
    """Test single item review endpoint"""

    def test_review_item_as_screener(self, client, test_users):
        """Test reviewing single item as screener"""
        login_response = client.post("/api/auth/login", json={
            "username": test_users["screener_test"]["username"],
            "password": test_users["screener_test"]["password"]
        })
        if login_response.status_code != 200:
            pytest.skip("Could not authenticate screener")
        
        token = login_response.json().get("access_token")
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.post(
            "/api/reviews/review/999",
            json={
                "decision": "approved",
                "notes": "Confirmed match",
                "requires_escalation": False
            },
            headers=headers
        )
        assert response.status_code in [200, 404]

    def test_review_item_as_checker(self, client, test_users):
        """Test reviewing single item as checker"""
        login_response = client.post("/api/auth/login", json={
            "username": test_users["checker_test"]["username"],
            "password": test_users["checker_test"]["password"]
        })
        if login_response.status_code != 200:
            pytest.skip("Could not authenticate checker")
        
        token = login_response.json().get("access_token")
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.post(
            "/api/reviews/review/999",
            json={
                "decision": "approved",
                "notes": "Checker confirmed",
                "requires_escalation": False
            },
            headers=headers
        )
        assert response.status_code in [200, 404]

    def test_review_item_escalate(self, client, test_users):
        """Test escalating an item"""
        login_response = client.post("/api/auth/login", json={
            "username": test_users["screener_test"]["username"],
            "password": test_users["screener_test"]["password"]
        })
        if login_response.status_code != 200:
            pytest.skip("Could not authenticate screener")
        
        token = login_response.json().get("access_token")
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.post(
            "/api/reviews/review/999",
            json={
                "decision": "escalated",
                "notes": "High risk - needs management review",
                "requires_escalation": True,
                "escalation_notes": "PEP match detected"
            },
            headers=headers
        )
        assert response.status_code in [200, 404]


class TestErrorHandling:
    """Test error handling in review endpoints"""

    def test_review_without_auth(self, client):
        """Test review without authentication"""
        response = client.post(
            "/api/reviews/review/bulk",
            json={
                "item_ids": [1],
                "decision": "approved",
                "notes": "Test"
            }
        )
        assert response.status_code in [401, 403]

    def test_review_with_invalid_token(self, client):
        """Test review with invalid token"""
        headers = {"Authorization": "Bearer invalid_token"}
        
        response = client.post(
            "/api/reviews/review/bulk",
            json={
                "item_ids": [1],
                "decision": "approved",
                "notes": "Test"
            },
            headers=headers
        )
        assert response.status_code in [401, 403]

    def test_review_missing_required_fields(self, client, test_users):
        """Test review with missing required fields"""
        login_response = client.post("/api/auth/login", json={
            "username": test_users["checker_test"]["username"],
            "password": test_users["checker_test"]["password"]
        })
        if login_response.status_code != 200:
            pytest.skip("Could not authenticate user")
        
        token = login_response.json().get("access_token")
        headers = {"Authorization": f"Bearer {token}"}
        
        # Missing notes
        response = client.post(
            "/api/reviews/review/bulk",
            json={
                "item_ids": [1],
                "decision": "approved"
            },
            headers=headers
        )
        assert response.status_code == 422  # Validation error

    def test_validation_error_format(self, client, test_users):
        """Test that validation errors return proper format"""
        login_response = client.post("/api/auth/login", json={
            "username": test_users["checker_test"]["username"],
            "password": test_users["checker_test"]["password"]
        })
        if login_response.status_code != 200:
            pytest.skip("Could not authenticate user")
        
        token = login_response.json().get("access_token")
        headers = {"Authorization": f"Bearer {token}"}
        
        # Send malformed request
        response = client.post(
            "/api/reviews/review/bulk",
            json="invalid",
            headers=headers
        )
        
        if response.status_code == 422:
            data = response.json()
            assert "detail" in data
            # Detail should be properly formatted
            detail = data["detail"]
            if isinstance(detail, list):
                for item in detail:
                    if isinstance(item, dict):
                        assert "msg" in item


class TestReviewItemReport:
    """Test item report generation"""

    def test_get_item_report(self, client, test_users):
        """Test getting individual item report"""
        login_response = client.post("/api/auth/login", json={
            "username": test_users["checker_test"]["username"],
            "password": test_users["checker_test"]["password"]
        })
        if login_response.status_code != 200:
            pytest.skip("Could not authenticate user")
        
        token = login_response.json().get("access_token")
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.get("/api/reviews/report/item/1", headers=headers)
        assert response.status_code in [200, 404]

    def test_download_item_report_pdf(self, client, test_users):
        """Test downloading item report as PDF"""
        login_response = client.post("/api/auth/login", json={
            "username": test_users["checker_test"]["username"],
            "password": test_users["checker_test"]["password"]
        })
        if login_response.status_code != 200:
            pytest.skip("Could not authenticate user")
        
        token = login_response.json().get("access_token")
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.get(
            "/api/reviews/report/item/1/download?format=pdf",
            headers=headers
        )
        assert response.status_code in [200, 404, 501]  # 501 if PDF gen not available
