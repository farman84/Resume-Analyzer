from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from analyzer import analyze_resume

app = FastAPI(
    title="AI Resume Analyzer API",
    description="API for matching resumes with job descriptions",
    version="1.0.0",
)

# Allow requests from the deployed Vercel frontend and local development.
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


class AnalyzeRequest(BaseModel):
    resume_text: str = Field(min_length=1, max_length=20000)
    job_description: str = Field(min_length=1, max_length=20000)


@app.get("/")
def root():
    return {"message": "AI Resume Analyzer API is running"}


@app.get("/api/health")
def health_check():
    return {"status": "ok"}


@app.post("/api/analyze")
def analyze(request: AnalyzeRequest):
    return analyze_resume(
        request.resume_text,
        request.job_description,
    )
