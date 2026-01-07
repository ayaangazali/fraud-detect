"""
Upload Route for Phase 4: Excel Parser Enhancement
Handles blacklist Excel file uploads and parsing
Updated in Phase 6: Added email notifications on upload completion
"""
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from datetime import datetime

from database.connection import get_db
from models.blacklist import BlacklistEntry
from utils.excel_parser import ExcelParser, ExcelParserError, validate_blacklist_excel
from utils.logbook import log_action
from utils.auth import get_current_active_user
from utils.email_service import get_email_service

router = APIRouter()


@router.post("/blacklist")
async def upload_blacklist(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    Upload blacklist/sanctions list Excel file
    
    **Phase 4 - Task 19: Upload Endpoint**
    
    Accepts:
    - Excel files (.xlsx, .xls)
    - Required column: name_arabic
    - Optional columns: name_english, civil_id, decree_number, etc.
    
    Returns:
    - Upload summary with record counts and batch ID
    """
    
    # Validate file type
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Only Excel files (.xlsx, .xls) are accepted."
        )
    
    try:
        # Read file contents
        file_contents = await file.read()
        
        # Validate file structure first
        validation = validate_blacklist_excel(file_bytes=file_contents)
        if not validation['valid']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid Excel structure: {validation['error']}"
            )
        
        # Parse blacklist data
        parser = ExcelParser(file_bytes=file_contents)
        records, summary = parser.parse_blacklist()
        
        if not records:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No valid records found in Excel file"
            )
        
        # Store records in database
        stored_count = 0
        errors = []
        
        for record in records:
            try:
                # Add upload metadata
                record['upload_filename'] = file.filename
                
                # Create database entry
                blacklist_entry = BlacklistEntry(**record)
                db.add(blacklist_entry)
                stored_count += 1
                
            except Exception as e:
                errors.append(f"Failed to store record: {str(e)}")
        
        # Commit all changes
        try:
            db.commit()
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error: {str(e)}"
            )
        
        # Log the upload action
        log_action(
            db=db,
            user_id=current_user.id,
            action="BLACKLIST_UPLOADED",
            details=f"Uploaded {stored_count} blacklist entries from {file.filename}",
            metadata={
                "filename": file.filename,
                "batch_id": summary['batch_id'],
                "total_rows": summary['total_rows'],
                "valid_records": summary['valid_records'],
                "stored_count": stored_count
            }
        )
        
        # Send email notification (Phase 6)
        try:
            email_service = get_email_service()
            email_service.send_upload_completion_notification(
                total_rows=summary['total_rows'],
                valid_rows=stored_count,
                errors_count=len(errors),
                uploaded_by=current_user.username,
                filename=file.filename
            )
        except Exception as e:
            # Don't fail the upload if email fails
            print(f"Warning: Could not send upload notification email: {str(e)}")
        
        return {
            "success": True,
            "message": f"Successfully uploaded {stored_count} blacklist entries",
            "data": {
                "filename": file.filename,
                "batch_id": summary['batch_id'],
                "total_rows": summary['total_rows'],
                "valid_records": summary['valid_records'],
                "stored_count": stored_count,
                "error_count": len(errors),
                "errors": errors[:10] if errors else [],  # Show first 10 errors
                "upload_time": datetime.now().isoformat()
            }
        }
        
    except ExcelParserError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Excel parsing error: {str(e)}"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Upload failed: {str(e)}"
        )


@router.get("/blacklist")
async def get_blacklist_entries(
    skip: int = 0,
    limit: int = 100,
    source: str = None,
    risk_level: str = None,
    status_filter: str = "Active",
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    Get blacklist entries with optional filtering
    
    Query Parameters:
    - skip: Number of records to skip (pagination)
    - limit: Maximum number of records to return
    - source: Filter by source (e.g., "Kuwait Government Decree")
    - risk_level: Filter by risk level (High, Medium, Low)
    - status_filter: Filter by status (Active, Removed, Under Review)
    """
    
    query = db.query(BlacklistEntry)
    
    # Apply filters
    if source:
        query = query.filter(BlacklistEntry.source == source)
    if risk_level:
        query = query.filter(BlacklistEntry.risk_level == risk_level)
    if status_filter:
        query = query.filter(BlacklistEntry.status == status_filter)
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    entries = query.offset(skip).limit(limit).all()
    
    return {
        "success": True,
        "data": {
            "total": total,
            "skip": skip,
            "limit": limit,
            "entries": [entry.to_dict() for entry in entries]
        }
    }


@router.get("/blacklist/{entry_id}")
async def get_blacklist_entry(
    entry_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Get a specific blacklist entry by ID"""
    
    entry = db.query(BlacklistEntry).filter(BlacklistEntry.id == entry_id).first()
    
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Blacklist entry with ID {entry_id} not found"
        )
    
    return {
        "success": True,
        "data": entry.to_dict()
    }


@router.delete("/blacklist/{entry_id}")
async def delete_blacklist_entry(
    entry_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    Delete a blacklist entry (soft delete by changing status)
    Requires admin or finalizer role
    """
    
    # Check user role
    if current_user.role not in ['admin', 'finalizer']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin or finalizer can delete blacklist entries"
        )
    
    entry = db.query(BlacklistEntry).filter(BlacklistEntry.id == entry_id).first()
    
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Blacklist entry with ID {entry_id} not found"
        )
    
    # Soft delete - change status to Removed
    entry.status = "Removed"
    db.commit()
    
    # Log the deletion
    log_action(
        db=db,
        user_id=current_user.id,
        action="BLACKLIST_ENTRY_REMOVED",
        details=f"Removed blacklist entry: {entry.name_arabic}",
        metadata={"entry_id": entry_id, "name": entry.name_arabic}
    )
    
    return {
        "success": True,
        "message": f"Blacklist entry {entry_id} marked as removed"
    }


@router.get("/blacklist/search/{query}")
async def search_blacklist(
    query: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    Search blacklist by name (Arabic or English) or Civil ID
    """
    
    # Search in name_arabic, name_english, and civil_id fields
    results = db.query(BlacklistEntry).filter(
        (BlacklistEntry.name_arabic.contains(query)) |
        (BlacklistEntry.name_english.contains(query)) |
        (BlacklistEntry.civil_id.contains(query))
    ).filter(
        BlacklistEntry.status == "Active"
    ).limit(50).all()
    
    return {
        "success": True,
        "data": {
            "query": query,
            "result_count": len(results),
            "results": [entry.to_dict() for entry in results]
        }
    }


@router.post("/blacklist/validate")
async def validate_blacklist_file(
    file: UploadFile = File(...),
    current_user = Depends(get_current_active_user)
):
    """
    Validate blacklist Excel file without uploading
    Returns validation results and preview of data
    """
    
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Only Excel files (.xlsx, .xls) are accepted."
        )
    
    try:
        file_contents = await file.read()
        
        # Validate structure
        validation = validate_blacklist_excel(file_bytes=file_contents)
        
        if validation['valid']:
            # Parse first few rows as preview
            parser = ExcelParser(file_bytes=file_contents)
            records, summary = parser.parse_blacklist()
            
            return {
                "success": True,
                "validation": validation,
                "preview": {
                    "total_rows": summary['total_rows'],
                    "valid_records": summary['valid_records'],
                    "first_5_records": records[:5],
                    "error_count": summary['error_count'],
                    "errors": summary['errors'][:10] if summary['errors'] else []
                }
            }
        else:
            return {
                "success": False,
                "validation": validation,
                "message": validation['error']
            }
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Validation failed: {str(e)}"
        )
