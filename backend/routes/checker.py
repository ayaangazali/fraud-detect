"""
Checker Review Routes - Handle checker review workflow
Checkers review flagged items and approve/reject or send back for recheck
"""
from fastapi import APIRouter, HTTPException, Depends, Body, Request
from sqlalchemy.orm import Session
from database.connection import get_db
from models.database import InReviewQueue, FlaggedItem, Logbook
from models.case import Case, CaseNote, CaseStatus, CasePriority, NoteType
from models.notification import EmailNotification, EmailType, EmailStatus
from models.auth import User, UserRole
from utils.auth import require_checker, get_current_user
from utils.logbook import add_to_logbook
from datetime import datetime
from typing import Optional
import json

router = APIRouter()


@router.post("/assign")
async def assign_checker(
    request: Request,
    flagged_item_id: int = Body(...),
    checker_id: Optional[int] = Body(default=None),  # None = auto-assign to current user
    current_user: User = Depends(require_checker),
    db: Session = Depends(get_db)
):
    """
    Assign a checker to a flagged item
    Can be auto-assigned (current user) or manually assigned to specific checker
    
    Required: flagged_item_id
    Optional: checker_id (if None, assigns to current user)
    """
    # Get the flagged item
    flagged_item = db.query(FlaggedItem).filter(FlaggedItem.id == flagged_item_id).first()
    if not flagged_item:
        raise HTTPException(status_code=404, detail="Flagged item not found")
    
    # Check if already assigned to a checker
    if flagged_item.checker_id is not None:
        raise HTTPException(
            status_code=400,
            detail=f"Flagged item already assigned to checker ID {flagged_item.checker_id}"
        )
    
    # Get case
    case = db.query(Case).filter(Case.id == flagged_item.case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Associated case not found")
    
    # Determine which checker to assign
    assigned_checker_id = checker_id if checker_id else current_user.id
    
    # If manually assigning, verify the target user is a checker
    if checker_id:
        target_checker = db.query(User).filter(
            User.id == checker_id,
            User.role == UserRole.CHECKER
        ).first()
        if not target_checker:
            raise HTTPException(status_code=404, detail="Target user not found or not a checker")
    
    # Get InReviewQueue item via case_id
    queue_item = db.query(InReviewQueue).filter(
        InReviewQueue.case_id == flagged_item.case_id
    ).first()
    if not queue_item:
        raise HTTPException(status_code=404, detail="Queue item not found")
    
    # Update FlaggedItem
    flagged_item.checker_id = assigned_checker_id
    flagged_item.checker_assigned_at = datetime.utcnow()
    
    # Update InReviewQueue
    queue_item.assigned_at = datetime.utcnow()
    queue_item.status = "checker_review"
    
    # Update Case status
    previous_status = case.status
    case.status = CaseStatus.CHECKER_REVIEW
    case.assigned_to_id = assigned_checker_id
    case.updated_at = datetime.utcnow()
    
    # Add CaseNote
    case_note = CaseNote(
        case_id=case.id,
        user_id=current_user.id,
        note_type=NoteType.SYSTEM,
        note=f"Checker assigned: {assigned_checker_id}",
        note_metadata=json.dumps({
            "action": "checker_assigned",
            "assigned_by": current_user.id,
            "assigned_to": assigned_checker_id,
            "auto_assign": checker_id is None
        })
    )
    db.add(case_note)
    
    # Queue email notification to the assigned checker
    checker_user = db.query(User).filter(User.id == assigned_checker_id).first()
    if checker_user:
        email_notification = EmailNotification(
            user_id=assigned_checker_id,
            to_email=checker_user.email,
            email_type=EmailType.CHECKER_ASSIGNED,
            subject=f"Checker Assignment: {case.case_number}",
            body=f"You have been assigned to review case {case.case_number}. "
                 f"Flag reason: {flagged_item.flag_reason}",
            status=EmailStatus.PENDING,
            email_metadata=json.dumps({
                "case_id": case.id,
                "case_number": case.case_number,
                "flagged_item_id": flagged_item.id,
                "assigned_by": current_user.id
            })
        )
        db.add(email_notification)
    
    # Add Logbook entry
    add_to_logbook(
        db=db,
        kamco_id=queue_item.kamco_id,
        in_review_queue_id=queue_item.id,
        case_id=case.id,
        action_type="assign",
        reviewed_by_id=current_user.id,
        previous_status=previous_status.value,
        new_status=case.status.value,
        notes=f"Checker assigned: {assigned_checker_id}",
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent")
    )
    
    db.commit()
    
    return {
        "success": True,
        "message": "Checker assigned successfully",
        "case_id": case.id,
        "case_number": case.case_number,
        "case_status": case.status.value,
        "assigned_checker_id": assigned_checker_id,
        "assigned_at": queue_item.assigned_at.isoformat()
    }


@router.post("/approve")
async def approve_flagged_item(
    request: Request,
    flagged_item_id: int = Body(...),
    checker_notes: str = Body(...),
    priority: str = Body(default="medium"),  # low, medium, high, critical
    current_user: User = Depends(require_checker),
    db: Session = Depends(get_db)
):
    """
    Approve a flagged item (moves to finalizer queue)
    Checker confirms the flag is valid and needs final approval
    
    Required: flagged_item_id, checker_notes (min 15 chars)
    Optional: priority (low/medium/high/critical)
    """
    # Validate checker notes
    if len(checker_notes.strip()) < 15:
        raise HTTPException(
            status_code=400,
            detail="Checker notes must be at least 15 characters"
        )
    
    # Validate priority
    valid_priorities = ["low", "medium", "high", "critical"]
    if priority not in valid_priorities:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid priority. Must be one of: {', '.join(valid_priorities)}"
        )
    
    # Get the flagged item
    flagged_item = db.query(FlaggedItem).filter(FlaggedItem.id == flagged_item_id).first()
    if not flagged_item:
        raise HTTPException(status_code=404, detail="Flagged item not found")
    
    # Verify this checker is assigned to this item
    if flagged_item.checker_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You are not assigned to this flagged item"
        )
    
    # Get case
    case = db.query(Case).filter(Case.id == flagged_item.case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Associated case not found")
    
    # Get queue item via case_id
    queue_item = db.query(InReviewQueue).filter(
        InReviewQueue.case_id == flagged_item.case_id
    ).first()
    if not queue_item:
        raise HTTPException(status_code=404, detail="Queue item not found")
    
    # Update FlaggedItem
    flagged_item.status = "approved"
    flagged_item.checker_notes = checker_notes
    flagged_item.checker_reviewed_at = datetime.utcnow()
    
    # Update InReviewQueue
    queue_item.reviewed_at = datetime.utcnow()
    queue_item.status = "awaiting_final"
    
    # Update Case status and priority
    previous_status = case.status
    case.status = CaseStatus.AWAITING_FINAL
    case.priority = CasePriority[priority.upper()]
    case.updated_at = datetime.utcnow()
    
    # Add CaseNote
    case_note = CaseNote(
        case_id=case.id,
        user_id=current_user.id,
        note_type=NoteType.STATUS_CHANGE,
        note=f"Checker approved: {checker_notes}",
        note_metadata=json.dumps({
            "action": "checker_approved",
            "previous_status": previous_status.value,
            "new_status": case.status.value,
            "priority": priority
        })
    )
    db.add(case_note)
    
    # Find a finalizer to notify
    finalizer = db.query(User).filter(User.role == UserRole.FINALIZER).first()
    if finalizer:
        email_notification = EmailNotification(
            user_id=finalizer.id,
            to_email=finalizer.email,
            email_type=EmailType.APPROVAL_REQUIRED,
            subject=f"Final Approval Required: {case.case_number}",
            body=f"Case {case.case_number} requires final approval. "
                 f"Checker notes: {checker_notes}",
            status=EmailStatus.PENDING,
            email_metadata=json.dumps({
                "case_id": case.id,
                "case_number": case.case_number,
                "flagged_item_id": flagged_item.id,
                "checker_id": current_user.id,
                "priority": priority
            })
        )
        db.add(email_notification)
    
    # Add Logbook entry
    add_to_logbook(
        db=db,
        kamco_id=queue_item.kamco_id,
        in_review_queue_id=queue_item.id,
        case_id=case.id,
        action_type="approve",
        reviewed_by_id=current_user.id,
        previous_status=previous_status.value,
        new_status=case.status.value,
        notes=f"Checker approved: {checker_notes}",
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent")
    )
    
    db.commit()
    
    return {
        "success": True,
        "message": "Flagged item approved by checker",
        "case_id": case.id,
        "case_number": case.case_number,
        "case_status": case.status.value,
        "priority": priority,
        "finalizer_notified": finalizer is not None
    }


@router.post("/recheck")
async def request_recheck(
    request: Request,
    flagged_item_id: int = Body(...),
    recheck_reason: str = Body(...),
    current_user: User = Depends(require_checker),
    db: Session = Depends(get_db)
):
    """
    Request screener to recheck the flagged item
    Checker sends item back to screener for additional review
    
    Required: flagged_item_id, recheck_reason (min 20 chars)
    """
    # Validate recheck reason
    if len(recheck_reason.strip()) < 20:
        raise HTTPException(
            status_code=400,
            detail="Recheck reason must be at least 20 characters"
        )
    
    # Get the flagged item
    flagged_item = db.query(FlaggedItem).filter(FlaggedItem.id == flagged_item_id).first()
    if not flagged_item:
        raise HTTPException(status_code=404, detail="Flagged item not found")
    
    # Verify this checker is assigned to this item
    if flagged_item.checker_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You are not assigned to this flagged item"
        )
    
    # Get case
    case = db.query(Case).filter(Case.id == flagged_item.case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Associated case not found")
    
    # Get queue item via case_id
    queue_item = db.query(InReviewQueue).filter(
        InReviewQueue.case_id == flagged_item.case_id
    ).first()
    if not queue_item:
        raise HTTPException(status_code=404, detail="Queue item not found")
    
    # Update FlaggedItem - clear checker assignment and mark for recheck
    flagged_item.checker_id = None
    flagged_item.checker_assigned_at = None
    flagged_item.status = "recheck_requested"
    flagged_item.checker_notes = recheck_reason
    
    # Update InReviewQueue - back to pending state
    queue_item.status = "pending"
    queue_item.requires_checker_review = False
    queue_item.assigned_at = None
    queue_item.reviewed_at = None
    
    # Update Case status
    previous_status = case.status
    case.status = CaseStatus.IN_REVIEW
    case.updated_at = datetime.utcnow()
    
    # Track recheck count in case metadata
    current_metadata = json.loads(case.description) if case.description and case.description.startswith('{') else {}
    recheck_count = current_metadata.get("recheck_count", 0) + 1
    current_metadata["recheck_count"] = recheck_count
    current_metadata["last_recheck_reason"] = recheck_reason
    current_metadata["last_recheck_at"] = datetime.utcnow().isoformat()
    
    # Add CaseNote with recheck details
    case_note = CaseNote(
        case_id=case.id,
        user_id=current_user.id,
        note_type=NoteType.STATUS_CHANGE,
        note=f"Recheck requested: {recheck_reason}",
        note_metadata=json.dumps({
            "action": "recheck_requested",
            "previous_status": previous_status.value,
            "new_status": case.status.value,
            "recheck_count": recheck_count,
            "checker_id": current_user.id
        })
    )
    db.add(case_note)
    
    # Send email notification to the original screener
    screener = db.query(User).filter(User.id == queue_item.screener_id).first()
    if screener:
        email_notification = EmailNotification(
            user_id=screener.id,
            to_email=screener.email,
            email_type=EmailType.RECHECK_REQUESTED,
            subject=f"Recheck Requested: {case.case_number}",
            body=f"Checker has requested a recheck for case {case.case_number}. "
                 f"Reason: {recheck_reason}",
            status=EmailStatus.PENDING,
            email_metadata=json.dumps({
                "case_id": case.id,
                "case_number": case.case_number,
                "flagged_item_id": flagged_item.id,
                "checker_id": current_user.id,
                "recheck_count": recheck_count
            })
        )
        db.add(email_notification)
    
    # Add Logbook entry
    add_to_logbook(
        db=db,
        kamco_id=queue_item.kamco_id,
        in_review_queue_id=queue_item.id,
        case_id=case.id,
        action_type="recheck",
        reviewed_by_id=current_user.id,
        previous_status=previous_status.value,
        new_status=case.status.value,
        notes=f"Recheck requested (#{recheck_count}): {recheck_reason}",
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent")
    )
    
    db.commit()
    
    return {
        "success": True,
        "message": "Recheck requested successfully",
        "case_id": case.id,
        "case_number": case.case_number,
        "case_status": case.status.value,
        "recheck_count": recheck_count,
        "screener_notified": screener is not None
    }
