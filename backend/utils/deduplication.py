"""
Deduplication System for Phase 5 - Task 23
Prevents duplicate blacklist entries and provides merge suggestions
"""
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session

from models.blacklist import BlacklistEntry
from utils.fuzzy_matcher_enhanced import FuzzyMatcherEnhanced
from utils.civil_id_validator import CivilIDValidator


class DeduplicationSystem:
    """
    System to detect and prevent duplicate blacklist entries
    """
    
    # Deduplication thresholds
    EXACT_NAME_MATCH_THRESHOLD = 95
    SIMILAR_NAME_THRESHOLD = 85
    
    def __init__(self, db: Session):
        """
        Initialize deduplication system
        
        Args:
            db: Database session
        """
        self.db = db
        self.fuzzy_matcher = FuzzyMatcherEnhanced()
        self.civil_id_validator = CivilIDValidator()
    
    def check_civil_id_duplicate(self, civil_id: str) -> Optional[BlacklistEntry]:
        """
        Check if Civil ID already exists in blacklist
        
        Args:
            civil_id: Civil ID to check
            
        Returns:
            Existing BlacklistEntry or None
        """
        if not civil_id:
            return None
        
        # Normalize Civil ID
        normalized = self.civil_id_validator.normalize_civil_id(civil_id)
        if not normalized:
            return None
        
        # Query database for exact match
        existing = self.db.query(BlacklistEntry).filter(
            BlacklistEntry.civil_id == normalized,
            BlacklistEntry.status == "Active"
        ).first()
        
        return existing
    
    def check_name_duplicate(
        self, 
        name_arabic: str,
        name_english: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Check for exact or near-exact name matches
        
        Args:
            name_arabic: Arabic name to check
            name_english: English name to check (optional)
            
        Returns:
            List of potential duplicates with match scores
        """
        duplicates = []
        
        # Get all active entries
        existing_entries = self.db.query(BlacklistEntry).filter(
            BlacklistEntry.status == "Active"
        ).all()
        
        for entry in existing_entries:
            # Check Arabic name
            if name_arabic and entry.name_arabic:
                arabic_match = self.fuzzy_matcher.match_names(
                    name_arabic,
                    entry.name_arabic
                )
                
                if arabic_match['match_score'] >= self.SIMILAR_NAME_THRESHOLD:
                    duplicates.append({
                        'entry': entry,
                        'match_type': 'arabic_name',
                        'match_score': arabic_match['match_score'],
                        'risk_level': arabic_match['risk_level'],
                        'confidence': arabic_match['confidence']
                    })
                    continue  # Don't double-count
            
            # Check English name if provided
            if name_english and entry.name_english:
                english_match = self.fuzzy_matcher.match_names(
                    name_english,
                    entry.name_english
                )
                
                if english_match['match_score'] >= self.SIMILAR_NAME_THRESHOLD:
                    duplicates.append({
                        'entry': entry,
                        'match_type': 'english_name',
                        'match_score': english_match['match_score'],
                        'risk_level': english_match['risk_level'],
                        'confidence': english_match['confidence']
                    })
        
        # Sort by match score (descending)
        duplicates.sort(key=lambda x: x['match_score'], reverse=True)
        
        return duplicates
    
    def check_decree_duplicate(
        self,
        decree_number: Optional[str],
        source: str
    ) -> List[BlacklistEntry]:
        """
        Check for entries with same decree number and source
        
        Args:
            decree_number: Decree number to check
            source: Source to check
            
        Returns:
            List of matching entries
        """
        if not decree_number or not source:
            return []
        
        # Query for exact matches
        existing = self.db.query(BlacklistEntry).filter(
            BlacklistEntry.decree_number == decree_number,
            BlacklistEntry.source == source,
            BlacklistEntry.status == "Active"
        ).all()
        
        return existing
    
    def check_for_duplicates(
        self,
        name_arabic: str,
        civil_id: Optional[str] = None,
        name_english: Optional[str] = None,
        decree_number: Optional[str] = None,
        source: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Comprehensive duplicate check
        
        Args:
            name_arabic: Arabic name
            civil_id: Civil ID (optional)
            name_english: English name (optional)
            decree_number: Decree number (optional)
            source: Source (optional)
            
        Returns:
            Dictionary with duplicate check results
        """
        results = {
            'has_duplicates': False,
            'duplicate_types': [],
            'civil_id_duplicate': None,
            'name_duplicates': [],
            'decree_duplicates': [],
            'recommendation': 'PROCEED',  # PROCEED, WARN, REJECT, MERGE
            'message': None
        }
        
        # Check 1: Civil ID duplicate (highest priority)
        if civil_id:
            civil_id_dup = self.check_civil_id_duplicate(civil_id)
            if civil_id_dup:
                results['has_duplicates'] = True
                results['duplicate_types'].append('civil_id')
                results['civil_id_duplicate'] = {
                    'id': civil_id_dup.id,
                    'name_arabic': civil_id_dup.name_arabic,
                    'civil_id': civil_id_dup.civil_id,
                    'source': civil_id_dup.source
                }
                results['recommendation'] = 'REJECT'
                results['message'] = f'Civil ID {civil_id} already exists in blacklist (Entry ID: {civil_id_dup.id})'
                return results  # Early return for Civil ID duplicate
        
        # Check 2: Name duplicates
        name_dups = self.check_name_duplicate(name_arabic, name_english)
        if name_dups:
            results['has_duplicates'] = True
            results['duplicate_types'].append('name')
            results['name_duplicates'] = [
                {
                    'id': dup['entry'].id,
                    'name_arabic': dup['entry'].name_arabic,
                    'name_english': dup['entry'].name_english,
                    'civil_id': dup['entry'].civil_id,
                    'match_score': dup['match_score'],
                    'match_type': dup['match_type'],
                    'confidence': dup['confidence']
                }
                for dup in name_dups[:5]  # Top 5
            ]
            
            # Check if any are exact matches (>= 95%)
            exact_matches = [d for d in name_dups if d['match_score'] >= self.EXACT_NAME_MATCH_THRESHOLD]
            if exact_matches:
                results['recommendation'] = 'WARN'
                results['message'] = f'Found {len(exact_matches)} near-exact name match(es). Consider merging or reviewing.'
            else:
                results['recommendation'] = 'WARN'
                results['message'] = f'Found {len(name_dups)} similar name(s). Review before adding.'
        
        # Check 3: Decree duplicates
        if decree_number and source:
            decree_dups = self.check_decree_duplicate(decree_number, source)
            if decree_dups:
                results['has_duplicates'] = True
                results['duplicate_types'].append('decree')
                results['decree_duplicates'] = [
                    {
                        'id': dup.id,
                        'name_arabic': dup.name_arabic,
                        'decree_number': dup.decree_number,
                        'source': dup.source
                    }
                    for dup in decree_dups
                ]
                
                if results['recommendation'] != 'REJECT':
                    results['recommendation'] = 'WARN'
                    results['message'] = f'Found {len(decree_dups)} entry(ies) with same decree number and source.'
        
        # If no issues found
        if not results['has_duplicates']:
            results['recommendation'] = 'PROCEED'
            results['message'] = 'No duplicates found. Safe to add.'
        
        return results
    
    def batch_check_duplicates(
        self,
        entries: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Check multiple entries for duplicates
        
        Args:
            entries: List of entry dictionaries to check
            
        Returns:
            List of results for each entry
        """
        results = []
        
        for idx, entry in enumerate(entries):
            check_result = self.check_for_duplicates(
                name_arabic=entry.get('name_arabic'),
                civil_id=entry.get('civil_id'),
                name_english=entry.get('name_english'),
                decree_number=entry.get('decree_number'),
                source=entry.get('source')
            )
            
            results.append({
                'index': idx,
                'entry': entry,
                **check_result
            })
        
        return results
    
    def find_internal_duplicates(
        self,
        entries: List[Dict[str, Any]]
    ) -> Dict[str, List[Tuple[int, int]]]:
        """
        Find duplicates within a batch of entries (before DB insertion)
        
        Args:
            entries: List of entry dictionaries
            
        Returns:
            Dictionary mapping duplicate type to list of (index1, index2) tuples
        """
        duplicates = {
            'civil_id': [],
            'name': []
        }
        
        # Check Civil ID duplicates
        civil_ids = {}
        for idx, entry in enumerate(entries):
            civil_id = entry.get('civil_id')
            if civil_id:
                normalized = self.civil_id_validator.normalize_civil_id(civil_id)
                if normalized:
                    if normalized in civil_ids:
                        duplicates['civil_id'].append((civil_ids[normalized], idx))
                    else:
                        civil_ids[normalized] = idx
        
        # Check name duplicates (quadratic complexity, but OK for reasonable batch sizes)
        for i in range(len(entries)):
            for j in range(i + 1, len(entries)):
                name1 = entries[i].get('name_arabic', '')
                name2 = entries[j].get('name_arabic', '')
                
                if name1 and name2:
                    match = self.fuzzy_matcher.match_names(name1, name2)
                    if match['match_score'] >= self.EXACT_NAME_MATCH_THRESHOLD:
                        duplicates['name'].append((i, j))
        
        return duplicates
    
    def suggest_merge(
        self,
        entry1: Dict[str, Any],
        entry2: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Suggest how to merge two similar entries
        
        Args:
            entry1: First entry
            entry2: Second entry
            
        Returns:
            Merged entry with all non-null fields
        """
        merged = {}
        
        # Merge all fields, preferring non-null values
        for key in set(list(entry1.keys()) + list(entry2.keys())):
            val1 = entry1.get(key)
            val2 = entry2.get(key)
            
            if val1 and val2:
                # Both have values - prefer longer/more complete one
                if len(str(val1)) >= len(str(val2)):
                    merged[key] = val1
                else:
                    merged[key] = val2
            elif val1:
                merged[key] = val1
            elif val2:
                merged[key] = val2
        
        return merged


# Convenience functions

def check_duplicate_before_insert(
    db: Session,
    name_arabic: str,
    civil_id: Optional[str] = None,
    name_english: Optional[str] = None
) -> Dict[str, Any]:
    """
    Quick duplicate check before inserting
    
    Args:
        db: Database session
        name_arabic: Arabic name
        civil_id: Civil ID (optional)
        name_english: English name (optional)
        
    Returns:
        Duplicate check results
    """
    dedup = DeduplicationSystem(db)
    return dedup.check_for_duplicates(
        name_arabic=name_arabic,
        civil_id=civil_id,
        name_english=name_english
    )
