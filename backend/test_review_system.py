"""
Test the new review management system
"""
import sys
sys.path.insert(0, '.')

from database.connection import get_db
from models.database import FlaggedItem
from models.auth import User

print("=" * 70)
print("REVIEW MANAGEMENT SYSTEM - TEST")
print("=" * 70)

db = next(get_db())

# Check if we have flagged items
flagged_count = db.query(FlaggedItem).count()
print(f"\n✅ Flagged items in database: {flagged_count}")

if flagged_count > 0:
    print("\n📋 Sample Flagged Items:")
    items = db.query(FlaggedItem).limit(5).all()
    for item in items:
        print(f"  - ID: {item.id} | {item.kamco_name} ↔ {item.blacklist_name}")
        print(f"    Score: {item.match_score:.1f}% | Severity: {item.severity} | Status: {item.status}")

# Check users who can review
reviewers = db.query(User).filter(User.role.in_(['screener', 'checker', 'admin'])).all()
print(f"\n✅ Reviewers available: {len(reviewers)}")
for reviewer in reviewers:
    print(f"  - {reviewer.username} ({reviewer.role})")

print("\n" + "=" * 70)
print("AVAILABLE ENDPOINTS:")
print("=" * 70)
print("POST   /api/reviews/review/{item_id}     - Review single item")
print("POST   /api/reviews/review/bulk          - Bulk review")
print("GET    /api/reviews/report/item/{id}     - Individual report")
print("GET    /api/reviews/report/cumulative    - Summary report")
print("POST   /api/reviews/email/report         - Email reports")
print("=" * 70)

if flagged_count > 0:
    print("\n✅ READY TO TEST!")
    print(f"\nExample API call:")
    print(f"""
curl -X POST http://localhost:8000/api/reviews/review/1 \\
  -H "Authorization: Bearer YOUR_TOKEN" \\
  -H "Content-Type: application/json" \\
  -d '{{"decision":"approved","notes":"Match confirmed"}}'
""")
else:
    print("\n⚠️  No flagged items found!")
    print("Upload the test file 'blacklist_with_matches.csv' first to create matches.")

print("\n📚 See REVIEW_SYSTEM_GUIDE.md for complete documentation")
