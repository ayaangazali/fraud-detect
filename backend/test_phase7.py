"""
Phase 7 Test Suite - Report Generation
Tests for report service, Excel/CSV/PDF generation, and API endpoints
"""
import sys
import os
from datetime import datetime, timedelta

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.report_schema import ReportFilter
from utils.excel_generator import ExcelGenerator, CSVGenerator
from utils.pdf_generator import PDFGenerator


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

def test_report_filter_creation():
    """Test report filter model creation"""
    filter_obj = ReportFilter(
        date_from=datetime.now() - timedelta(days=7),
        date_to=datetime.now(),
        entity_types=['client', 'vendor'],
        risk_levels=['critical', 'high']
    )
    
    assert filter_obj.date_from is not None, "Should have date_from"
    assert filter_obj.date_to is not None, "Should have date_to"
    assert len(filter_obj.entity_types) == 2, "Should have 2 entity types"
    assert len(filter_obj.risk_levels) == 2, "Should have 2 risk levels"
    
    print(f"✅ Report filter created successfully")


def test_excel_generator_initialization():
    """Test Excel generator initialization"""
    generator = ExcelGenerator()
    
    assert generator.reports_dir == "reports", "Should have reports directory"
    assert generator.wb is not None, "Should have workbook"
    assert os.path.exists(generator.reports_dir), "Reports directory should exist"
    
    print(f"✅ Excel generator initialized")


def test_csv_generator_initialization():
    """Test CSV generator initialization"""
    generator = CSVGenerator()
    
    assert generator.reports_dir == "reports", "Should have reports directory"
    assert os.path.exists(generator.reports_dir), "Reports directory should exist"
    
    print(f"✅ CSV generator initialized")


def test_pdf_generator_initialization():
    """Test PDF generator initialization"""
    generator = PDFGenerator()
    
    assert generator.reports_dir == "reports", "Should have reports directory"
    assert os.path.exists(generator.reports_dir), "Reports directory should exist"
    
    print(f"✅ PDF generator initialized")


def test_excel_screening_summary_generation():
    """Test Excel screening summary report generation"""
    generator = ExcelGenerator()
    
    # Sample data
    data = {
        'total_screenings': 100,
        'total_matches': 25,
        'critical_matches': 5,
        'high_matches': 10,
        'medium_matches': 7,
        'low_matches': 3,
        'match_rate': 25.0,
        'entity_breakdown': {'client': 50, 'vendor': 30, 'staff': 20},
        'top_blacklist_matches': [
            {'name': 'Test Entry 1', 'source': 'UN', 'count': 10, 'avg_score': 85.5},
            {'name': 'Test Entry 2', 'source': 'OFAC', 'count': 8, 'avg_score': 78.2}
        ],
        'screening_trend': [
            {'date': '2026-01-01', 'count': 10, 'matches': 3},
            {'date': '2026-01-02', 'count': 15, 'matches': 5}
        ]
    }
    
    metadata = {
        'title': 'Test Screening Summary',
        'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'generated_by': 'test_user',
        'date_from': '2026-01-01',
        'date_to': '2026-01-07'
    }
    
    filepath = generator.generate_screening_summary_excel(data, metadata)
    
    assert os.path.exists(filepath), "Excel file should be created"
    assert filepath.endswith('.xlsx'), "Should be Excel file"
    assert os.path.getsize(filepath) > 0, "File should not be empty"
    
    print(f"✅ Excel screening summary generated: {filepath}")
    print(f"   File size: {os.path.getsize(filepath)} bytes")


def test_excel_flagged_items_generation():
    """Test Excel flagged items report generation"""
    generator = ExcelGenerator()
    
    data = {
        'total_flagged': 50,
        'pending_count': 15,
        'approved_count': 20,
        'rejected_count': 10,
        'resolved_count': 5,
        'average_resolution_time': 2.5,
        'flags_by_severity': {'critical': 10, 'high': 20, 'medium': 15, 'low': 5},
        'flags_by_category': {'name_match': 30, 'civil_id_match': 20},
        'flags_by_user': {'screener1': 25, 'screener2': 25},
        'flagged_items': [
            {
                'id': 1,
                'kamco_name': 'Test Entity 1',
                'kamco_type': 'client',
                'blacklist_name': 'Match 1',
                'match_score': 85,
                'status': 'pending',
                'severity': 'high',
                'flagged_by': 'screener1',
                'created_at': '2026-01-01T10:00:00'
            }
        ]
    }
    
    metadata = {
        'title': 'Test Flagged Items Report',
        'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'generated_by': 'test_user'
    }
    
    filepath = generator.generate_flagged_items_excel(data, metadata)
    
    assert os.path.exists(filepath), "Excel file should be created"
    assert filepath.endswith('.xlsx'), "Should be Excel file"
    
    print(f"✅ Excel flagged items report generated: {filepath}")


def test_csv_generation():
    """Test CSV file generation"""
    generator = CSVGenerator()
    
    data = [
        {'id': 1, 'name': 'Test 1', 'type': 'client', 'score': 85},
        {'id': 2, 'name': 'Test 2', 'type': 'vendor', 'score': 90}
    ]
    
    headers = ['id', 'name', 'type', 'score']
    
    filepath = generator.generate_csv(data, headers, 'test_report')
    
    assert os.path.exists(filepath), "CSV file should be created"
    assert filepath.endswith('.csv'), "Should be CSV file"
    assert os.path.getsize(filepath) > 0, "File should not be empty"
    
    # Read and verify content
    with open(filepath, 'r') as f:
        content = f.read()
        assert 'id,name,type,score' in content, "Should have headers"
        assert 'Test 1' in content, "Should have data"
    
    print(f"✅ CSV file generated: {filepath}")


def test_pdf_screening_summary_generation():
    """Test PDF screening summary generation"""
    try:
        generator = PDFGenerator()
        
        data = {
            'total_screenings': 100,
            'total_matches': 25,
            'critical_matches': 5,
            'high_matches': 10,
            'medium_matches': 7,
            'low_matches': 3,
            'match_rate': 25.0,
            'entity_breakdown': {'client': 50, 'vendor': 30, 'staff': 20},
            'top_blacklist_matches': [
                {'name': 'Test Entry 1', 'source': 'UN', 'count': 10, 'avg_score': 85.5}
            ],
            'screening_trend': []
        }
        
        metadata = {
            'title': 'Test PDF Report',
            'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'generated_by': 'test_user',
            'date_from': '2026-01-01',
            'date_to': '2026-01-07'
        }
        
        filepath = generator.generate_screening_summary_pdf(data, metadata)
        
        assert os.path.exists(filepath), "PDF file should be created"
        assert filepath.endswith('.pdf'), "Should be PDF file"
        assert os.path.getsize(filepath) > 0, "File should not be empty"
        
        print(f"✅ PDF screening summary generated: {filepath}")
        print(f"   File size: {os.path.getsize(filepath)} bytes")
    
    except ImportError as e:
        print(f"⚠️  PDF generation skipped (ReportLab not installed): {str(e)}")
        # Don't fail the test if ReportLab is not installed
        pass


def test_reports_directory_structure():
    """Test reports directory exists and is writable"""
    reports_dir = "reports"
    
    assert os.path.exists(reports_dir), "Reports directory should exist"
    assert os.path.isdir(reports_dir), "Should be a directory"
    assert os.access(reports_dir, os.W_OK), "Should be writable"
    
    # Count files
    files = os.listdir(reports_dir)
    report_files = [f for f in files if f.endswith(('.xlsx', '.csv', '.pdf'))]
    
    print(f"✅ Reports directory verified")
    print(f"   Total report files: {len(report_files)}")


def test_file_cleanup():
    """Test cleaning up old test files"""
    reports_dir = "reports"
    
    if os.path.exists(reports_dir):
        files = os.listdir(reports_dir)
        test_files = [f for f in files if f.startswith('test_')]
        
        for test_file in test_files:
            try:
                filepath = os.path.join(reports_dir, test_file)
                os.remove(filepath)
                print(f"   Cleaned up: {test_file}")
            except Exception as e:
                print(f"   Could not remove {test_file}: {str(e)}")
    
    print(f"✅ Cleanup completed")


# Main execution

def main():
    """Run all tests"""
    print("="*80)
    print("PHASE 7 TEST SUITE - REPORT GENERATION")
    print("="*80)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    runner = TestRunner()
    
    # Run tests
    runner.run_test("Test 1: Report filter creation", test_report_filter_creation)
    runner.run_test("Test 2: Excel generator initialization", test_excel_generator_initialization)
    runner.run_test("Test 3: CSV generator initialization", test_csv_generator_initialization)
    runner.run_test("Test 4: PDF generator initialization", test_pdf_generator_initialization)
    runner.run_test("Test 5: Excel screening summary generation", test_excel_screening_summary_generation)
    runner.run_test("Test 6: Excel flagged items generation", test_excel_flagged_items_generation)
    runner.run_test("Test 7: CSV generation", test_csv_generation)
    runner.run_test("Test 8: PDF screening summary generation", test_pdf_screening_summary_generation)
    runner.run_test("Test 9: Reports directory structure", test_reports_directory_structure)
    runner.run_test("Test 10: File cleanup", test_file_cleanup)
    
    # Print summary
    runner.print_summary()
    
    print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"\n📊 Check 'reports/' directory for generated test files")
    
    # Return exit code
    return 0 if runner.failed_tests == 0 else 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
