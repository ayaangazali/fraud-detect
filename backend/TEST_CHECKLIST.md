# 🧪 Authentication Testing Checklist

## ✅ Pre-Deployment Verification

### 1. Environment Setup
- [ ] Virtual environment activated
- [ ] All dependencies installed (`pip install -r requirements.txt`)
- [ ] Test dependencies installed (`pip install pytest pytest-asyncio httpx`)
- [ ] Database seeded (`python3 seed_database.py`)
- [ ] Server running (`python3 main.py`)

### 2. Quick Verification Tests
```bash
# Run these commands to verify everything works

# 1. Quick debug test
cd backend
source venv/bin/activate
python3 debug_login.py

# Expected: All 5 checks should pass ✅
```

### 3. Full Test Suite
```bash
# 2. Run complete test suite
./run_tests.sh

# Expected: All 66+ tests should pass ✅
```

### 4. Manual Login Tests

#### Test 1: Successful Login ✅
```bash
curl -X POST http://127.0.0.1:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "screener_test", "password": "Screener123"}'
```
**Expected**: Status 200, returns access_token and user data

#### Test 2: Wrong Password ❌
```bash
curl -X POST http://127.0.0.1:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "screener_test", "password": "WrongPassword"}'
```
**Expected**: Status 401, message shows remaining attempts

#### Test 3: Rate Limiting 🛡️
```bash
# Try 6 wrong passwords
for i in {1..6}; do
  curl -X POST http://127.0.0.1:8000/api/auth/login \
    -d '{"username": "test_user_$$", "password": "Wrong"}'
  echo ""
done
```
**Expected**: 6th attempt returns 429 (Too Many Requests)

#### Test 4: SQL Injection Protection 🔒
```bash
curl -X POST http://127.0.0.1:8000/api/auth/login \
  -d '{"username": "admin'\'' OR '\''1'\''='\''1", "password": "anything"}'
```
**Expected**: Status 401, injection attempt fails

#### Test 5: Token Authentication 🎫
```bash
# Get token
TOKEN=$(curl -s -X POST http://127.0.0.1:8000/api/auth/login \
  -d '{"username": "screener_test", "password": "Screener123"}' | \
  python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

# Use token
curl -X GET http://127.0.0.1:8000/api/auth/me \
  -H "Authorization: Bearer $TOKEN"
```
**Expected**: Status 200, returns user profile

### 5. Browser Tests

#### Test in Browser UI
- [ ] Navigate to http://localhost:3001/login
- [ ] Enter: screener@kamco.com / Screener123
- [ ] Click "Login"
- [ ] Should redirect to dashboard
- [ ] User name should appear in header
- [ ] Token should be stored in localStorage

#### Test Failed Login
- [ ] Try wrong password 3 times
- [ ] Should see error messages
- [ ] Should see remaining attempts
- [ ] Should not be redirected

#### Test Logout
- [ ] Click logout button
- [ ] Should redirect to login page
- [ ] Token should be removed from localStorage
- [ ] Cannot access protected pages

### 6. Security Verification

#### Password Security
- [ ] Passwords are hashed in database (check with SQL query)
- [ ] Same password produces different hashes
- [ ] Old passwords cannot be used to login after change

#### Token Security
- [ ] Access tokens expire after 15 minutes
- [ ] Expired tokens are rejected
- [ ] Refresh tokens work correctly
- [ ] Logout invalidates tokens

#### Rate Limiting
- [ ] 5 failed attempts locks account
- [ ] Lockout lasts 5 minutes
- [ ] Successful login resets counter
- [ ] Different usernames have independent limits

#### Input Sanitization
- [ ] SQL injection attempts fail
- [ ] XSS attempts fail
- [ ] Special characters in username/password work
- [ ] Unicode characters work

### 7. Role-Based Access

#### Screener Role
- [ ] Can login with screener@kamco.com / Screener123
- [ ] Can access screener-only pages
- [ ] Cannot access checker/finalizer pages

#### Checker Role
- [ ] Can login with checker@kamco.com / Checker123
- [ ] Can access checker-only pages
- [ ] Cannot access screener/finalizer-only pages

#### Finalizer Role
- [ ] Can login with finalizer@kamco.com / Finalizer123
- [ ] Can access finalizer-only pages
- [ ] Cannot access screener/checker-only pages

### 8. Audit Logging

#### Check Logs
```bash
# View security logs
tail -f backend/logs/security.log

# Should show:
# - Login attempts (success and failure)
# - Logout events
# - Token operations
# - Rate limit violations
# - IP addresses
```

### 9. Error Handling

#### Test Error Messages
- [ ] Wrong username: "Incorrect username or password"
- [ ] Wrong password: "Incorrect username or password" + remaining attempts
- [ ] Inactive account: "User account is inactive"
- [ ] Rate limited: "Too many failed attempts. Account locked for X seconds"
- [ ] Invalid token: "Could not validate credentials"
- [ ] Expired token: "Token has expired"

### 10. Performance

#### Load Test
```bash
# Simulate 100 concurrent logins
for i in {1..100}; do
  curl -X POST http://127.0.0.1:8000/api/auth/login \
    -d '{"username": "screener_test", "password": "Screener123"}' &
done
wait

# All should succeed without errors
```

## 📊 Test Results

### Expected Metrics
- ✅ **Test Pass Rate**: 100% (66/66 tests)
- ✅ **Code Coverage**: ~90% of auth code
- ✅ **Response Time**: <100ms for login
- ✅ **Security Score**: A+ (no vulnerabilities)

### Performance Benchmarks
- Login endpoint: <100ms average
- Token validation: <10ms average
- Password hashing: ~200ms (bcrypt is intentionally slow)
- Database query: <50ms average

## 🐛 Troubleshooting

### Issue: Tests fail with "Module not found"
**Solution**: 
```bash
pip install pytest pytest-asyncio httpx
```

### Issue: "No users in database"
**Solution**:
```bash
python3 seed_database.py
```

### Issue: Server not responding
**Solution**:
```bash
# Check if server is running
curl http://127.0.0.1:8000/health

# Start server if needed
python3 main.py
```

### Issue: 401 error even with correct credentials
**Solution**:
```bash
# Run debug script
python3 debug_login.py

# Re-seed database if needed
python3 seed_database.py
```

### Issue: Rate limiting not working
**Solution**:
```bash
# Restart server to reset rate limiter
# Or wait 5 minutes for lockout to expire
```

## ✅ Sign-Off

### Before Production Deployment

- [ ] All automated tests pass
- [ ] All manual tests pass
- [ ] Browser tests work
- [ ] Security verification complete
- [ ] Audit logging works
- [ ] Error handling tested
- [ ] Performance acceptable
- [ ] Documentation complete
- [ ] CI/CD pipeline configured

### Approval

**Tested by**: ___________________
**Date**: ___________________
**Status**: ___________________
**Notes**: ___________________

---

**Last Updated**: January 12, 2026
**Test Suite Version**: 1.0
**System**: Kamco Fraud Detection - Authentication Module
