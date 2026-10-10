"""
matcher.py — Match scoring for the AI Resume Analyzer.

Given two sets of canonical skill names (resume skills and job skills),
computes:

  coverage_score  = matched / job_skills  * 100
    "What percentage of this job's required skills appear in my resume?"

  overlap_score   = matched / union * 100
    "What percentage of all skills mentioned across both documents do I share?"

Both scores are integers in the range [0, 100].

Returns a MatchResult dataclass with all relevant sets and scores.
No external dependencies.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import FrozenSet


@dataclass(frozen=True)
class MatchResult:
    """All computed matching data for one analysis request."""

    # Input skill sets (canonical names, lowercase-normalised keys).
    resume_skills: FrozenSet[str]
    job_skills: FrozenSet[str]

    # Derived sets.
    matched_skills: FrozenSet[str]   = field(init=False)
    missing_skills: FrozenSet[str]   = field(init=False)
    extra_skills:   FrozenSet[str]   = field(init=False)  # resume-only, not shown to user

    # Scores (0–100 integers).
    coverage_score: int = field(init=False)
    overlap_score:  int = field(init=False)

    # Optional explanatory note (populated when skills lists are empty).
    score_note: str | None = field(init=False)

    def __post_init__(self) -> None:
        matched = self.resume_skills & self.job_skills
        missing = self.job_skills - self.resume_skills
        extra   = self.resume_skills - self.job_skills
        union   = self.resume_skills | self.job_skills

        # Use object.__setattr__ because the dataclass is frozen.
        object.__setattr__(self, "matched_skills", frozenset(matched))
        object.__setattr__(self, "missing_skills",  frozenset(missing))
        object.__setattr__(self, "extra_skills",    frozenset(extra))

        # Coverage score: matched / job skills.
        if self.job_skills:
            cov = round(len(matched) / len(self.job_skills) * 100)
        else:
            cov = 0

        # Overlap score: matched / union.
        if union:
            ovl = round(len(matched) / len(union) * 100)
        else:
            ovl = 0

        object.__setattr__(self, "coverage_score", max(0, min(100, cov)))
        object.__setattr__(self, "overlap_score",  max(0, min(100, ovl)))

        # Determine any explanatory note.
        if not union:
            note = (
                "No recognised skills were found in either text. "
                "Try adding more specific skill names to your resume and job description."
            )
        elif not self.job_skills:
            note = (
                "No recognised skills were found in the job description. "
                "Coverage score cannot be calculated."
            )
        else:
            note = None

        object.__setattr__(self, "score_note", note)


def compute_match(
    resume_skills: FrozenSet[str],
    job_skills: FrozenSet[str],
) -> MatchResult:
    """Compute matching scores between *resume_skills* and *job_skills*.

    Args:
        resume_skills: Frozenset of canonical skill names from the resume.
        job_skills:    Frozenset of canonical skill names from the job description.

    Returns:
        A :class:`MatchResult` with scores, matched/missing/extra sets, and
        an optional ``score_note`` for edge cases.
    """
    return MatchResult(
        resume_skills=frozenset(resume_skills),
        job_skills=frozenset(job_skills),
    )
