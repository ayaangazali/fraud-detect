"""
Civil ID Validator and Matcher for Phase 5 - Task 22
Handles Civil ID normalization and exact matching
Note: Civil IDs are random unique numbers with no specific format validation
"""
import re
from typing import Optional, Dict, Any, List, Tuple


class CivilIDValidator:
    """
    Civil ID validator and matcher
    
    Civil IDs are unique identifiers with no specific format requirements.
    This class provides normalization and exact matching functionality.
    """
    
    @staticmethod
    def normalize_civil_id(civil_id: str) -> Optional[str]:
        """
        Normalize Civil ID by removing non-alphanumeric characters and trimming whitespace
        
        Args:
            civil_id: Raw Civil ID string
            
        Returns:
            Normalized string or None if empty
        """
        if not civil_id:
            return None
        
        # Convert to string and strip whitespace
        normalized = str(civil_id).strip()
        
        # Remove common separators (spaces, dashes, dots) but keep alphanumeric
        normalized = re.sub(r'[\s\-\.\,\_]+', '', normalized)
        
        # Return None if empty after normalization
        if not normalized:
            return None
        
        return normalized
    
    @staticmethod
    def validate_civil_id(civil_id: str) -> Dict[str, Any]:
        """
        Validate Civil ID (basic check - not empty)
        
        Args:
            civil_id: Civil ID to validate
            
        Returns:
            Dictionary with validation results:
            {
                'valid': bool,
                'normalized': str or None,
                'error': str or None
            }
        """
        if not civil_id:
            return {
                'valid': False,
                'normalized': None,
                'error': 'Civil ID is empty'
            }
        
        # Normalize
        normalized = CivilIDValidator.normalize_civil_id(civil_id)
        
        if not normalized:
            return {
                'valid': False,
                'normalized': None,
                'error': 'Civil ID is empty after normalization'
            }
        
        # Any non-empty Civil ID is valid
        return {
            'valid': True,
            'normalized': normalized,
            'error': None
        }
    
    @staticmethod
    def extract_info(civil_id: str) -> Optional[Dict[str, Any]]:
        """
        Extract basic information from Civil ID
        
        Args:
            civil_id: Valid Civil ID
            
        Returns:
            Dictionary with basic info or None if invalid
        """
        validation = CivilIDValidator.validate_civil_id(civil_id)
        
        if not validation['valid']:
            return None
        
        normalized = validation['normalized']
        
        return {
            'civil_id': normalized,
            'length': len(normalized),
            'is_numeric': normalized.isdigit(),
            'is_alphanumeric': normalized.isalnum()
        }
    
    @staticmethod
    def match_civil_ids(civil_id1: str, civil_id2: str) -> Dict[str, Any]:
        """
        Exact match two Civil IDs
        
        Args:
            civil_id1: First Civil ID
            civil_id2: Second Civil ID
            
        Returns:
            Dictionary with match results:
            {
                'match': bool,
                'confidence': str,
                'civil_id1_valid': bool,
                'civil_id2_valid': bool,
                'normalized1': str or None,
                'normalized2': str or None
            }
        """
        # Validate both IDs
        val1 = CivilIDValidator.validate_civil_id(civil_id1)
        val2 = CivilIDValidator.validate_civil_id(civil_id2)
        
        # Check if both are valid
        if not val1['valid'] or not val2['valid']:
            return {
                'match': False,
                'confidence': 'NONE',
                'civil_id1_valid': val1['valid'],
                'civil_id2_valid': val2['valid'],
                'normalized1': val1.get('normalized'),
                'normalized2': val2.get('normalized'),
                'error': 'One or both Civil IDs are invalid'
            }
        
        # Exact string match
        match = val1['normalized'] == val2['normalized']
        
        return {
            'match': match,
            'confidence': 'EXACT' if match else 'NONE',
            'civil_id1_valid': True,
            'civil_id2_valid': True,
            'normalized1': val1['normalized'],
            'normalized2': val2['normalized'],
            'error': None
        }
    
    @staticmethod
    def search_civil_id_in_list(
        target_civil_id: str,
        civil_id_list: List[str]
    ) -> List[Tuple[str, bool]]:
        """
        Search for Civil ID in a list
        
        Args:
            target_civil_id: Civil ID to search for
            civil_id_list: List of Civil IDs to search in
            
        Returns:
            List of (civil_id, is_match) tuples
        """
        target_val = CivilIDValidator.validate_civil_id(target_civil_id)
        
        if not target_val['valid']:
            return []
        
        target_normalized = target_val['normalized']
        matches = []
        
        for civil_id in civil_id_list:
            val = CivilIDValidator.validate_civil_id(civil_id)
            if val['valid']:
                is_match = val['normalized'] == target_normalized
                matches.append((val['normalized'], is_match))
        
        return matches
    
    @staticmethod
    def find_duplicates(civil_id_list: List[str]) -> Dict[str, List[int]]:
        """
        Find duplicate Civil IDs in a list
        
        Args:
            civil_id_list: List of Civil IDs
            
        Returns:
            Dictionary mapping Civil ID to list of indices where it appears
        """
        normalized_map = {}
        
        for idx, civil_id in enumerate(civil_id_list):
            val = CivilIDValidator.validate_civil_id(civil_id)
            if val['valid']:
                normalized = val['normalized']
                if normalized not in normalized_map:
                    normalized_map[normalized] = []
                normalized_map[normalized].append(idx)
        
        # Return only duplicates (appear more than once)
        duplicates = {
            civil_id: indices 
            for civil_id, indices in normalized_map.items() 
            if len(indices) > 1
        }
        
        return duplicates
    
    @staticmethod
    def format_civil_id(civil_id: str, format_pattern: str = 'XXXXXXXXXX') -> Optional[str]:
        """
        Format Civil ID for display
        
        Args:
            civil_id: Civil ID to format
            format_pattern: Pattern to use (X = digit, any other char = separator)
            
        Returns:
            Formatted Civil ID or None if invalid
        """
        val = CivilIDValidator.validate_civil_id(civil_id)
        
        if not val['valid']:
            return None
        
        normalized = val['normalized']
        
        # Common formats:
        # 'XXX-XXXXXX-X' = 272-081412-3
        # 'XX XXXX XXXX XX' = 27 2081 4123 55
        
        result = []
        digit_idx = 0
        
        for char in format_pattern:
            if char.upper() == 'X' and digit_idx < len(normalized):
                result.append(normalized[digit_idx])
                digit_idx += 1
            else:
                result.append(char)
        
        return ''.join(result)


# Convenience functions

def is_valid_civil_id(civil_id: str) -> bool:
    """
    Quick check if Civil ID is valid
    
    Args:
        civil_id: Civil ID to check
        
    Returns:
        True if valid, False otherwise
    """
    result = CivilIDValidator.validate_civil_id(civil_id)
    return result['valid']


def match_civil_ids(civil_id1: str, civil_id2: str) -> bool:
    """
    Quick check if two Civil IDs match
    
    Args:
        civil_id1: First Civil ID
        civil_id2: Second Civil ID
        
    Returns:
        True if exact match, False otherwise
    """
    result = CivilIDValidator.match_civil_ids(civil_id1, civil_id2)
    return result['match']


def normalize_civil_id(civil_id: str) -> Optional[str]:
    """
    Quick normalize Civil ID
    
    Args:
        civil_id: Civil ID to normalize
        
    Returns:
        Normalized 12-digit string or None
    """
    return CivilIDValidator.normalize_civil_id(civil_id)
