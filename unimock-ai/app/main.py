import sys
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Ensure UTF-8 output encoding for Windows PowerShell
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from app.routers.resume import router as resume_router
from app.routers.interview import router as interview_router
from app.routers.records import router as records_router
from app.routers.reports import router as reports_router

app = FastAPI(
    title="UniMock AI Backend Service",
    description="Backend API Service for High School & College Second-Stage Mock Interview Platform powered by Gemma-4-31B-it and RAG.",
    version="1.0.0"
)

# Configure CORS Middleware for Frontend React App
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows React Vite frontend at http://localhost:5173
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(resume_router)
app.include_router(interview_router)
app.include_router(records_router)
app.include_router(reports_router)

@app.get("/api/health")
async def health_check():
    return {
        "status": "online",
        "service": "UniMock AI Engine Backend",
        "model": "models/gemma-4-31b-it",
        "embedding_model": "models/gemini-embedding-2"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
