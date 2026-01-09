#!/usr/bin/env python3
"""
Test script for screening queue endpoint
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_queue():
    print("🔐 Step 1: Logging in...")
    login_response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={
            "username": "checker_test",
            "password": "password123"
        }
    )
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        print(login_response.text)
        return
    
    token = login_response.json()["access_token"]
    print(f"✅ Login successful! Token: {token[:20]}...")
    
    print("\n📋 Step 2: Fetching screening queue...")
    queue_response = requests.get(
        f"{BASE_URL}/api/screening/queue",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if queue_response.status_code != 200:
        print(f"❌ Queue fetch failed: {queue_response.status_code}")
        print(queue_response.text)
        return
    
    data = queue_response.json()
    print(f"✅ Queue fetched successfully!")
    print(f"\n📊 Queue count: {data['count']}")
    
    if data['count'] > 0:
        print(f"\n🔍 First item details:")
        first_item = data['queue'][0]
        print(f"  ID: {first_item['id']}")
        print(f"  Kamco Name: {first_item['kamco_name']}")
        print(f"  Kamco Type: {first_item['kamco_type']}")
        print(f"  Blacklist Name: {first_item['blacklist_name']}")
        print(f"  Match Score: {first_item['match_score']}")
        print(f"  Severity: {first_item['severity']}")
        
        if first_item.get('kamco_details'):
            print(f"\n  📦 Kamco Details:")
            for key, value in first_item['kamco_details'].items():
                print(f"    - {key}: {value}")
        
        if first_item.get('blacklist_details'):
            print(f"\n  ⚠️  Blacklist Details:")
            for key, value in first_item['blacklist_details'].items():
                if value:
                    print(f"    - {key}: {value}")
    
    print("\n✅ TEST PASSED - Queue endpoint working correctly!")

if __name__ == "__main__":
    try:
        test_queue()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
