"""
Logbook deduplication utilities
Prevents re-scanning of previously reviewed items
"""
from sqlalchemy.orm import Session
from models.database import Logbook
from typing import Optional, Dict, Any
from datetime import datetime
import json


def log_action(
    db: Session,
    user_id: int,
    action: str,
    details: str,
    metadata: Optional[Dict[str, Any]] = None
) -> None:
    """
    Log an action to the logbook for audit trail
    
    Args:
        db: Database session
        user_id: ID of user performing action
        action: Action type (e.g., "BLACKLIST_UPLOADED", "SCAN", "FLAG", etc.)
        details: Human-readable description
        metadata: Optional additional data as dictionary
    """
    try:
        # Map action names to valid action_type values
        action_type_map = {
            "BLACKLIST_UPLOADED": "upload",
            "FILE_UPLOADED": "upload",
            "SCAN": "scan",
            "FLAG": "flag",
            "CLEAR": "clear",
            "APPROVE": "approve",
            "REJECT": "reject",
            "OVERRIDE": "override",
            "RECHECK": "recheck",
            "ESCALATE": "escalate",
        }
        
        # Get the action_type or default to the action itself (lowercased)
        action_type = action_type_map.get(action, action.lower())
        
        # Create a simple log entry using Logbook model
        logbook_entry = Logbook(
            kamco_name="SYSTEM",
            kamco_type="system_action",
            kamco_id=user_id,
            blacklist_name=action,
            blacklist_source="system",
            match_score=0.0,
            action_type=action_type,  # NOW REQUIRED!
            reviewed_by=str(user_id),
            reviewed_by_id=user_id,  # Add the FK relationship
            decision="logged",
            notes=f"{details} | Metadata: {json.dumps(metadata) if metadata else 'None'}"
        )
        
        db.add(logbook_entry)
        db.commit()
    except Exception as e:
        print(f"Warning: Could not log action: {str(e)}")
        db.rollback()


def check_if_reviewed(
    db: Session,
    kamco_name: str,
    kamco_type: str,
    blacklist_name: str
) -> Optional[Logbook]:
    """
    Check if a (kamco_name, blacklist_name) pair has been reviewed before
    
    Args:
        db: Database session
        kamco_name: Name from Kamco database
        kamco_type: Type (clients, vendors, staff, others)
        blacklist_name: Name from blacklist
        
    Returns:
        Logbook entry if exists, None otherwise
    """
    return db.query(Logbook).filter(
        Logbook.kamco_name == kamco_name,
        Logbook.kamco_type == kamco_type,
        Logbook.blacklist_name == blacklist_name
    ).first()

def add_to_logbook(
    db: Session,
    kamco_name: str,
    kamco_type: str,
    kamco_id: int,
    blacklist_name: str,
    blacklist_source: str,
    match_score: float,
    reviewed_by: str,
    decision: str,
    notes: Optional[str] = None
) -> Logbook:
    """
    Add a reviewed item to the logbook
    
    Args:
        db: Database session
        kamco_name: Name from Kamco database
        kamco_type: Type (clients, vendors, staff, others)
        kamco_id: Kamco database record ID
        blacklist_name: Name from blacklist
        blacklist_source: Source of blacklist entry
        match_score: Fuzzy match score
        reviewed_by: Username of reviewer
        decision: 'cleared' or 'flagged'
        notes: Optional notes
        
    Returns:
        Created Logbook entry
    """
    logbook_entry = Logbook(
        kamco_name=kamco_name,
        kamco_type=kamco_type,
        kamco_id=kamco_id,
        blacklist_name=blacklist_name,
        blacklist_source=blacklist_source,
        match_score=match_score,
        reviewed_by=reviewed_by,
        decision=decision,
        notes=notes
    )
    
    db.add(logbook_entry)
    db.commit()
    db.refresh(logbook_entry)
    
    return logbook_entry

def is_duplicate(
    db: Session,
    kamco_name: str,
    kamco_type: str,
    blacklist_name: str
) -> bool:
    """
    Simple boolean check if item has been reviewed
    
    Args:
        db: Database session
        kamco_name: Name from Kamco database
        kamco_type: Type (clients, vendors, staff, others)
        blacklist_name: Name from blacklist
        
    Returns:
        True if already reviewed, False otherwise
    """
    return check_if_reviewed(db, kamco_name, kamco_type, blacklist_name) is not None
