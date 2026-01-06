"""
Fuzzy matching algorithm using rapidfuzz
Matches blacklist names against Kamco database
"""
from rapidfuzz import fuzz
from typing import List, Tuple, Optional

# Matching thresholds
NAME_MATCH_THRESHOLD = 80  # 80% similarity for name matching
ACTOR_MATCH_THRESHOLD = 75  # 75% similarity for actor matching

def fuzzy_match_name(kamco_name: str, blacklist_name: str) -> int:
    """
    Calculate fuzzy match score between two names using token_sort_ratio
    
    Args:
        kamco_name: Name from Kamco database
        blacklist_name: Name from blacklist
        
    Returns:
        Match score (0-100)
    """
    if not kamco_name or not blacklist_name:
        return 0
    
    # Normalize names
    kamco_normalized = kamco_name.strip().lower()
    blacklist_normalized = blacklist_name.strip().lower()
    
    # Use token_sort_ratio for better matching of names with different word orders
    score = fuzz.token_sort_ratio(kamco_normalized, blacklist_normalized)
    
    return int(score)

def find_matches(
    kamco_name: str,
    blacklist_names: List[Tuple[str, str]],  # [(name, source), ...]
    threshold: int = NAME_MATCH_THRESHOLD
) -> List[Tuple[str, str, int]]:
    """
    Find all matching names from blacklist that exceed threshold
    
    Args:
        kamco_name: Name from Kamco database
        blacklist_names: List of (name, source) tuples from blacklist
        threshold: Minimum match score (default: 80)
        
    Returns:
        List of (blacklist_name, source, score) tuples sorted by score (descending)
    """
    matches = []
    
    for blacklist_name, source in blacklist_names:
        score = fuzzy_match_name(kamco_name, blacklist_name)
        
        if score >= threshold:
            matches.append((blacklist_name, source, score))
    
    # Sort by score (descending)
    matches.sort(key=lambda x: x[2], reverse=True)
    
    return matches

def match_actor(
    kamco_actor: Optional[str],
    blacklist_name: str
) -> Tuple[bool, int]:
    """
    Check if actor name matches blacklist name
    Only used for Clients and Vendors
    
    Args:
        kamco_actor: Actor/representative name from Kamco database
        blacklist_name: Name from blacklist
        
    Returns:
        (is_match, score) tuple
    """
    if not kamco_actor:
        return (False, 0)
    
    score = fuzzy_match_name(kamco_actor, blacklist_name)
    is_match = score >= ACTOR_MATCH_THRESHOLD
    
    return (is_match, score)
