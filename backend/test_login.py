#!/usr/bin/env python3
"""
Quick test to verify login endpoint works
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_login():
    """Test login with username"""
    
    print("=" * 60)
    print("TESTING LOGIN ENDPOINT")
    print("=" * 60)
    
    # Test data
    login_data = {
        "username": "checker_test",
        "password": "password123"
    }
    
    print(f"\n📤 Sending POST request to {BASE_URL}/api/auth/login")
    print(f"📦 Payload: {json.dumps(login_data, indent=2)}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"\n📨 Response Status: {response.status_code}")
        print(f"📋 Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ LOGIN SUCCESSFUL!")
            print(f"👤 User: {data.get('user', {}).get('username')}")
            print(f"🔑 Access Token: {data.get('access_token')[:50]}...")
            print(f"🔄 Refresh Token: {data.get('refresh_token')[:50]}...")
            print(f"⏱️  Expires In: {data.get('expires_in')} seconds")
            return True
        else:
            print(f"\n❌ LOGIN FAILED!")
            print(f"Error: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to backend server")
        print("Make sure the backend is running on http://localhost:8000")
        return False
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        return False

if __name__ == "__main__":
    success = test_login()
    print("\n" + "=" * 60)
    if success:
        print("✅ TEST PASSED - Login is working!")
    else:
        print("❌ TEST FAILED - Login is not working")
    print("=" * 60)
