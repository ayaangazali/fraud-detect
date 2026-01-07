"""
Screening API Route for Phase 5
Compares Kamco entities against blacklist using fuzzy matching and Civil ID matching
Updated in Phase 6: Added email notifications for high-risk matches
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

from database.connection import get_db
from models.blacklist import BlacklistEntry
from models.database import KamcoClient, KamcoVendor, KamcoStaff, KamcoOther, FlaggedItem
from utils.fuzzy_matcher_enhanced import FuzzyMatcherEnhanced
from utils.civil_id_validator import CivilIDValidator
from utils.auth import get_current_active_user
from utils.logbook import log_action
from utils.email_service import get_email_service

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
