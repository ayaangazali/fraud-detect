"""
Kamco Entities Upload Route
Handles CSV uploads in the kamco_entities_sample.csv format
Robust error handling and validation
"""
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from datetime import datetime
import csv
import io
import pandas as pd

from database.connection import get_db
from models.database import KamcoClient, KamcoVendor, KamcoStaff, KamcoOther, FlaggedItem
from models.blacklist import BlacklistEntry
from utils.logbook import log_action
from utils.auth import get_current_active_user
from utils.fuzzy_matcher_enhanced import FuzzyMatcherEnhanced

router = APIRouter()


# Entity Type Mapping
ENTITY_TYPE_MODELS = {
    'Client': (KamcoClient, 'clients'),
    'Vendor': (KamcoVendor, 'vendors'),
    'Staff': (KamcoStaff, 'staff'),
    'Other': (KamcoOther, 'others')
}


def validate_csv_structure(headers: List[str]) -> tuple[bool, str]:
    """
    Validate CSV has required columns for Kamco entities
    
    Returns: (is_valid, error_message)
    """
    required_fields = ['Customer_ID', 'Name_English', 'Entity_Type']
    missing_fields = [field for field in required_fields if field not in headers]
    
    if missing_fields:
        return False, f"Missing required columns: {', '.join(missing_fields)}"
    
    return True, ""


def parse_kamco_entity_csv(file_contents: bytes, filename: str) -> Dict[str, Any]:
    """
    Parse Kamco entities CSV file
    
    Expected format: kamco_entities_sample.csv structure
    - Customer_ID, Name_English, Name_Arabic, Entity_Type, etc.
    
    Returns:
        {
            'success': bool,
            'entities': List[Dict],  # Parsed entities grouped by type
            'summary': Dict,  # Statistics
            'errors': List[str]  # Any parsing errors
        }
    """
    try:
        # Decode file contents
        try:
            text_content = file_contents.decode('utf-8-sig')  # Handle BOM
        except UnicodeDecodeError:
            try:
                text_content = file_contents.decode('latin-1')
            except:
                return {
                    'success': False,
                    'entities': {},
                    'summary': {},
                    'errors': ['Failed to decode CSV file. Please ensure it is UTF-8 or Latin-1 encoded.']
                }
        
        # Parse CSV
        csv_reader = csv.DictReader(io.StringIO(text_content))
        headers = csv_reader.fieldnames
        
        # Validate structure
        is_valid, error_msg = validate_csv_structure(headers)
        if not is_valid:
            return {
                'success': False,
                'entities': {},
                'summary': {},
                'errors': [error_msg]
            }
        
        # Parse rows
        entities_by_type = {
            'Client': [],
            'Vendor': [],
            'Staff': [],
            'Other': []
        }
        errors = []
        total_rows = 0
        skipped_rows = 0
        
        for row_num, row in enumerate(csv_reader, start=2):  # Start at 2 (header is row 1)
            total_rows += 1
            
            try:
                # Get entity type
                entity_type = row.get('Entity_Type', '').strip()
                
                if not entity_type:
                    errors.append(f"Row {row_num}: Missing Entity_Type")
                    skipped_rows += 1
                    continue
                
                if entity_type not in ENTITY_TYPE_MODELS:
                    errors.append(f"Row {row_num}: Invalid Entity_Type '{entity_type}'. Must be: Client, Vendor, Staff, or Other")
                    skipped_rows += 1
                    continue
                
                # Validate required fields
                customer_id = row.get('Customer_ID', '').strip()
                name_english = row.get('Name_English', '').strip()
                
                if not customer_id:
                    errors.append(f"Row {row_num}: Missing Customer_ID")
                    skipped_rows += 1
                    continue
                
                if not name_english:
                    errors.append(f"Row {row_num}: Missing Name_English")
                    skipped_rows += 1
                    continue
                
                # Create entity dict
                entity = {
                    'customer_id': customer_id,
                    'name': name_english,  # Primary name
                    'name_arabic': row.get('Name_Arabic', '').strip() or None,
                    'entity_category': row.get('Entity_Category', '').strip() or None,
                    'civil_id': row.get('ID_Number', '').strip() or None,
                    'contact_person': row.get('Contact_Person', '').strip() or None,
                    'entity_subtype': row.get('Type_Individual_Corporate', '').strip() or None,
                    'nationality': row.get('Nationality', '').strip() or None,
                    'country': row.get('Country_of_Origin', '').strip() or None,
                    'industry': row.get('Industry_Sector', '').strip() or None,
                    'risk_level': row.get('Risk_Level', '').strip() or None,
                    'status': row.get('Account_Status', '').strip() or 'Active',
                    'phone': row.get('Phone', '').strip() or None,
                    'email': row.get('Email', '').strip() or None,
                    'address': row.get('Address', '').strip() or None,
                    'notes': row.get('Notes', '').strip() or None,
                }
                
                # Parse registration date
                reg_date_str = row.get('Registration_Date', '').strip()
                if reg_date_str:
                    try:
                        # Try different date formats
                        for date_format in ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%Y/%m/%d']:
                            try:
                                entity['registration_date'] = datetime.strptime(reg_date_str, date_format)
                                break
                            except ValueError:
                                continue
                    except:
                        entity['registration_date'] = None
                else:
                    entity['registration_date'] = None
                
                # Add to appropriate list
                entities_by_type[entity_type].append(entity)
                
            except Exception as e:
                errors.append(f"Row {row_num}: Unexpected error - {str(e)}")
                skipped_rows += 1
                continue
        
        # Calculate summary
        total_valid = sum(len(entities) for entities in entities_by_type.values())
        
        summary = {
            'total_rows': total_rows,
            'valid_entities': total_valid,
            'skipped_rows': skipped_rows,
            'clients': len(entities_by_type['Client']),
            'vendors': len(entities_by_type['Vendor']),
            'staff': len(entities_by_type['Staff']),
            'others': len(entities_by_type['Other']),
            'filename': filename,
            'parsed_at': datetime.now().isoformat()
        }
        
        return {
            'success': True,
            'entities': entities_by_type,
            'summary': summary,
            'errors': errors
        }
        
    except Exception as e:
        return {
            'success': False,
            'entities': {},
            'summary': {},
            'errors': [f"Fatal parsing error: {str(e)}"]
        }


@router.post("/kamco-entities")
async def upload_kamco_entities(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    Upload Kamco entities CSV file
    
    **Expected CSV Format:**
    - Customer_ID (required)
    - Name_English (required)
    - Name_Arabic (optional)
    - Entity_Type (required): Client, Vendor, Staff, or Other
    - Entity_Category (optional)
    - ID_Number (optional): Civil ID or Registration Number
    - Registration_Date (optional)
    - Contact_Person (optional)
    - Type_Individual_Corporate (optional)
    - Nationality (optional)
    - Country_of_Origin (optional)
    - Industry_Sector (optional)
    - Risk_Level (optional)
    - Account_Status (optional)
    - Phone (optional)
    - Email (optional)
    - Address (optional)
    - Notes (optional)
    
    **Returns:**
    - Upload summary with record counts
    - Auto-screening results (if blacklist data exists)
    - Detailed error information if any
    
    **Auto-Screening:**
    - Automatically screens uploaded entities against existing blacklist
    - Creates flagged items for matches >= 70%
    - Provides match summary in response
    """
    
    # Validate file type
    if not file.filename.lower().endswith('.csv'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Only CSV files (.csv) are accepted."
        )
    
    try:
        # Read file contents
        file_contents = await file.read()
        
        # Parse CSV
        parse_result = parse_kamco_entity_csv(file_contents, file.filename)
        
        if not parse_result['success']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    'message': 'Failed to parse CSV file',
                    'errors': parse_result['errors']
                }
            )
        
        entities_by_type = parse_result['entities']
        summary = parse_result['summary']
        parse_errors = parse_result['errors']
        
        if summary['valid_entities'] == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    'message': 'No valid entities found in CSV file',
                    'errors': parse_errors
                }
            )
        
        # Store entities in database
        stored_counts = {
            'clients': 0,
            'vendors': 0,
            'staff': 0,
            'others': 0
        }
        storage_errors = []
        
        try:
            # Store Clients
            for entity_data in entities_by_type['Client']:
                try:
                    # Check for duplicates
                    existing = db.query(KamcoClient).filter(
                        KamcoClient.customer_id == entity_data['customer_id']
                    ).first()
                    
                    if existing:
                        storage_errors.append(f"Client {entity_data['customer_id']} already exists - skipped")
                        continue
                    
                    client = KamcoClient(**entity_data)
                    db.add(client)
                    stored_counts['clients'] += 1
                except Exception as e:
                    storage_errors.append(f"Failed to store client {entity_data.get('customer_id', 'unknown')}: {str(e)}")
            
            # Store Vendors
            for entity_data in entities_by_type['Vendor']:
                try:
                    existing = db.query(KamcoVendor).filter(
                        KamcoVendor.customer_id == entity_data['customer_id']
                    ).first()
                    
                    if existing:
                        storage_errors.append(f"Vendor {entity_data['customer_id']} already exists - skipped")
                        continue
                    
                    vendor = KamcoVendor(**entity_data)
                    db.add(vendor)
                    stored_counts['vendors'] += 1
                except Exception as e:
                    storage_errors.append(f"Failed to store vendor {entity_data.get('customer_id', 'unknown')}: {str(e)}")
            
            # Store Staff
            for entity_data in entities_by_type['Staff']:
                try:
                    existing = db.query(KamcoStaff).filter(
                        KamcoStaff.customer_id == entity_data['customer_id']
                    ).first()
                    
                    if existing:
                        storage_errors.append(f"Staff {entity_data['customer_id']} already exists - skipped")
                        continue
                    
                    staff = KamcoStaff(**entity_data)
                    db.add(staff)
                    stored_counts['staff'] += 1
                except Exception as e:
                    storage_errors.append(f"Failed to store staff {entity_data.get('customer_id', 'unknown')}: {str(e)}")
            
            # Store Others
            for entity_data in entities_by_type['Other']:
                try:
                    existing = db.query(KamcoOther).filter(
                        KamcoOther.customer_id == entity_data['customer_id']
                    ).first()
                    
                    if existing:
                        storage_errors.append(f"Other entity {entity_data['customer_id']} already exists - skipped")
                        continue
                    
                    other = KamcoOther(**entity_data)
                    db.add(other)
                    stored_counts['others'] += 1
                except Exception as e:
                    storage_errors.append(f"Failed to store other entity {entity_data.get('customer_id', 'unknown')}: {str(e)}")
            
            # Commit all entities
            db.commit()
            
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error: {str(e)}"
            )
        
        total_stored = sum(stored_counts.values())
        
        # Log the upload
        log_action(
            db=db,
            user_id=current_user.id,
            action="KAMCO_ENTITIES_UPLOADED",
            details=f"Uploaded {total_stored} Kamco entities from {file.filename}",
            metadata={
                "filename": file.filename,
                "total_rows": summary['total_rows'],
                "valid_entities": summary['valid_entities'],
                "stored": stored_counts,
                "total_stored": total_stored,
                "parse_errors": len(parse_errors),
                "storage_errors": len(storage_errors)
            }
        )
        
        # AUTO-SCREEN: Run screening against existing blacklist
        screening_results = None
        try:
            blacklist_count = db.query(BlacklistEntry).filter(
                BlacklistEntry.status == "Active"
            ).count()
            
            if blacklist_count > 0:
                print(f"🔍 Auto-screening: Found {blacklist_count} blacklist entries, running screening...")
                
                matcher = FuzzyMatcherEnhanced()
                blacklist_entries = db.query(BlacklistEntry).filter(
                    BlacklistEntry.status == "Active"
                ).all()
                
                matches_found = 0
                
                # Screen each entity type
                for entity_type, (model, type_key) in ENTITY_TYPE_MODELS.items():
                    entities = db.query(model).all()
                    
                    for entity in entities:
                        for blacklist_entry in blacklist_entries:
                            # Match against both English and Arabic names
                            best_match = {'match_score': 0}
                            best_blacklist_name = ""
                            
                            # Check English name
                            if blacklist_entry.name_english:
                                english_match = matcher.match_names(
                                    entity.name,
                                    blacklist_entry.name_english,
                                    use_multiple_algorithms=True
                                )
                                if english_match['match_score'] > best_match['match_score']:
                                    best_match = english_match
                                    best_blacklist_name = blacklist_entry.name_english
                            
                            # Check Arabic name
                            if hasattr(entity, 'name_arabic') and entity.name_arabic and blacklist_entry.name_arabic:
                                arabic_match = matcher.match_names(
                                    entity.name_arabic,
                                    blacklist_entry.name_arabic,
                                    use_multiple_algorithms=True
                                )
                                if arabic_match['match_score'] > best_match['match_score']:
                                    best_match = arabic_match
                                    best_blacklist_name = blacklist_entry.name_arabic
                            
                            # Flag if match score >= 70
                            if best_match['match_score'] >= 70:
                                # Check if already flagged
                                existing_flag = db.query(FlaggedItem).filter(
                                    FlaggedItem.kamco_name == entity.name,
                                    FlaggedItem.kamco_type == type_key,
                                    FlaggedItem.blacklist_name == best_blacklist_name
                                ).first()
                                
                                if not existing_flag:
                                    # Determine severity
                                    if best_match['match_score'] >= 90:
                                        severity = 'high'
                                    elif best_match['match_score'] >= 80:
                                        severity = 'medium'
                                    else:
                                        severity = 'low'
                                    
                                    flagged_item = FlaggedItem(
                                        kamco_name=entity.name,
                                        kamco_type=type_key,
                                        kamco_id=entity.id,
                                        blacklist_name=best_blacklist_name,
                                        blacklist_source=blacklist_entry.source or "Blacklist",
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
                    "blacklist_entries": blacklist_count,
                    "entities_screened": total_stored,
                    "matches_found": matches_found,
                    "auto_screened": True
                }
                print(f"✅ Auto-screening complete: {matches_found} matches found and flagged")
            else:
                print("ℹ️  No blacklist data found - skipping auto-screening")
                screening_results = {
                    "blacklist_entries": 0,
                    "entities_screened": total_stored,
                    "matches_found": 0,
                    "auto_screened": False,
                    "message": "No blacklist data to screen against. Upload blacklist file first."
                }
        
        except Exception as e:
            print(f"⚠️  Warning: Auto-screening failed: {str(e)}")
            screening_results = {
                "error": str(e),
                "auto_screened": False
            }
        
        # Prepare response
        all_errors = parse_errors + storage_errors
        
        return {
            "success": True,
            "message": f"Successfully uploaded {total_stored} Kamco entities",
            "data": {
                "filename": file.filename,
                "upload_time": datetime.now().isoformat(),
                "summary": {
                    "total_rows": summary['total_rows'],
                    "valid_entities": summary['valid_entities'],
                    "stored_entities": total_stored,
                    "by_type": stored_counts,
                    "skipped": summary['skipped_rows'] + (summary['valid_entities'] - total_stored)
                },
                "screening": screening_results,
                "errors": all_errors[:20] if all_errors else [],  # Show first 20 errors
                "total_errors": len(all_errors)
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Upload failed: {str(e)}"
        )


@router.get("/kamco-entities/summary")
async def get_kamco_entities_summary(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    Get summary of Kamco entities in database
    """
    try:
        summary = {
            "clients": db.query(KamcoClient).count(),
            "vendors": db.query(KamcoVendor).count(),
            "staff": db.query(KamcoStaff).count(),
            "others": db.query(KamcoOther).count()
        }
        summary["total"] = sum(summary.values())
        
        return {
            "success": True,
            "data": summary
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get summary: {str(e)}"
        )


@router.delete("/kamco-entities/clear")
async def clear_kamco_entities(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    Clear all Kamco entities from database
    Requires finalizer or admin role
    """
    if current_user.role not in ['finalizer', 'admin']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only finalizer or admin can clear Kamco entities"
        )
    
    try:
        # Delete all entities
        counts = {
            "clients": db.query(KamcoClient).delete(),
            "vendors": db.query(KamcoVendor).delete(),
            "staff": db.query(KamcoStaff).delete(),
            "others": db.query(KamcoOther).delete()
        }
        
        db.commit()
        
        # Log action
        log_action(
            db=db,
            user_id=current_user.id,
            action="KAMCO_ENTITIES_CLEARED",
            details=f"Cleared all Kamco entities",
            metadata={"counts": counts, "total": sum(counts.values())}
        )
        
        return {
            "success": True,
            "message": f"Cleared {sum(counts.values())} Kamco entities",
            "data": counts
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to clear entities: {str(e)}"
        )
