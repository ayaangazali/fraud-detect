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
from models.database import FlaggedItem, KamcoClient, KamcoVendor, KamcoStaff, KamcoOther
from utils.excel_parser import ExcelParser, ExcelParserError, validate_blacklist_excel
from utils.logbook import log_action
from utils.auth import get_current_active_user
from utils.email_service import get_email_service
from utils.fuzzy_matcher_enhanced import FuzzyMatcherEnhanced

router = APIRouter()


@router.post("/blacklist")
async def upload_blacklist(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    Upload blacklist/sanctions list file
    
    **Supports Multiple Formats:**
    - Excel files (.xlsx, .xls)
    - CSV files (.csv)
    - XML files (.xml)
    - JSON files (.json)
    
    **Required fields:**
    - At least one of: name_english OR name_arabic
    
    **Optional fields:**
    - civil_id, passport_number, nationality, source, date_added, notes
    
    Returns:
    - Upload summary with record counts and auto-screening results
    """
    
    # Validate file type
    supported_extensions = ('.xlsx', '.xls', '.csv', '.xml', '.json')
    if not file.filename.lower().endswith(supported_extensions):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Supported formats: {', '.join(supported_extensions)}"
        )
    
    try:
        # Read file contents
        file_contents = await file.read()
        
        # Parse using multi-format parser
        from utils.multi_format_parser import parse_blacklist_file
        
        try:
            result = parse_blacklist_file(file_contents, file.filename)
            records = result['data']
            summary = result['summary']
            errors = result['errors']
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to parse file: {str(e)}"
            )
        
        if not records:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No valid records found in file"
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
        
        # AUTO-SCREEN: Run screening automatically if Kamco data exists
        screening_results = None
        try:
            # Check if any Kamco data exists
            kamco_count = (
                db.query(KamcoClient).count() +
                db.query(KamcoVendor).count() +
                db.query(KamcoStaff).count() +
                db.query(KamcoOther).count()
            )
            
            if kamco_count > 0:
                print(f"🔍 Auto-screening: Found {kamco_count} Kamco entities, running screening...")
                
                # Initialize matcher
                matcher = FuzzyMatcherEnhanced()
                
                # Get all blacklist entries
                blacklist_entries = db.query(BlacklistEntry).all()
                
                # Screen all entity types
                matches_found = 0
                for entity_type, model in [
                    ("clients", KamcoClient),
                    ("vendors", KamcoVendor),
                    ("staff", KamcoStaff),
                    ("others", KamcoOther)
                ]:
                    entities = db.query(model).all()
                    
                    for entity in entities:
                        for blacklist_entry in blacklist_entries:
                            # Try matching with both English and Arabic names
                            best_match = {'match_score': 0}
                            best_blacklist_name = ""
                            
                            # Check English name
                            if blacklist_entry.name_english:
                                english_match = matcher.match_names(entity.name, blacklist_entry.name_english, use_multiple_algorithms=True)
                                if english_match['match_score'] > best_match['match_score']:
                                    best_match = english_match
                                    best_blacklist_name = blacklist_entry.name_english
                            
                            # Check Arabic name
                            if blacklist_entry.name_arabic:
                                arabic_match = matcher.match_names(entity.name, blacklist_entry.name_arabic, use_multiple_algorithms=True)
                                if arabic_match['match_score'] > best_match['match_score']:
                                    best_match = arabic_match
                                    best_blacklist_name = blacklist_entry.name_arabic
                            
                            # Create flagged item if best match score >= 70
                            if best_match['match_score'] >= 70:
                                # Check if already flagged
                                existing = db.query(FlaggedItem).filter(
                                    FlaggedItem.kamco_name == entity.name,
                                    FlaggedItem.kamco_type == entity_type,
                                    FlaggedItem.blacklist_name == best_blacklist_name
                                ).first()
                                
                                if not existing:
                                    # Determine severity based on match score
                                    if best_match['match_score'] >= 90:
                                        severity = 'high'
                                    elif best_match['match_score'] >= 80:
                                        severity = 'medium'
                                    else:
                                        severity = 'low'
                                    
                                    flagged_item = FlaggedItem(
                                        kamco_name=entity.name,
                                        kamco_type=entity_type,
                                        kamco_id=entity.id,
                                        blacklist_name=best_blacklist_name,
                                        blacklist_source=blacklist_entry.source or "Uploaded",
                                        match_score=best_match['match_score'],
                                        severity=severity,
                                        status='pending',
                                        flagged_by_id=current_user.id,
                                        flag_reason=f"Auto-flagged: Name match {best_match['match_score']:.1f}%",
                                        flag_reason_category='match_confirmed'
                                    )
                                    db.add(flagged_item)
                                    matches_found += 1
                
                db.commit()
                screening_results = {
                    "kamco_entities": kamco_count,
                    "matches_found": matches_found,
                    "auto_screened": True
                }
                print(f"✅ Auto-screening complete: {matches_found} matches found and flagged")
            else:
                print("ℹ️  No Kamco data found - skipping auto-screening")
                screening_results = {
                    "kamco_entities": 0,
                    "matches_found": 0,
                    "auto_screened": False,
                    "message": "No Kamco data to screen against. Upload Kamco file first."
                }
                
        except Exception as e:
            print(f"Warning: Auto-screening failed: {str(e)}")
            # Don't fail the upload if screening fails
            screening_results = {
                "error": str(e),
                "auto_screened": False
            }
        
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
                "upload_time": datetime.now().isoformat(),
                "screening": screening_results  # Include screening results
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


@router.get("/history")
async def get_upload_history(
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    Get upload history
    
    Returns recent upload operations with statistics
    """
    try:
        from models.database import Logbook, User
        from sqlalchemy import desc, or_
        
        # Get recent upload-related log entries (check multiple possible action types)
        uploads = db.query(Logbook).filter(
            or_(
                Logbook.action_type == 'upload',
                Logbook.action_type == 'file_upload',
                Logbook.action_type.like('%upload%')
            )
        ).order_by(
            desc(Logbook.created_at)
        ).limit(limit).all()
        
        history = []
        for upload in uploads:
            # Get user info
            user_name = upload.reviewed_by or 'System'
            if upload.reviewed_by_id:
                user = db.query(User).filter(User.id == upload.reviewed_by_id).first()
                if user:
                    user_name = user.username
            
            history.append({
                'id': upload.id,
                'uploaded_by': user_name,
                'action': upload.action_type,
                'details': upload.notes or 'File upload',
                'filename': 'blacklist_file.xlsx',  # Stored in notes if available
                'timestamp': upload.created_at.isoformat() if upload.created_at else None,
                'status': upload.decision or 'completed'
            })
        
        # Get blacklist entry statistics
        total_entries = db.query(BlacklistEntry).count()
        
        # If no upload logs, return empty history but success
        return {
            'success': True,
            'history': history,
            'total_blacklist_entries': total_entries,
            'count': len(history),
            'message': 'No upload history found' if len(history) == 0 else None
        }
        
    except Exception as e:
        # Log the error but return success with empty data rather than 500
        import logging
        logging.error(f"Error fetching upload history: {str(e)}")
        
        # Return empty history rather than failing
        return {
            'success': True,
            'history': [],
            'total_blacklist_entries': 0,
            'count': 0,
            'message': 'Upload history not available'
        }
