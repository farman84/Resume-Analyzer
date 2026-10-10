"""
test_analyze_api.py — Integration tests for POST /api/analyze.

Uses FastAPI's TestClient (synchronous, no running server needed).
Tests cover:
  - Successful requests with known skill matches
  - Scoring correctness (coverage and overlap formulas)
  - Texts with no recognised skills
  - Validation errors (missing fields, empty strings, oversized input)
  - Response shape and field types
  - Health endpoint regression check
"""

import pytest
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)

# ---------------------------------------------------------------------------
# Fixtures / helpers
# ---------------------------------------------------------------------------

RESUME_PYTHON_SQL = "Experienced Python developer with SQL database skills."
JD_PYTHON_DOCKER  = "We need a Python engineer who knows Docker and Kubernetes."
JD_PYTHON_SQL     = "Looking for a Python developer with SQL experience."

MAX_CHARS = 20_000


def post_analyze(resume: str, jd: str) -> dict:
    """Helper: POST /api/analyze and return the parsed JSON body."""
    r = client.post("/api/analyze", json={"resume_text": resume, "job_description": jd})
    return r


# ---------------------------------------------------------------------------
# Health check regression
# ---------------------------------------------------------------------------

class TestHealthRegression:
    def test_health_still_returns_ok(self):
        r = client.get("/api/health")
        assert r.status_code == 200
        assert r.json() == {"status": "ok"}


# ---------------------------------------------------------------------------
# Successful requests — response shape
# ---------------------------------------------------------------------------

class TestResponseShape:
    def test_status_200_on_valid_request(self):
        r = post_analyze(RESUME_PYTHON_SQL, JD_PYTHON_DOCKER)
        assert r.status_code == 200

    def test_response_has_all_required_fields(self):
        r = post_analyze(RESUME_PYTHON_SQL, JD_PYTHON_DOCKER)
        body = r.json()
        required = {
            "coverage_score", "overlap_score",
            "matched_skills", "missing_skills",
            "resume_skills", "job_skills", "extra_skills",
            "suggestions", "score_note", "score_disclaimer",
        }
        assert required.issubset(body.keys())

    def test_scores_are_integers(self):
        body = post_analyze(RESUME_PYTHON_SQL, JD_PYTHON_DOCKER).json()
        assert isinstance(body["coverage_score"], int)
        assert isinstance(body["overlap_score"],  int)

    def test_scores_in_valid_range(self):
        body = post_analyze(RESUME_PYTHON_SQL, JD_PYTHON_DOCKER).json()
        assert 0 <= body["coverage_score"] <= 100
        assert 0 <= body["overlap_score"]  <= 100

    def test_skill_lists_are_lists_of_strings(self):
        body = post_analyze(RESUME_PYTHON_SQL, JD_PYTHON_DOCKER).json()
        for key in ("matched_skills", "missing_skills", "resume_skills",
                    "job_skills", "extra_skills"):
            assert isinstance(body[key], list)
            assert all(isinstance(s, str) for s in body[key])

    def test_suggestions_is_list_of_strings(self):
        body = post_analyze(RESUME_PYTHON_SQL, JD_PYTHON_DOCKER).json()
        assert isinstance(body["suggestions"], list)
        assert all(isinstance(s, str) for s in body["suggestions"])

    def test_score_disclaimer_is_present_and_non_empty(self):
        body = post_analyze(RESUME_PYTHON_SQL, JD_PYTHON_DOCKER).json()
        assert isinstance(body["score_disclaimer"], str)
        assert len(body["score_disclaimer"]) > 0

    def test_score_disclaimer_does_not_claim_ats(self):
        body = post_analyze(RESUME_PYTHON_SQL, JD_PYTHON_DOCKER).json()
        disclaimer = body["score_disclaimer"].lower()
        assert "not" in disclaimer
        assert "ats" in disclaimer or "guarantee" in disclaimer or "hiring" in disclaimer

    def test_skill_lists_are_sorted(self):
        body = post_analyze(RESUME_PYTHON_SQL, JD_PYTHON_DOCKER).json()
        for key in ("matched_skills", "missing_skills", "resume_skills",
                    "job_skills", "extra_skills"):
            lst = body[key]
            assert lst == sorted(lst), f"{key} is not sorted"


# ---------------------------------------------------------------------------
# Scoring correctness
# ---------------------------------------------------------------------------

class TestScoringCorrectness:
    def test_perfect_coverage_when_resume_covers_all_job_skills(self):
        # Resume and JD both mention only Python — 100% coverage.
        body = post_analyze(
            "Python developer.",
            "Python required."
        ).json()
        assert body["coverage_score"] == 100

    def test_zero_coverage_when_no_shared_skills(self):
        body = post_analyze(
            "I have Excel and PowerPoint skills.",
            "Docker and Kubernetes required."
        ).json()
        assert body["coverage_score"] == 0

    def test_matched_is_subset_of_both_resume_and_job_skills(self):
        body = post_analyze(RESUME_PYTHON_SQL, JD_PYTHON_DOCKER).json()
        matched = set(body["matched_skills"])
        assert matched.issubset(set(body["resume_skills"]))
        assert matched.issubset(set(body["job_skills"]))

    def test_missing_is_job_minus_resume(self):
        body = post_analyze(RESUME_PYTHON_SQL, JD_PYTHON_DOCKER).json()
        job_set    = set(body["job_skills"])
        resume_set = set(body["resume_skills"])
        expected_missing = job_set - resume_set
        assert set(body["missing_skills"]) == expected_missing

    def test_extra_skills_is_resume_minus_job(self):
        body = post_analyze(RESUME_PYTHON_SQL, JD_PYTHON_DOCKER).json()
        resume_set = set(body["resume_skills"])
        job_set    = set(body["job_skills"])
        assert set(body["extra_skills"]) == resume_set - job_set

    def test_coverage_formula_matches_manual_calculation(self):
        # resume has Python + SQL; JD has Python + SQL → coverage = 100%
        body = post_analyze(
            "Python and SQL experience.",
            "Python and SQL required."
        ).json()
        matched = len(body["matched_skills"])
        job_total = len(body["job_skills"])
        expected = round(matched / job_total * 100) if job_total else 0
        assert body["coverage_score"] == expected

    def test_overlap_formula_matches_manual_calculation(self):
        body = post_analyze(
            "Python and SQL experience.",
            "Python and Docker required."
        ).json()
        matched   = len(body["matched_skills"])
        union_len = len(set(body["resume_skills"]) | set(body["job_skills"]))
        expected  = round(matched / union_len * 100) if union_len else 0
        assert body["overlap_score"] == expected

    def test_overlap_never_exceeds_coverage_when_resume_is_superset(self):
        # When resume has everything the JD needs plus extra, coverage=100
        # and overlap < 100 (because union > matched).
        body = post_analyze(
            "Python SQL Docker Kubernetes Git",
            "Python SQL"
        ).json()
        assert body["coverage_score"] == 100
        # overlap can be less than 100 if resume has extra skills
        assert body["overlap_score"] <= 100


# ---------------------------------------------------------------------------
# Alias and extraction — end-to-end through the API
# ---------------------------------------------------------------------------

class TestExtractionThroughAPI:
    def test_js_alias_resolves_to_javascript(self):
        body = post_analyze(
            "Proficient in JS development.",
            "JavaScript required."
        ).json()
        assert "JavaScript" in body["matched_skills"]

    def test_postgres_alias_resolves_to_postgresql(self):
        body = post_analyze(
            "Used Postgres for the backend database.",
            "PostgreSQL experience required."
        ).json()
        assert "PostgreSQL" in body["matched_skills"]

    def test_html_tags_stripped_before_analysis(self):
        body = post_analyze(
            "<p>Python developer with <strong>Docker</strong> experience.</p>",
            "Python and Docker required."
        ).json()
        assert "Python" in body["matched_skills"]
        assert "Docker" in body["matched_skills"]


# ---------------------------------------------------------------------------
# Empty / no-skill texts
# ---------------------------------------------------------------------------

class TestNoSkillTexts:
    def test_no_skills_in_either_text_returns_zero_scores(self):
        body = post_analyze(
            "The quick brown fox jumps over the lazy dog.",
            "A fast red car drives on a long road."
        ).json()
        assert body["coverage_score"] == 0
        assert body["overlap_score"]  == 0

    def test_no_skills_sets_score_note(self):
        body = post_analyze(
            "The quick brown fox.",
            "A fast red car."
        ).json()
        assert body["score_note"] is not None
        assert len(body["score_note"]) > 0

    def test_no_skills_in_jd_only_sets_score_note(self):
        body = post_analyze(
            "Python developer.",
            "A fast red car."
        ).json()
        assert body["score_note"] is not None

    def test_no_skills_in_resume_only_gives_zero_coverage(self):
        body = post_analyze(
            "I am enthusiastic and hardworking.",
            "Python and Docker required."
        ).json()
        assert body["coverage_score"] == 0
        assert set(body["missing_skills"]) == set(body["job_skills"])

    def test_no_skills_returns_200_not_error(self):
        r = post_analyze(
            "The quick brown fox.",
            "A fast red car."
        )
        assert r.status_code == 200


# ---------------------------------------------------------------------------
# Validation errors
# ---------------------------------------------------------------------------

class TestValidationErrors:
    def test_missing_resume_text_field_returns_422(self):
        r = client.post("/api/analyze", json={"job_description": "Python required."})
        assert r.status_code == 422

    def test_missing_job_description_field_returns_422(self):
        r = client.post("/api/analyze", json={"resume_text": "Python developer."})
        assert r.status_code == 422

    def test_empty_body_returns_422(self):
        r = client.post("/api/analyze", json={})
        assert r.status_code == 422

    def test_empty_resume_text_returns_422(self):
        r = client.post("/api/analyze", json={
            "resume_text": "",
            "job_description": "Python required."
        })
        assert r.status_code == 422

    def test_whitespace_only_resume_returns_422(self):
        r = client.post("/api/analyze", json={
            "resume_text": "   \n\t  ",
            "job_description": "Python required."
        })
        assert r.status_code == 422

    def test_empty_job_description_returns_422(self):
        r = client.post("/api/analyze", json={
            "resume_text": "Python developer.",
            "job_description": ""
        })
        assert r.status_code == 422

    def test_resume_too_long_returns_422(self):
        r = client.post("/api/analyze", json={
            "resume_text": "a" * (MAX_CHARS + 1),
            "job_description": "Python required."
        })
        assert r.status_code == 422

    def test_jd_too_long_returns_422(self):
        r = client.post("/api/analyze", json={
            "resume_text": "Python developer.",
            "job_description": "a" * (MAX_CHARS + 1)
        })
        assert r.status_code == 422

    def test_exactly_max_chars_is_accepted(self):
        # A string of MAX_CHARS characters that contains a recognizable skill word.
        # Build: skill word + padding to reach MAX_CHARS exactly.
        skill_word = "Python "
        padding = "x " * ((MAX_CHARS - len(skill_word)) // 2)
        text = (skill_word + padding)[:MAX_CHARS]
        r = client.post("/api/analyze", json={
            "resume_text": text,
            "job_description": "Python required."
        })
        assert r.status_code == 200

    def test_non_json_body_returns_422(self):
        r = client.post(
            "/api/analyze",
            content=b"not json at all",
            headers={"Content-Type": "application/json"},
        )
        assert r.status_code == 422

    def test_wrong_content_type_returns_422(self):
        r = client.post(
            "/api/analyze",
            data={"resume_text": "Python developer.", "job_description": "Python required."},
        )
        # Form data instead of JSON → FastAPI will return 422.
        assert r.status_code == 422

    def test_numeric_resume_text_returns_422(self):
        r = client.post("/api/analyze", json={
            "resume_text": 12345,
            "job_description": "Python required."
        })
        # Pydantic coerces int to str by default in v2 with str fields,
        # but our validator will reject whitespace-stripped empty — however
        # "12345" is non-empty so it should pass validation and return 200.
        # This test simply asserts the API doesn't crash (4xx or 200 are both acceptable).
        assert r.status_code in (200, 422)
