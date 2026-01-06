"""
Scan routes - Handle blacklist upload and scanning
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from database.connection import get_db
from models.database import KamcoClient, KamcoVendor, KamcoStaff, KamcoOther, InReviewQueue
from utils.excel_parser import parse_blacklist_excel
from utils.actor_extractor import extract_actor
from utils.fuzzy_matcher import find_matches, match_actor
from utils.logbook import is_duplicate
from typing import List, Dict

router = APIRouter()

@router.post("/upload")
async def upload_blacklist(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload and parse blacklist Excel file
    Returns parsed data for preview/validation
    """
    # Validate file type
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="Only Excel files (.xlsx, .xls) are allowed")
    
    # Parse Excel file
    parsed_data = await parse_blacklist_excel(file)
    
    # Count totals
    totals = {
        sheet_name: len(rows)
        for sheet_name, rows in parsed_data.items()
    }
    
    return {
        "success": True,
        "message": "Blacklist uploaded successfully",
        "filename": file.filename,
        "totals": totals,
        "preview": {
            sheet_name: rows[:3]  # Preview first 3 rows
            for sheet_name, rows in parsed_data.items()
        }
    }

@router.post("/run")
async def run_scan(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Run full scan: Parse blacklist, match against Kamco database, deduplicate, add to queue
    """
    # Parse blacklist Excel
    blacklist_data = await parse_blacklist_excel(file)
    
    matches_found = 0
    new_matches = 0
    duplicates_skipped = 0
    
    # Process each sheet type
    for sheet_type in ['clients', 'vendors', 'staff', 'others']:
        blacklist_rows = blacklist_data.get(sheet_type, [])
        
        if not blacklist_rows:
            continue
        
        # Get Kamco database records for this type
        kamco_records = get_kamco_records(db, sheet_type)
        
        # Prepare blacklist names for matching
        blacklist_names = []
        for row in blacklist_rows:
            name = row.get('Name') or row.get('name')
            if name:
                source = row.get('Source') or row.get('source') or 'Unknown'
                blacklist_names.append((name, source))
        
        # Match each Kamco record against blacklist
        for kamco_record in kamco_records:
            kamco_name = kamco_record.name
            kamco_id = kamco_record.id
            
            # Find fuzzy matches
            matches = find_matches(kamco_name, blacklist_names, threshold=80)
            
            for blacklist_name, source, score in matches:
                matches_found += 1
                
                # Check logbook for duplicates
                if is_duplicate(db, kamco_name, sheet_type, blacklist_name):
                    duplicates_skipped += 1
                    continue
                
                # Check for actor match (only for clients/vendors)
                actor_match_score = None
                actor_name = None
                
                if sheet_type in ['clients', 'vendors']:
                    actor_name = getattr(kamco_record, 'actor_name', None)
                    if actor_name:
                        is_actor_match, actor_score = match_actor(actor_name, blacklist_name)
                        if is_actor_match:
                            actor_match_score = actor_score
                
                # Add to in-review queue
                queue_item = InReviewQueue(
                    kamco_name=kamco_name,
                    kamco_type=sheet_type,
                    kamco_id=kamco_id,
                    blacklist_name=blacklist_name,
                    blacklist_source=source,
                    match_score=score,
                    actor_name=actor_name,
                    actor_match_score=actor_match_score
                )
                
                db.add(queue_item)
                new_matches += 1
    
    db.commit()
    
    return {
        "success": True,
        "message": f"Scan completed. Found {new_matches} new matches.",
        "stats": {
            "total_matches_found": matches_found,
            "new_matches_added": new_matches,
            "duplicates_skipped": duplicates_skipped
        }
    }

def get_kamco_records(db: Session, sheet_type: str):
    """Get Kamco database records for a specific type"""
    if sheet_type == 'clients':
        return db.query(KamcoClient).all()
    elif sheet_type == 'vendors':
        return db.query(KamcoVendor).all()
    elif sheet_type == 'staff':
        return db.query(KamcoStaff).all()
    elif sheet_type == 'others':
        return db.query(KamcoOther).all()
    else:
        return []
