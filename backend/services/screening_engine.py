"""
Blacklist Screening Engine
Compares uploaded blacklist against KAMCO entities database
Uses weighted fuzzy matching to find potential matches
"""
import csv
import io
from datetime import datetime, timezone
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import re
from difflib import SequenceMatcher
from sqlalchemy.orm import Session

# Try to import rapidfuzz for better performance, fall back to difflib
try:
    from rapidfuzz import fuzz
    USE_RAPIDFUZZ = True
except ImportError:
    USE_RAPIDFUZZ = False


class MatchConfidence(str, Enum):
    EXACT = "exact"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    POTENTIAL = "potential"


class DecisionStatus(str, Enum):
    PENDING = "pending"
    FLAGGED = "flagged"
    CLEARED = "cleared"
    ESCALATED = "escalated"


@dataclass
class BlacklistEntry:
    """Represents a single entry from uploaded blacklist"""
    reference_number: str = ""
    full_name_english: str = ""
    full_name_arabic: str = ""
    alias_names: str = ""
    date_of_birth: str = ""
    place_of_birth: str = ""
    nationality: str = ""
    secondary_nationality: str = ""
    civil_id: str = ""
    passport_number: str = ""
    national_id: str = ""
    gender: str = ""
    list_type: str = ""
    list_source: str = ""
    listing_date: str = ""
    expiry_date: str = ""
    reason_for_listing: str = ""
    crime_category: str = ""
    risk_level: str = ""
    sanctions_program: str = ""
    un_reference: str = ""
    country_of_residence: str = ""
    city: str = ""
    address: str = ""
    phone_number: str = ""
    email: str = ""
    occupation: str = ""
    employer: str = ""
    position: str = ""
    pep_status: str = ""
    pep_position: str = ""
    pep_country: str = ""
    associated_entities: str = ""
    associated_individuals: str = ""
    bank_accounts: str = ""
    additional_info: str = ""
    source_url: str = ""
    last_updated: str = ""
    status: str = ""
    notes: str = ""
    
    # Raw data for any extra fields
    raw_data: Dict = field(default_factory=dict)


@dataclass
class KamcoEntity:
    """Represents a KAMCO entity (client, vendor, staff, etc.)"""
    entity_id: int = 0
    customer_id: str = ""
    entity_type: str = ""
    entity_category: str = ""
    name_english: str = ""
    name_arabic: str = ""
    civil_id: str = ""
    passport_number: str = ""
    date_of_birth: str = ""
    nationality: str = ""
    secondary_nationality: str = ""
    country_of_residence: str = ""
    city: str = ""
    address: str = ""
    phone: str = ""
    email: str = ""
    occupation: str = ""
    employer: str = ""
    position: str = ""
    account_status: str = ""
    risk_level: str = ""
    onboarding_date: str = ""
    last_review_date: str = ""
    notes: str = ""
    
    # Additional fields
    extra_data: Dict = field(default_factory=dict)


@dataclass
class MatchResult:
    """Result of comparing a blacklist entry against a KAMCO entity"""
    match_id: str = ""
    blacklist_entry: BlacklistEntry = None
    kamco_entity: KamcoEntity = None
    
    # Match scores
    overall_score: float = 0.0
    name_english_score: float = 0.0
    name_arabic_score: float = 0.0
    civil_id_score: float = 0.0
    passport_score: float = 0.0
    dob_score: float = 0.0
    nationality_score: float = 0.0
    
    # Match details
    confidence: MatchConfidence = MatchConfidence.POTENTIAL
    match_reasons: List[str] = field(default_factory=list)
    
    # Decision tracking
    decision_status: DecisionStatus = DecisionStatus.PENDING
    previous_decision: Optional[str] = None
    previous_decision_date: Optional[str] = None
    previous_decision_by: Optional[str] = None
    previous_notes: Optional[str] = None
    is_re_review: bool = False
    
    # Metadata
    screened_at: str = ""
    screened_by: int = 0


class ScreeningEngine:
    """
    Main screening engine that compares blacklist entries against KAMCO database
    """
    
    # Default weights for matching fields
    DEFAULT_WEIGHTS = {
        "name_english": 30,
        "name_arabic": 25,
        "civil_id": 20,
        "passport_number": 10,
        "date_of_birth": 10,
        "nationality": 5,
    }
    
    def __init__(self, weights: Dict[str, float] = None, threshold: float = 70.0):
        """
        Initialize screening engine
        
        Args:
            weights: Custom weights for matching fields (must sum to 100)
            threshold: Minimum score to consider a match (0-100)
        """
        self.weights = weights or self.DEFAULT_WEIGHTS
        self.threshold = threshold
        
        # Validate weights sum to 100
        weight_sum = sum(self.weights.values())
        if abs(weight_sum - 100) > 0.01:
            # Normalize weights
            for key in self.weights:
                self.weights[key] = (self.weights[key] / weight_sum) * 100
    
    def parse_blacklist_csv(self, csv_content: str) -> List[BlacklistEntry]:
        """
        Parse uploaded blacklist CSV into BlacklistEntry objects
        Handles flexible column names and missing fields
        """
        entries = []
        
        # Try to parse CSV
        try:
            # Handle both string and bytes
            if isinstance(csv_content, bytes):
                csv_content = csv_content.decode('utf-8-sig')  # Handle BOM
            
            reader = csv.DictReader(io.StringIO(csv_content))
            
            for row in reader:
                entry = BlacklistEntry()
                entry.raw_data = dict(row)
                
                # Map columns flexibly (handle different naming conventions)
                column_mapping = {
                    'reference_number': ['Reference_Number', 'Ref_No', 'ID', 'Reference'],
                    'full_name_english': ['Full_Name_English', 'Name_English', 'Name', 'Full_Name', 'English_Name'],
                    'full_name_arabic': ['Full_Name_Arabic', 'Name_Arabic', 'Arabic_Name', 'الاسم'],
                    'alias_names': ['Alias_Names', 'Aliases', 'AKA', 'Also_Known_As'],
                    'date_of_birth': ['Date_of_Birth', 'DOB', 'Birth_Date', 'Birthday'],
                    'place_of_birth': ['Place_of_Birth', 'POB', 'Birth_Place'],
                    'nationality': ['Nationality', 'Citizenship', 'Country'],
                    'secondary_nationality': ['Secondary_Nationality', 'Other_Nationality', 'Dual_Citizenship'],
                    'civil_id': ['Civil_ID', 'CivilID', 'Civil_Number', 'ID_Number'],
                    'passport_number': ['Passport_Number', 'Passport', 'Passport_No'],
                    'national_id': ['National_ID', 'NationalID', 'SSN'],
                    'gender': ['Gender', 'Sex'],
                    'list_type': ['List_Type', 'ListType', 'Type'],
                    'list_source': ['List_Source', 'Source', 'Authority'],
                    'listing_date': ['Listing_Date', 'Date_Listed', 'Added_Date'],
                    'expiry_date': ['Expiry_Date', 'Expires', 'Valid_Until'],
                    'reason_for_listing': ['Reason_for_Listing', 'Reason', 'Listing_Reason'],
                    'crime_category': ['Crime_Category', 'Category', 'Offense_Type'],
                    'risk_level': ['Risk_Level', 'Risk', 'Severity'],
                    'sanctions_program': ['Sanctions_Program', 'Program', 'Regime'],
                    'un_reference': ['UN_Reference', 'UN_Ref', 'UN_Number'],
                    'country_of_residence': ['Country_of_Residence', 'Residence', 'Current_Country'],
                    'city': ['City', 'Town'],
                    'address': ['Address', 'Street_Address', 'Location'],
                    'phone_number': ['Phone_Number', 'Phone', 'Tel', 'Mobile'],
                    'email': ['Email', 'Email_Address', 'E-mail'],
                    'occupation': ['Occupation', 'Job', 'Profession'],
                    'employer': ['Employer', 'Company', 'Organization'],
                    'position': ['Position', 'Title', 'Role'],
                    'pep_status': ['PEP_Status', 'PEP', 'Politically_Exposed'],
                    'pep_position': ['PEP_Position', 'Political_Position'],
                    'pep_country': ['PEP_Country', 'Political_Country'],
                    'associated_entities': ['Associated_Entities', 'Related_Companies', 'Affiliates'],
                    'associated_individuals': ['Associated_Individuals', 'Related_Persons', 'Associates'],
                    'bank_accounts': ['Bank_Accounts', 'Accounts', 'Financial_Accounts'],
                    'additional_info': ['Additional_Info', 'Notes', 'Comments', 'Remarks'],
                    'source_url': ['Source_URL', 'URL', 'Link', 'Reference_URL'],
                    'last_updated': ['Last_Updated', 'Updated', 'Modified_Date'],
                    'status': ['Status', 'State', 'Active'],
                    'notes': ['Notes', 'Comments', 'Remarks'],
                }
                
                # Map row values to entry fields
                for field_name, possible_columns in column_mapping.items():
                    for col in possible_columns:
                        if col in row and row[col]:
                            setattr(entry, field_name, str(row[col]).strip())
                            break
                
                entries.append(entry)
                
        except Exception as e:
            print(f"Error parsing CSV: {e}")
            raise ValueError(f"Failed to parse blacklist CSV: {str(e)}")
        
        return entries
    
    def _fuzzy_match(self, str1: str, str2: str) -> float:
        """
        Calculate fuzzy match score between two strings
        Returns score from 0-100
        """
        if not str1 or not str2:
            return 0.0
        
        # Normalize strings
        str1 = str1.lower().strip()
        str2 = str2.lower().strip()
        
        if str1 == str2:
            return 100.0
        
        if USE_RAPIDFUZZ:
            # Use rapidfuzz for better performance
            return fuzz.ratio(str1, str2)
        else:
            # Fall back to SequenceMatcher
            return SequenceMatcher(None, str1, str2).ratio() * 100
    
    def _fuzzy_match_name(self, name1: str, name2: str) -> float:
        """
        Specialized name matching that handles:
        - Name order variations (First Last vs Last First)
        - Missing middle names
        - Common prefixes (Al-, El-, Ibn, etc.)
        """
        if not name1 or not name2:
            return 0.0
        
        # Normalize
        name1 = name1.lower().strip()
        name2 = name2.lower().strip()
        
        if name1 == name2:
            return 100.0
        
        # Remove common prefixes for comparison
        prefixes = ['al-', 'el-', 'ibn ', 'bin ', 'bint ', 'abu ', 'um ', 'al ', 'el ']
        name1_clean = name1
        name2_clean = name2
        for prefix in prefixes:
            name1_clean = name1_clean.replace(prefix, '')
            name2_clean = name2_clean.replace(prefix, '')
        
        # Direct match score
        direct_score = self._fuzzy_match(name1, name2)
        
        # Try matching with reordered names
        parts1 = name1_clean.split()
        parts2 = name2_clean.split()
        
        # Check if all parts of shorter name exist in longer name
        shorter, longer = (parts1, parts2) if len(parts1) <= len(parts2) else (parts2, parts1)
        matches = sum(1 for part in shorter if any(self._fuzzy_match(part, p) > 80 for p in longer))
        partial_score = (matches / len(shorter)) * 100 if shorter else 0
        
        # Return best score
        return max(direct_score, partial_score)
    
    def _exact_match(self, str1: str, str2: str) -> float:
        """
        Check for exact match (case-insensitive)
        Returns 100 if exact match, 0 otherwise
        """
        if not str1 or not str2:
            return 0.0
        
        return 100.0 if str1.lower().strip() == str2.lower().strip() else 0.0
    
    def calculate_match_score(
        self,
        blacklist_entry: BlacklistEntry,
        kamco_entity: KamcoEntity
    ) -> MatchResult:
        """
        Calculate weighted match score between blacklist entry and KAMCO entity
        """
        result = MatchResult()
        result.blacklist_entry = blacklist_entry
        result.kamco_entity = kamco_entity
        result.match_id = f"MATCH-{blacklist_entry.reference_number}-{kamco_entity.customer_id}"
        result.screened_at = datetime.now(timezone.utc).isoformat()
        
        # Calculate individual field scores
        
        # Name English (fuzzy matching with name handling)
        result.name_english_score = self._fuzzy_match_name(
            blacklist_entry.full_name_english,
            kamco_entity.name_english
        )
        
        # Name Arabic (fuzzy matching)
        result.name_arabic_score = self._fuzzy_match(
            blacklist_entry.full_name_arabic,
            kamco_entity.name_arabic
        )
        
        # Civil ID (exact match for IDs)
        if blacklist_entry.civil_id and kamco_entity.civil_id:
            # Normalize IDs (remove spaces, dashes)
            bl_civil = re.sub(r'[\s-]', '', blacklist_entry.civil_id)
            ke_civil = re.sub(r'[\s-]', '', kamco_entity.civil_id)
            result.civil_id_score = 100.0 if bl_civil == ke_civil else 0.0
        else:
            result.civil_id_score = 0.0
        
        # Passport (exact match)
        if blacklist_entry.passport_number and kamco_entity.passport_number:
            bl_passport = re.sub(r'[\s-]', '', blacklist_entry.passport_number.upper())
            ke_passport = re.sub(r'[\s-]', '', kamco_entity.passport_number.upper())
            result.passport_score = 100.0 if bl_passport == ke_passport else 0.0
        else:
            result.passport_score = 0.0
        
        # Date of Birth (exact match)
        result.dob_score = self._exact_match(
            blacklist_entry.date_of_birth,
            kamco_entity.date_of_birth
        )
        
        # Nationality (fuzzy match)
        result.nationality_score = self._fuzzy_match(
            blacklist_entry.nationality,
            kamco_entity.nationality
        )
        
        # Calculate weighted overall score
        result.overall_score = (
            (result.name_english_score * self.weights.get('name_english', 30) / 100) +
            (result.name_arabic_score * self.weights.get('name_arabic', 25) / 100) +
            (result.civil_id_score * self.weights.get('civil_id', 20) / 100) +
            (result.passport_score * self.weights.get('passport_number', 10) / 100) +
            (result.dob_score * self.weights.get('date_of_birth', 10) / 100) +
            (result.nationality_score * self.weights.get('nationality', 5) / 100)
        )
        
        # Determine confidence level
        result.confidence = self._determine_confidence(result)
        
        # Build match reasons
        result.match_reasons = self._build_match_reasons(result)
        
        return result
    
    def _determine_confidence(self, result: MatchResult) -> MatchConfidence:
        """Determine match confidence based on scores"""
        
        # EXACT: Name + ID match exactly
        if result.name_english_score >= 95 and (result.civil_id_score == 100 or result.passport_score == 100):
            return MatchConfidence.EXACT
        
        # HIGH: Name very similar + some ID match
        if result.name_english_score >= 90 and (result.civil_id_score == 100 or result.passport_score == 100):
            return MatchConfidence.HIGH
        
        # HIGH: Overall score very high
        if result.overall_score >= 85:
            return MatchConfidence.HIGH
        
        # MEDIUM: Good name match or overall score
        if result.overall_score >= 70 or result.name_english_score >= 85:
            return MatchConfidence.MEDIUM
        
        # LOW: Some matches
        if result.overall_score >= 50 or result.name_english_score >= 70:
            return MatchConfidence.LOW
        
        # POTENTIAL: Weak matches
        return MatchConfidence.POTENTIAL
    
    def _build_match_reasons(self, result: MatchResult) -> List[str]:
        """Build list of reasons why this is a match"""
        reasons = []
        
        if result.name_english_score >= 95:
            reasons.append(f"Exact name match (English): {result.name_english_score:.0f}%")
        elif result.name_english_score >= 80:
            reasons.append(f"Similar name (English): {result.name_english_score:.0f}%")
        elif result.name_english_score >= 60:
            reasons.append(f"Partial name match (English): {result.name_english_score:.0f}%")
        
        if result.name_arabic_score >= 95:
            reasons.append(f"Exact name match (Arabic): {result.name_arabic_score:.0f}%")
        elif result.name_arabic_score >= 80:
            reasons.append(f"Similar name (Arabic): {result.name_arabic_score:.0f}%")
        
        if result.civil_id_score == 100:
            reasons.append("Civil ID matches exactly")
        
        if result.passport_score == 100:
            reasons.append("Passport number matches exactly")
        
        if result.dob_score == 100:
            reasons.append("Date of birth matches")
        
        if result.nationality_score >= 80:
            reasons.append(f"Same nationality: {result.nationality_score:.0f}%")
        
        return reasons
    
    def screen_blacklist(
        self,
        blacklist_entries: List[BlacklistEntry],
        kamco_entities: List[KamcoEntity],
        previous_decisions: Dict[str, dict] = None
    ) -> List[MatchResult]:
        """
        Screen all blacklist entries against KAMCO entities
        
        Args:
            blacklist_entries: List of parsed blacklist entries
            kamco_entities: List of KAMCO entities from database
            previous_decisions: Dict of previous decisions by match key
            
        Returns:
            List of matches above threshold, sorted by score
        """
        matches = []
        previous_decisions = previous_decisions or {}
        
        for bl_entry in blacklist_entries:
            for ke in kamco_entities:
                result = self.calculate_match_score(bl_entry, ke)
                
                # Only include matches above threshold
                if result.overall_score >= self.threshold:
                    # Check for previous decision
                    match_key = self._get_match_key(bl_entry, ke)
                    if match_key in previous_decisions:
                        prev = previous_decisions[match_key]
                        result.previous_decision = prev.get('decision')
                        result.previous_decision_date = prev.get('date')
                        result.previous_decision_by = prev.get('user')
                        result.previous_notes = prev.get('notes')
                        result.is_re_review = True
                    
                    matches.append(result)
        
        # Sort by overall score descending
        matches.sort(key=lambda x: x.overall_score, reverse=True)
        
        return matches
    
    def _get_match_key(self, bl_entry: BlacklistEntry, ke: KamcoEntity) -> str:
        """Generate unique key for a blacklist-entity pair"""
        # Use combination of blacklist reference and entity customer ID
        bl_id = bl_entry.reference_number or bl_entry.full_name_english
        return f"{bl_id}::{ke.customer_id}"


def convert_db_entity_to_kamco(db_entity) -> KamcoEntity:
    """Convert database entity to KamcoEntity dataclass"""
    ke = KamcoEntity()
    ke.entity_id = getattr(db_entity, 'id', 0)
    ke.customer_id = getattr(db_entity, 'customer_id', '')
    ke.entity_type = getattr(db_entity, 'entity_type', '')
    ke.entity_category = getattr(db_entity, 'entity_category', '')
    ke.name_english = getattr(db_entity, 'name_english', '')
    ke.name_arabic = getattr(db_entity, 'name_arabic', '')
    ke.civil_id = getattr(db_entity, 'civil_id', '')
    ke.passport_number = getattr(db_entity, 'passport_number', '')
    ke.date_of_birth = str(getattr(db_entity, 'date_of_birth', ''))
    ke.nationality = getattr(db_entity, 'nationality', '')
    ke.secondary_nationality = getattr(db_entity, 'secondary_nationality', '')
    ke.country_of_residence = getattr(db_entity, 'country_of_residence', '')
    ke.city = getattr(db_entity, 'city', '')
    ke.address = getattr(db_entity, 'address', '')
    ke.phone = getattr(db_entity, 'phone', '')
    ke.email = getattr(db_entity, 'email', '')
    ke.occupation = getattr(db_entity, 'occupation', '')
    ke.employer = getattr(db_entity, 'employer', '')
    ke.position = getattr(db_entity, 'position', '')
    ke.account_status = getattr(db_entity, 'account_status', '')
    ke.risk_level = getattr(db_entity, 'risk_level', '')
    return ke


# Alias for backward compatibility with routes
class BlacklistScreeningEngine(ScreeningEngine):
    """
    Wrapper class for the screening route integration
    Provides simplified interface for blacklist upload workflow
    """
    
    def __init__(self, threshold: float = 70.0):
        """Initialize with new workflow weights"""
        # Updated weights for new blacklist screening workflow
        weights = {
            "name_english": 40,  # Primary matching field
            "name_arabic": 35,   # Important for Arabic names
            "civil_id": 15,      # ID matching
            "passport_number": 0,
            "date_of_birth": 0,
            "nationality": 10,   # Supporting field
        }
        super().__init__(weights=weights, threshold=threshold)
    
    def process_blacklist_csv(self, csv_content: str) -> List[Dict]:
        """
        Process CSV and return list of dicts for route integration
        """
        entries = self.parse_blacklist_csv(csv_content)
        
        # Convert to dict format expected by routes
        return [
            {
                'reference_number': e.reference_number,
                'full_name_english': e.full_name_english,
                'full_name_arabic': e.full_name_arabic,
                'civil_id': e.civil_id,
                'nationality': e.nationality,
                'risk_level': e.risk_level,
                'source': e.list_source,
                'raw_data': e.raw_data
            }
            for e in entries
        ]
    
    def screen_against_kamco(
        self,
        blacklist_entries: List[Dict],
        kamco_entities: List[Dict],
        threshold: float,
        existing_decisions: set = None
    ) -> List[Dict]:
        """
        Screen blacklist entries against KAMCO entities
        Returns list of dicts with match details
        
        Args:
            blacklist_entries: List of blacklist entry dicts from CSV
            kamco_entities: List of KAMCO entity dicts from database
            threshold: Minimum score to consider a match (0-100)
            existing_decisions: Set of already-decided match keys to skip
        """
        self.threshold = threshold
        existing_decisions = existing_decisions or set()
        
        matches = []
        
        for bl_entry in blacklist_entries:
            for ke in kamco_entities:
                # Calculate match score
                score_breakdown = {}
                
                # Name English score
                name_en_score = self._fuzzy_match_name(
                    bl_entry.get('full_name_english', ''),
                    ke.get('name_english', '')
                )
                score_breakdown['name_english'] = name_en_score
                
                # Name Arabic score
                name_ar_score = self._fuzzy_match(
                    bl_entry.get('full_name_arabic', ''),
                    ke.get('name_arabic', '')
                )
                score_breakdown['name_arabic'] = name_ar_score
                
                # ID Number score
                id_score = 0.0
                bl_id = bl_entry.get('civil_id', '')
                ke_id = ke.get('civil_id', '')
                if bl_id and ke_id:
                    bl_id_clean = str(bl_id).replace(' ', '').replace('-', '')
                    ke_id_clean = str(ke_id).replace(' ', '').replace('-', '')
                    id_score = 100.0 if bl_id_clean == ke_id_clean else 0.0
                score_breakdown['id_number'] = id_score
                
                # Nationality score
                nat_score = self._fuzzy_match(
                    bl_entry.get('nationality', ''),
                    ke.get('nationality', '')
                )
                score_breakdown['nationality'] = nat_score
                
                # Calculate overall weighted score
                overall_score = (
                    name_en_score * 0.40 +
                    name_ar_score * 0.35 +
                    id_score * 0.15 +
                    nat_score * 0.10
                )
                
                # Check if above threshold
                if overall_score >= threshold:
                    match_key = f"{ke.get('id')}_{bl_entry.get('reference_number', bl_entry.get('full_name_english', ''))}"
                    
                    # Check if already decided
                    if match_key in existing_decisions:
                        continue  # Skip already decided matches
                    
                    # Determine risk level based on score
                    if overall_score >= 95:
                        risk_level = "CRITICAL"
                    elif overall_score >= 85:
                        risk_level = "HIGH"
                    elif overall_score >= 75:
                        risk_level = "MEDIUM"
                    else:
                        risk_level = "LOW"
                    
                    # Check if this is a re-review (same entity appeared before)
                    is_re_review = False
                    re_review_reason = None
                    # Logic for re-review would check against historical matches
                    
                    matches.append({
                        'kamco_entity': ke,
                        'blacklist_entry': bl_entry,
                        'overall_score': round(overall_score, 2),
                        'score_breakdown': score_breakdown,
                        'risk_level': risk_level,
                        'is_re_review': is_re_review,
                        're_review_reason': re_review_reason,
                        'match_key': match_key
                    })
        
        # Sort by score descending
        matches.sort(key=lambda x: x['overall_score'], reverse=True)
        
        return matches
