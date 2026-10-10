"""
AI Resume Analyzer — FastAPI application entry point.

Registered routes:
  GET  /api/health    — liveness check (Phase 1)
  POST /api/analyze   — resume analysis (Phase 3)
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers.analyze import router as analyze_router

app = FastAPI(
    title="AI Resume Analyzer API",
    version="0.3.0",
    description="Analyze resume and job-description text to surface matched and missing skills.",
)

# Allow the Vite dev server to call the API during local development.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

app.include_router(analyze_router)


@app.get("/api/health", tags=["health"])
def health_check():
    """Confirm the API is running."""
    return {"status": "ok"}
