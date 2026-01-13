"""
Kamco Compliance Screening - FastAPI Backend
Main application entry point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Import routes
from routes import scan, review, auth, checker, finalizer, upload, screening, reports, audit, review_manager, users, kamco_upload

# Import audit middleware
from middleware.audit_middleware import setup_audit_middleware

# Initialize FastAPI app
app = FastAPI(
    title="Kamco Compliance Screening API",
    description="Backend API for compliance screening with multi-sheet Excel parsing and fuzzy matching",
    version="1.0.0"
)

# CORS configuration
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup audit middleware (must be after CORS)
setup_audit_middleware(app)

# Health check endpoint
@app.get("/")
async def root():
    return {
        "status": "healthy",
        "message": "Kamco Compliance Screening API",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.get("/api")
async def api_root():
    """API root endpoint"""
    return {
        "status": "ok",
        "message": "Kamco Compliance API",
        "version": "1.0.0",
        "endpoints": {
            "auth": "/api/auth",
            "upload": "/api/upload",
            "screening": "/api/screening",
            "review": "/api/review",
            "reports": "/api/reports",
            "audit": "/api/audit"
        }
    }

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/users", tags=["User Management"])
app.include_router(kamco_upload.router, prefix="/api/upload", tags=["Kamco Entities Upload"])
app.include_router(upload.router, prefix="/api/upload", tags=["Upload"])
app.include_router(scan.router, prefix="/api/scan", tags=["Scan"])
app.include_router(review.router, prefix="/api/review", tags=["Review"])
app.include_router(review_manager.router, prefix="/api/reviews", tags=["Review Manager"])
app.include_router(checker.router, prefix="/api/review/checker", tags=["Checker"])
app.include_router(finalizer.router, prefix="/api/review/finalizer", tags=["Finalizer"])
app.include_router(screening.router, prefix="/api/screening", tags=["Screening"])
app.include_router(reports.router, prefix="/api/reports", tags=["Reports"])
app.include_router(audit.router, prefix="/api/audit", tags=["Audit Logs"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
1