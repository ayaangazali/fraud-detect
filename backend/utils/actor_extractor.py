"""
Actor field extraction for Clients and Vendors sheets
Extracts representative/actor information for enhanced matching
"""
from typing import Optional, Dict, List

def extract_actor(row: Dict, sheet_type: str) -> Optional[str]:
    """
    Extract actor/representative name from a row
    Only applicable for Clients and Vendors sheets
    
    Args:
        row: Dictionary representing a row from Excel
        sheet_type: Type of sheet ('clients' or 'vendors')
        
    Returns:
        Actor name if found, None otherwise
    """
    if sheet_type not in ['clients', 'vendors']:
        return None
    
    # Common field names for actor/representative
    actor_field_names = [
        'Actor', 'actor', 'ACTOR',
        'Representative', 'representative', 'REPRESENTATIVE',
        'Agent', 'agent', 'AGENT',
        'Contact Person', 'contact person', 'CONTACT PERSON',
        'Authorized Person', 'authorized person', 'AUTHORIZED PERSON'
    ]
    
    for field_name in actor_field_names:
        if field_name in row and row[field_name]:
            actor_value = str(row[field_name]).strip()
            if actor_value and actor_value.lower() not in ['', 'n/a', 'na', 'none', '-']:
                return actor_value
    
    return None

def extract_actors_from_sheet(rows: List[Dict], sheet_type: str) -> List[Dict]:
    """
    Extract actor information from all rows in a sheet
    
    Args:
        rows: List of row dictionaries
        sheet_type: Type of sheet ('clients' or 'vendors')
        
    Returns:
        List of rows with added 'actor' field
    """
    result = []
    for row in rows:
        enriched_row = row.copy()
        enriched_row['actor'] = extract_actor(row, sheet_type)
        result.append(enriched_row)
    
    return result
