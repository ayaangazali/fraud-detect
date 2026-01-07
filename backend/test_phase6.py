"""
Phase 6 Test Suite - Email Notifications
Tests for email service, SMTP configuration, and notification triggers
"""
import sys
import os
from datetime import datetime

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.email_service import EmailService, get_email_service


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

def test_email_service_initialization():
    """Test email service initialization"""
    service = EmailService()
    
    print(f"SMTP Host: {service.smtp_host}")
    print(f"SMTP Port: {service.smtp_port}")
    print(f"Email From: {service.email_from}")
    print(f"Email To: {service.email_to}")
    print(f"SMTP Configured: {service.smtp_configured}")
    
    assert service.email_to == "aagazali@kamcoinvest.com", "Should have hardcoded recipient"
    assert service.smtp_host is not None, "Should have SMTP host"
    assert service.smtp_port > 0, "Should have valid SMTP port"
    
    print(f"✅ Email service initialized correctly")


def test_singleton_pattern():
    """Test email service singleton pattern"""
    service1 = get_email_service()
    service2 = get_email_service()
    
    assert service1 is service2, "Should return same instance (singleton)"
    print(f"✅ Singleton pattern working correctly")


def test_screening_alert_email():
    """Test screening alert email generation"""
    service = EmailService()
    
    result = service.send_screening_alert(
        entity_name="Test Company Ltd",
        entity_type="client",
        blacklist_name="محمد أحمد العتيبي",
        match_score=95,
        risk_level="CRITICAL",
        civil_id_match=True
    )
    
    assert result, "Email should be sent/logged successfully"
    print(f"✅ Screening alert email sent/logged")
    
    # Check if email was logged to file
    log_dir = "logs"
    if os.path.exists(log_dir):
        files = os.listdir(log_dir)
        email_files = [f for f in files if f.startswith("email_")]
        print(f"📁 Found {len(email_files)} email log files in {log_dir}/")


def test_flagged_item_notification():
    """Test flagged item notification email"""
    service = EmailService()
    
    result = service.send_flagged_item_notification(
        entity_name="Test Vendor Inc",
        entity_type="vendor",
        reason="High similarity match (92%) with blacklist entry",
        flagged_by="screener_user"
    )
    
    assert result, "Email should be sent/logged successfully"
    print(f"✅ Flagged item notification sent/logged")


def test_case_decision_notification_approved():
    """Test case decision notification (approved)"""
    service = EmailService()
    
    result = service.send_case_decision_notification(
        case_id=123,
        entity_name="Test Company Ltd",
        decision="APPROVED",
        decided_by="finalizer_user",
        notes="False positive - different person with similar name"
    )
    
    assert result, "Email should be sent/logged successfully"
    print(f"✅ Case approval notification sent/logged")


def test_case_decision_notification_rejected():
    """Test case decision notification (rejected)"""
    service = EmailService()
    
    result = service.send_case_decision_notification(
        case_id=456,
        entity_name="Suspicious Entity",
        decision="REJECTED",
        decided_by="finalizer_user",
        notes="Confirmed match with sanctioned individual"
    )
    
    assert result, "Email should be sent/logged successfully"
    print(f"✅ Case rejection notification sent/logged")


def test_upload_completion_notification_success():
    """Test upload completion notification (success)"""
    service = EmailService()
    
    result = service.send_upload_completion_notification(
        total_rows=100,
        valid_rows=100,
        errors_count=0,
        uploaded_by="admin_user",
        filename="blacklist_2026_01.xlsx"
    )
    
    assert result, "Email should be sent/logged successfully"
    print(f"✅ Upload success notification sent/logged")


def test_upload_completion_notification_with_errors():
    """Test upload completion notification (with errors)"""
    service = EmailService()
    
    result = service.send_upload_completion_notification(
        total_rows=100,
        valid_rows=85,
        errors_count=15,
        uploaded_by="admin_user",
        filename="blacklist_2026_01_v2.xlsx"
    )
    
    assert result, "Email should be sent/logged successfully"
    print(f"✅ Upload with errors notification sent/logged")


def test_async_email_sending():
    """Test asynchronous email sending"""
    service = EmailService()
    
    # Send async (should not block)
    result = service.send_screening_alert(
        entity_name="Async Test Entity",
        entity_type="staff",
        blacklist_name="Test Blacklist Entry",
        match_score=88,
        risk_level="HIGH",
        civil_id_match=False
    )
    
    assert result, "Async email should be queued successfully"
    print(f"✅ Async email queued (non-blocking)")
    
    # Give thread time to complete
    import time
    time.sleep(1)
    print(f"✅ Async email sent/logged")


def test_email_log_directory():
    """Test email log directory creation"""
    log_dir = "logs"
    
    # Send an email to trigger log creation
    service = EmailService()
    service.send_screening_alert(
        entity_name="Log Test",
        entity_type="client",
        blacklist_name="Test",
        match_score=75,
        risk_level="MEDIUM",
        civil_id_match=False
    )
    
    import time
    time.sleep(1)  # Wait for async email
    
    assert os.path.exists(log_dir), "Logs directory should be created"
    
    files = os.listdir(log_dir)
    email_files = [f for f in files if f.startswith("email_") and f.endswith(".html")]
    
    print(f"📁 Found {len(email_files)} email log files")
    assert len(email_files) > 0, "Should have email log files"
    
    # Read and verify one file
    if email_files:
        sample_file = os.path.join(log_dir, email_files[0])
        with open(sample_file, 'r', encoding='utf-8') as f:
            content = f.read()
            assert '<!DOCTYPE html>' in content, "Should contain HTML content"
            assert 'aagazali@kamcoinvest.com' in content, "Should contain recipient email"
            print(f"✅ Email log file format verified: {email_files[0]}")


# Main execution

def main():
    """Run all tests"""
    print("="*80)
    print("PHASE 6 TEST SUITE - EMAIL NOTIFICATIONS")
    print("="*80)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"\nNote: Emails will be logged to 'logs/' directory (SMTP not configured)")
    
    runner = TestRunner()
    
    # Run tests
    runner.run_test("Test 1: Email service initialization", test_email_service_initialization)
    runner.run_test("Test 2: Singleton pattern", test_singleton_pattern)
    runner.run_test("Test 3: Screening alert email", test_screening_alert_email)
    runner.run_test("Test 4: Flagged item notification", test_flagged_item_notification)
    runner.run_test("Test 5: Case approval notification", test_case_decision_notification_approved)
    runner.run_test("Test 6: Case rejection notification", test_case_decision_notification_rejected)
    runner.run_test("Test 7: Upload success notification", test_upload_completion_notification_success)
    runner.run_test("Test 8: Upload with errors notification", test_upload_completion_notification_with_errors)
    runner.run_test("Test 9: Async email sending", test_async_email_sending)
    runner.run_test("Test 10: Email log directory", test_email_log_directory)
    
    # Print summary
    runner.print_summary()
    
    print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"\n📧 Check 'logs/' directory for generated email files")
    
    # Return exit code
    return 0 if runner.failed_tests == 0 else 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
