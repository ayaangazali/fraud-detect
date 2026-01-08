"""
Test complete upload flow including auto-screening
"""
import sys
sys.path.insert(0, '.')

from database.connection import get_db
from models.blacklist import BlacklistEntry
from models.database import FlaggedItem, KamcoClient, KamcoVendor, KamcoStaff, KamcoOther
from models.auth import User
from utils.multi_format_parser import parse_blacklist_file
from utils.fuzzy_matcher_enhanced import FuzzyMatcherEnhanced

print("=" * 60)
print("TESTING COMPLETE UPLOAD FLOW WITH AUTO-SCREENING")
print("=" * 60)

# Setup
db = next(get_db())

# Get test user
user = db.query(User).filter(User.email == 'screener@kamco.com').first()
if not user:
    print("❌ Test user not found")
    sys.exit(1)

print(f"\n✅ Test user: {user.email}")

# Clear previous test data
print("\n🧹 Cleaning previous test data...")
db.query(FlaggedItem).delete()
db.query(BlacklistEntry).delete()
db.commit()
print("✅ Cleaned")

# Parse file
print("\n📄 Parsing blacklist file...")
with open('../test_data/blacklist_mock_data.csv', 'rb') as f:
    file_bytes = f.read()

result = parse_blacklist_file(file_bytes, 'blacklist_mock_data.csv')
records = result['data']
summary = result['summary']

print(f"✅ Parsed {len(records)} records")
print(f"   Batch ID: {summary['batch_id']}")

# Store records
print("\n💾 Storing records in database...")
stored_count = 0
errors = []

for record in records:
    try:
        record['upload_filename'] = 'blacklist_mock_data.csv'
        blacklist_entry = BlacklistEntry(**record)
        db.add(blacklist_entry)
        stored_count += 1
    except Exception as e:
        errors.append(str(e))

db.commit()
print(f"✅ Stored {stored_count} records")

# Auto-screening
print("\n🔍 AUTO-SCREENING...")

# Check Kamco data
kamco_count = (
    db.query(KamcoClient).count() +
    db.query(KamcoVendor).count() +
    db.query(KamcoStaff).count() +
    db.query(KamcoOther).count()
)

print(f"   Kamco entities found: {kamco_count}")

if kamco_count > 0:
    matcher = FuzzyMatcherEnhanced()
    blacklist_entries = db.query(BlacklistEntry).all()
    
    matches_found = 0
    
    for entity_type, model in [
        ("clients", KamcoClient),
        ("vendors", KamcoVendor),
        ("staff", KamcoStaff),
        ("others", KamcoOther)
    ]:
        entities = db.query(model).all()
        print(f"   Screening {len(entities)} {entity_type}...")
        
        for entity in entities:
            for blacklist_entry in blacklist_entries:
                blacklist_name = blacklist_entry.name_arabic or blacklist_entry.name_english or ""
                if not blacklist_name:
                    continue
                
                name_match = matcher.match_names(entity.name, blacklist_name, use_multiple_algorithms=True)
                
                if name_match['match_score'] >= 70:
                    # Check if already flagged
                    existing = db.query(FlaggedItem).filter(
                        FlaggedItem.kamco_name == entity.name,
                        FlaggedItem.kamco_type == entity_type,
                        FlaggedItem.blacklist_name == blacklist_name
                    ).first()
                    
                    if not existing:
                        # Determine severity
                        if name_match['match_score'] >= 90:
                            severity = 'high'
                        elif name_match['match_score'] >= 80:
                            severity = 'medium'
                        else:
                            severity = 'low'
                        
                        flagged_item = FlaggedItem(
                            kamco_name=entity.name,
                            kamco_type=entity_type,
                            kamco_id=entity.id,
                            blacklist_name=blacklist_name,
                            blacklist_source=blacklist_entry.source or "Uploaded",
                            match_score=name_match['match_score'],
                            severity=severity,
                            status='pending',
                            flagged_by_id=user.id,
                            flag_reason=f"Auto-flagged: Name match {name_match['match_score']:.1f}%",
                            flag_reason_category='match_confirmed'
                        )
                        db.add(flagged_item)
                        matches_found += 1
                        print(f"      ✅ Match: {entity.name} <-> {blacklist_name} ({name_match['match_score']:.1f}%)")
    
    db.commit()
    print(f"\n✅ Auto-screening complete: {matches_found} matches found and flagged")
else:
    print("   ℹ️  No Kamco data to screen against")

# Results
print("\n" + "=" * 60)
print("RESULTS")
print("=" * 60)
print(f"Blacklist entries: {db.query(BlacklistEntry).count()}")
print(f"Flagged items: {db.query(FlaggedItem).count()}")
print(f"Kamco entities: {kamco_count}")
print("\n✅ TEST COMPLETE!")
