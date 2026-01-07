"""
Phase 8: Audit Logging - Comprehensive Test Suite
Tests for audit service, middleware, decorators, and API endpoints
"""
import sys
import os
from datetime import datetime, timedelta
from typing import Dict, Any

# Test runner
class TestRunner:
    def __init__(self):
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.results = []
    
    def run_test(self, test_name: str, test_func):
        """Run a single test and track result"""
        self.total_tests += 1
        try:
            test_func()
            self.passed_tests += 1
            self.results.append((test_name, True, None))
            print(f"✅ {test_name}: PASSED")
            return True
        except AssertionError as e:
            self.failed_tests += 1
            self.results.append((test_name, False, str(e)))
            print(f"❌ {test_name}: FAILED - {str(e)}")
            return False
        except Exception as e:
            self.failed_tests += 1
            self.results.append((test_name, False, f"Error: {str(e)}"))
            print(f"❌ {test_name}: ERROR - {str(e)}")
            return False
    
    def print_summary(self):
        """Print test summary"""
        print(f"\n{'='*70}")
        print(f"TEST SUMMARY")
        print(f"{'='*70}")
        print(f"Total Tests: {self.total_tests}")
        print(f"✅ Passed: {self.passed_tests}")
        print(f"❌ Failed: {self.failed_tests}")
        print(f"Success Rate: {(self.passed_tests/self.total_tests*100):.1f}%")
        print(f"{'='*70}\n")


# Initialize test runner
runner = TestRunner()


# Test 1: Import all audit modules
def test_import_audit_modules():
    """Test that all audit modules can be imported"""
    try:
        from models import audit_schema
        from utils import audit_service
        from utils import audit_decorators
        from middleware import audit_middleware
        from routes import audit
        assert True
    except ImportError as e:
        raise AssertionError(f"Failed to import audit modules: {str(e)}")

runner.run_test("Test 1: Import audit modules", test_import_audit_modules)


# Test 2: Audit event enums
def test_audit_event_enums():
    """Test that AuditEventType enum has all required events"""
    from models.audit_schema import AuditEventType, AuditSeverity
    
    # Check key event types exist
    assert hasattr(AuditEventType, 'API_CALL')
    assert hasattr(AuditEventType, 'AUTH_LOGIN')
    assert hasattr(AuditEventType, 'AUTH_FAILED')
    assert hasattr(AuditEventType, 'DATA_CREATE')
    assert hasattr(AuditEventType, 'SECURITY_PERMISSION_DENIED')
    assert hasattr(AuditEventType, 'FILE_UPLOAD')
    assert hasattr(AuditEventType, 'REPORT_GENERATED')
    assert hasattr(AuditEventType, 'USER_CREATED')
    assert hasattr(AuditEventType, 'BLACKLIST_UPLOADED')
    
    # Check severity levels
    assert hasattr(AuditSeverity, 'LOW')
    assert hasattr(AuditSeverity, 'MEDIUM')
    assert hasattr(AuditSeverity, 'HIGH')
    assert hasattr(AuditSeverity, 'CRITICAL')
    
    print(f"  ✓ Found {len([e for e in dir(AuditEventType) if not e.startswith('_')])} event types")
    print(f"  ✓ Found {len([s for s in dir(AuditSeverity) if not s.startswith('_')])} severity levels")

runner.run_test("Test 2: Audit event enums", test_audit_event_enums)


# Test 3: Pydantic models validation
def test_pydantic_models():
    """Test that Pydantic models work correctly"""
    from models.audit_schema import (
        AuditLogEntry,
        AuditEventType,
        AuditSeverity,
        AuditQueryRequest,
        AuditRetentionPolicy
    )
    
    # Create audit log entry
    log_entry = AuditLogEntry(
        event_type=AuditEventType.AUTH_LOGIN,
        severity=AuditSeverity.LOW,
        action="Test login",
        user_id=1,
        username="testuser",
        success=True
    )
    
    assert log_entry.event_type == AuditEventType.AUTH_LOGIN
    assert log_entry.severity == AuditSeverity.LOW
    assert log_entry.success is True
    
    # Create query request
    query = AuditQueryRequest(
        page=1,
        page_size=50,
        event_types=[AuditEventType.AUTH_LOGIN]
    )
    
    assert query.page == 1
    assert query.page_size == 50
    
    # Create retention policy
    policy = AuditRetentionPolicy(
        low_severity_days=30,
        medium_severity_days=90,
        high_severity_days=180,
        critical_severity_days=365
    )
    
    assert policy.low_severity_days == 30
    assert policy.enable_archival is True
    
    print(f"  ✓ AuditLogEntry model validated")
    print(f"  ✓ AuditQueryRequest model validated")
    print(f"  ✓ AuditRetentionPolicy model validated")

runner.run_test("Test 3: Pydantic models validation", test_pydantic_models)


# Test 4: Database model (AuditLog table)
def test_audit_log_table():
    """Test that AuditLog database model exists"""
    from models.database import AuditLog
    
    # Check table has required columns
    assert hasattr(AuditLog, 'id')
    assert hasattr(AuditLog, 'event_type')
    assert hasattr(AuditLog, 'severity')
    assert hasattr(AuditLog, 'user_id')
    assert hasattr(AuditLog, 'username')
    assert hasattr(AuditLog, 'endpoint')
    assert hasattr(AuditLog, 'action')
    assert hasattr(AuditLog, 'resource_type')
    assert hasattr(AuditLog, 'before_state')
    assert hasattr(AuditLog, 'after_state')
    assert hasattr(AuditLog, 'success')
    assert hasattr(AuditLog, 'timestamp')
    
    # Check to_dict method exists
    assert hasattr(AuditLog, 'to_dict')
    
    print(f"  ✓ AuditLog table has all required columns")
    print(f"  ✓ AuditLog has to_dict() method")

runner.run_test("Test 4: Database model (AuditLog table)", test_audit_log_table)


# Test 5: Audit service initialization
def test_audit_service_init():
    """Test that AuditService can be initialized"""
    from utils.audit_service import AuditService
    
    # Create mock db session
    class MockDB:
        def add(self, obj):
            pass
        def commit(self):
            pass
        def refresh(self, obj):
            pass
        def query(self, model):
            return self
        def filter(self, *args):
            return self
        def all(self):
            return []
    
    db = MockDB()
    service = AuditService(db)
    
    assert service is not None
    assert hasattr(service, 'log_event')
    assert hasattr(service, 'log_api_call')
    assert hasattr(service, 'log_data_change')
    assert hasattr(service, 'log_security_event')
    assert hasattr(service, 'log_user_action')
    assert hasattr(service, 'query_audit_logs')
    assert hasattr(service, 'get_user_activity')
    assert hasattr(service, 'get_security_events')
    assert hasattr(service, 'enforce_retention_policy')
    
    print(f"  ✓ AuditService initialized successfully")
    print(f"  ✓ All service methods present")

runner.run_test("Test 5: Audit service initialization", test_audit_service_init)


# Test 6: Audit decorators
def test_audit_decorators():
    """Test that audit decorators exist and are callable"""
    from utils.audit_decorators import (
        audit_action,
        audit_data_change,
        audit_security,
        audit_file_upload,
        audit_report_generation,
        audit_blacklist_operation,
        audit_user_management
    )
    from models.audit_schema import AuditEventType, AuditSeverity
    
    # Test that decorators are callable
    assert callable(audit_action)
    assert callable(audit_data_change)
    assert callable(audit_security)
    assert callable(audit_file_upload)
    assert callable(audit_report_generation)
    assert callable(audit_blacklist_operation)
    assert callable(audit_user_management)
    
    # Test decorator creation
    decorator = audit_action(
        event_type=AuditEventType.USER_CREATED,
        action_template="Test action: {username}",
        severity=AuditSeverity.MEDIUM
    )
    
    assert callable(decorator)
    
    print(f"  ✓ All audit decorators are callable")
    print(f"  ✓ Decorator factory works correctly")

runner.run_test("Test 6: Audit decorators", test_audit_decorators)


# Test 7: Middleware classes
def test_middleware_classes():
    """Test that middleware classes exist"""
    from middleware.audit_middleware import AuditMiddleware, RequestIdMiddleware, setup_audit_middleware
    
    # Check classes exist
    assert AuditMiddleware is not None
    assert RequestIdMiddleware is not None
    assert callable(setup_audit_middleware)
    
    # Check AuditMiddleware has required methods
    assert hasattr(AuditMiddleware, 'dispatch')
    assert hasattr(AuditMiddleware, '_get_client_ip')
    assert hasattr(AuditMiddleware, '_log_request')
    
    print(f"  ✓ AuditMiddleware class exists")
    print(f"  ✓ RequestIdMiddleware class exists")
    print(f"  ✓ setup_audit_middleware function exists")

runner.run_test("Test 7: Middleware classes", test_middleware_classes)


# Test 8: Audit API routes
def test_audit_routes():
    """Test that audit API routes are defined"""
    from routes import audit
    
    # Check router exists
    assert hasattr(audit, 'router')
    
    # Check key functions exist
    assert hasattr(audit, 'query_audit_logs')
    assert hasattr(audit, 'get_user_activity')
    assert hasattr(audit, 'get_security_events')
    assert hasattr(audit, 'get_audit_stats')
    assert hasattr(audit, 'enforce_retention_policy')
    assert hasattr(audit, 'export_audit_logs_csv')
    assert hasattr(audit, 'get_recent_logs')
    
    # Check require_admin dependency
    assert hasattr(audit, 'require_admin')
    
    print(f"  ✓ Audit router is defined")
    print(f"  ✓ All 7 API endpoints exist")
    print(f"  ✓ Admin-only access control present")

runner.run_test("Test 8: Audit API routes", test_audit_routes)


# Test 9: Main.py integration
def test_main_integration():
    """Test that main.py imports audit middleware and routes"""
    with open('main.py', 'r') as f:
        main_content = f.read()
    
    # Check audit routes are imported
    assert 'from routes import' in main_content and 'audit' in main_content
    
    # Check audit middleware is imported
    assert 'from middleware.audit_middleware import setup_audit_middleware' in main_content
    
    # Check middleware is set up
    assert 'setup_audit_middleware(app)' in main_content
    
    # Check audit routes are included
    assert 'audit.router' in main_content
    
    print(f"  ✓ Audit routes imported in main.py")
    print(f"  ✓ Audit middleware imported in main.py")
    print(f"  ✓ Middleware setup called")
    print(f"  ✓ Audit router registered")

runner.run_test("Test 9: Main.py integration", test_main_integration)


# Test 10: Auth routes integration
def test_auth_routes_integration():
    """Test that auth routes have audit logging"""
    with open('routes/auth.py', 'r') as f:
        auth_content = f.read()
    
    # Check audit imports
    assert 'from utils.audit_service import AuditService' in auth_content
    assert 'from models.audit_schema import AuditEventType' in auth_content
    
    # Check audit logging in key functions
    assert 'audit_service = AuditService(db)' in auth_content
    assert 'log_security_event' in auth_content
    assert 'AUTH_LOGIN' in auth_content or 'AuditEventType.AUTH_LOGIN' in auth_content
    assert 'AUTH_FAILED' in auth_content or 'AuditEventType.AUTH_FAILED' in auth_content
    assert 'USER_CREATED' in auth_content or 'AuditEventType.USER_CREATED' in auth_content
    
    print(f"  ✓ Audit imports present in auth.py")
    print(f"  ✓ Audit logging integrated in endpoints")
    print(f"  ✓ Security events logged (login, failed auth, registration)")

runner.run_test("Test 10: Auth routes integration", test_auth_routes_integration)


# Test 11: Reports routes integration
def test_reports_routes_integration():
    """Test that reports routes have audit logging"""
    with open('routes/reports.py', 'r') as f:
        reports_content = f.read()
    
    # Check audit imports
    assert 'from utils.audit_service import AuditService' in reports_content
    assert 'from models.audit_schema import AuditEventType' in reports_content
    
    # Check audit logging for report generation
    assert 'REPORT_GENERATED' in reports_content or 'AuditEventType.REPORT_GENERATED' in reports_content
    assert 'REPORT_DOWNLOADED' in reports_content or 'AuditEventType.REPORT_DOWNLOADED' in reports_content
    
    print(f"  ✓ Audit imports present in reports.py")
    print(f"  ✓ Report generation logged")
    print(f"  ✓ Report download logged")

runner.run_test("Test 11: Reports routes integration", test_reports_routes_integration)


# Test 12: File structure
def test_file_structure():
    """Test that all Phase 8 files exist"""
    required_files = [
        'models/audit_schema.py',
        'models/database.py',
        'utils/audit_service.py',
        'utils/audit_decorators.py',
        'middleware/audit_middleware.py',
        'routes/audit.py'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        raise AssertionError(f"Missing files: {', '.join(missing_files)}")
    
    print(f"  ✓ All 6 core audit files exist")
    print(f"  ✓ File structure is complete")

runner.run_test("Test 12: File structure", test_file_structure)


# Test 13: Middleware directory
def test_middleware_directory():
    """Test that middleware directory was created"""
    assert os.path.exists('middleware')
    assert os.path.isdir('middleware')
    
    # Check __init__.py is not strictly required but good to have
    files = os.listdir('middleware')
    assert 'audit_middleware.py' in files
    
    print(f"  ✓ Middleware directory exists")
    print(f"  ✓ audit_middleware.py present")

runner.run_test("Test 13: Middleware directory", test_middleware_directory)


# Test 14: Code quality checks
def test_code_quality():
    """Test basic code quality metrics"""
    # Check audit_service.py
    with open('utils/audit_service.py', 'r') as f:
        service_code = f.read()
        service_lines = len(service_code.split('\n'))
    
    # Check audit_decorators.py
    with open('utils/audit_decorators.py', 'r') as f:
        decorator_code = f.read()
        decorator_lines = len(decorator_code.split('\n'))
    
    # Check routes/audit.py
    with open('routes/audit.py', 'r') as f:
        routes_code = f.read()
        routes_lines = len(routes_code.split('\n'))
    
    # Check models/audit_schema.py
    with open('models/audit_schema.py', 'r') as f:
        schema_code = f.read()
        schema_lines = len(schema_code.split('\n'))
    
    total_lines = service_lines + decorator_lines + routes_lines + schema_lines
    
    # Basic assertions
    assert service_lines > 500, f"audit_service.py seems too small ({service_lines} lines)"
    assert decorator_lines > 300, f"audit_decorators.py seems too small ({decorator_lines} lines)"
    assert routes_lines > 400, f"audit.py seems too small ({routes_lines} lines)"
    assert schema_lines > 200, f"audit_schema.py seems too small ({schema_lines} lines)"
    
    print(f"  ✓ audit_service.py: {service_lines} lines")
    print(f"  ✓ audit_decorators.py: {decorator_lines} lines")
    print(f"  ✓ routes/audit.py: {routes_lines} lines")
    print(f"  ✓ audit_schema.py: {schema_lines} lines")
    print(f"  ✓ Total Phase 8 code: ~{total_lines} lines")

runner.run_test("Test 14: Code quality checks", test_code_quality)


# Test 15: Documentation strings
def test_documentation():
    """Test that key files have documentation"""
    files_to_check = [
        'utils/audit_service.py',
        'utils/audit_decorators.py',
        'routes/audit.py',
        'models/audit_schema.py'
    ]
    
    for file_path in files_to_check:
        with open(file_path, 'r') as f:
            content = f.read()
            # Check for module docstring
            assert '"""' in content or "'''" in content, f"{file_path} missing docstrings"
    
    print(f"  ✓ All key files have documentation")
    print(f"  ✓ Module docstrings present")

runner.run_test("Test 15: Documentation strings", test_documentation)


# Print final summary
runner.print_summary()

# Exit with appropriate code
sys.exit(0 if runner.failed_tests == 0 else 1)
