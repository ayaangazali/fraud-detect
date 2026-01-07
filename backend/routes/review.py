"""
Review routes - Handle flagging, approvals, and checker workflows
Phase 6: Email notifications for flagged items
"""
from fastapi import APIRouter, HTTPException, Depends, Body, Request
from sqlalchemy.orm import Session
from database.connection import get_db
from models.database import InReviewQueue, FlaggedItem, Logbook
from models.case import Case, CaseNote, CaseStatus, CasePriority, NoteType
from models.notification import EmailNotification, EmailType, EmailStatus
from models.auth import User
from utils.auth import require_screener, require_checker, get_current_user
from utils.logbook import add_to_logbook
from utils.email_service import get_email_service
from datetime import datetime
from typing import Optional
import json

router = APIRouter()

@router.get("/queue")
async def get_review_queue(
    type_filter: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get items in review queue
    Optional filter by type (clients, vendors, staff, others)
    """
    query = db.query(InReviewQueue)
    
    if type_filter and type_filter != 'all':
        query = query.filter(InReviewQueue.kamco_type == type_filter)
    
    items = query.order_by(InReviewQueue.created_at.desc()).all()
    
    return {
        "success": True,
        "count": len(items),
        "items": [
            {
                "id": item.id,
                "kamco_name": item.kamco_name,
                "kamco_type": item.kamco_type,
                "kamco_id": item.kamco_id,
                "blacklist_name": item.blacklist_name,
                "blacklist_source": item.blacklist_source,
                "match_score": item.match_score,
                "actor_name": item.actor_name,
                "actor_match_score": item.actor_match_score,
                "created_at": item.created_at.isoformat() if item.created_at else None
            }
            for item in items
        ]
    }

@router.post("/flag")
async def flag_item(
    request: Request,
    queue_item_id: int = Body(...),
    flag_reason: str = Body(...),
    flag_reason_category: str = Body(default="match_confirmed"),
    severity: str = Body(default="medium"),
    current_user: User = Depends(require_screener),
    db: Session = Depends(get_db)
):
    """
    Flag an item from review queue with reason
    Phase 3 Enhancement: Creates case, links to queue item, calculates risk score,
    queues email notification, adds comprehensive audit log
    """
    # Get item from queue
    queue_item = db.query(InReviewQueue).filter(InReviewQueue.id == queue_item_id).first()
    
    if not queue_item:
        raise HTTPException(status_code=404, detail="Queue item not found")
    
    # Validate flag reason (min 20 chars as per Phase 3)
    if len(flag_reason.strip()) < 20:
        raise HTTPException(
            status_code=400, 
            detail="Flag reason must be at least 20 characters"
        )
    
    # Validate flag_reason_category
    valid_categories = ["match_confirmed", "suspicious_activity", "high_risk", "regulatory"]
    if flag_reason_category not in valid_categories:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid flag_reason_category. Must be one of: {', '.join(valid_categories)}"
        )
    
    # Validate severity
    valid_severities = ["low", "medium", "high", "critical"]
    if severity not in valid_severities:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid severity. Must be one of: {', '.join(valid_severities)}"
        )
    
    try:
        # 1. CREATE CASE
        case = Case(
            case_number=Case.generate_case_number(),
            status=CaseStatus.IN_REVIEW,
            priority=CasePriority.HIGH if severity in ["high", "critical"] else CasePriority.MEDIUM,
            created_by_id=current_user.id,
            assigned_to_id=None,  # Will be assigned to checker later
            title=f"Match Review - {queue_item.kamco_name}",
            description=f"Potential match detected: {queue_item.kamco_name} ({queue_item.kamco_type}) matched with {queue_item.blacklist_name} from {queue_item.blacklist_source}. Match score: {queue_item.match_score}%"
        )
        db.add(case)
        db.flush()  # Get case.id
        
        # 2. CALCULATE RISK SCORE (1-10 scale)
        # Base score from match percentage (0-10)
        base_score = min(10, queue_item.match_score / 10)
        # Bonus for actor presence (+3)
        actor_bonus = 3 if queue_item.actor_name else 0
        risk_score = min(10, int(base_score + actor_bonus))
        
        # Determine if checker review required (risk_score >= 7)
        requires_checker_review = risk_score >= 7
        
        # 3. UPDATE INREVIEWQUEUE WITH CASE LINKAGE
        queue_item.case_id = case.id
        queue_item.screener_id = current_user.id
        queue_item.risk_score = risk_score
        queue_item.requires_checker_review = requires_checker_review
        queue_item.status = "in_progress"
        queue_item.assigned_at = datetime.utcnow()
        
        # Store match metadata
        match_metadata = {
            "match_algorithm": "fuzzy_match",
            "confidence_level": queue_item.match_score,
            "actor_name": queue_item.actor_name,
            "actor_match_score": queue_item.actor_match_score,
            "individual_scores": {
                "name_similarity": queue_item.match_score,
                "actor_presence": bool(queue_item.actor_name)
            },
            "match_reasons": [flag_reason_category]
        }
        queue_item.match_metadata = json.dumps(match_metadata)
        
        # 4. CREATE FLAGGED ITEM
        flagged_item = FlaggedItem(
            case_id=case.id,
            kamco_name=queue_item.kamco_name,
            kamco_type=queue_item.kamco_type,
            kamco_id=queue_item.kamco_id,
            blacklist_name=queue_item.blacklist_name,
            blacklist_source=queue_item.blacklist_source,
            match_score=queue_item.match_score,
            flag_reason=flag_reason,
            flagged_by=current_user.username,  # Legacy field
            flagged_by_id=current_user.id,
            flag_reason_category=flag_reason_category,
            severity=severity,
            status="pending"
        )
        db.add(flagged_item)
        db.flush()
        
        # 5. ADD CASE NOTE
        case_note = CaseNote(
            case_id=case.id,
            user_id=current_user.id,
            note=f"Item flagged by {current_user.username}. Reason: {flag_reason}",
            note_type=NoteType.SYSTEM,
            note_metadata=json.dumps({
                "action": "flag_created",
                "risk_score": risk_score,
                "severity": severity,
                "category": flag_reason_category
            })
        )
        db.add(case_note)
        
        # 6. QUEUE EMAIL NOTIFICATION (if checker review required)
        if requires_checker_review:
            # Find a checker to notify (simple assignment - first available checker)
            from models.auth import UserRole
            checker = db.query(User).filter(User.role == UserRole.CHECKER).first()
            
            if checker:
                email_notification = EmailNotification(
                    user_id=checker.id,
                    to_email=checker.email,
                    email_type=EmailType.FLAG_CREATED,
                    subject=f"New High-Risk Flag - Case {case.case_number}",
                    body=f"A new high-risk flag has been created requiring your review.\n\n"
                         f"Case: {case.case_number}\n"
                         f"Entity: {queue_item.kamco_name} ({queue_item.kamco_type})\n"
                         f"Match: {queue_item.blacklist_name} ({queue_item.blacklist_source})\n"
                         f"Risk Score: {risk_score}/10\n"
                         f"Severity: {severity}\n\n"
                         f"Please review this case at your earliest convenience.",
                    status=EmailStatus.PENDING,
                    email_metadata=json.dumps({
                        "case_id": case.id,
                        "case_number": case.case_number,
                        "priority": case.priority.value,
                        "risk_score": risk_score
                    })
                )
                db.add(email_notification)
        
        # 7. ADD TO LOGBOOK
        logbook_entry = Logbook(
            case_id=case.id,
            entity_id=queue_item.kamco_id,
            entity_type=queue_item.kamco_type,
            entity_name=queue_item.kamco_name,
            blacklist_name=queue_item.blacklist_name,
            blacklist_source=queue_item.blacklist_source,
            match_score=queue_item.match_score,
            decision="flagged",
            reviewed_by=current_user.username,  # Legacy field
            reviewed_by_id=current_user.id,
            action_type="flag",
            previous_status=None,
            new_status=CaseStatus.IN_REVIEW.value,
            notes=flag_reason,
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent")
        )
        db.add(logbook_entry)
        
        # Commit all changes
        db.commit()
        db.refresh(case)
        db.refresh(flagged_item)
        
        # Send email notification (Phase 6) - non-blocking
        try:
            email_service = get_email_service()
            email_service.send_flagged_item_notification(
                entity_name=queue_item.kamco_name,
                entity_type=queue_item.kamco_type,
                reason=flag_reason,
                flagged_by=current_user.username
            )
        except Exception as e:
            # Don't fail the flagging if email fails
            print(f"Warning: Could not send flagged item email notification: {str(e)}")
        
        return {
            "success": True,
            "message": "Item flagged successfully",
            "case_id": case.id,
            "case_number": case.case_number,
            "flagged_item_id": flagged_item.id,
            "risk_score": risk_score,
            "requires_checker_review": requires_checker_review,
            "checker_notified": requires_checker_review and checker is not None
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to flag item: {str(e)}")

@router.post("/undo")
async def undo_flag(
    request: Request,
    flagged_item_id: int = Body(...),
    undo_reason: str = Body(...),
    current_user: User = Depends(require_screener),
    db: Session = Depends(get_db)
):
    """
    Undo a flag and move item back to review queue
    Phase 3 Enhancement: Validates ownership, prevents undo after checker review,
    updates case status, adds case note, queues notification if needed
    """
    # Get flagged item
    flagged_item = db.query(FlaggedItem).filter(FlaggedItem.id == flagged_item_id).first()
    
    if not flagged_item:
        raise HTTPException(status_code=404, detail="Flagged item not found")
    
    # Get associated queue item
    queue_item = db.query(InReviewQueue).filter(
        InReviewQueue.kamco_id == flagged_item.kamco_id,
        InReviewQueue.kamco_type == flagged_item.kamco_type
    ).first()
    
    if not queue_item:
        raise HTTPException(
            status_code=404, 
            detail="Associated queue item not found. Item may have been processed."
        )
    
    # 1. VALIDATE OWNERSHIP
    if queue_item.screener_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You can only undo items you flagged"
        )
    
    # 2. CHECK IF ALREADY REVIEWED BY CHECKER
    if flagged_item.checker_id is not None:
        raise HTTPException(
            status_code=403,
            detail="Cannot undo - item has already been reviewed by a checker"
        )
    
    # Validate undo reason
    if len(undo_reason.strip()) < 10:
        raise HTTPException(
            status_code=400,
            detail="Undo reason must be at least 10 characters"
        )
    
    try:
        # Get associated case
        case = None
        if flagged_item.case_id:
            case = db.query(Case).filter(Case.id == flagged_item.case_id).first()
        
        # 3. UPDATE CASE STATUS
        if case:
            previous_status = case.status.value
            case.status = CaseStatus.CLEARED
            case.updated_at = datetime.utcnow()
            
            # 4. ADD CASE NOTE
            case_note = CaseNote(
                case_id=case.id,
                user_id=current_user.id,
                note=f"Flag undone by {current_user.username}. Reason: {undo_reason}",
                note_type=NoteType.SYSTEM,
                note_metadata=json.dumps({
                    "action": "undo_flag",
                    "previous_status": previous_status,
                    "new_status": CaseStatus.CLEARED.value
                })
            )
            db.add(case_note)
        
        # 5. QUEUE EMAIL NOTIFICATION IF CHECKER WAS NOTIFIED
        checker_was_notified = False
        if queue_item.requires_checker_review and flagged_item.case_id:
            # Check if email was sent to checker
            existing_notification = db.query(EmailNotification).filter(
                EmailNotification.email_type == EmailType.FLAG_CREATED,
                EmailNotification.email_metadata.like(f'%"case_id": {flagged_item.case_id}%')
            ).first()
            
            if existing_notification and existing_notification.user_id:
                checker_was_notified = True
                # Notify checker that flag was undone
                checker = db.query(User).filter(User.id == existing_notification.user_id).first()
                if checker:
                    notification = EmailNotification(
                        user_id=checker.id,
                        to_email=checker.email,
                        email_type=EmailType.RECHECK_REQUESTED,  # Reusing this type for undo notification
                        subject=f"Flag Undone - Case {case.case_number if case else 'N/A'}",
                        body=f"A flag has been undone by the screener.\n\n"
                             f"Entity: {flagged_item.kamco_name} ({flagged_item.kamco_type})\n"
                             f"Match: {flagged_item.blacklist_name}\n"
                             f"Reason for undo: {undo_reason}\n\n"
                             f"No action required - this is for your information.",
                        status=EmailStatus.PENDING,
                        email_metadata=json.dumps({
                            "case_id": case.id if case else None,
                            "case_number": case.case_number if case else None,
                            "action": "undo_flag"
                        })
                    )
                    db.add(notification)
        
        # 6. RESET QUEUE ITEM STATUS
        queue_item.status = "pending"
        queue_item.case_id = None  # Unlink from case
        queue_item.screener_id = None
        queue_item.risk_score = None
        queue_item.requires_checker_review = False
        queue_item.assigned_at = None
        queue_item.match_metadata = None
        
        # 7. DELETE FLAGGED ITEM
        db.delete(flagged_item)
        
        # 8. ADD TO LOGBOOK
        logbook_entry = Logbook(
            case_id=case.id if case else None,
            entity_id=flagged_item.kamco_id,
            entity_type=flagged_item.kamco_type,
            entity_name=flagged_item.kamco_name,
            blacklist_name=flagged_item.blacklist_name,
            blacklist_source=flagged_item.blacklist_source,
            match_score=flagged_item.match_score,
            decision="cleared",
            reviewed_by=current_user.username,
            reviewed_by_id=current_user.id,
            action_type="clear",
            previous_status=case.status.value if case else "in_review",
            new_status=CaseStatus.CLEARED.value,
            notes=f"Flag undone. Reason: {undo_reason}",
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent")
        )
        db.add(logbook_entry)
        
        db.commit()
        
        return {
            "success": True,
            "message": "Flag undone successfully",
            "case_id": case.id if case else None,
            "case_number": case.case_number if case else None,
            "case_status": CaseStatus.CLEARED.value,
            "checker_notified": checker_was_notified
        }
        
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to undo flag: {str(e)}")

@router.get("/flagged")
async def get_flagged_items(
    type_filter: Optional[str] = None,
    status_filter: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get flagged items
    Optional filters: type, status
    """
    query = db.query(FlaggedItem)
    
    if type_filter and type_filter != 'all':
        query = query.filter(FlaggedItem.kamco_type == type_filter)
    
    if status_filter:
        query = query.filter(FlaggedItem.status == status_filter)
    
    items = query.order_by(FlaggedItem.flagged_at.desc()).all()
    
    return {
        "success": True,
        "count": len(items),
        "items": [
            {
                "id": item.id,
                "kamco_name": item.kamco_name,
                "kamco_type": item.kamco_type,
                "blacklist_name": item.blacklist_name,
                "blacklist_source": item.blacklist_source,
                "match_score": item.match_score,
                "flag_reason": item.flag_reason,
                "flagged_by": item.flagged_by,
                "flagged_at": item.flagged_at.isoformat() if item.flagged_at else None,
                "status": item.status,
                "reviewed_by": item.reviewed_by,
                "reviewed_at": item.reviewed_at.isoformat() if item.reviewed_at else None,
                "review_notes": item.review_notes
            }
            for item in items
        ]
    }

@router.post("/approve")
async def approve_flagged_item(
    flagged_item_id: int = Body(...),
    reviewed_by: str = Body(...),
    notes: Optional[str] = Body(None),
    db: Session = Depends(get_db)
):
    """
    Checker approves a flagged item (adds to logbook as 'flagged')
    """
    flagged_item = db.query(FlaggedItem).filter(FlaggedItem.id == flagged_item_id).first()
    
    if not flagged_item:
        raise HTTPException(status_code=404, detail="Flagged item not found")
    
    # Update flagged item status
    flagged_item.status = "approved"
    flagged_item.reviewed_by = reviewed_by
    flagged_item.reviewed_at = datetime.utcnow()
    flagged_item.review_notes = notes
    
    # Add to logbook
    add_to_logbook(
        db=db,
        kamco_name=flagged_item.kamco_name,
        kamco_type=flagged_item.kamco_type,
        kamco_id=flagged_item.kamco_id,
        blacklist_name=flagged_item.blacklist_name,
        blacklist_source=flagged_item.blacklist_source,
        match_score=flagged_item.match_score,
        reviewed_by=reviewed_by,
        decision="flagged",
        notes=notes
    )
    
    db.commit()
    
    return {
        "success": True,
        "message": "Flagged item approved and added to logbook"
    }

@router.post("/recheck")
async def request_recheck(
    flagged_item_id: int = Body(...),
    recheck_reason: str = Body(...),
    reviewed_by: str = Body(...),
    db: Session = Depends(get_db)
):
    """
    Checker requests re-check (moves back to queue)
    """
    if len(recheck_reason.strip()) < 15:
        raise HTTPException(status_code=400, detail="Re-check reason must be at least 15 characters")
    
    flagged_item = db.query(FlaggedItem).filter(FlaggedItem.id == flagged_item_id).first()
    
    if not flagged_item:
        raise HTTPException(status_code=404, detail="Flagged item not found")
    
    # Update status to recheck
    flagged_item.status = "recheck"
    flagged_item.reviewed_by = reviewed_by
    flagged_item.reviewed_at = datetime.utcnow()
    flagged_item.review_notes = recheck_reason
    
    # Move back to review queue
    queue_item = InReviewQueue(
        kamco_name=flagged_item.kamco_name,
        kamco_type=flagged_item.kamco_type,
        kamco_id=flagged_item.kamco_id,
        blacklist_name=flagged_item.blacklist_name,
        blacklist_source=flagged_item.blacklist_source,
        match_score=flagged_item.match_score
    )
    
    db.add(queue_item)
    db.commit()
    
    # TODO: Send email notification to screener
    
    return {
        "success": True,
        "message": "Re-check requested. Item moved back to queue."
    }

@router.post("/override")
async def override_flag(
    flagged_item_id: int = Body(...),
    override_reason: str = Body(...),
    reviewed_by: str = Body(...),
    db: Session = Depends(get_db)
):
    """
    Checker overrides flag (adds to logbook as 'cleared')
    """
    if len(override_reason.strip()) < 20:
        raise HTTPException(status_code=400, detail="Override reason must be at least 20 characters")
    
    flagged_item = db.query(FlaggedItem).filter(FlaggedItem.id == flagged_item_id).first()
    
    if not flagged_item:
        raise HTTPException(status_code=404, detail="Flagged item not found")
    
    # Update flagged item status
    flagged_item.status = "overridden"
    flagged_item.reviewed_by = reviewed_by
    flagged_item.reviewed_at = datetime.utcnow()
    flagged_item.review_notes = override_reason
    
    # Add to logbook as CLEARED
    add_to_logbook(
        db=db,
        kamco_name=flagged_item.kamco_name,
        kamco_type=flagged_item.kamco_type,
        kamco_id=flagged_item.kamco_id,
        blacklist_name=flagged_item.blacklist_name,
        blacklist_source=flagged_item.blacklist_source,
        match_score=flagged_item.match_score,
        reviewed_by=reviewed_by,
        decision="cleared",
        notes=f"Override: {override_reason}"
    )
    
    db.commit()
    
    return {
        "success": True,
        "message": "Flag overridden. Item marked as cleared in logbook."
    }
