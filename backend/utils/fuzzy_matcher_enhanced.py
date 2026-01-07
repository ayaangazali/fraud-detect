"""
Enhanced Fuzzy Matching for Phase 5
Supports Arabic text, diacritics removal, and advanced name normalization
"""
from rapidfuzz import fuzz, process
from typing import List, Dict, Tuple, Optional, Any
import re
import unicodedata


class FuzzyMatcherEnhanced:
    """
    Enhanced fuzzy matcher with Arabic text support
    """
    
    # Match thresholds
    EXACT_MATCH_THRESHOLD = 95      # 95-100% = Exact/Near-exact
    HIGH_MATCH_THRESHOLD = 85       # 85-94% = Strong match
    MEDIUM_MATCH_THRESHOLD = 70     # 70-84% = Possible match
    LOW_MATCH_THRESHOLD = 50        # 50-69% = Weak match
    
    # Risk levels based on match score
    RISK_LEVELS = {
        'CRITICAL': (95, 100),   # Requires immediate blocking
        'HIGH': (85, 94),        # Requires thorough review
        'MEDIUM': (70, 84),      # Requires review
        'LOW': (50, 69),         # Optional review
        'MINIMAL': (0, 49)       # Likely false positive
    }
    
    def __init__(self):
        """Initialize the enhanced matcher"""
        self.match_cache = {}  # Cache for performance
        
    @staticmethod
    def normalize_arabic_text(text: str) -> str:
        """
        Normalize Arabic text by removing diacritics and normalizing letters
        
        Args:
            text: Arabic text to normalize
            
        Returns:
            Normalized text
        """
        if not text:
            return ""
        
        # Remove Arabic diacritics (tashkeel)
        arabic_diacritics = re.compile("""
            ّ    | # Shadda
            َ    | # Fatha
            ً    | # Tanwin Fath
            ُ    | # Damma
            ٌ    | # Tanwin Damm
            ِ    | # Kasra
            ٍ    | # Tanwin Kasr
            ْ    | # Sukun
            ـ     # Tatweel
        """, re.VERBOSE)
        
        text = re.sub(arabic_diacritics, '', text)
        
        # Normalize Arabic letters
        # Alef variations to base Alef
        text = re.sub('[إأآا]', 'ا', text)
        # Teh Marbuta to Heh
        text = re.sub('ة', 'ه', text)
        # Alef Maksura to Yeh
        text = re.sub('ى', 'ي', text)
        
        return text
    
    @staticmethod
    def normalize_text(text: str, remove_special_chars: bool = True) -> str:
        """
        Normalize text (works for both Arabic and English)
        
        Args:
            text: Text to normalize
            remove_special_chars: Whether to remove special characters
            
        Returns:
            Normalized text
        """
        if not text:
            return ""
        
        # Strip whitespace
        text = text.strip()
        
        # Convert to lowercase (works for English, safe for Arabic)
        text = text.lower()
        
        # Normalize Arabic if present
        text = FuzzyMatcherEnhanced.normalize_arabic_text(text)
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Remove special characters if requested
        if remove_special_chars:
            # Keep only letters, numbers, and spaces
            text = re.sub(r'[^\w\s]', ' ', text, flags=re.UNICODE)
            text = ' '.join(text.split())  # Clean up extra spaces
        
        return text
    
    def calculate_match_score(
        self, 
        text1: str, 
        text2: str,
        algorithm: str = 'token_set_ratio'
    ) -> int:
        """
        Calculate match score between two texts
        
        Args:
            text1: First text
            text2: Second text
            algorithm: Matching algorithm to use
                - 'token_set_ratio': Best for names with different word orders
                - 'token_sort_ratio': Good for names with misspellings
                - 'partial_ratio': Good for partial name matches
                - 'ratio': Simple character-by-character comparison
                
        Returns:
            Match score (0-100)
        """
        if not text1 or not text2:
            return 0
        
        # Normalize both texts
        text1_norm = self.normalize_text(text1)
        text2_norm = self.normalize_text(text2)
        
        if not text1_norm or not text2_norm:
            return 0
        
        # Check cache
        cache_key = f"{text1_norm}:{text2_norm}:{algorithm}"
        if cache_key in self.match_cache:
            return self.match_cache[cache_key]
        
        # Calculate score based on algorithm
        if algorithm == 'token_set_ratio':
            score = fuzz.token_set_ratio(text1_norm, text2_norm)
        elif algorithm == 'token_sort_ratio':
            score = fuzz.token_sort_ratio(text1_norm, text2_norm)
        elif algorithm == 'partial_ratio':
            score = fuzz.partial_ratio(text1_norm, text2_norm)
        elif algorithm == 'ratio':
            score = fuzz.ratio(text1_norm, text2_norm)
        else:
            # Default to token_set_ratio
            score = fuzz.token_set_ratio(text1_norm, text2_norm)
        
        # Cache the result
        self.match_cache[cache_key] = int(score)
        
        return int(score)
    
    def match_names(
        self,
        name1: str,
        name2: str,
        use_multiple_algorithms: bool = True
    ) -> Dict[str, Any]:
        """
        Match two names using multiple algorithms and return detailed results
        
        Args:
            name1: First name
            name2: Second name
            use_multiple_algorithms: Whether to use multiple algorithms for better accuracy
            
        Returns:
            Dictionary with match results:
            {
                'match_score': int,
                'risk_level': str,
                'is_match': bool,
                'confidence': str,
                'algorithms_used': dict,
                'normalized_name1': str,
                'normalized_name2': str
            }
        """
        if not name1 or not name2:
            return {
                'match_score': 0,
                'risk_level': 'MINIMAL',
                'is_match': False,
                'confidence': 'NONE',
                'algorithms_used': {},
                'normalized_name1': '',
                'normalized_name2': ''
            }
        
        # Normalize names
        norm1 = self.normalize_text(name1)
        norm2 = self.normalize_text(name2)
        
        # Calculate scores using different algorithms
        scores = {
            'token_set_ratio': self.calculate_match_score(name1, name2, 'token_set_ratio'),
            'token_sort_ratio': self.calculate_match_score(name1, name2, 'token_sort_ratio'),
            'partial_ratio': self.calculate_match_score(name1, name2, 'partial_ratio'),
            'ratio': self.calculate_match_score(name1, name2, 'ratio')
        }
        
        if use_multiple_algorithms:
            # Use weighted average (token_set_ratio has highest weight)
            final_score = int(
                scores['token_set_ratio'] * 0.4 +
                scores['token_sort_ratio'] * 0.3 +
                scores['partial_ratio'] * 0.2 +
                scores['ratio'] * 0.1
            )
        else:
            # Use best single algorithm for names
            final_score = scores['token_set_ratio']
        
        # Determine risk level
        risk_level = self._get_risk_level(final_score)
        
        # Determine if it's a match
        is_match = final_score >= self.MEDIUM_MATCH_THRESHOLD
        
        # Determine confidence
        if final_score >= self.EXACT_MATCH_THRESHOLD:
            confidence = 'VERY_HIGH'
        elif final_score >= self.HIGH_MATCH_THRESHOLD:
            confidence = 'HIGH'
        elif final_score >= self.MEDIUM_MATCH_THRESHOLD:
            confidence = 'MEDIUM'
        elif final_score >= self.LOW_MATCH_THRESHOLD:
            confidence = 'LOW'
        else:
            confidence = 'VERY_LOW'
        
        return {
            'match_score': final_score,
            'risk_level': risk_level,
            'is_match': is_match,
            'confidence': confidence,
            'algorithms_used': scores,
            'normalized_name1': norm1,
            'normalized_name2': norm2
        }
    
    def _get_risk_level(self, score: int) -> str:
        """Get risk level based on match score"""
        for level, (min_score, max_score) in self.RISK_LEVELS.items():
            if min_score <= score <= max_score:
                return level
        return 'MINIMAL'
    
    def find_best_matches(
        self,
        query_name: str,
        candidate_names: List[Dict[str, Any]],
        top_n: int = 10,
        min_score: int = None
    ) -> List[Dict[str, Any]]:
        """
        Find best matches from a list of candidates
        
        Args:
            query_name: Name to match against
            candidate_names: List of candidate dictionaries with at least 'name' key
            top_n: Maximum number of results to return
            min_score: Minimum match score (defaults to MEDIUM_MATCH_THRESHOLD)
            
        Returns:
            List of matched candidates sorted by score (descending)
        """
        if min_score is None:
            min_score = self.MEDIUM_MATCH_THRESHOLD
        
        results = []
        
        for candidate in candidate_names:
            candidate_name = candidate.get('name', '')
            if not candidate_name:
                continue
            
            match_result = self.match_names(query_name, candidate_name)
            
            if match_result['match_score'] >= min_score:
                result = {
                    **candidate,
                    **match_result
                }
                results.append(result)
        
        # Sort by match score (descending)
        results.sort(key=lambda x: x['match_score'], reverse=True)
        
        # Return top N
        return results[:top_n]
    
    def batch_match(
        self,
        query_names: List[str],
        candidate_names: List[Dict[str, Any]],
        min_score: int = None
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Match multiple query names against candidates
        
        Args:
            query_names: List of names to match
            candidate_names: List of candidate dictionaries
            min_score: Minimum match score
            
        Returns:
            Dictionary mapping query names to their matches
        """
        results = {}
        
        for query_name in query_names:
            matches = self.find_best_matches(
                query_name, 
                candidate_names,
                min_score=min_score
            )
            results[query_name] = matches
        
        return results
    
    def clear_cache(self):
        """Clear the match cache"""
        self.match_cache.clear()


# Convenience functions

def match_names_simple(name1: str, name2: str) -> int:
    """
    Simple name matching function that returns a score
    
    Args:
        name1: First name
        name2: Second name
        
    Returns:
        Match score (0-100)
    """
    matcher = FuzzyMatcherEnhanced()
    result = matcher.match_names(name1, name2, use_multiple_algorithms=False)
    return result['match_score']


def is_name_match(name1: str, name2: str, threshold: int = 70) -> bool:
    """
    Check if two names match above a threshold
    
    Args:
        name1: First name
        name2: Second name
        threshold: Minimum match score (default 70)
        
    Returns:
        True if match score >= threshold
    """
    score = match_names_simple(name1, name2)
    return score >= threshold
