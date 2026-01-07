"""
Phase 8 Verification Script
Checks all Phase 8 components for consistency and correctness
"""
import sys
import os

# Add backend to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def check_imports():
    """Verify all imports work correctly"""
    print("✓ Checking imports...")
    
    try:
        from models.audit_schema import (
            AuditEventType, AuditSeverity, AuditLogEntry,
            AuditQueryRequest, AuditLogResponse
        )
        print("  ✓ models.audit_schema imports OK")
    except Exception as e:
        print(f"  ✗ models.audit_schema import failed: {e}")
        return False
    
    try:
        from models.database import AuditLog
        print("  ✓ models.database.AuditLog import OK")
    except Exception as e:
        print(f"  ✗ models.database.AuditLog import failed: {e}")
        return False
    
    try:
        from utils.audit_service import AuditService, get_audit_service
        print("  ✓ utils.audit_service imports OK")
    except Exception as e:
        print(f"  ✗ utils.audit_service import failed: {e}")
        return False
    
    try:
        from middleware.audit_middleware import AuditMiddleware, setup_audit_middleware
        print("  ✓ middleware.audit_middleware imports OK")
    except Exception as e:
        print(f"  ✗ middleware.audit_middleware import failed: {e}")
        return False
    
    try:
        from utils.audit_decorators import (
            audit_action, audit_data_change, audit_security
        )
        print("  ✓ utils.audit_decorators imports OK")
    except Exception as e:
        print(f"  ✗ utils.audit_decorators import failed: {e}")
        return False
    
    try:
        from routes import audit
        print("  ✓ routes.audit import OK")
    except Exception as e:
        print(f"  ✗ routes.audit import failed: {e}")
        return False
    
    return True


def check_database_model():
    """Verify AuditLog database model"""
    print("\n✓ Checking AuditLog database model...")
    
    try:
        from models.database import AuditLog
        from sqlalchemy import inspect
        
        # Check if table has expected columns
        expected_columns = [
            'id', 'event_type', 'severity', 'user_id', 'username', 'user_role',
            'endpoint', 'http_method', 'ip_address', 'user_agent', 'action',
            'resource_type', 'resource_id', 'before_state', 'after_state',
            'metadata_json', 'tags', 'success', 'error_message', 
            'execution_time_ms', 'timestamp'
        ]
        
        # Note: We can't check actual columns without a database instance
        # Just verify the class has the right attributes
        for col in expected_columns:
            if not hasattr(AuditLog, col):
                print(f"  ✗ Missing column: {col}")
                return False
        
        print(f"  ✓ All {len(expected_columns)} columns present")
        
        # Check to_dict method exists
        if not hasattr(AuditLog, 'to_dict'):
            print("  ✗ Missing to_dict method")
            return False
        
        print("  ✓ to_dict method exists")
        return True
        
    except Exception as e:
        print(f"  ✗ Database model check failed: {e}")
        return False


def check_enum_values():
    """Verify enum values are correct"""
    print("\n✓ Checking enum values...")
    
    try:
        from models.audit_schema import AuditEventType, AuditSeverity
        
        # Check AuditEventType has expected values
        expected_event_types = [
            'API_CALL', 'AUTH_LOGIN', 'AUTH_FAILED', 'DATA_CREATE',
            'SECURITY_PERMISSION_DENIED', 'FILE_UPLOAD', 'REPORT_GENERATED',
            'USER_CREATED', 'BLACKLIST_UPLOADED'
        ]
        
        for event_type in expected_event_types:
            if not hasattr(AuditEventType, event_type):
                print(f"  ✗ Missing event type: {event_type}")
                return False
        
        print(f"  ✓ Key AuditEventType values present")
        
        # Check AuditSeverity
        expected_severities = ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']
        for severity in expected_severities:
            if not hasattr(AuditSeverity, severity):
                print(f"  ✗ Missing severity: {severity}")
                return False
        
        print(f"  ✓ All AuditSeverity values present")
        return True
        
    except Exception as e:
        print(f"  ✗ Enum check failed: {e}")
        return False


def check_service_methods():
    """Verify AuditService has required methods"""
    print("\n✓ Checking AuditService methods...")
    
    try:
        from utils.audit_service import AuditService
        
        expected_methods = [
            'log_event', 'log_api_call', 'log_data_change',
            'log_security_event', 'log_user_action', 'query_audit_logs',
            'get_user_activity', 'get_security_events', 'enforce_retention_policy'
        ]
        
        for method in expected_methods:
            if not hasattr(AuditService, method):
                print(f"  ✗ Missing method: {method}")
                return False
        
        print(f"  ✓ All {len(expected_methods)} methods present")
        return True
        
    except Exception as e:
        print(f"  ✗ Service methods check failed: {e}")
        return False


def check_api_endpoints():
    """Verify audit API endpoints"""
    print("\n✓ Checking audit API endpoints...")
    
    try:
        from routes import audit
        
        # Check router exists
        if not hasattr(audit, 'router'):
            print("  ✗ Missing router")
            return False
        
        print("  ✓ Router exists")
        
        # Check that key endpoint functions exist
        expected_endpoints = [
            'query_audit_logs', 'get_user_activity', 'get_security_events',
            'get_audit_stats', 'enforce_retention_policy', 'export_audit_logs_csv',
            'get_recent_logs'
        ]
        
        for endpoint in expected_endpoints:
            if not hasattr(audit, endpoint):
                print(f"  ✗ Missing endpoint: {endpoint}")
                return False
        
        print(f"  ✓ All {len(expected_endpoints)} endpoints present")
        return True
        
    except Exception as e:
        print(f"  ✗ API endpoints check failed: {e}")
        return False


def check_middleware():
    """Verify middleware setup"""
    print("\n✓ Checking middleware...")
    
    try:
        from middleware.audit_middleware import AuditMiddleware, setup_audit_middleware
        
        print("  ✓ AuditMiddleware class exists")
        print("  ✓ setup_audit_middleware function exists")
        
        # Check AuditMiddleware has dispatch method
        if not hasattr(AuditMiddleware, 'dispatch'):
            print("  ✗ Missing dispatch method")
            return False
        
        print("  ✓ dispatch method exists")
        return True
        
    except Exception as e:
        print(f"  ✗ Middleware check failed: {e}")
        return False


def check_decorators():
    """Verify decorator functions"""
    print("\n✓ Checking decorators...")
    
    try:
        from utils.audit_decorators import (
            audit_action, audit_data_change, audit_security,
            audit_file_upload, audit_report_generation
        )
        
        print("  ✓ All decorator functions present")
        return True
        
    except Exception as e:
        print(f"  ✗ Decorators check failed: {e}")
        return False


def check_integration():
    """Verify integration with existing routes"""
    print("\n✓ Checking integration with existing routes...")
    
    try:
        # Check auth.py has audit logging
        with open('routes/auth.py', 'r') as f:
            content = f.read()
            if 'audit_service' not in content:
                print("  ✗ auth.py missing audit integration")
                return False
            print("  ✓ auth.py has audit logging")
        
        # Check reports.py has audit logging
        with open('routes/reports.py', 'r') as f:
            content = f.read()
            if 'audit_service' not in content:
                print("  ✗ reports.py missing audit integration")
                return False
            print("  ✓ reports.py has audit logging")
        
        # Check main.py has audit middleware
        with open('main.py', 'r') as f:
            content = f.read()
            if 'setup_audit_middleware' not in content:
                print("  ✗ main.py missing audit middleware setup")
                return False
            if 'audit.router' not in content:
                print("  ✗ main.py missing audit router registration")
                return False
            print("  ✓ main.py has audit middleware and router")
        
        return True
        
    except Exception as e:
        print(f"  ✗ Integration check failed: {e}")
        return False


def main():
    """Run all verification checks"""
    print("="*70)
    print("PHASE 8 AUDIT LOGGING - COMPREHENSIVE VERIFICATION")
    print("="*70)
    
    checks = [
        ("Imports", check_imports),
        ("Database Model", check_database_model),
        ("Enum Values", check_enum_values),
        ("Service Methods", check_service_methods),
        ("API Endpoints", check_api_endpoints),
        ("Middleware", check_middleware),
        ("Decorators", check_decorators),
        ("Integration", check_integration)
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n✗ {name} check crashed: {e}")
            results.append((name, False))
    
    print("\n" + "="*70)
    print("VERIFICATION SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status} - {name}")
    
    print(f"\nTotal: {passed}/{total} checks passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 ALL CHECKS PASSED! Phase 8 is ready for deployment.")
        return 0
    else:
        print(f"\n⚠️  {total-passed} check(s) failed. Please review the issues above.")
        return 1


if __name__ == "__main__":
    exit(main())
