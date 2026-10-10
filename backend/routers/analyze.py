"""
routers/analyze.py — POST /api/analyze endpoint for the AI Resume Analyzer.

Request  → AnalyzeRequest  (resume_text, job_description)
Response ← AnalyzeResponse (scores, skill sets, suggestions, disclaimer)

The handler delegates all analysis work to the Phase 2 service modules:
  services.skill_extractor  →  extract_skills()
  services.matcher          →  compute_match()
  services.suggester        →  generate_suggestions()

No analysis logic lives here — this module is pure FastAPI plumbing.
"""

from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel, field_validator

from services.skill_extractor import extract_skills
from services.matcher import compute_match
from services.suggester import generate_suggestions


router = APIRouter(prefix="/api", tags=["analyze"])

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_MAX_CHARS = 20_000
_SCORE_DISCLAIMER = (
    "These scores reflect keyword overlap between your resume and the job "
    "description. They are not ATS scores or measures of hiring probability."
)


# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------

class AnalyzeRequest(BaseModel):
    """Validated request body for the analyze endpoint."""

    resume_text: str
    job_description: str

    @field_validator("resume_text", "job_description")
    @classmethod
    def must_be_non_empty_and_within_limit(cls, value: str, info) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError(f"{info.field_name} must not be empty or whitespace.")
        if len(value) > _MAX_CHARS:
            raise ValueError(
                f"{info.field_name} must be at most {_MAX_CHARS:,} characters "
                f"(received {len(value):,})."
            )
        return value


class AnalyzeResponse(BaseModel):
    """JSON response body returned by the analyze endpoint."""

    coverage_score: int
    overlap_score: int
    matched_skills: list[str]
    missing_skills: list[str]
    resume_skills: list[str]
    job_skills: list[str]
    extra_skills: list[str]
    suggestions: list[str]
    score_note: str | None
    score_disclaimer: str


# ---------------------------------------------------------------------------
# Route handler
# ---------------------------------------------------------------------------

@router.post(
    "/analyze",
    response_model=AnalyzeResponse,
    summary="Analyze resume against a job description",
    description=(
        "Extracts skills from both texts, computes a keyword match score, "
        "and returns matched skills, missing skills, and improvement suggestions. "
        "Scores are keyword-overlap metrics — not ATS scores or hiring guarantees."
    ),
)
def analyze(request: AnalyzeRequest) -> AnalyzeResponse:
    """Run the full analysis pipeline and return results."""

    # Step 1 — extract skills from each text.
    resume_skills = extract_skills(request.resume_text)
    job_skills    = extract_skills(request.job_description)

    # Step 2 — compute scores and derived sets.
    match = compute_match(resume_skills, job_skills)

    # Step 3 — generate suggestions.
    suggestions = generate_suggestions(match.missing_skills, match.coverage_score)

    # Step 4 — build the response.
    # Skill lists are sorted for deterministic, readable output.
    return AnalyzeResponse(
        coverage_score  = match.coverage_score,
        overlap_score   = match.overlap_score,
        matched_skills  = sorted(match.matched_skills),
        missing_skills  = sorted(match.missing_skills),
        resume_skills   = sorted(match.resume_skills),
        job_skills      = sorted(match.job_skills),
        extra_skills    = sorted(match.extra_skills),
        suggestions     = suggestions,
        score_note      = match.score_note,
        score_disclaimer= _SCORE_DISCLAIMER,
    )
