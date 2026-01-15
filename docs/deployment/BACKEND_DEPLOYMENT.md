# Backend Deployment Guide

## Quick Deploy Options

### Option 1: Railway (Recommended - Easiest)

Railway is the easiest way to deploy Python backends.

1. **Install Railway CLI** (optional):
   ```bash
   npm install -g @railway/cli
   ```

2. **Deploy via GitHub**:
   - Go to [railway.app](https://railway.app)
   - Sign in with GitHub
   - Click "New Project" → "Deploy from GitHub repo"
   - Select your `fraud-detect` repository
   - Railway will auto-detect Python and deploy

3. **Configure Environment Variables**:
   In Railway dashboard, add these variables:
   ```
   SECRET_KEY=<generate-new-secret-key>
   DATABASE_URL=sqlite:///./database/kamco.db
   FRONTEND_URL=https://your-vercel-app.vercel.app
   ACCESS_TOKEN_EXPIRE_MINUTES=15
   REFRESH_TOKEN_EXPIRE_DAYS=7
   ```

4. **Set Build Settings**:
   - Root Directory: `/backend`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

5. **Get Your Backend URL**:
   - Railway provides: `https://your-app.railway.app`
   - Copy this URL

### Option 2: Render

1. Go to [render.com](https://render.com)
2. Sign in and click "New +" → "Web Service"
3. Connect your GitHub repo
4. Configure:
   - **Name**: kamco-backend
   - **Root Directory**: `backend`
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables (same as Railway)
6. Deploy

### Option 3: Heroku

1. Install Heroku CLI:
   ```bash
   brew install heroku/brew/heroku
   ```

2. Login and create app:
   ```bash
   heroku login
   heroku create kamco-backend
   ```

3. Deploy:
   ```bash
   cd backend
   git subtree push --prefix backend heroku main
   ```

## Update Frontend

After deploying backend, update Vercel environment variables:

1. Go to Vercel Dashboard → Your Project → Settings → Environment Variables
2. Add:
   ```
   VITE_API_URL=https://your-backend-url.railway.app/api
   ```
3. Redeploy frontend

## Configure CORS

Make sure your backend allows requests from Vercel. In `backend/main.py`, update CORS:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "https://your-vercel-app.vercel.app"  # Add your Vercel URL
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Database Considerations

**Current**: SQLite (file-based)
- ✅ Easy for development
- ❌ Not ideal for production (Railway/Render may reset filesystem)

**Recommended for Production**: PostgreSQL
- Railway/Render offer free PostgreSQL databases
- Update `DATABASE_URL` to PostgreSQL connection string

## Verification

1. Test backend directly:
   ```bash
   curl https://your-backend-url.railway.app/health
   ```

2. Test from frontend:
   - Login page should work
   - No more 404 errors

## Troubleshooting

### Backend not starting
- Check Railway/Render logs
- Verify all environment variables are set
- Check that `requirements.txt` includes all dependencies

### CORS errors
- Add your Vercel URL to `allow_origins` in `main.py`
- Redeploy backend

### 404 errors persist
- Verify `VITE_API_URL` in Vercel environment variables
- Redeploy frontend after setting env var

## Cost

- **Railway**: $5/month for hobby plan (includes 500 hours)
- **Render**: Free tier available (spins down after inactivity)
- **Heroku**: Free tier available (similar limitations)

## Next Steps

1. Deploy backend to Railway/Render
2. Get backend URL
3. Add `VITE_API_URL` to Vercel environment variables
4. Redeploy frontend
5. Test the application

---

**Status**: Choose your deployment platform and follow the steps above.
