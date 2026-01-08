#!/usr/bin/env python3
"""
Quick diagnostic script to check upload endpoint authentication
"""

import sys
sys.path.insert(0, '.')

from fastapi.testclient import TestClient
from main import app
from database.connection import SessionLocal
from models.auth import User, UserRole
from utils.auth import create_access_token

# Create test client
client = TestClient(app)

print("=" * 70)
print("UPLOAD ENDPOINT AUTHENTICATION DIAGNOSTIC")
print("=" * 70)
print()

# Get a test user from database
db = SessionLocal()
try:
    # Try to find a screener user
    screener = db.query(User).filter(User.role == UserRole.SCREENER).first()
    checker = db.query(User).filter(User.role == UserRole.CHECKER).first()
    finalizer = db.query(User).filter(User.role == UserRole.FINALIZER).first()
    
    print("Users in database:")
    print(f"  Screener: {screener.username if screener else 'NONE'}")
    print(f"  Checker: {checker.username if checker else 'NONE'}")
    print(f"  Finalizer: {finalizer.username if finalizer else 'NONE'}")
    print()
    
    if screener:
        # Create access token for screener
        token = create_access_token({"user_id": screener.id})
        print(f"Testing with Screener user: {screener.username}")
        print(f"  User ID: {screener.id}")
        print(f"  Role: {screener.role}")
        print(f"  Active: {screener.is_active}")
        print(f"  Token: {token[:50]}...")
        print()
        
        # Test upload endpoint
        headers = {"Authorization": f"Bearer {token}"}
        
        # Create a dummy file
        files = {"file": ("test.xlsx", b"dummy content", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
        
        response = client.post("/api/upload/blacklist", files=files, headers=headers)
        
        print(f"Response Status: {response.status_code}")
        print(f"Response: {response.text[:200]}")
        print()
        
        if response.status_code == 403:
            print("❌ 403 FORBIDDEN - Checking possible causes:")
            print(f"  1. User is_active: {screener.is_active}")
            print(f"  2. User role: {screener.role}")
            print("  3. Check if endpoint requires specific role")
        elif response.status_code == 401:
            print("❌ 401 UNAUTHORIZED - Token issue")
        elif response.status_code == 200:
            print("✅ 200 OK - Upload working!")
        else:
            print(f"❓ {response.status_code} - Other response")
    else:
        print("❌ No screener user found in database!")
        print("   Run: python3 scripts/seed_database.py")
        
finally:
    db.close()

print("=" * 70)
