"""
Test upload API endpoint with authentication
"""
import sys
sys.path.insert(0, '.')

import requests
from database.connection import get_db
from models.blacklist import BlacklistEntry
from models.auth import User
from datetime import datetime, timedelta
from utils.auth import create_access_token

print("=" * 70)
print("TESTING UPLOAD API ENDPOINT WITH AUTHENTICATION")
print("=" * 70)

# Base URL (assumes backend is running on port 8000)
BASE_URL = "http://localhost:8000/api"

# Get test user and create token
db = next(get_db())
user = db.query(User).filter(User.email == 'screener@kamco.com').first()

if not user:
    print("❌ Test user not found")
    sys.exit(1)

print(f"\n✅ Test user: {user.email}")

# Create access token
access_token = create_access_token(
    data={"sub": user.email},
    expires_delta=timedelta(minutes=30)
)
print(f"✅ Access token created")

# Clear previous blacklist data
print("\n🧹 Cleaning previous blacklist data...")
db.query(BlacklistEntry).delete()
db.commit()
print("✅ Cleaned")

# Prepare file upload
print("\n📤 Testing file upload...")
with open('../test_data/blacklist_mock_data.csv', 'rb') as f:
    files = {'file': ('blacklist_mock_data.csv', f, 'text/csv')}
    headers = {'Authorization': f'Bearer {access_token}'}
    
    response = requests.post(
        f'{BASE_URL}/upload/blacklist',
        files=files,
        headers=headers
    )

print(f"\n📊 Response Status: {response.status_code}")

if response.status_code == 200:
    data = response.json()
    print(f"✅ SUCCESS!")
    print(f"\nResponse:")
    print(f"  Success: {data.get('success')}")
    print(f"  Message: {data.get('message')}")
    
    upload_data = data.get('data', {})
    print(f"\nUpload Details:")
    print(f"  Filename: {upload_data.get('filename')}")
    print(f"  Batch ID: {upload_data.get('batch_id')}")
    print(f"  Total Rows: {upload_data.get('total_rows')}")
    print(f"  Stored Count: {upload_data.get('stored_count')}")
    
    screening = upload_data.get('screening', {})
    if screening:
        print(f"\nAuto-Screening Results:")
        print(f"  Kamco Entities: {screening.get('kamco_entities')}")
        print(f"  Matches Found: {screening.get('matches_found')}")
        print(f"  Auto-Screened: {screening.get('auto_screened')}")
    
    # Verify in database
    count = db.query(BlacklistEntry).count()
    print(f"\n🔍 Database verification: {count} blacklist entries")
    
else:
    print(f"❌ FAILED")
    print(f"Response: {response.text}")

print("\n" + "=" * 70)
if response.status_code == 200:
    print("🎉 UPLOAD API TEST PASSED!")
else:
    print("❌ UPLOAD API TEST FAILED")
print("=" * 70)
