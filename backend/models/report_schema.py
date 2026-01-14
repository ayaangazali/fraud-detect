"""
Report Schema Models for Phase 7 - Report Generation
Pydantic models for API requests/responses and data structures
"""
from enum import Enum
from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel


class ReportTypeEnum(str, Enum):
    """Report type enumeration for API"""
    SCREENING_SUMMARY = "screening_summary"
    FLAGGED_ITEMS = "flagged_items"
    CASE_HISTORY = "case_history"
    COMPLIANCE_AUDIT = "compliance_audit"


class ReportFormatEnum(str, Enum):
    """Report export format"""
    PDF = "pdf"
    EXCEL = "excel"
    CSV = "csv"


class ReportFilter(BaseModel):
    """Report filter configuration"""
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    entity_types: Optional[List[str]] = None  # clients, vendors, staff, others
    risk_levels: Optional[List[str]] = None   # critical, high, medium, low
    user_id: Optional[int] = None             # Filter by specific user
    status: Optional[str] = None              # For flagged items/cases
    include_resolved: bool = True
    include_archived: bool = False


class ReportGenerationRequest(BaseModel):
    """Report generation request"""
    report_type: ReportTypeEnum
    report_format: ReportFormatEnum
    filters: Optional[ReportFilter] = None
    title: Optional[str] = None
    description: Optional[str] = None
    include_charts: bool = True
    include_summary: bool = True
    language: str = "en"  # en or ar


class ReportMetadataResponse(BaseModel):
    """Report metadata response"""
    report_id: str
    report_type: str
    report_format: str
    title: str
    generated_at: str
    generated_by: str
    date_range: Optional[Dict[str, str]] = None
    filters_applied: Optional[Dict[str, Any]] = None
    total_records: int
    file_path: str
    file_size: int  # in bytes
    download_url: str
    status: str


# Report Data Models

class ScreeningSummaryData(BaseModel):
    """Data structure for screening summary report"""
    total_screenings: int
    total_matches: int
    total_flagged: int = 0  # Items flagged by screener
    approved: int = 0  # Items approved
    pending_review: int = 0  # Items pending checker review
    critical_matches: int
    high_matches: int
    medium_matches: int
    low_matches: int
    civil_id_matches: int
    name_only_matches: int
    entity_breakdown: Dict[str, int]  # {client: 10, vendor: 5, ...}
    top_blacklist_matches: List[Dict[str, Any]]
    screening_trend: List[Dict[str, Any]]  # Daily/weekly aggregation
    match_rate: float  # percentage


class FlaggedItemsData(BaseModel):
    """Data structure for flagged items report"""
    total_flagged: int
    pending_count: int
    approved_count: int
    rejected_count: int
    resolved_count: int
    flags_by_severity: Dict[str, int]
    flags_by_category: Dict[str, int]
    flags_by_user: Dict[str, int]
    average_resolution_time: Optional[float] = None  # in days
    flagged_items: List[Dict[str, Any]]


class CaseHistoryData(BaseModel):
    """Data structure for case history report"""
    total_cases: int
    open_cases: int
    closed_cases: int
    approved_cases: int
    rejected_cases: int
    cases_by_status: Dict[str, int]
    cases_by_priority: Dict[str, int]
    average_resolution_time: Optional[float] = None
    sla_compliance_rate: Optional[float] = None
    cases: List[Dict[str, Any]]


class ComplianceAuditData(BaseModel):
    """Data structure for compliance audit report"""
    total_actions: int
    actions_by_type: Dict[str, int]
    actions_by_user: Dict[str, int]
    blacklist_changes: int
    screenings_performed: int
    decisions_made: int
    access_events: int
    audit_trail: List[Dict[str, Any]]
    compliance_score: Optional[float] = None


# Chart Data Models

class ChartData(BaseModel):
    """Chart/visualization data"""
    chart_type: str  # bar, line, pie, etc.
    title: str
    labels: List[str]
    datasets: List[Dict[str, Any]]  # {label, data, backgroundColor, etc.}


class ReportSummary(BaseModel):
    """Executive summary for reports"""
    key_metrics: Dict[str, Any]
    highlights: List[str]
    alerts: List[str]
    recommendations: List[str]
    risk_overview: Optional[Dict[str, int]] = None
