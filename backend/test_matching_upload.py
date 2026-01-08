"""
Test upload with matching data to verify auto-screening works
"""
import sys
sys.path.insert(0, '.')

from database.connection import get_db
from models.blacklist import BlacklistEntry
from models.database import FlaggedItem, KamcoClient, KamcoVendor, KamcoStaff, KamcoOther
from models.auth import User
from utils.multi_format_parser import parse_blacklist_file
from utils.fuzzy_matcher_enhanced import FuzzyMatcherEnhanced

print("=" * 70)
print("TESTING AUTO-SCREENING WITH MATCHING DATA")
print("=" * 70)

# Setup
db = next(get_db())

# Get test user
user = db.query(User).filter(User.email == 'screener@kamco.com').first()
if not user:
    print("❌ Test user not found")
    sys.exit(1)

print(f"\n✅ Test user: {user.email}")

# Clear previous data
print("\n🧹 Cleaning previous data...")
db.query(FlaggedItem).delete()
db.query(BlacklistEntry).delete()
db.commit()
print("✅ Cleaned")

# Parse file with matching names
print("\n📄 Parsing blacklist with matching names...")
with open('../test_data/blacklist_with_matches.csv', 'rb') as f:
    file_bytes = f.read()

result = parse_blacklist_file(file_bytes, 'blacklist_with_matches.csv')
records = result['data']
summary = result['summary']

print(f"✅ Parsed {len(records)} records")

# Store records
print("\n💾 Storing records...")
stored_count = 0

for record in records:
    try:
        record['upload_filename'] = 'blacklist_with_matches.csv'
        blacklist_entry = BlacklistEntry(**record)
        db.add(blacklist_entry)
        stored_count += 1
    except Exception as e:
        print(f"❌ Error storing record: {e}")

db.commit()
print(f"✅ Stored {stored_count} records")

# Get Kamco data
print("\n🔍 Checking Kamco entities...")
kamco_data = {
    'clients': db.query(KamcoClient).all(),
    'vendors': db.query(KamcoVendor).all(),
    'staff': db.query(KamcoStaff).all(),
    'others': db.query(KamcoOther).all()
}

total_kamco = sum(len(entities) for entities in kamco_data.values())
print(f"✅ Found {total_kamco} Kamco entities:")
for entity_type, entities in kamco_data.items():
    print(f"   - {entity_type}: {len(entities)}")

# Auto-screening
print("\n🔍 AUTO-SCREENING...")
matcher = FuzzyMatcherEnhanced()
blacklist_entries = db.query(BlacklistEntry).all()

matches_found = 0
match_details = []

for entity_type, entities in kamco_data.items():
    print(f"\n   Screening {len(entities)} {entity_type}...")
    
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
            
            if best_match['match_score'] >= 70:
                # Check if already flagged
                existing = db.query(FlaggedItem).filter(
                    FlaggedItem.kamco_name == entity.name,
                    FlaggedItem.kamco_type == entity_type,
                    FlaggedItem.blacklist_name == best_blacklist_name
                ).first()
                
                if not existing:
                    # Determine severity
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
                        flagged_by_id=user.id,
                        flag_reason=f"Auto-flagged: Name match {best_match['match_score']:.1f}%",
                        flag_reason_category='match_confirmed'
                    )
                    db.add(flagged_item)
                    matches_found += 1
                    
                    match_info = f"      ✅ {entity.name} <-> {best_blacklist_name} ({best_match['match_score']:.1f}% - {severity.upper()})"
                    print(match_info)
                    match_details.append(match_info)

db.commit()

# Results
print("\n" + "=" * 70)
print("RESULTS")
print("=" * 70)
print(f"📊 Blacklist entries: {db.query(BlacklistEntry).count()}")
print(f"📊 Kamco entities: {total_kamco}")
print(f"🎯 Matches found: {matches_found}")
print(f"📋 Flagged items in database: {db.query(FlaggedItem).count()}")

if matches_found > 0:
    print("\n🎉 SUCCESS! Matches were found!")
    print("\nMatch Summary:")
    for detail in match_details:
        print(detail)
else:
    print("\n⚠️  WARNING: No matches found. Check matching algorithm threshold.")

# Severity breakdown
print("\n📊 Severity Breakdown:")
high_count = db.query(FlaggedItem).filter(FlaggedItem.severity == 'high').count()
medium_count = db.query(FlaggedItem).filter(FlaggedItem.severity == 'medium').count()
low_count = db.query(FlaggedItem).filter(FlaggedItem.severity == 'low').count()
print(f"   HIGH: {high_count}")
print(f"   MEDIUM: {medium_count}")
print(f"   LOW: {low_count}")

print("\n" + "=" * 70)
