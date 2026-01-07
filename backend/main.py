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
from routes import scan, review, auth, checker, finalizer, upload

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

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(upload.router, prefix="/api/upload", tags=["Upload"])
app.include_router(scan.router, prefix="/api/scan", tags=["Scan"])
app.include_router(review.router, prefix="/api/review", tags=["Review"])
app.include_router(checker.router, prefix="/api/review/checker", tags=["Checker"])
app.include_router(finalizer.router, prefix="/api/review/finalizer", tags=["Finalizer"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
