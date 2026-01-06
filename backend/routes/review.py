"""
Review routes - Handle flagging, approvals, and checker workflows
"""
from fastapi import APIRouter, HTTPException, Depends, Body
from sqlalchemy.orm import Session
from database.connection import get_db
from models.database import InReviewQueue, FlaggedItem, Logbook
from utils.logbook import add_to_logbook
from datetime import datetime
from typing import Optional

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
    queue_item_id: int = Body(...),
    flag_reason: str = Body(...),
    flagged_by: str = Body(...),
    db: Session = Depends(get_db)
):
    """
    Flag an item from review queue with reason
    """
    # Get item from queue
    queue_item = db.query(InReviewQueue).filter(InReviewQueue.id == queue_item_id).first()
    
    if not queue_item:
        raise HTTPException(status_code=404, detail="Queue item not found")
    
    # Validate flag reason
    if len(flag_reason.strip()) < 10:
        raise HTTPException(status_code=400, detail="Flag reason must be at least 10 characters")
    
    # Create flagged item
    flagged_item = FlaggedItem(
        kamco_name=queue_item.kamco_name,
        kamco_type=queue_item.kamco_type,
        kamco_id=queue_item.kamco_id,
        blacklist_name=queue_item.blacklist_name,
        blacklist_source=queue_item.blacklist_source,
        match_score=queue_item.match_score,
        flag_reason=flag_reason,
        flagged_by=flagged_by,
        status="pending"
    )
    
    db.add(flagged_item)
    
    # Remove from review queue
    db.delete(queue_item)
    
    db.commit()
    db.refresh(flagged_item)
    
    return {
        "success": True,
        "message": "Item flagged successfully",
        "flagged_item_id": flagged_item.id
    }

@router.post("/undo")
async def undo_flag(
    flagged_item_id: int = Body(...),
    db: Session = Depends(get_db)
):
    """
    Undo a flag and move item back to review queue
    """
    # Get flagged item
    flagged_item = db.query(FlaggedItem).filter(FlaggedItem.id == flagged_item_id).first()
    
    if not flagged_item:
        raise HTTPException(status_code=404, detail="Flagged item not found")
    
    # Create queue item
    queue_item = InReviewQueue(
        kamco_name=flagged_item.kamco_name,
        kamco_type=flagged_item.kamco_type,
        kamco_id=flagged_item.kamco_id,
        blacklist_name=flagged_item.blacklist_name,
        blacklist_source=flagged_item.blacklist_source,
        match_score=flagged_item.match_score
    )
    
    db.add(queue_item)
    
    # Delete flagged item
    db.delete(flagged_item)
    
    db.commit()
    
    return {
        "success": True,
        "message": "Flag undone successfully"
    }

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
