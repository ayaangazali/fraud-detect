# Environment Setup Guide

## ⚠️ IMPORTANT: Never commit `.env` files to git!

The `.env` file contains sensitive information like API keys, database credentials, and secret keys. It should NEVER be committed to version control.

## Setup Instructions

### Backend Environment

1. **Copy the example file:**
   ```bash
   cd backend
   cp .env.example .env
   ```

2. **Edit `.env` and update the values:**
   ```bash
   nano .env  # or use your preferred editor
   ```

3. **Required variables:**
   - `SECRET_KEY` - Generate a secure random key (minimum 32 characters)
   - `DATABASE_URL` - Path to your SQLite database
   - `FRONTEND_URL` - URL where your frontend is running

4. **Optional variables:**
   - `SMTP_*` - Email configuration (for notifications)
   - `ACCESS_TOKEN_EXPIRE_MINUTES` - JWT token expiration
   - `REFRESH_TOKEN_EXPIRE_DAYS` - Refresh token expiration

### Generate a Secure Secret Key

```bash
# Using Python
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# Using OpenSSL
openssl rand -base64 32
```

### Production Deployment

For production environments:

1. **Never use the example values**
2. **Use strong, unique secret keys**
3. **Use environment variables or secrets management**
4. **Enable HTTPS**
5. **Use a proper database (PostgreSQL recommended)**

### Vercel Deployment

Add environment variables in Vercel dashboard:
1. Go to your project settings
2. Navigate to "Environment Variables"
3. Add each variable from `.env.example`
4. Set appropriate values for production

### What's Protected

The `.gitignore` file prevents these from being committed:
- `.env`
- `.env.*` (all variants)
- `backend/.env`
- `frontend/.env`
- Database files (`*.db`, `*.sqlite`)
- Python cache files (`__pycache__`, `*.pyc`)
- Node modules
- Build outputs

### Verification

Check that `.env` is not tracked:
```bash
git ls-files | grep .env
# Should return nothing (exit code 1)
```

Check git status:
```bash
git status
# .env should NOT appear in the list
```

---

✅ **Current Status**: `.env` files are properly ignored and NOT tracked by git.
