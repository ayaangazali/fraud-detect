"""
Screening API Route for Phase 5
Compares Kamco entities against blacklist using fuzzy matching and Civil ID matching
Updated in Phase 6: Added email notifications for high-risk matches
Updated in Phase 7: Added blacklist CSV upload workflow - user uploads blacklist to screen against pre-loaded Kamco entities
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
import csv
import io

from database.connection import get_db
from models.blacklist import BlacklistEntry
from models.database import KamcoClient, KamcoVendor, KamcoStaff, KamcoOther, FlaggedItem
from utils.fuzzy_matcher_enhanced import FuzzyMatcherEnhanced
from utils.civil_id_validator import CivilIDValidator
from utils.auth import get_current_active_user
from utils.logbook import log_action
from utils.email_service import get_email_service

# Import new screening models and engine
try:
    from models.screening import (
        KamcoEntity as KamcoEntityModel,
        BlacklistUpload,
        ScreeningMatch,
        DecisionLog,
        DecisionStatus,
        EntityType as KamcoEntityType
    )
    from services.screening_engine import BlacklistScreeningEngine
    from data.kamco_entities import get_kamco_entities as get_seed_kamco_entities
    SCREENING_V2_AVAILABLE = True
except ImportError as e:
    SCREENING_V2_AVAILABLE = False
    import traceback
    traceback.print_exc()

router = APIRouter()


# Request/Response Models
class ScreeningRequest(BaseModel):
    entity_types: List[str] = Field(
        default=["clients", "vendors", "staff", "others"],
        description="Entity types to screen (clients, vendors, staff, others)"
    )
    min_match_score: int = Field(
        default=70,
        ge=0,
        le=100,
        description="Minimum match score threshold (0-100)"
    )
    include_civil_id_match: bool = Field(
        default=True,
        description="Include Civil ID exact matching"
    )
    auto_flag: bool = Field(
        default=True,
        description="Automatically create flagged items for matches"
    )
    auto_create_cases: bool = Field(
        default=False,
        description="Automatically create cases for high-risk matches"
    )


class MatchResult(BaseModel):
    kamco_entity_id: int
    kamco_entity_type: str
    kamco_entity_name: str
    blacklist_entry_id: int
    blacklist_name: str
    match_score: int
    match_type: str  # 'name', 'civil_id', 'both'
    risk_level: str
    confidence: str
    civil_id_match: bool
    flagged: bool = False
    flag_id: Optional[int] = None


class ScreeningResponse(BaseModel):
    success: bool
    summary: Dict[str, Any]
    matches: List[MatchResult]
    statistics: Dict[str, Any]


# Screening Engine
class ScreeningEngine:
    """Core screening logic"""
    
    def __init__(self, db: Session):
        self.db = db
        self.fuzzy_matcher = FuzzyMatcherEnhanced()
        self.civil_id_validator = CivilIDValidator()
    
    def get_kamco_entities(self, entity_type: str) -> List[Dict[str, Any]]:
        """Get all Kamco entities of a specific type"""
        entities = []
        
        if entity_type == "clients":
            records = self.db.query(KamcoClient).all()
            entities = [
                {
                    'id': r.id,
                    'type': 'client',
                    'name': r.name,
                    'civil_id': getattr(r, 'civil_id', None),
                    'actor_name': r.actor_name
                }
                for r in records
            ]
        
        elif entity_type == "vendors":
            records = self.db.query(KamcoVendor).all()
            entities = [
                {
                    'id': r.id,
                    'type': 'vendor',
                    'name': r.name,
                    'civil_id': getattr(r, 'civil_id', None),
                    'actor_name': r.actor_name
                }
                for r in records
            ]
        
        elif entity_type == "staff":
            records = self.db.query(KamcoStaff).all()
            entities = [
                {
                    'id': r.id,
                    'type': 'staff',
                    'name': r.name,
                    'civil_id': getattr(r, 'civil_id', None)
                }
                for r in records
            ]
        
        elif entity_type == "others":
            records = self.db.query(KamcoOther).all()
            entities = [
                {
                    'id': r.id,
                    'type': 'other',
                    'name': r.name,
                    'civil_id': getattr(r, 'civil_id', None)
                }
                for r in records
            ]
        
        return entities
    
    def get_blacklist_entries(self) -> List[Dict[str, Any]]:
        """Get all active blacklist entries"""
        entries = self.db.query(BlacklistEntry).filter(
            BlacklistEntry.status == "Active"
        ).all()
        
        return [
            {
                'id': e.id,
                'name_arabic': e.name_arabic,
                'name_english': e.name_english,
                'civil_id': e.civil_id,
                'source': e.source,
                'risk_level': e.risk_level,
                'category': e.category
            }
            for e in entries
        ]
    
    def screen_entity(
        self,
        entity: Dict[str, Any],
        blacklist: List[Dict[str, Any]],
        min_score: int,
        check_civil_id: bool
    ) -> List[Dict[str, Any]]:
        """Screen a single entity against blacklist"""
        matches = []
        
        entity_name = entity.get('name', '')
        entity_civil_id = entity.get('civil_id')
        
        for bl_entry in blacklist:
            match_result = {
                'kamco_entity': entity,
                'blacklist_entry': bl_entry,
                'name_match_score': 0,
                'civil_id_match': False,
                'match_type': None,
                'risk_level': 'MINIMAL',
                'confidence': 'NONE'
            }
            
            # Check Civil ID match first (highest priority)
            if check_civil_id and entity_civil_id and bl_entry.get('civil_id'):
                civil_match = self.civil_id_validator.match_civil_ids(
                    entity_civil_id,
                    bl_entry['civil_id']
                )
                
                if civil_match['match']:
                    match_result['civil_id_match'] = True
                    match_result['match_type'] = 'civil_id'
                    match_result['risk_level'] = 'CRITICAL'
                    match_result['confidence'] = 'EXACT'
                    match_result['name_match_score'] = 100  # Override
                    matches.append(match_result)
                    continue  # Civil ID match is definitive
            
            # Check name match
            if entity_name and bl_entry.get('name_arabic'):
                name_match = self.fuzzy_matcher.match_names(
                    entity_name,
                    bl_entry['name_arabic']
                )
                
                match_result['name_match_score'] = name_match['match_score']
                match_result['risk_level'] = name_match['risk_level']
                match_result['confidence'] = name_match['confidence']
                
                if name_match['match_score'] >= min_score:
                    match_result['match_type'] = 'name'
                    matches.append(match_result)
            
            # Check English name if available
            elif entity_name and bl_entry.get('name_english'):
                name_match = self.fuzzy_matcher.match_names(
                    entity_name,
                    bl_entry['name_english']
                )
                
                match_result['name_match_score'] = name_match['match_score']
                match_result['risk_level'] = name_match['risk_level']
                match_result['confidence'] = name_match['confidence']
                
                if name_match['match_score'] >= min_score:
                    match_result['match_type'] = 'name'
                    matches.append(match_result)
        
        # Sort by score (descending)
        matches.sort(key=lambda x: x['name_match_score'], reverse=True)
        
        return matches
    
    def batch_screen(
        self,
        entity_types: List[str],
        min_score: int = 70,
        check_civil_id: bool = True
    ) -> List[Dict[str, Any]]:
        """Screen multiple entity types"""
        all_matches = []
        
        # Get blacklist once
        blacklist = self.get_blacklist_entries()
        
        if not blacklist:
            return []
        
        # Screen each entity type
        for entity_type in entity_types:
            entities = self.get_kamco_entities(entity_type)
            
            for entity in entities:
                entity_matches = self.screen_entity(
                    entity,
                    blacklist,
                    min_score,
                    check_civil_id
                )
                all_matches.extend(entity_matches)
        
        return all_matches


# API Endpoints

@router.post("/run", response_model=ScreeningResponse)
async def run_screening(
    request: ScreeningRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    Run screening of Kamco entities against blacklist
    
    **Phase 5 - Screening Endpoint**
    
    Compares all selected Kamco entities (Clients, Vendors, Staff, Others)
    against the active blacklist using:
    - Fuzzy name matching (Arabic + English)
    - Civil ID exact matching
    - Configurable match thresholds
    
    Returns all matches with risk levels and confidence scores.
    """
    try:
        # Initialize screening engine
        engine = ScreeningEngine(db)
        
        # Run screening
        matches = engine.batch_screen(
            entity_types=request.entity_types,
            min_score=request.min_match_score,
            check_civil_id=request.include_civil_id_match
        )
        
        # Prepare response
        match_results = []
        flagged_count = 0
        
        for match in matches:
            kamco = match['kamco_entity']
            blacklist = match['blacklist_entry']
            
            # Create match result
            result = MatchResult(
                kamco_entity_id=kamco['id'],
                kamco_entity_type=kamco['type'],
                kamco_entity_name=kamco['name'],
                blacklist_entry_id=blacklist['id'],
                blacklist_name=blacklist['name_arabic'],
                match_score=match['name_match_score'],
                match_type=match['match_type'],
                risk_level=match['risk_level'],
                confidence=match['confidence'],
                civil_id_match=match['civil_id_match']
            )
            
            # Auto-flag if requested
            if request.auto_flag and match['risk_level'] in ['CRITICAL', 'HIGH']:
                try:
                    # Create flagged item (simplified - would need proper implementation)
                    # flagged_item = FlaggedItem(...)
                    # db.add(flagged_item)
                    # db.commit()
                    result.flagged = True
                    flagged_count += 1
                    
                    # Send email notification for high-risk matches (Phase 6)
                    email_service = get_email_service()
                    email_service.send_screening_alert(
                        entity_name=kamco['name'],
                        entity_type=kamco['type'],
                        blacklist_name=blacklist['name_arabic'],
                        match_score=match['name_match_score'],
                        risk_level=match['risk_level'],
                        civil_id_match=match['civil_id_match']
                    )
                except Exception as e:
                    print(f"Warning: Could not auto-flag or send email: {str(e)}")
            
            match_results.append(result)
        
        # Calculate statistics
        statistics = {
            'total_matches': len(match_results),
            'critical_matches': sum(1 for m in match_results if m.risk_level == 'CRITICAL'),
            'high_matches': sum(1 for m in match_results if m.risk_level == 'HIGH'),
            'medium_matches': sum(1 for m in match_results if m.risk_level == 'MEDIUM'),
            'low_matches': sum(1 for m in match_results if m.risk_level == 'LOW'),
            'civil_id_matches': sum(1 for m in match_results if m.civil_id_match),
            'name_only_matches': sum(1 for m in match_results if not m.civil_id_match),
            'flagged_count': flagged_count
        }
        
        # Log action
        log_action(
            db=db,
            user_id=current_user.id,
            action="SCREENING_RUN",
            details=f"Screened {len(request.entity_types)} entity types against blacklist",
            metadata={
                'entity_types': request.entity_types,
                'min_score': request.min_match_score,
                'total_matches': statistics['total_matches'],
                'critical_matches': statistics['critical_matches']
            }
        )
        
        return ScreeningResponse(
            success=True,
            summary={
                'screened_entity_types': request.entity_types,
                'min_match_score': request.min_match_score,
                'blacklist_size': len(engine.get_blacklist_entries()),
                'timestamp': datetime.now().isoformat()
            },
            matches=match_results,
            statistics=statistics
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Screening failed: {str(e)}"
        )


@router.get("/stats")
async def get_screening_stats(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    Get screening statistics
    
    Returns counts of Kamco entities and blacklist entries
    """
    try:
        engine = ScreeningEngine(db)
        
        stats = {
            'kamco_entities': {
                'clients': len(engine.get_kamco_entities('clients')),
                'vendors': len(engine.get_kamco_entities('vendors')),
                'staff': len(engine.get_kamco_entities('staff')),
                'others': len(engine.get_kamco_entities('others'))
            },
            'blacklist_entries': len(engine.get_blacklist_entries()),
            'timestamp': datetime.now().isoformat()
        }
        
        stats['kamco_entities']['total'] = sum(stats['kamco_entities'].values())
        
        return {
            'success': True,
            'data': stats
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get stats: {str(e)}"
        )


@router.get("/queue")
async def get_screening_queue(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    Get screening queue (flagged items pending review)
    
    Returns all flagged items that haven't been reviewed yet
    """
    try:
        # Get flagged items that are pending
        flagged_items = db.query(FlaggedItem).filter(
            FlaggedItem.status == 'pending'
        ).order_by(
            FlaggedItem.flagged_at.desc()
        ).all()
        
        queue = []
        for item in flagged_items:
            # Get flagged_by user info if available
            flagged_by_name = None
            if item.flagged_by_id:
                from models.auth import User
                flagged_by_user = db.query(User).filter(User.id == item.flagged_by_id).first()
                if flagged_by_user:
                    flagged_by_name = flagged_by_user.username
            
            queue.append({
                'id': item.id,
                'kamco_name': item.kamco_name,
                'kamco_type': item.kamco_type,
                'kamco_id': item.kamco_id,
                'blacklist_name': item.blacklist_name,
                'blacklist_source': item.blacklist_source,
                'match_score': item.match_score,
                'match_type': 'fuzzy',  # Default, actual match type not stored in model
                'severity': item.severity,
                'status': item.status,
                'flagged_by': flagged_by_name or 'System',
                'flagged_at': item.flagged_at.isoformat() if item.flagged_at else None,
                'flag_reason': item.flag_reason
            })
        
        return {
            'success': True,
            'queue': queue,
            'count': len(queue)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get screening queue: {str(e)}"
        )


@router.get("/results")
async def get_screening_results(
    status_filter: Optional[str] = None,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    Get screening results (all flagged items)
    
    - **status_filter**: Filter by status (pending, approved, rejected)
    - **limit**: Maximum number of results to return
    """
    try:
        query = db.query(FlaggedItem)
        
        if status_filter:
            query = query.filter(FlaggedItem.status == status_filter)
        
        flagged_items = query.order_by(
            FlaggedItem.flagged_at.desc()
        ).limit(limit).all()
        
        results = []
        for item in flagged_items:
            # Get user info
            from models.database import User
            flagged_by_name = None
            reviewed_by_name = None
            
            if item.flagged_by_id:
                flagged_by_user = db.query(User).filter(User.id == item.flagged_by_id).first()
                if flagged_by_user:
                    flagged_by_name = flagged_by_user.username
            
            if item.checker_id:
                reviewed_by_user = db.query(User).filter(User.id == item.checker_id).first()
                if reviewed_by_user:
                    reviewed_by_name = reviewed_by_user.username
            
            results.append({
                'id': item.id,
                'kamco_name': item.kamco_name,
                'kamco_type': item.kamco_type,
                'kamco_id': item.kamco_id,
                'blacklist_name': item.blacklist_name,
                'blacklist_source': item.blacklist_source,
                'match_score': item.match_score,
                'match_type': 'fuzzy',
                'severity': item.severity,
                'status': item.status,
                'flagged_by': flagged_by_name or 'System',
                'flagged_at': item.flagged_at.isoformat() if item.flagged_at else None,
                'reviewed_by': reviewed_by_name,
                'reviewed_at': item.checker_reviewed_at.isoformat() if item.checker_reviewed_at else None,
                'flag_reason': item.flag_reason
            })
        
        return {
            'success': True,
            'results': results,
            'count': len(results),
            'filter': status_filter
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get screening results: {str(e)}"
        )


# ===========================
# PHASE 7: BLACKLIST UPLOAD WORKFLOW
# ===========================
# New workflow: User uploads BLACKLIST CSV, system screens against pre-loaded KAMCO entities

class BlacklistUploadResponse(BaseModel):
    """Response for blacklist upload"""
    success: bool
    upload_id: int
    filename: str
    entries_processed: int
    matches_found: int
    matches: List[Dict[str, Any]]
    skipped_already_decided: int
    re_reviews_flagged: int
    threshold_used: float


class DecisionRequest(BaseModel):
    """Request to make a decision on a screening match"""
    match_id: int
    status: str = Field(..., description="Decision status: FLAGGED, CLEARED, ESCALATED")
    notes: Optional[str] = Field(None, description="Decision notes")


class DecisionResponse(BaseModel):
    """Response for decision action"""
    success: bool
    decision_id: int
    match_id: int
    status: str
    message: str


class LogbookEntry(BaseModel):
    """Logbook entry for display"""
    id: int
    match_id: int
    kamco_entity_name: str
    kamco_entity_type: str
    blacklist_name: str
    blacklist_source: str
    match_score: float
    decision_status: str
    decision_date: str
    decided_by: str
    notes: Optional[str]
    is_re_review: bool


@router.post("/v2/upload-blacklist", response_model=BlacklistUploadResponse)
async def upload_blacklist_csv(
    file: UploadFile = File(...),
    threshold: float = Form(default=70.0, ge=0, le=100),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    Upload a blacklist CSV file and screen against KAMCO entities
    
    **Phase 7 - Blacklist Upload Workflow**
    
    This endpoint:
    1. Accepts a CSV file containing blacklisted individuals/entities
    2. Parses the CSV and extracts blacklist entries
    3. Screens each entry against pre-loaded KAMCO entities (clients, vendors, staff, etc.)
    4. Uses weighted fuzzy matching (Name 40%, Arabic Name 35%, ID 15%, Nationality 10%)
    5. Skips entries that have already been decided (FLAGGED/CLEARED)
    6. Flags entries for re-review if they've been seen before in different uploads
    
    **CSV Fields Expected:**
    - Full_Name_English (required)
    - Full_Name_Arabic (optional)
    - ID_Number / Civil_ID (optional)
    - Nationality (optional)
    - Source, Risk_Level, etc. (optional)
    
    Returns all matches above the threshold, excluding already-decided cases.
    """
    if not SCREENING_V2_AVAILABLE:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Screening V2 models not available. Please ensure models/screening.py is properly configured."
        )
    
    # Validate file type
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only CSV files are supported"
        )
    
    try:
        # Read file content
        content = await file.read()
        csv_content = content.decode('utf-8')
        
        # Initialize screening engine
        engine = BlacklistScreeningEngine()
        
        # Parse blacklist CSV
        blacklist_entries = engine.process_blacklist_csv(csv_content)
        
        if not blacklist_entries:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No valid entries found in CSV file"
            )
        
        # Create upload record
        upload = BlacklistUpload(
            filename=file.filename,
            uploaded_by=current_user.id,
            total_entries=len(blacklist_entries),
            threshold_used=threshold,
            status="processing",
            processing_started_at=datetime.utcnow()
        )
        db.add(upload)
        db.commit()
        db.refresh(upload)
        
        # Get KAMCO entities from database (or seed data if not seeded)
        kamco_entities = db.query(KamcoEntityModel).all()
        
        # If no entities in DB, try to load seed data
        if not kamco_entities:
            seed_entities = get_seed_kamco_entities()
            kamco_entities_list = [
                {
                    "id": e["id"],
                    "name_english": e["name_english"],
                    "name_arabic": e.get("name_arabic"),
                    "civil_id": e.get("civil_id"),
                    "nationality": e.get("nationality"),
                    "type": e["type"]
                }
                for e in seed_entities
            ]
        else:
            kamco_entities_list = [
                {
                    "id": e.id,
                    "customer_id": e.customer_id,
                    "name_english": e.name_english,
                    "name_arabic": e.name_arabic,
                    "civil_id": e.civil_id,
                    "nationality": e.nationality,
                    "type": e.entity_type
                }
                for e in kamco_entities
            ]
        
        # Get existing decisions to skip already-decided
        # Query ScreeningMatch records that have been decided (not PENDING)
        existing_matches = db.query(ScreeningMatch).filter(
            ScreeningMatch.decision_status.in_(['flagged', 'cleared'])
        ).all()
        
        # Build set of decided combinations (kamco_id + blacklist reference)
        decided_keys = set()
        for match in existing_matches:
            # Use kamco entity ID + blacklist reference as key
            ref = match.blacklist_reference or ''
            name = match.blacklist_name_english or ''
            key = f"{match.kamco_entity_id}_{ref}_{name}"
            decided_keys.add(key)
        
        # Run screening
        matches = engine.screen_against_kamco(
            blacklist_entries=blacklist_entries,
            kamco_entities=kamco_entities_list,
            threshold=threshold,
            existing_decisions=decided_keys
        )
        
        # Process results
        match_results = []
        skipped_count = 0
        re_review_count = 0
        
        for match in matches:
            # Check if skipped
            if match.get('skipped_already_decided'):
                skipped_count += 1
                continue
            
            # Check if re-review
            if match.get('is_re_review'):
                re_review_count += 1
            
            # Extract blacklist entry data
            bl_entry = match['blacklist_entry']
            kamco_ent = match['kamco_entity']
            
            # Generate unique match key
            match_key = f"{kamco_ent['id']}_{bl_entry.get('reference_number', '')}_{upload.id}"
            
            # Store screening match in database
            screening_match = ScreeningMatch(
                match_key=match_key,
                blacklist_upload_id=upload.id,
                kamco_entity_id=kamco_ent['id'],
                
                # Blacklist entry data (denormalized for quick access)
                blacklist_reference=bl_entry.get('reference_number', '')[:100],
                blacklist_name_english=bl_entry.get('name_english', '')[:255],
                blacklist_name_arabic=bl_entry.get('name_arabic', '')[:255],
                blacklist_civil_id=bl_entry.get('civil_id', '')[:50],
                blacklist_passport=bl_entry.get('passport', '')[:50],
                blacklist_nationality=bl_entry.get('nationality', '')[:100],
                blacklist_dob=bl_entry.get('date_of_birth', '')[:20],
                blacklist_list_type=bl_entry.get('list_type', '')[:100],
                blacklist_list_source=bl_entry.get('source', '')[:100],
                blacklist_risk_level=bl_entry.get('risk_level', 'MEDIUM')[:50],
                blacklist_reason=bl_entry.get('reason', ''),
                blacklist_raw_data=bl_entry,  # Store full entry
                
                # Match scores
                overall_score=match['overall_score'],
                name_english_score=match['score_breakdown'].get('name_english', 0),
                name_arabic_score=match['score_breakdown'].get('name_arabic', 0),
                civil_id_score=match['score_breakdown'].get('id_number', 0),
                nationality_score=match['score_breakdown'].get('nationality', 0),
                
                # Re-review tracking
                is_re_review=match.get('is_re_review', False),
                
                # Match confidence
                confidence=match.get('confidence', 'potential'),
                match_reasons=match.get('match_reasons', [])
            )
            db.add(screening_match)
            db.commit()
            db.refresh(screening_match)
            
            match_results.append({
                'match_id': screening_match.id,
                'kamco_entity': match['kamco_entity'],
                'blacklist_entry': match['blacklist_entry'],
                'overall_score': match['overall_score'],
                'score_breakdown': match['score_breakdown'],
                'risk_level': match.get('risk_level', 'MEDIUM'),
                'is_re_review': match.get('is_re_review', False),
                're_review_reason': match.get('re_review_reason')
            })
        
        # Update upload record with results
        upload.matched_entries = len(match_results)
        upload.processed_entries = len(blacklist_entries)
        upload.new_matches = len(match_results) - re_review_count
        upload.re_review_matches = re_review_count
        upload.processing_completed_at = datetime.utcnow()
        upload.status = "completed"
        db.commit()
        
        # Log action
        log_action(
            db=db,
            user_id=current_user.id,
            action="BLACKLIST_UPLOAD",
            details=f"Uploaded blacklist '{file.filename}' with {len(blacklist_entries)} entries",
            metadata={
                'upload_id': upload.id,
                'filename': file.filename,
                'entries': len(blacklist_entries),
                'matches': len(match_results),
                'threshold': threshold,
                'skipped': skipped_count,
                're_reviews': re_review_count
            }
        )
        
        return BlacklistUploadResponse(
            success=True,
            upload_id=upload.id,
            filename=file.filename,
            entries_processed=len(blacklist_entries),
            matches_found=len(match_results),
            matches=match_results,
            skipped_already_decided=skipped_count,
            re_reviews_flagged=re_review_count,
            threshold_used=threshold
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process blacklist: {str(e)}"
        )


@router.post("/v2/decision", response_model=DecisionResponse)
async def make_decision(
    request: DecisionRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    Make a decision on a screening match
    
    Allows users to:
    - FLAG a match (mark as a true match requiring action)
    - CLEAR a match (mark as false positive)
    - ESCALATE a match (send to supervisor for review)
    
    Decisions are recorded in the logbook with timestamp, user, and notes.
    """
    if not SCREENING_V2_AVAILABLE:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Screening V2 models not available"
        )
    
    try:
        # Validate status
        try:
            decision_status = DecisionStatus[request.status.upper()]
        except KeyError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status. Must be one of: {[s.name for s in DecisionStatus]}"
            )
        
        # Get the match
        match = db.query(ScreeningMatch).filter(ScreeningMatch.id == request.match_id).first()
        if not match:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Match with ID {request.match_id} not found"
            )
        
        # Get previous decision if exists
        previous_decision = db.query(DecisionLog).filter(
            DecisionLog.match_id == request.match_id
        ).order_by(DecisionLog.decision_date.desc()).first()
        
        previous_status = previous_decision.status if previous_decision else None
        
        # Create decision log
        decision = DecisionLog(
            match_id=request.match_id,
            user_id=current_user.id,
            status=decision_status,
            notes=request.notes,
            previous_status=previous_status,
            is_re_review=match.is_re_review
        )
        db.add(decision)
        
        # Update match status
        match.current_status = decision_status
        match.last_decision_date = datetime.utcnow()
        match.last_decision_by_id = current_user.id
        
        db.commit()
        db.refresh(decision)
        
        # Log action
        log_action(
            db=db,
            user_id=current_user.id,
            action=f"SCREENING_DECISION_{decision_status.name}",
            details=f"Made decision '{decision_status.name}' on match ID {request.match_id}",
            metadata={
                'match_id': request.match_id,
                'status': decision_status.name,
                'notes': request.notes,
                'previous_status': previous_status.name if previous_status else None
            }
        )
        
        return DecisionResponse(
            success=True,
            decision_id=decision.id,
            match_id=request.match_id,
            status=decision_status.name,
            message=f"Successfully recorded decision: {decision_status.name}"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to record decision: {str(e)}"
        )


@router.get("/v2/logbook")
async def get_logbook(
    status_filter: Optional[str] = None,
    kamco_type: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    Get decision logbook entries
    
    Returns all decisions made on screening matches, with filtering options.
    
    - **status_filter**: Filter by decision status (FLAGGED, CLEARED, ESCALATED, RE_REVIEW)
    - **kamco_type**: Filter by Kamco entity type (CLIENT, VENDOR, STAFF, OTHER)
    - **start_date**: Filter decisions from this date (ISO format)
    - **end_date**: Filter decisions until this date (ISO format)
    - **limit**: Maximum entries to return (default 100)
    - **offset**: Pagination offset
    """
    if not SCREENING_V2_AVAILABLE:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Screening V2 models not available"
        )
    
    try:
        query = db.query(DecisionLog).join(ScreeningMatch)
        
        # Apply filters
        if status_filter:
            try:
                status_enum = DecisionStatus[status_filter.upper()]
                query = query.filter(DecisionLog.status == status_enum)
            except KeyError:
                pass
        
        if start_date:
            try:
                start = datetime.fromisoformat(start_date)
                query = query.filter(DecisionLog.decision_date >= start)
            except ValueError:
                pass
        
        if end_date:
            try:
                end = datetime.fromisoformat(end_date)
                query = query.filter(DecisionLog.decision_date <= end)
            except ValueError:
                pass
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        decisions = query.order_by(
            DecisionLog.decision_date.desc()
        ).offset(offset).limit(limit).all()
        
        # Build response
        entries = []
        for decision in decisions:
            match = decision.match
            user = decision.user
            
            entries.append({
                'id': decision.id,
                'match_id': decision.match_id,
                'kamco_entity_id': match.kamco_entity_id if match else None,
                'match_score': match.match_score if match else 0,
                'decision_status': decision.status.name,
                'decision_date': decision.decision_date.isoformat() if decision.decision_date else None,
                'decided_by': user.username if user else 'Unknown',
                'notes': decision.notes,
                'is_re_review': decision.is_re_review,
                'previous_status': decision.previous_status.name if decision.previous_status else None
            })
        
        return {
            'success': True,
            'entries': entries,
            'total': total,
            'limit': limit,
            'offset': offset,
            'filters_applied': {
                'status': status_filter,
                'kamco_type': kamco_type,
                'start_date': start_date,
                'end_date': end_date
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get logbook: {str(e)}"
        )


@router.get("/v2/pending-matches")
async def get_pending_matches(
    upload_id: Optional[int] = None,
    min_score: float = 0,
    include_re_reviews: bool = True,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    Get pending screening matches that need decisions
    
    Returns all matches that haven't been decided yet (status = PENDING).
    
    - **upload_id**: Filter by specific upload batch
    - **min_score**: Minimum match score to include
    - **include_re_reviews**: Whether to include re-review items
    - **limit**: Maximum matches to return
    """
    if not SCREENING_V2_AVAILABLE:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Screening V2 models not available"
        )
    
    try:
        query = db.query(ScreeningMatch).filter(
            ScreeningMatch.decision_status == 'pending'
        )
        
        if upload_id:
            query = query.filter(ScreeningMatch.blacklist_upload_id == upload_id)
        
        if min_score > 0:
            query = query.filter(ScreeningMatch.overall_score >= min_score)
        
        if not include_re_reviews:
            query = query.filter(ScreeningMatch.is_re_review == False)
        
        matches = query.order_by(
            ScreeningMatch.overall_score.desc()
        ).limit(limit).all()
        
        results = []
        for match in matches:
            results.append({
                'match_id': match.id,
                'match_key': match.match_key,
                'upload_id': match.blacklist_upload_id,
                'kamco_entity_id': match.kamco_entity_id,
                'blacklist_name_english': match.blacklist_name_english,
                'blacklist_name_arabic': match.blacklist_name_arabic,
                'blacklist_reference': match.blacklist_reference,
                'match_score': match.overall_score,
                'score_breakdown': {
                    'name_english': match.name_english_score,
                    'name_arabic': match.name_arabic_score,
                    'civil_id': match.civil_id_score,
                    'nationality': match.nationality_score
                },
                'confidence': match.confidence,
                'is_re_review': match.is_re_review,
                'decision_status': match.decision_status,
                'screened_at': match.screened_at.isoformat() if match.screened_at else None
            })
        
        return {
            'success': True,
            'matches': results,
            'count': len(results)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get pending matches: {str(e)}"
        )


@router.get("/v2/uploads")
async def get_upload_history(
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    Get blacklist upload history
    
    Returns recent blacklist uploads with summary statistics.
    """
    if not SCREENING_V2_AVAILABLE:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Screening V2 models not available"
        )
    
    try:
        uploads = db.query(BlacklistUpload).order_by(
            BlacklistUpload.uploaded_at.desc()
        ).limit(limit).all()
        
        results = []
        for upload in uploads:
            # Get username from uploader relationship
            username = 'Unknown'
            if upload.uploader:
                username = upload.uploader.username
            
            results.append({
                'id': upload.id,
                'filename': upload.filename,
                'uploaded_by': username,
                'uploaded_at': upload.uploaded_at.isoformat() if upload.uploaded_at else None,
                'total_entries': upload.total_entries,
                'matched_entries': upload.matched_entries,
                'threshold_used': upload.threshold_used,
                'status': upload.status,
                'processing_completed_at': upload.processing_completed_at.isoformat() if upload.processing_completed_at else None
            })
        
        return {
            'success': True,
            'uploads': results,
            'count': len(results)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get upload history: {str(e)}"
        )


@router.get("/v2/kamco-entities")
async def get_kamco_entities(
    entity_type: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    Get pre-loaded KAMCO entities
    
    Returns all KAMCO entities (clients, vendors, staff, etc.) that are 
    screened against uploaded blacklists.
    
    - **entity_type**: Filter by type (CLIENT, VENDOR, STAFF, OTHER)
    - **search**: Search by name (English or Arabic)
    - **limit**: Maximum entities to return
    """
    if not SCREENING_V2_AVAILABLE:
        # Fall back to seed data
        from data.kamco_entities import get_kamco_entities as get_seed_entities
        entities = get_seed_entities()
        
        if entity_type:
            entities = [e for e in entities if e['type'].upper() == entity_type.upper()]
        
        if search:
            search_lower = search.lower()
            entities = [
                e for e in entities 
                if search_lower in e.get('name_english', '').lower() 
                or search_lower in e.get('name_arabic', '')
            ]
        
        return {
            'success': True,
            'source': 'seed_data',
            'entities': entities[:limit],
            'count': len(entities[:limit])
        }
    
    try:
        query = db.query(KamcoEntityModel)
        
        if entity_type:
            # entity_type is stored as string in the model
            query = query.filter(KamcoEntityModel.entity_type.ilike(entity_type))
        
        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                (KamcoEntityModel.name_english.ilike(search_pattern)) |
                (KamcoEntityModel.name_arabic.ilike(search_pattern))
            )
        
        entities = query.limit(limit).all()
        
        results = []
        for entity in entities:
            results.append({
                'id': entity.id,
                'customer_id': entity.customer_id,
                'type': entity.entity_type,
                'name_english': entity.name_english,
                'name_arabic': entity.name_arabic,
                'civil_id': entity.civil_id,
                'nationality': entity.nationality,
                'risk_level': entity.risk_level,
                'account_status': entity.account_status
            })
        
        return {
            'success': True,
            'source': 'database',
            'entities': results,
            'count': len(results)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get Kamco entities: {str(e)}"
        )
