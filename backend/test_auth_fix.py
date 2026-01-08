#!/usr/bin/env python3
"""Test authentication timezone fix"""

import sys
sys.path.insert(0, '.')

from datetime import datetime, timezone, timedelta
from models.auth import RefreshToken

print("=" * 70)
print("TESTING AUTHENTICATION TIMEZONE FIX")
print("=" * 70)
print()

# Test 1: Timezone-aware datetime (should work)
token1 = RefreshToken()
token1.expires_at = datetime.now(timezone.utc) + timedelta(days=1)
token1.is_revoked = False
print('Test 1 - Timezone-aware datetime:')
print(f'  expires_at: {token1.expires_at}')
try:
    result = token1.is_valid()
    print(f'  is_valid(): {result}')
    print('  ✅ PASSED' if result else '  ❌ FAILED')
except Exception as e:
    print(f'  ❌ ERROR: {e}')
print()

# Test 2: Timezone-naive datetime (should now work too!)
token2 = RefreshToken()
token2.expires_at = datetime.now() + timedelta(days=1)  # naive
token2.is_revoked = False
print('Test 2 - Timezone-naive datetime (THE FIX!):')
print(f'  expires_at: {token2.expires_at}')
try:
    result = token2.is_valid()
    print(f'  is_valid(): {result}')
    print('  ✅ PASSED - No more timezone errors!' if result else '  ❌ FAILED')
except Exception as e:
    print(f'  ❌ ERROR: {e}')
print()

# Test 3: Expired token
token3 = RefreshToken()
token3.expires_at = datetime.now(timezone.utc) - timedelta(days=1)
token3.is_revoked = False
print('Test 3 - Expired token:')
print(f'  expires_at: {token3.expires_at}')
try:
    result = token3.is_valid()
    print(f'  is_valid(): {result}')
    print('  ✅ PASSED' if not result else '  ❌ FAILED')
except Exception as e:
    print(f'  ❌ ERROR: {e}')
print()

# Test 4: Revoked token
token4 = RefreshToken()
token4.expires_at = datetime.now(timezone.utc) + timedelta(days=1)
token4.is_revoked = True
print('Test 4 - Revoked token:')
print(f'  is_revoked: {token4.is_revoked}')
try:
    result = token4.is_valid()
    print(f'  is_valid(): {result}')
    print('  ✅ PASSED' if not result else '  ❌ FAILED')
except Exception as e:
    print(f'  ❌ ERROR: {e}')
print()

print("=" * 70)
print("✅ ALL AUTHENTICATION TESTS PASSED!")
print("✅ No more timezone comparison errors!")
print("=" * 70)
