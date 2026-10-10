from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers.analyze import router as analyze_router

app = FastAPI(
    title="AI Resume Analyzer API",
    description="API for matching resumes with job descriptions",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://resume-analyzer-eta-nine.vercel.app",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)


@app.get("/")
def root():
    return {"message": "AI Resume Analyzer API is running"}


@app.get("/api/health")
def health_check():
    return {"status": "ok"}


app.include_router(analyze_router)