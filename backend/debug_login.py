"""
Quick Login Test - Debug the 401 Error
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

print("=" * 60)
print("🔍 DEBUGGING LOGIN 401 ERROR")
print("=" * 60)
print()

# Test 1: Check if server is running
print("1️⃣  Checking if server is running...")
try:
    response = requests.get(f"{BASE_URL}/health", timeout=5)
    print(f"   ✅ Server is running: {response.status_code}")
    print(f"   Response: {response.json()}")
except Exception as e:
    print(f"   ❌ Server not responding: {e}")
    print("   💡 Start the server with: python3 main.py")
    exit(1)

print()

# Test 2: Check if database has users
print("2️⃣  Checking database for test users...")
try:
    import sys
    sys.path.append('.')
    from database.connection import SessionLocal
    from models.auth import User
    
    db = SessionLocal()
    users = db.query(User).all()
    
    if users:
        print(f"   ✅ Found {len(users)} users in database:")
        for user in users:
            print(f"      - {user.username} ({user.email}) - Role: {user.role.value} - Active: {user.is_active}")
    else:
        print("   ❌ No users found in database")
        print("   💡 Run: python3 seed_database.py")
        exit(1)
    
    db.close()
except Exception as e:
    print(f"   ⚠️  Could not check database: {e}")

print()

# Test 3: Try login with correct credentials
print("3️⃣  Testing login with screener_test...")
login_data = {
    "username": "screener_test",
    "password": "Screener123"
}

try:
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json=login_data,
        headers={"Content-Type": "application/json"},
        timeout=5
    )
    
    print(f"   Status Code: {response.status_code}")
    
    if response.status_code == 200:
        print("   ✅ LOGIN SUCCESSFUL!")
        data = response.json()
        print(f"   User: {data['user']['username']}")
        print(f"   Role: {data['user']['role']}")
        print(f"   Token Type: {data['token_type']}")
        print(f"   Access Token: {data['access_token'][:50]}...")
    else:
        print(f"   ❌ LOGIN FAILED!")
        print(f"   Response: {response.text}")
        
except Exception as e:
    print(f"   ❌ Error during login: {e}")

print()

# Test 4: Try login with wrong password
print("4️⃣  Testing login with wrong password...")
wrong_login_data = {
    "username": "screener_test",
    "password": "WrongPassword123"
}

try:
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json=wrong_login_data,
        timeout=5
    )
    
    print(f"   Status Code: {response.status_code}")
    
    if response.status_code == 401:
        print("   ✅ Correctly rejected wrong password")
    else:
        print(f"   ⚠️  Unexpected response: {response.status_code}")
        
except Exception as e:
    print(f"   ❌ Error: {e}")

print()

# Test 5: Verify password hashing
print("5️⃣  Testing password hashing directly...")
try:
    from utils.auth import hash_password, verify_password
    
    test_password = "Screener123"
    hashed = hash_password(test_password)
    
    print(f"   Original: {test_password}")
    print(f"   Hashed: {hashed[:40]}...")
    print(f"   Verification: {verify_password(test_password, hashed)}")
    
    # Check against actual database hash
    from database.connection import SessionLocal
    from models.auth import User
    
    db = SessionLocal()
    screener = db.query(User).filter(User.username == "screener_test").first()
    
    if screener:
        print(f"   DB Hash: {screener.hashed_password[:40]}...")
        verify_result = verify_password(test_password, screener.hashed_password)
        print(f"   DB Verification: {verify_result}")
        
        if not verify_result:
            print("   ⚠️  PASSWORD MISMATCH IN DATABASE!")
            print("   💡 Re-run: python3 seed_database.py")
    
    db.close()
    
except Exception as e:
    print(f"   ❌ Error: {e}")

print()
print("=" * 60)
print("🔍 DEBUG COMPLETE")
print("=" * 60)
