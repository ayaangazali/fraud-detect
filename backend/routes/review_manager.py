"""
Review Management Routes
Handles flagged item review, notes, reports, and email notifications
"""
from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel

from database.connection import get_db
from models.database import FlaggedItem, KamcoClient, KamcoVendor, KamcoStaff, KamcoOther, Logbook
from models.blacklist import BlacklistEntry
from models.auth import User
from utils.auth import get_current_active_user
from utils.logbook import log_action
from utils.email_service import get_email_service

router = APIRouter()

# Pydantic models for request/response
class ReviewDecision(BaseModel):
    decision: str  # 'approved', 'rejected', 'escalated'
    notes: str
    requires_escalation: bool = False
    escalation_notes: Optional[str] = None

class BulkReviewRequest(BaseModel):
    item_ids: List[int]
    decision: str
    notes: str

class EmailReportRequest(BaseModel):
    item_ids: Optional[List[int]] = None  # If None, sends all pending/reviewed
    recipients: List[str]
    include_summary: bool = True
    include_individual_reports: bool = True

# ===== REVIEW ENDPOINTS =====

@router.post("/review/{item_id}")
async def review_flagged_item(
    item_id: int,
    review: ReviewDecision,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Review a flagged item with decision and notes
    
    Decisions:
    - approved: Confirm the flag (entity is truly a match)
    - rejected: Clear the flag (false positive)
    - escalated: Needs higher-level review
    """
    # Get flagged item
    item = db.query(FlaggedItem).filter(FlaggedItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Flagged item not found")
    
    # Store previous status
    previous_status = item.status
    
    # Update based on decision
    if review.decision == 'approved':
        item.status = 'approved'
        item.resolution_type = 'flagged'
        item.resolved_at = datetime.now()
    elif review.decision == 'rejected':
        item.status = 'rejected'
        item.resolution_type = 'cleared'
        item.resolved_at = datetime.now()
    elif review.decision == 'escalated':
        item.status = 'escalated'
        item.escalated_at = datetime.now()
        item.escalation_level = 'management'
    else:
        raise HTTPException(status_code=400, detail="Invalid decision type")
    
    # Update review info
    item.reviewed_at = datetime.now()
    item.checker_id = current_user.id
    item.checker_reviewed_at = datetime.now()
    item.checker_notes = review.notes
    item.review_notes = review.notes  # Legacy field
    
    # Handle escalation
    if review.requires_escalation:
        item.requires_compliance_approval = True
        item.compliance_notes = review.escalation_notes
        item.escalation_level = 'compliance'
    
    db.commit()
    db.refresh(item)
    
    # Log the action
    log_action(
        db=db,
        user_id=current_user.id,
        action=f"REVIEW_{review.decision.upper()}",
        details=f"Reviewed flagged item: {item.kamco_name} vs {item.blacklist_name}",
        metadata={
            "item_id": item.id,
            "decision": review.decision,
            "previous_status": previous_status,
            "new_status": item.status,
            "match_score": item.match_score,
            "severity": item.severity,
            "notes": review.notes
        }
    )
    
    # Create logbook entry
    logbook_entry = Logbook(
        kamco_name=item.kamco_name,
        kamco_type=item.kamco_type,
        kamco_id=item.kamco_id,
        blacklist_name=item.blacklist_name,
        blacklist_source=item.blacklist_source,
        match_score=item.match_score,
        action_type=f"review_{review.decision}",
        previous_status=previous_status,
        new_status=item.status,
        reviewed_by_id=current_user.id,
        decision=review.decision,
        notes=review.notes,
        requires_escalation=review.requires_escalation,
        escalation_notes=review.escalation_notes
    )
    db.add(logbook_entry)
    db.commit()
    
    # Send email notification for escalations
    if review.decision == 'escalated' or review.requires_escalation:
        try:
            email_service = get_email_service()
            # Get admin emails (users with admin or finalizer role)
            admins = db.query(User).filter(
                User.role.in_(['admin', 'finalizer']),
                User.is_active == True
            ).all()
            
            admin_emails = [admin.email for admin in admins if admin.email]
            
            if admin_emails:
                email_service.send_escalation_notification(
                    item_id=item.id,
                    kamco_name=item.kamco_name,
                    blacklist_name=item.blacklist_name,
                    match_score=item.match_score,
                    severity=item.severity,
                    escalation_reason=review.escalation_notes or review.notes,
                    reviewed_by=current_user.username,
                    recipients=admin_emails
                )
        except Exception as e:
            print(f"Warning: Could not send escalation email: {e}")
    
    return {
        "success": True,
        "message": f"Item {review.decision}",
        "data": item.to_dict()
    }

@router.post("/review/bulk")
async def bulk_review(
    request: BulkReviewRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Review multiple flagged items at once with the same decision
    """
    updated_count = 0
    errors = []
    
    for item_id in request.item_ids:
        try:
            item = db.query(FlaggedItem).filter(FlaggedItem.id == item_id).first()
            if not item:
                errors.append(f"Item {item_id} not found")
                continue
            
            # Update item
            previous_status = item.status
            
            if request.decision == 'approved':
                item.status = 'approved'
                item.resolution_type = 'flagged'
            elif request.decision == 'rejected':
                item.status = 'rejected'
                item.resolution_type = 'cleared'
            
            item.reviewed_at = datetime.now()
            item.checker_id = current_user.id
            item.checker_notes = request.notes
            item.resolved_at = datetime.now()
            
            # Log action
            log_action(
                db=db,
                user_id=current_user.id,
                action=f"BULK_REVIEW_{request.decision.upper()}",
                details=f"Bulk reviewed: {item.kamco_name}",
                metadata={"item_id": item.id, "decision": request.decision}
            )
            
            updated_count += 1
            
        except Exception as e:
            errors.append(f"Item {item_id}: {str(e)}")
    
    db.commit()
    
    return {
        "success": True,
        "message": f"Reviewed {updated_count} items",
        "data": {
            "updated_count": updated_count,
            "errors": errors
        }
    }

# ===== REPORT ENDPOINTS =====

@router.get("/report/item/{item_id}")
async def get_item_report(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get detailed report for a single flagged item
    """
    item = db.query(FlaggedItem).filter(FlaggedItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Flagged item not found")
    
    # Get Kamco entity details
    kamco_entity = None
    if item.kamco_type == 'clients':
        kamco_entity = db.query(KamcoClient).filter(KamcoClient.id == item.kamco_id).first()
    elif item.kamco_type == 'vendors':
        kamco_entity = db.query(KamcoVendor).filter(KamcoVendor.id == item.kamco_id).first()
    elif item.kamco_type == 'staff':
        kamco_entity = db.query(KamcoStaff).filter(KamcoStaff.id == item.kamco_id).first()
    elif item.kamco_type == 'others':
        kamco_entity = db.query(KamcoOther).filter(KamcoOther.id == item.kamco_id).first()
    
    # Get blacklist entry
    blacklist_entry = db.query(BlacklistEntry).filter(
        BlacklistEntry.name_english == item.blacklist_name
    ).first()
    
    if not blacklist_entry:
        blacklist_entry = db.query(BlacklistEntry).filter(
            BlacklistEntry.name_arabic == item.blacklist_name
        ).first()
    
    # Get audit trail
    audit_trail = db.query(Logbook).filter(
        Logbook.kamco_name == item.kamco_name,
        Logbook.blacklist_name == item.blacklist_name
    ).order_by(Logbook.reviewed_at.desc()).all()
    
    # Get reviewer info
    reviewer = db.query(User).filter(User.id == item.checker_id).first() if item.checker_id else None
    flagger = db.query(User).filter(User.id == item.flagged_by_id).first() if item.flagged_by_id else None
    
    report = {
        "item_id": item.id,
        "report_generated_at": datetime.now().isoformat(),
        "generated_by": current_user.username,
        
        # Match Information
        "match_details": {
            "kamco_name": item.kamco_name,
            "kamco_type": item.kamco_type,
            "blacklist_name": item.blacklist_name,
            "match_score": item.match_score,
            "severity": item.severity
        },
        
        # Kamco Entity Details
        "kamco_entity": {
            "name": kamco_entity.name if kamco_entity else item.kamco_name,
            "type": item.kamco_type,
            **(_get_entity_details(kamco_entity, item.kamco_type) if kamco_entity else {})
        },
        
        # Blacklist Details
        "blacklist_details": {
            "name_english": blacklist_entry.name_english if blacklist_entry else None,
            "name_arabic": blacklist_entry.name_arabic if blacklist_entry else None,
            "source": item.blacklist_source or (blacklist_entry.source if blacklist_entry else None),
            "civil_id": blacklist_entry.civil_id if blacklist_entry else None,
            "passport_number": blacklist_entry.passport_number if blacklist_entry else None,
            "nationality": blacklist_entry.nationality if blacklist_entry else None,
            "notes": blacklist_entry.notes if blacklist_entry else None
        },
        
        # Review Status
        "review_status": {
            "status": item.status,
            "resolution_type": item.resolution_type,
            "flagged_at": item.flagged_at.isoformat() if item.flagged_at else None,
            "reviewed_at": item.reviewed_at.isoformat() if item.reviewed_at else None,
            "resolved_at": item.resolved_at.isoformat() if item.resolved_at else None,
            "flagged_by": flagger.username if flagger else item.flagged_by,
            "reviewed_by": reviewer.username if reviewer else None,
            "flag_reason": item.flag_reason,
            "checker_notes": item.checker_notes,
            "escalation_level": item.escalation_level,
            "requires_compliance": item.requires_compliance_approval
        },
        
        # Audit Trail
        "audit_trail": [
            {
                "action": log.action_type,
                "decision": log.decision,
                "notes": log.notes,
                "reviewed_at": log.reviewed_at.isoformat() if log.reviewed_at else None,
                "reviewed_by_id": log.reviewed_by_id
            }
            for log in audit_trail
        ],
        
        # Risk Assessment
        "risk_assessment": {
            "match_score_level": _get_match_level(item.match_score),
            "severity": item.severity,
            "recommended_action": _get_recommended_action(item.match_score, item.severity)
        }
    }
    
    return {
        "success": True,
        "data": report
    }

@router.get("/report/cumulative")
async def get_cumulative_report(
    status: Optional[str] = None,
    severity: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get cumulative report of all flagged items with statistics and summaries
    """
    # Build query
    query = db.query(FlaggedItem)
    
    if status:
        query = query.filter(FlaggedItem.status == status)
    if severity:
        query = query.filter(FlaggedItem.severity == severity)
    if start_date:
        query = query.filter(FlaggedItem.flagged_at >= start_date)
    if end_date:
        query = query.filter(FlaggedItem.flagged_at <= end_date)
    
    items = query.all()
    
    # Calculate statistics
    total_items = len(items)
    
    # Status breakdown
    status_breakdown = {}
    for item in items:
        status_breakdown[item.status] = status_breakdown.get(item.status, 0) + 1
    
    # Severity breakdown
    severity_breakdown = {}
    for item in items:
        severity_breakdown[item.severity] = severity_breakdown.get(item.severity, 0) + 1
    
    # Entity type breakdown
    type_breakdown = {}
    for item in items:
        type_breakdown[item.kamco_type] = type_breakdown.get(item.kamco_type, 0) + 1
    
    # Match score distribution
    high_confidence = sum(1 for item in items if item.match_score >= 90)
    medium_confidence = sum(1 for item in items if 70 <= item.match_score < 90)
    low_confidence = sum(1 for item in items if item.match_score < 70)
    
    # Reviewer stats
    reviewer_stats = {}
    for item in items:
        if item.checker_id:
            reviewer_stats[item.checker_id] = reviewer_stats.get(item.checker_id, 0) + 1
    
    # Get reviewer names
    reviewer_names = {}
    for reviewer_id in reviewer_stats.keys():
        user = db.query(User).filter(User.id == reviewer_id).first()
        if user:
            reviewer_names[reviewer_id] = user.username
    
    # Top matches (highest scores)
    top_matches = sorted(items, key=lambda x: x.match_score, reverse=True)[:10]
    
    report = {
        "report_generated_at": datetime.now().isoformat(),
        "generated_by": current_user.username,
        "filters": {
            "status": status,
            "severity": severity,
            "start_date": start_date,
            "end_date": end_date
        },
        
        # Summary Statistics
        "summary": {
            "total_flagged_items": total_items,
            "total_approved": status_breakdown.get('approved', 0),
            "total_rejected": status_breakdown.get('rejected', 0),
            "total_pending": status_breakdown.get('pending', 0),
            "total_escalated": status_breakdown.get('escalated', 0),
            "approval_rate": (status_breakdown.get('approved', 0) / total_items * 100) if total_items > 0 else 0,
            "rejection_rate": (status_breakdown.get('rejected', 0) / total_items * 100) if total_items > 0 else 0
        },
        
        # Breakdowns
        "breakdowns": {
            "by_status": status_breakdown,
            "by_severity": severity_breakdown,
            "by_entity_type": type_breakdown,
            "by_match_confidence": {
                "high": high_confidence,
                "medium": medium_confidence,
                "low": low_confidence
            }
        },
        
        # Reviewer Performance
        "reviewer_stats": [
            {
                "reviewer_id": reviewer_id,
                "reviewer_name": reviewer_names.get(reviewer_id, "Unknown"),
                "items_reviewed": count
            }
            for reviewer_id, count in reviewer_stats.items()
        ],
        
        # Top Matches
        "top_matches": [
            {
                "id": item.id,
                "kamco_name": item.kamco_name,
                "blacklist_name": item.blacklist_name,
                "match_score": item.match_score,
                "severity": item.severity,
                "status": item.status
            }
            for item in top_matches
        ],
        
        # All Items (summary)
        "items": [
            {
                "id": item.id,
                "kamco_name": item.kamco_name,
                "kamco_type": item.kamco_type,
                "blacklist_name": item.blacklist_name,
                "match_score": item.match_score,
                "severity": item.severity,
                "status": item.status,
                "flagged_at": item.flagged_at.isoformat() if item.flagged_at else None,
                "reviewed_at": item.reviewed_at.isoformat() if item.reviewed_at else None
            }
            for item in items
        ]
    }
    
    return {
        "success": True,
        "data": report
    }

# ===== EMAIL ENDPOINTS =====

@router.post("/email/report")
async def email_report(
    request: EmailReportRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Email reports to specified recipients
    """
    try:
        email_service = get_email_service()
        
        # Get items to include in report
        if request.item_ids:
            items = db.query(FlaggedItem).filter(FlaggedItem.id.in_(request.item_ids)).all()
        else:
            # Default: all pending and recently reviewed items
            items = db.query(FlaggedItem).filter(
                FlaggedItem.status.in_(['pending', 'approved', 'rejected', 'escalated'])
            ).all()
        
        # Generate cumulative report if requested
        cumulative_data = None
        if request.include_summary:
            # Reuse the cumulative report logic
            cumulative_response = await get_cumulative_report(db=db, current_user=current_user)
            cumulative_data = cumulative_response['data']
        
        # Generate individual reports if requested
        individual_reports = []
        if request.include_individual_reports:
            for item in items[:20]:  # Limit to 20 for email size
                try:
                    report_response = await get_item_report(item.id, db=db, current_user=current_user)
                    individual_reports.append(report_response['data'])
                except Exception as e:
                    print(f"Error generating report for item {item.id}: {e}")
        
        # Send email
        email_service.send_screening_report(
            recipients=request.recipients,
            summary=cumulative_data if request.include_summary else None,
            individual_reports=individual_reports if request.include_individual_reports else None,
            sent_by=current_user.username
        )
        
        # Log the action
        log_action(
            db=db,
            user_id=current_user.id,
            action="EMAIL_REPORT_SENT",
            details=f"Sent screening report to {len(request.recipients)} recipients",
            metadata={
                "recipients": request.recipients,
                "item_count": len(items),
                "include_summary": request.include_summary,
                "include_individual": request.include_individual_reports
            }
        )
        
        return {
            "success": True,
            "message": f"Report emailed to {len(request.recipients)} recipients",
            "data": {
                "recipients": request.recipients,
                "items_included": len(items),
                "timestamp": datetime.now().isoformat()
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to send email: {str(e)}"
        )

# ===== HELPER FUNCTIONS =====

def _get_entity_details(entity, entity_type: str) -> Dict[str, Any]:
    """Extract relevant details from entity based on type"""
    if entity_type == 'clients':
        return {
            "account_number": entity.account_number,
            "date_opened": entity.date_opened,
            "actor_name": entity.actor_name,
            "country": entity.country,
            "notes": entity.notes
        }
    elif entity_type == 'vendors':
        return {
            "vendor_id": entity.vendor_id,
            "date_registered": entity.date_registered,
            "actor_name": entity.actor_name,
            "category": entity.category,
            "notes": entity.notes
        }
    elif entity_type == 'staff':
        return {
            "employee_id": entity.employee_id,
            "department": entity.department,
            "position": entity.position,
            "hire_date": entity.hire_date,
            "notes": entity.notes
        }
    elif entity_type == 'others':
        return {
            "category": entity.category,
            "reference_id": entity.reference_id,
            "description": entity.description,
            "notes": entity.notes
        }
    return {}

def _get_match_level(score: float) -> str:
    """Get match confidence level from score"""
    if score >= 95:
        return "Exact Match"
    elif score >= 90:
        return "Very High Confidence"
    elif score >= 80:
        return "High Confidence"
    elif score >= 70:
        return "Medium Confidence"
    else:
        return "Low Confidence"

def _get_recommended_action(score: float, severity: str) -> str:
    """Get recommended action based on score and severity"""
    if score >= 95 and severity in ['high', 'critical']:
        return "Immediate review and escalation recommended"
    elif score >= 90:
        return "Approve flag and investigate further"
    elif score >= 80:
        return "Review details and compare supporting documents"
    elif score >= 70:
        return "Manual verification recommended"
    else:
        return "Consider rejecting as potential false positive"


# ===== ENHANCED BULK REVIEW ENDPOINTS =====

@router.post("/bulk-items-details")
async def get_bulk_items_details(
    item_ids: List[int] = Body(..., embed=True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get full details for multiple flagged items for bulk review wizard
    Returns comprehensive information for side-by-side comparison
    """
    items_details = []
    
    for item_id in item_ids:
        item = db.query(FlaggedItem).filter(FlaggedItem.id == item_id).first()
        if not item:
            continue
            
        # Get Kamco entity details
        kamco_entity = None
        kamco_details = {}
        
        if item.kamco_type == 'clients':
            kamco_entity = db.query(KamcoClient).filter(KamcoClient.id == item.kamco_id).first()
            if kamco_entity:
                kamco_details = {
                    "name": kamco_entity.name,
                    "name_arabic": getattr(kamco_entity, 'name_arabic', None),
                    "type": "Client",
                    "civil_id": kamco_entity.civil_id,
                    "account_number": getattr(kamco_entity, 'account_number', None),
                    "nationality": getattr(kamco_entity, 'nationality', None),
                    "country": getattr(kamco_entity, 'country', None),
                    "risk_level": getattr(kamco_entity, 'risk_level', None),
                    "status": getattr(kamco_entity, 'status', 'Active'),
                    "date_added": kamco_entity.date_added.isoformat() if hasattr(kamco_entity, 'date_added') and kamco_entity.date_added else None,
                }
        elif item.kamco_type == 'vendors':
            kamco_entity = db.query(KamcoVendor).filter(KamcoVendor.id == item.kamco_id).first()
            if kamco_entity:
                kamco_details = {
                    "name": kamco_entity.name,
                    "name_arabic": getattr(kamco_entity, 'name_arabic', None),
                    "type": "Vendor",
                    "civil_id": kamco_entity.civil_id,
                    "vendor_id": getattr(kamco_entity, 'vendor_id', None),
                    "country": getattr(kamco_entity, 'country', None),
                    "service_type": getattr(kamco_entity, 'service_type', None),
                    "status": getattr(kamco_entity, 'status', 'Active'),
                    "date_added": kamco_entity.date_added.isoformat() if hasattr(kamco_entity, 'date_added') and kamco_entity.date_added else None,
                }
        elif item.kamco_type == 'staff':
            kamco_entity = db.query(KamcoStaff).filter(KamcoStaff.id == item.kamco_id).first()
            if kamco_entity:
                kamco_details = {
                    "name": kamco_entity.name,
                    "name_arabic": getattr(kamco_entity, 'name_arabic', None),
                    "type": "Staff",
                    "civil_id": kamco_entity.civil_id,
                    "employee_id": getattr(kamco_entity, 'employee_id', None),
                    "department": getattr(kamco_entity, 'department', None),
                    "position": getattr(kamco_entity, 'position', None),
                    "status": getattr(kamco_entity, 'status', 'Active'),
                    "date_added": kamco_entity.date_added.isoformat() if hasattr(kamco_entity, 'date_added') and kamco_entity.date_added else None,
                }
        elif item.kamco_type == 'others':
            kamco_entity = db.query(KamcoOther).filter(KamcoOther.id == item.kamco_id).first()
            if kamco_entity:
                kamco_details = {
                    "name": kamco_entity.name,
                    "name_arabic": getattr(kamco_entity, 'name_arabic', None),
                    "type": "Other",
                    "civil_id": kamco_entity.civil_id,
                    "category": getattr(kamco_entity, 'category', None),
                    "description": getattr(kamco_entity, 'description', None),
                    "status": getattr(kamco_entity, 'status', 'Active'),
                    "date_added": kamco_entity.date_added.isoformat() if hasattr(kamco_entity, 'date_added') and kamco_entity.date_added else None,
                }
        
        # Get blacklist entry details
        blacklist_entry = db.query(BlacklistEntry).filter(
            BlacklistEntry.name_english == item.blacklist_name
        ).first()
        
        if not blacklist_entry:
            blacklist_entry = db.query(BlacklistEntry).filter(
                BlacklistEntry.name_arabic == item.blacklist_name
            ).first()
        
        blacklist_details = {}
        if blacklist_entry:
            blacklist_details = {
                "name_english": blacklist_entry.name_english,
                "name_arabic": blacklist_entry.name_arabic,
                "civil_id": blacklist_entry.civil_id,
                "passport": getattr(blacklist_entry, 'passport', None),
                "country": blacklist_entry.country,
                "list_name": getattr(blacklist_entry, 'list_name', 'Sanctions List'),
                "reason": getattr(blacklist_entry, 'reason', None),
                "date_added": blacklist_entry.date_added.isoformat() if blacklist_entry.date_added else None,
                "status": "Active",
            }
        
        # Compile item details
        item_detail = {
            "id": item.id,
            "match_info": {
                "match_score": item.match_score,
                "match_type": item.match_type,
                "severity": item.severity,
                "confidence_level": _get_match_level(item.match_score),
                "recommended_action": _get_recommended_action(item.match_score, item.severity),
            },
            "kamco_entity": kamco_details,
            "blacklist_entry": blacklist_details,
            "current_status": item.status,
            "flagged_at": item.flagged_at.isoformat() if item.flagged_at else None,
            "flagged_by": item.flagged_by_id,
        }
        
        items_details.append(item_detail)
    
    return {
        "success": True,
        "count": len(items_details),
        "items": items_details
    }


@router.post("/submit-bulk-wizard")
async def submit_bulk_wizard_reviews(
    reviews: List[Dict[str, Any]] = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Submit multiple reviews from bulk review wizard
    Each review can have a different decision
    
    Request body: List of {item_id, decision, notes, escalation_notes}
    """
    results = []
    errors = []
    
    for review_data in reviews:
        item_id = review_data.get('item_id')
        decision = review_data.get('decision')
        notes = review_data.get('notes', '')
        escalation_notes = review_data.get('escalation_notes')
        
        try:
            item = db.query(FlaggedItem).filter(FlaggedItem.id == item_id).first()
            if not item:
                errors.append({"item_id": item_id, "error": "Item not found"})
                continue
            
            # Update item based on decision
            if decision == 'approved':
                item.status = 'approved'
                item.checker_decision = 'approved'
            elif decision == 'rejected':
                item.status = 'rejected'
                item.checker_decision = 'rejected'
            elif decision == 'escalated':
                item.status = 'escalated'
                item.checker_decision = 'escalated'
                item.escalation_notes = escalation_notes or notes
            
            item.checker_id = current_user.id
            item.checker_notes = notes
            item.reviewed_at = datetime.now()
            
            # Log to logbook
            log_action(
                db=db,
                kamco_name=item.kamco_name,
                kamco_type=item.kamco_type,
                blacklist_name=item.blacklist_name,
                match_score=item.match_score,
                severity=item.severity,
                decision=decision,
                reviewed_by=current_user.username,
                note=notes
            )
            
            db.commit()
            
            results.append({
                "item_id": item_id,
                "status": "success",
                "decision": decision
            })
            
        except Exception as e:
            db.rollback()
            errors.append({"item_id": item_id, "error": str(e)})
    
    return {
        "success": len(errors) == 0,
        "processed": len(results),
        "failed": len(errors),
        "results": results,
        "errors": errors
    }


@router.post("/generate-reports-batch")
async def generate_reports_batch(
    item_ids: List[int] = Body(..., embed=True),
    report_format: str = Body("pdf", embed=True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Generate individual reports for multiple items
    Returns list of report metadata/download links
    """
    from utils.pdf_generator import get_pdf_generator
    from utils.excel_generator import get_excel_generator
    import os
    
    reports = []
    errors = []
    
    for item_id in item_ids:
        try:
            # Get item report data using existing endpoint logic
            item = db.query(FlaggedItem).filter(FlaggedItem.id == item_id).first()
            if not item:
                errors.append({"item_id": item_id, "error": "Item not found"})
                continue
            
            # Generate report
            report_title = f"Item_{item_id}_{item.kamco_name.replace(' ', '_')}"
            
            if report_format.lower() == 'pdf':
                pdf_generator = get_pdf_generator()
                # Generate simple PDF report (you can enhance this)
                from reportlab.lib.pagesizes import letter
                from reportlab.pdfgen import canvas
                
                filename = f"reports/item_report_{item_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                os.makedirs('reports', exist_ok=True)
                
                c = canvas.Canvas(filename, pagesize=letter)
                c.setFont("Helvetica-Bold", 16)
                c.drawString(100, 750, f"Flagged Item Report - ID: {item_id}")
                c.setFont("Helvetica", 12)
                c.drawString(100, 720, f"Kamco Entity: {item.kamco_name}")
                c.drawString(100, 700, f"Blacklist Match: {item.blacklist_name}")
                c.drawString(100, 680, f"Match Score: {item.match_score}%")
                c.drawString(100, 660, f"Severity: {item.severity.upper()}")
                c.drawString(100, 640, f"Status: {item.status.upper()}")
                c.drawString(100, 620, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                c.drawString(100, 600, f"Generated By: {current_user.username}")
                c.save()
                
                reports.append({
                    "item_id": item_id,
                    "filename": filename,
                    "format": "pdf",
                    "title": report_title
                })
            
            elif report_format.lower() == 'excel':
                excel_generator = get_excel_generator()
                # Similar Excel generation logic
                filename = f"reports/item_report_{item_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                # Implement Excel generation
                reports.append({
                    "item_id": item_id,
                    "filename": filename,
                    "format": "excel",
                    "title": report_title
                })
                
        except Exception as e:
            errors.append({"item_id": item_id, "error": str(e)})
    
    return {
        "success": len(errors) == 0,
        "generated": len(reports),
        "failed": len(errors),
        "reports": reports,
        "errors": errors,
        "message": f"Generated {len(reports)} reports successfully"
    }
