"""
Finalizer Routes - Handle final approval workflow
Finalizers provide final sign-off on flagged items and can override or escalate
"""
from fastapi import APIRouter, HTTPException, Depends, Body, Request
from sqlalchemy.orm import Session
from database.connection import get_db
from models.database import InReviewQueue, FlaggedItem, Logbook
from models.case import Case, CaseNote, CaseStatus, CasePriority, NoteType
from models.notification import EmailNotification, EmailType, EmailStatus
from models.auth import User, UserRole
from utils.auth import require_finalizer, get_current_user
from utils.logbook import add_to_logbook
from datetime import datetime
from typing import Optional
import json

router = APIRouter()


@router.post("/approve")
async def approve_final(
    request: Request,
    flagged_item_id: int = Body(...),
    finalizer_notes: str = Body(...),
    resolution_type: str = Body(default="approved"),  # approved, approved_with_conditions
    current_user: User = Depends(require_finalizer),
    db: Session = Depends(get_db)
):
    """
    Final approval of a flagged item
    This closes the case and completes the workflow
    
    Required: flagged_item_id, finalizer_notes (min 20 chars)
    Optional: resolution_type (approved/approved_with_conditions)
    """
    # Validate finalizer notes
    if len(finalizer_notes.strip()) < 20:
        raise HTTPException(
            status_code=400,
            detail="Finalizer notes must be at least 20 characters"
        )
    
    # Validate resolution type
    valid_resolution_types = ["approved", "approved_with_conditions"]
    if resolution_type not in valid_resolution_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid resolution type. Must be one of: {', '.join(valid_resolution_types)}"
        )
    
    # Get the flagged item
    flagged_item = db.query(FlaggedItem).filter(FlaggedItem.id == flagged_item_id).first()
    if not flagged_item:
        raise HTTPException(status_code=404, detail="Flagged item not found")
    
    # Verify checker has approved this item
    if flagged_item.status != "approved":
        raise HTTPException(
            status_code=400,
            detail="Item must be approved by checker before final approval"
        )
    
    if flagged_item.checker_id is None:
        raise HTTPException(
            status_code=400,
            detail="Item must be reviewed by checker before final approval"
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
    flagged_item.finalizer_id = current_user.id
    flagged_item.finalizer_notes = finalizer_notes
    flagged_item.finalizer_reviewed_at = datetime.utcnow()
    flagged_item.resolution_type = resolution_type
    flagged_item.status = "final_approved"
    flagged_item.resolution_date = datetime.utcnow()
    
    # Update InReviewQueue
    queue_item.status = "completed"
    queue_item.reviewed_at = datetime.utcnow()
    
    # Update Case status
    previous_status = case.status
    case.status = CaseStatus.CLOSED
    case.resolved_at = datetime.utcnow()
    case.updated_at = datetime.utcnow()
    
    # Add CaseNote
    case_note = CaseNote(
        case_id=case.id,
        user_id=current_user.id,
        note_type=NoteType.STATUS_CHANGE,
        note=f"Final approval: {finalizer_notes}",
        note_metadata=json.dumps({
            "action": "final_approved",
            "previous_status": previous_status.value,
            "new_status": case.status.value,
            "resolution_type": resolution_type
        })
    )
    db.add(case_note)
    
    # Send notification emails to screener and checker
    # Email to screener
    screener = db.query(User).filter(User.id == queue_item.screener_id).first()
    if screener:
        email_notification = EmailNotification(
            user_id=screener.id,
            to_email=screener.email,
            email_type=EmailType.CASE_CLOSED,
            subject=f"Case Closed: {case.case_number}",
            body=f"Case {case.case_number} has been approved by finalizer. "
                 f"Resolution: {resolution_type}. Notes: {finalizer_notes}",
            status=EmailStatus.PENDING,
            email_metadata=json.dumps({
                "case_id": case.id,
                "case_number": case.case_number,
                "flagged_item_id": flagged_item.id,
                "finalizer_id": current_user.id,
                "resolution_type": resolution_type
            })
        )
        db.add(email_notification)
    
    # Email to checker
    checker = db.query(User).filter(User.id == flagged_item.checker_id).first()
    if checker:
        email_notification = EmailNotification(
            user_id=checker.id,
            to_email=checker.email,
            email_type=EmailType.CASE_CLOSED,
            subject=f"Case Closed: {case.case_number}",
            body=f"Case {case.case_number} that you reviewed has been approved by finalizer. "
                 f"Resolution: {resolution_type}.",
            status=EmailStatus.PENDING,
            email_metadata=json.dumps({
                "case_id": case.id,
                "case_number": case.case_number,
                "flagged_item_id": flagged_item.id,
                "finalizer_id": current_user.id,
                "resolution_type": resolution_type
            })
        )
        db.add(email_notification)
    
    # Add Logbook entry
    add_to_logbook(
        db=db,
        kamco_id=queue_item.kamco_id,
        in_review_queue_id=queue_item.id,
        case_id=case.id,
        action_type="final_approve",
        approved_by_id=current_user.id,
        previous_status=previous_status.value,
        new_status=case.status.value,
        notes=f"Final approval ({resolution_type}): {finalizer_notes}",
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent")
    )
    
    db.commit()
    
    return {
        "success": True,
        "message": "Case approved and closed",
        "case_id": case.id,
        "case_number": case.case_number,
        "case_status": case.status.value,
        "resolution_type": resolution_type,
        "resolved_at": case.resolved_at.isoformat(),
        "screener_notified": screener is not None,
        "checker_notified": checker is not None
    }


@router.post("/override")
async def override_decision(
    request: Request,
    flagged_item_id: int = Body(...),
    override_reason: str = Body(...),
    override_action: str = Body(...),  # reject, close_without_action, escalate_external
    current_user: User = Depends(require_finalizer),
    db: Session = Depends(get_db)
):
    """
    Override a checker's decision or take special action
    Finalizers have authority to reject flags or close cases without standard approval
    
    Required: flagged_item_id, override_reason (min 30 chars), override_action
    Actions: reject (reject the flag), close_without_action (close without taking action), 
             escalate_external (send to external compliance)
    """
    # Validate override reason
    if len(override_reason.strip()) < 30:
        raise HTTPException(
            status_code=400,
            detail="Override reason must be at least 30 characters"
        )
    
    # Validate override action
    valid_override_actions = ["reject", "close_without_action", "escalate_external"]
    if override_action not in valid_override_actions:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid override action. Must be one of: {', '.join(valid_override_actions)}"
        )
    
    # Get the flagged item
    flagged_item = db.query(FlaggedItem).filter(FlaggedItem.id == flagged_item_id).first()
    if not flagged_item:
        raise HTTPException(status_code=404, detail="Flagged item not found")
    
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
    
    # Determine new status based on override action
    if override_action == "reject":
        case_status = CaseStatus.REJECTED
        queue_status = "completed"
        flagged_item_status = "rejected"
        resolution_type = "rejected_by_finalizer"
    elif override_action == "close_without_action":
        case_status = CaseStatus.CLOSED
        queue_status = "completed"
        flagged_item_status = "closed_no_action"
        resolution_type = "closed_no_action"
    else:  # escalate_external
        case_status = CaseStatus.ESCALATED
        queue_status = "escalated"
        flagged_item_status = "escalated_external"
        resolution_type = "escalated_external"
    
    # Update FlaggedItem
    flagged_item.finalizer_id = current_user.id
    flagged_item.finalizer_notes = f"OVERRIDE: {override_reason}"
    flagged_item.finalizer_reviewed_at = datetime.utcnow()
    flagged_item.status = flagged_item_status
    flagged_item.resolution_type = resolution_type
    flagged_item.resolution_date = datetime.utcnow()
    
    # Update InReviewQueue
    queue_item.status = queue_status
    queue_item.reviewed_at = datetime.utcnow()
    if override_action == "escalate_external":
        queue_item.escalation_reason = override_reason
    
    # Update Case status
    previous_status = case.status
    case.status = case_status
    case.updated_at = datetime.utcnow()
    if override_action != "escalate_external":
        case.resolved_at = datetime.utcnow()
    
    # Add CaseNote
    case_note = CaseNote(
        case_id=case.id,
        user_id=current_user.id,
        note_type=NoteType.STATUS_CHANGE,
        note=f"Finalizer override ({override_action}): {override_reason}",
        note_metadata=json.dumps({
            "action": "finalizer_override",
            "previous_status": previous_status.value,
            "new_status": case.status.value,
            "override_action": override_action,
            "resolution_type": resolution_type
        })
    )
    db.add(case_note)
    
    # Send notification emails
    # Email to screener
    screener = db.query(User).filter(User.id == queue_item.screener_id).first()
    if screener:
        email_type = EmailType.CASE_REJECTED if override_action == "reject" else EmailType.CASE_CLOSED
        email_notification = EmailNotification(
            user_id=screener.id,
            to_email=screener.email,
            email_type=email_type,
            subject=f"Finalizer Override: {case.case_number}",
            body=f"Finalizer has overridden case {case.case_number}. "
                 f"Action: {override_action}. Reason: {override_reason}",
            status=EmailStatus.PENDING,
            email_metadata=json.dumps({
                "case_id": case.id,
                "case_number": case.case_number,
                "flagged_item_id": flagged_item.id,
                "finalizer_id": current_user.id,
                "override_action": override_action
            })
        )
        db.add(email_notification)
    
    # Email to checker if assigned
    if flagged_item.checker_id:
        checker = db.query(User).filter(User.id == flagged_item.checker_id).first()
        if checker:
            email_type = EmailType.CASE_REJECTED if override_action == "reject" else EmailType.CASE_CLOSED
            email_notification = EmailNotification(
                user_id=checker.id,
                to_email=checker.email,
                email_type=email_type,
                subject=f"Finalizer Override: {case.case_number}",
                body=f"Finalizer has overridden case {case.case_number} that you reviewed. "
                     f"Action: {override_action}.",
                status=EmailStatus.PENDING,
                email_metadata=json.dumps({
                    "case_id": case.id,
                    "case_number": case.case_number,
                    "flagged_item_id": flagged_item.id,
                    "finalizer_id": current_user.id,
                    "override_action": override_action
                })
            )
            db.add(email_notification)
    
    # Add Logbook entry
    add_to_logbook(
        db=db,
        kamco_id=queue_item.kamco_id,
        in_review_queue_id=queue_item.id,
        case_id=case.id,
        action_type="override",
        approved_by_id=current_user.id,
        previous_status=previous_status.value,
        new_status=case.status.value,
        notes=f"Finalizer override ({override_action}): {override_reason}",
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent")
    )
    
    db.commit()
    
    return {
        "success": True,
        "message": f"Override applied: {override_action}",
        "case_id": case.id,
        "case_number": case.case_number,
        "case_status": case.status.value,
        "override_action": override_action,
        "resolution_type": resolution_type,
        "screener_notified": screener is not None,
        "checker_notified": flagged_item.checker_id is not None
    }


@router.post("/escalate")
async def escalate_to_management(
    request: Request,
    flagged_item_id: int = Body(...),
    escalation_reason: str = Body(...),
    escalation_level: str = Body(default="management"),  # management, executive, legal
    priority: str = Body(default="high"),  # high, critical
    current_user: User = Depends(require_finalizer),
    db: Session = Depends(get_db)
):
    """
    Escalate a case to higher management or legal
    Used for complex cases that require senior decision-making
    
    Required: flagged_item_id, escalation_reason (min 40 chars)
    Optional: escalation_level (management/executive/legal), priority (high/critical)
    """
    # Validate escalation reason
    if len(escalation_reason.strip()) < 40:
        raise HTTPException(
            status_code=400,
            detail="Escalation reason must be at least 40 characters"
        )
    
    # Validate escalation level
    valid_escalation_levels = ["management", "executive", "legal"]
    if escalation_level not in valid_escalation_levels:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid escalation level. Must be one of: {', '.join(valid_escalation_levels)}"
        )
    
    # Validate priority
    valid_priorities = ["high", "critical"]
    if priority not in valid_priorities:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid priority for escalation. Must be one of: {', '.join(valid_priorities)}"
        )
    
    # Get the flagged item
    flagged_item = db.query(FlaggedItem).filter(FlaggedItem.id == flagged_item_id).first()
    if not flagged_item:
        raise HTTPException(status_code=404, detail="Flagged item not found")
    
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
    flagged_item.finalizer_id = current_user.id
    flagged_item.finalizer_notes = f"ESCALATED: {escalation_reason}"
    flagged_item.finalizer_reviewed_at = datetime.utcnow()
    flagged_item.status = "escalated"
    flagged_item.escalation_level = escalation_level
    
    # Update InReviewQueue
    queue_item.status = "escalated"
    queue_item.escalation_reason = escalation_reason
    
    # Update Case status
    previous_status = case.status
    case.status = CaseStatus.ESCALATED
    case.priority = CasePriority[priority.upper()]
    case.updated_at = datetime.utcnow()
    
    # Add CaseNote
    case_note = CaseNote(
        case_id=case.id,
        user_id=current_user.id,
        note_type=NoteType.STATUS_CHANGE,
        note=f"Escalated to {escalation_level}: {escalation_reason}",
        note_metadata=json.dumps({
            "action": "escalated",
            "previous_status": previous_status.value,
            "new_status": case.status.value,
            "escalation_level": escalation_level,
            "priority": priority
        })
    )
    db.add(case_note)
    
    # Send notification to all finalizers and relevant parties
    finalizers = db.query(User).filter(User.role == UserRole.FINALIZER).all()
    for finalizer in finalizers:
        if finalizer.id != current_user.id:  # Don't email the escalating finalizer
            email_notification = EmailNotification(
                user_id=finalizer.id,
                to_email=finalizer.email,
                email_type=EmailType.ESCALATION,
                subject=f"ESCALATION [{escalation_level.upper()}]: {case.case_number}",
                body=f"Case {case.case_number} has been escalated to {escalation_level}. "
                     f"Priority: {priority}. Reason: {escalation_reason}",
                status=EmailStatus.PENDING,
                email_metadata=json.dumps({
                    "case_id": case.id,
                    "case_number": case.case_number,
                    "flagged_item_id": flagged_item.id,
                    "escalated_by": current_user.id,
                    "escalation_level": escalation_level,
                    "priority": priority
                })
            )
            db.add(email_notification)
    
    # Also notify screener and checker
    screener = db.query(User).filter(User.id == queue_item.screener_id).first()
    if screener:
        email_notification = EmailNotification(
            user_id=screener.id,
            to_email=screener.email,
            email_type=EmailType.ESCALATION,
            subject=f"Case Escalated: {case.case_number}",
            body=f"Your case {case.case_number} has been escalated to {escalation_level}.",
            status=EmailStatus.PENDING,
            email_metadata=json.dumps({
                "case_id": case.id,
                "case_number": case.case_number,
                "escalation_level": escalation_level
            })
        )
        db.add(email_notification)
    
    if flagged_item.checker_id:
        checker = db.query(User).filter(User.id == flagged_item.checker_id).first()
        if checker:
            email_notification = EmailNotification(
                user_id=checker.id,
                to_email=checker.email,
                email_type=EmailType.ESCALATION,
                subject=f"Case Escalated: {case.case_number}",
                body=f"Case {case.case_number} that you reviewed has been escalated to {escalation_level}.",
                status=EmailStatus.PENDING,
                email_metadata=json.dumps({
                    "case_id": case.id,
                    "case_number": case.case_number,
                    "escalation_level": escalation_level
                })
            )
            db.add(email_notification)
    
    # Add Logbook entry
    add_to_logbook(
        db=db,
        kamco_id=queue_item.kamco_id,
        in_review_queue_id=queue_item.id,
        case_id=case.id,
        action_type="escalate",
        approved_by_id=current_user.id,
        previous_status=previous_status.value,
        new_status=case.status.value,
        notes=f"Escalated to {escalation_level} ({priority}): {escalation_reason}",
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent")
    )
    
    db.commit()
    
    return {
        "success": True,
        "message": f"Case escalated to {escalation_level}",
        "case_id": case.id,
        "case_number": case.case_number,
        "case_status": case.status.value,
        "escalation_level": escalation_level,
        "priority": priority,
        "finalizers_notified": len(finalizers) - 1,  # Exclude current user
        "screener_notified": screener is not None,
        "checker_notified": flagged_item.checker_id is not None
    }
