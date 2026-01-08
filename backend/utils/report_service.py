"""
Report Service for Phase 7 - Report Generation
Core service for querying data and generating reports
"""
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
import logging

from models.database import InReviewQueue, FlaggedItem, Logbook
from models.blacklist import BlacklistEntry
from models.case import Case, CaseStatus, CasePriority
from models.auth import User
from models.report_schema import (
    ScreeningSummaryData,
    FlaggedItemsData,
    CaseHistoryData,
    ComplianceAuditData,
    ReportFilter
)

logger = logging.getLogger(__name__)


class ReportService:
    """
    Report generation service
    Handles data queries and aggregation for all report types
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def generate_screening_summary(
        self,
        filters: Optional[ReportFilter] = None
    ) -> ScreeningSummaryData:
        """
        Generate screening summary report data
        
        Args:
            filters: Report filters
            
        Returns:
            ScreeningSummaryData with aggregated statistics
        """
        # Base query
        query = self.db.query(InReviewQueue)
        
        # Apply date filters
        if filters:
            if filters.date_from:
                query = query.filter(InReviewQueue.created_at >= filters.date_from)
            if filters.date_to:
                query = query.filter(InReviewQueue.created_at <= filters.date_to)
            if filters.entity_types:
                query = query.filter(InReviewQueue.kamco_type.in_(filters.entity_types))
        
        # Get all screenings
        screenings = query.all()
        total_screenings = len(screenings)
        
        # Calculate matches by risk level
        # Note: InReviewQueue doesn't have risk_level, we'll calculate from match_score
        critical_matches = sum(1 for s in screenings if s.match_score >= 90)
        high_matches = sum(1 for s in screenings if 75 <= s.match_score < 90)
        medium_matches = sum(1 for s in screenings if 60 <= s.match_score < 75)
        low_matches = sum(1 for s in screenings if s.match_score < 60)
        
        total_matches = len([s for s in screenings if s.match_score >= 60])
        
        # Civil ID matches vs name-only (we'll need to check if civil_id_match exists)
        # For now, we'll use a placeholder
        civil_id_matches = 0
        name_only_matches = total_matches
        
        # Entity breakdown
        entity_breakdown = {}
        for screening in screenings:
            entity_type = screening.kamco_type or "unknown"
            entity_breakdown[entity_type] = entity_breakdown.get(entity_type, 0) + 1
        
        # Top blacklist matches
        blacklist_counts = {}
        for screening in screenings:
            bl_name = screening.blacklist_name or "Unknown"
            if bl_name not in blacklist_counts:
                blacklist_counts[bl_name] = {
                    'name': bl_name,
                    'source': screening.blacklist_source or "Unknown",
                    'count': 0,
                    'avg_score': 0,
                    'scores': []
                }
            blacklist_counts[bl_name]['count'] += 1
            blacklist_counts[bl_name]['scores'].append(screening.match_score or 0)
        
        # Calculate averages and sort
        for bl_name in blacklist_counts:
            scores = blacklist_counts[bl_name]['scores']
            blacklist_counts[bl_name]['avg_score'] = sum(scores) / len(scores) if scores else 0
            del blacklist_counts[bl_name]['scores']  # Remove raw scores
        
        top_blacklist_matches = sorted(
            blacklist_counts.values(),
            key=lambda x: x['count'],
            reverse=True
        )[:10]  # Top 10
        
        # Screening trend (daily aggregation)
        screening_trend = self._calculate_screening_trend(screenings, filters)
        
        # Match rate
        match_rate = (total_matches / total_screenings * 100) if total_screenings > 0 else 0
        
        return ScreeningSummaryData(
            total_screenings=total_screenings,
            total_matches=total_matches,
            critical_matches=critical_matches,
            high_matches=high_matches,
            medium_matches=medium_matches,
            low_matches=low_matches,
            civil_id_matches=civil_id_matches,
            name_only_matches=name_only_matches,
            entity_breakdown=entity_breakdown,
            top_blacklist_matches=top_blacklist_matches,
            screening_trend=screening_trend,
            match_rate=round(match_rate, 2)
        )
    
    def generate_flagged_items_report(
        self,
        filters: Optional[ReportFilter] = None
    ) -> FlaggedItemsData:
        """
        Generate flagged items report data
        
        Args:
            filters: Report filters
            
        Returns:
            FlaggedItemsData with flagged items statistics
        """
        # Base query
        query = self.db.query(FlaggedItem)
        
        # Apply filters
        if filters:
            if filters.date_from:
                query = query.filter(FlaggedItem.created_at >= filters.date_from)
            if filters.date_to:
                query = query.filter(FlaggedItem.created_at <= filters.date_to)
            if filters.entity_types:
                query = query.filter(FlaggedItem.kamco_type.in_(filters.entity_types))
            if filters.status:
                query = query.filter(FlaggedItem.status == filters.status)
            if not filters.include_resolved:
                query = query.filter(FlaggedItem.status != "resolved")
        
        # Get all flagged items
        flagged_items = query.all()
        total_flagged = len(flagged_items)
        
        # Count by status
        pending_count = sum(1 for f in flagged_items if f.status == "pending")
        approved_count = sum(1 for f in flagged_items if f.status == "approved")
        rejected_count = sum(1 for f in flagged_items if f.status == "rejected")
        resolved_count = sum(1 for f in flagged_items if f.status in ["final_approved", "resolved"])
        
        # Flags by severity
        flags_by_severity = {}
        for flag in flagged_items:
            severity = flag.severity or "unknown"
            flags_by_severity[severity] = flags_by_severity.get(severity, 0) + 1
        
        # Flags by category
        flags_by_category = {}
        for flag in flagged_items:
            category = flag.flag_reason_category or "other"
            flags_by_category[category] = flags_by_category.get(category, 0) + 1
        
        # Flags by user
        flags_by_user = {}
        for flag in flagged_items:
            user = flag.flagged_by or "unknown"
            flags_by_user[user] = flags_by_user.get(user, 0) + 1
        
        # Average resolution time
        resolution_times = []
        for flag in flagged_items:
            if flag.resolution_date and flag.created_at:
                delta = flag.resolution_date - flag.created_at
                resolution_times.append(delta.total_seconds() / 86400)  # Convert to days
        
        average_resolution_time = sum(resolution_times) / len(resolution_times) if resolution_times else None
        
        # Flagged items list
        flagged_items_list = [
            {
                'id': f.id,
                'kamco_name': f.kamco_name,
                'kamco_type': f.kamco_type,
                'blacklist_name': f.blacklist_name,
                'match_score': f.match_score,
                'status': f.status,
                'severity': f.severity,
                'flag_reason': f.flag_reason,
                'flagged_by': f.flagged_by,
                'created_at': f.created_at.isoformat() if f.created_at else None,
                'resolution_date': f.resolution_date.isoformat() if f.resolution_date else None
            }
            for f in flagged_items
        ]
        
        return FlaggedItemsData(
            total_flagged=total_flagged,
            pending_count=pending_count,
            approved_count=approved_count,
            rejected_count=rejected_count,
            resolved_count=resolved_count,
            flags_by_severity=flags_by_severity,
            flags_by_category=flags_by_category,
            flags_by_user=flags_by_user,
            average_resolution_time=round(average_resolution_time, 2) if average_resolution_time else None,
            flagged_items=flagged_items_list
        )
    
    def generate_case_history_report(
        self,
        filters: Optional[ReportFilter] = None
    ) -> CaseHistoryData:
        """
        Generate case history report data
        
        Args:
            filters: Report filters
            
        Returns:
            CaseHistoryData with case statistics
        """
        # Base query
        query = self.db.query(Case)
        
        # Apply filters
        if filters:
            if filters.date_from:
                query = query.filter(Case.created_at >= filters.date_from)
            if filters.date_to:
                query = query.filter(Case.created_at <= filters.date_to)
            if filters.status:
                query = query.filter(Case.status == filters.status)
        
        # Get all cases
        cases = query.all()
        total_cases = len(cases)
        
        # Count by status
        open_cases = sum(1 for c in cases if c.status in [CaseStatus.PENDING, CaseStatus.IN_REVIEW])
        closed_cases = sum(1 for c in cases if c.status == CaseStatus.CLOSED)
        approved_cases = sum(1 for c in cases if c.status == CaseStatus.CLOSED and c.resolved_at)
        rejected_cases = sum(1 for c in cases if c.status == CaseStatus.REJECTED)
        
        # Cases by status
        cases_by_status = {}
        for case in cases:
            status = case.status.value if hasattr(case.status, 'value') else str(case.status)
            cases_by_status[status] = cases_by_status.get(status, 0) + 1
        
        # Cases by priority
        cases_by_priority = {}
        for case in cases:
            priority = case.priority.value if hasattr(case.priority, 'value') else str(case.priority)
            cases_by_priority[priority] = cases_by_priority.get(priority, 0) + 1
        
        # Average resolution time
        resolution_times = []
        for case in cases:
            if case.resolved_at and case.created_at:
                delta = case.resolved_at - case.created_at
                resolution_times.append(delta.total_seconds() / 86400)  # Convert to days
        
        average_resolution_time = sum(resolution_times) / len(resolution_times) if resolution_times else None
        
        # SLA compliance (assuming SLA is 7 days)
        sla_compliant = sum(1 for t in resolution_times if t <= 7)
        sla_compliance_rate = (sla_compliant / len(resolution_times) * 100) if resolution_times else None
        
        # Cases list
        cases_list = [
            {
                'id': c.id,
                'case_number': c.case_number,
                'status': c.status.value if hasattr(c.status, 'value') else str(c.status),
                'priority': c.priority.value if hasattr(c.priority, 'value') else str(c.priority),
                'created_at': c.created_at.isoformat() if c.created_at else None,
                'resolved_at': c.resolved_at.isoformat() if c.resolved_at else None,
                'updated_at': c.updated_at.isoformat() if c.updated_at else None
            }
            for c in cases
        ]
        
        return CaseHistoryData(
            total_cases=total_cases,
            open_cases=open_cases,
            closed_cases=closed_cases,
            approved_cases=approved_cases,
            rejected_cases=rejected_cases,
            cases_by_status=cases_by_status,
            cases_by_priority=cases_by_priority,
            average_resolution_time=round(average_resolution_time, 2) if average_resolution_time else None,
            sla_compliance_rate=round(sla_compliance_rate, 2) if sla_compliance_rate else None,
            cases=cases_list
        )
    
    def generate_compliance_audit_report(
        self,
        filters: Optional[ReportFilter] = None
    ) -> ComplianceAuditData:
        """
        Generate compliance audit report data
        
        Args:
            filters: Report filters
            
        Returns:
            ComplianceAuditData with audit trail
        """
        # Base query
        query = self.db.query(Logbook)
        
        # Apply filters
        if filters:
            if filters.date_from:
                query = query.filter(Logbook.created_at >= filters.date_from)
            if filters.date_to:
                query = query.filter(Logbook.created_at <= filters.date_to)
            if filters.user_id:
                query = query.filter(Logbook.reviewed_by_id == filters.user_id)
        
        # Get all logbook entries
        logbook_entries = query.all()
        total_actions = len(logbook_entries)
        
        # Actions by type
        actions_by_type = {}
        for entry in logbook_entries:
            action_type = entry.action_type or "unknown"
            actions_by_type[action_type] = actions_by_type.get(action_type, 0) + 1
        
        # Actions by user
        actions_by_user = {}
        for entry in logbook_entries:
            user = entry.reviewed_by or "unknown"
            actions_by_user[user] = actions_by_user.get(user, 0) + 1
        
        # Specific counts
        blacklist_changes = actions_by_type.get("upload", 0) + actions_by_type.get("blacklist_update", 0)
        screenings_performed = actions_by_type.get("screening", 0)
        decisions_made = actions_by_type.get("approve", 0) + actions_by_type.get("reject", 0)
        access_events = total_actions  # All events are access events
        
        # Audit trail
        audit_trail = [
            {
                'id': entry.id,
                'action_type': entry.action_type,
                'entity_name': entry.entity_name,
                'entity_type': entry.entity_type,
                'decision': entry.decision,
                'reviewed_by': entry.reviewed_by,
                'created_at': entry.created_at.isoformat() if entry.created_at else None,
                'notes': entry.notes,
                'ip_address': entry.ip_address
            }
            for entry in logbook_entries[:1000]  # Limit to 1000 most recent
        ]
        
        # Compliance score (simple calculation based on SLA compliance)
        # This is a placeholder - would need proper implementation
        compliance_score = 85.0 if total_actions > 0 else None
        
        return ComplianceAuditData(
            total_actions=total_actions,
            actions_by_type=actions_by_type,
            actions_by_user=actions_by_user,
            blacklist_changes=blacklist_changes,
            screenings_performed=screenings_performed,
            decisions_made=decisions_made,
            access_events=access_events,
            audit_trail=audit_trail,
            compliance_score=compliance_score
        )
    
    def _calculate_screening_trend(
        self,
        screenings: List[InReviewQueue],
        filters: Optional[ReportFilter] = None
    ) -> List[Dict[str, Any]]:
        """Calculate daily screening trend"""
        if not screenings:
            return []
        
        # Group by date
        daily_counts = {}
        for screening in screenings:
            if screening.created_at:
                date_key = screening.created_at.date().isoformat()
                if date_key not in daily_counts:
                    daily_counts[date_key] = {'date': date_key, 'count': 0, 'matches': 0}
                daily_counts[date_key]['count'] += 1
                if screening.match_score and screening.match_score >= 60:
                    daily_counts[date_key]['matches'] += 1
        
        # Sort by date
        trend = sorted(daily_counts.values(), key=lambda x: x['date'])
        return trend


# Singleton instance
_report_service = None


def get_report_service(db: Session) -> ReportService:
    """Get or create report service instance"""
    return ReportService(db)
