"""
test_matcher.py — Unit tests for services/matcher.py
"""

import pytest
from services.matcher import compute_match, MatchResult


class TestMatchedAndMissingSkills:
    def test_matched_is_intersection(self):
        resume   = frozenset({"Python", "SQL", "Docker"})
        job      = frozenset({"Python", "SQL", "Kubernetes"})
        result   = compute_match(resume, job)
        assert result.matched_skills == {"Python", "SQL"}

    def test_missing_is_job_minus_resume(self):
        resume   = frozenset({"Python", "SQL"})
        job      = frozenset({"Python", "SQL", "Docker"})
        result   = compute_match(resume, job)
        assert result.missing_skills == {"Docker"}

    def test_extra_skills_is_resume_minus_job(self):
        resume   = frozenset({"Python", "SQL", "Excel"})
        job      = frozenset({"Python", "SQL"})
        result   = compute_match(resume, job)
        assert result.extra_skills == {"Excel"}

    def test_no_overlap(self):
        resume   = frozenset({"Excel", "PowerPoint"})
        job      = frozenset({"Docker", "Kubernetes"})
        result   = compute_match(resume, job)
        assert result.matched_skills == frozenset()
        assert result.missing_skills == {"Docker", "Kubernetes"}

    def test_full_overlap(self):
        skills   = frozenset({"Python", "SQL", "Docker"})
        result   = compute_match(skills, skills)
        assert result.matched_skills == skills
        assert result.missing_skills == frozenset()
        assert result.extra_skills   == frozenset()


class TestCoverageScore:
    def test_full_coverage_is_100(self):
        skills   = frozenset({"Python", "SQL", "Docker"})
        result   = compute_match(skills, skills)
        assert result.coverage_score == 100

    def test_zero_coverage_no_overlap(self):
        resume   = frozenset({"Excel"})
        job      = frozenset({"Docker", "Kubernetes"})
        result   = compute_match(resume, job)
        assert result.coverage_score == 0

    def test_coverage_two_of_three(self):
        resume   = frozenset({"Python", "SQL"})
        job      = frozenset({"Python", "SQL", "Docker"})
        result   = compute_match(resume, job)
        assert result.coverage_score == 67  # round(2/3 * 100)

    def test_coverage_one_of_four(self):
        resume   = frozenset({"Python"})
        job      = frozenset({"Python", "SQL", "Docker", "Kubernetes"})
        result   = compute_match(resume, job)
        assert result.coverage_score == 25  # round(1/4 * 100)

    def test_coverage_score_is_integer(self):
        resume   = frozenset({"Python", "SQL"})
        job      = frozenset({"Python", "SQL", "Docker"})
        result   = compute_match(resume, job)
        assert isinstance(result.coverage_score, int)

    def test_coverage_clamped_to_100(self):
        # With correct logic this should never exceed 100, but verify clamping.
        skills   = frozenset({"Python"})
        result   = compute_match(skills, skills)
        assert result.coverage_score <= 100

    def test_coverage_zero_when_job_skills_empty(self):
        resume   = frozenset({"Python", "SQL"})
        result   = compute_match(resume, frozenset())
        assert result.coverage_score == 0


class TestOverlapScore:
    def test_full_overlap_is_100(self):
        skills   = frozenset({"Python", "SQL"})
        result   = compute_match(skills, skills)
        assert result.overlap_score == 100

    def test_zero_overlap_no_shared_skills(self):
        resume   = frozenset({"Excel"})
        job      = frozenset({"Docker"})
        result   = compute_match(resume, job)
        assert result.overlap_score == 0  # matched=0, union=2 → 0%

    def test_overlap_two_matched_union_four(self):
        # resume={A,B,C}, job={A,B,D} → matched=2, union=4 → 50%
        resume   = frozenset({"Python", "SQL", "Excel"})
        job      = frozenset({"Python", "SQL", "Docker"})
        result   = compute_match(resume, job)
        assert result.overlap_score == 50  # 2/4

    def test_overlap_one_matched_union_four(self):
        resume   = frozenset({"Python", "Excel"})
        job      = frozenset({"Python", "Docker"})
        result   = compute_match(resume, job)
        assert result.overlap_score == 33  # round(1/3 * 100) -- union=3

    def test_overlap_score_is_integer(self):
        resume   = frozenset({"Python"})
        job      = frozenset({"Python", "Docker"})
        result   = compute_match(resume, job)
        assert isinstance(result.overlap_score, int)

    def test_overlap_zero_when_both_empty(self):
        result   = compute_match(frozenset(), frozenset())
        assert result.overlap_score == 0


class TestEdgeCases:
    def test_both_empty_sets(self):
        result = compute_match(frozenset(), frozenset())
        assert result.coverage_score == 0
        assert result.overlap_score  == 0
        assert result.matched_skills == frozenset()
        assert result.missing_skills == frozenset()
        assert result.score_note is not None

    def test_empty_resume(self):
        job    = frozenset({"Python", "Docker"})
        result = compute_match(frozenset(), job)
        assert result.coverage_score == 0
        assert result.missing_skills == job

    def test_empty_job(self):
        resume = frozenset({"Python", "Docker"})
        result = compute_match(resume, frozenset())
        assert result.coverage_score == 0
        assert result.extra_skills == resume
        assert result.score_note is not None

    def test_score_note_none_when_skills_present(self):
        resume = frozenset({"Python"})
        job    = frozenset({"Python", "Docker"})
        result = compute_match(resume, job)
        assert result.score_note is None

    def test_returns_matchresult_instance(self):
        result = compute_match(frozenset({"Python"}), frozenset({"Python"}))
        assert isinstance(result, MatchResult)

    def test_input_sets_preserved(self):
        resume = frozenset({"Python", "SQL"})
        job    = frozenset({"Python", "Docker"})
        result = compute_match(resume, job)
        assert result.resume_skills == resume
        assert result.job_skills    == job

    def test_duplicate_skills_handled_via_frozenset(self):
        # frozenset naturally deduplicates; passing a list would fail type check,
        # but we test that the function accepts frozensets correctly.
        result = compute_match(frozenset({"Python"}), frozenset({"Python"}))
        assert result.coverage_score == 100
