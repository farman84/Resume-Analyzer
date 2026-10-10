"""
test_suggester.py — Unit tests for services/suggester.py
"""

import pytest
from services.suggester import generate_suggestions, MAX_SUGGESTIONS, HIGH_SCORE_THRESHOLD


class TestBasicSuggestions:
    def test_missing_single_skill_produces_suggestion(self):
        suggestions = generate_suggestions(frozenset({"Docker"}), coverage_score=50)
        assert len(suggestions) >= 1
        assert any("Docker" in s for s in suggestions)

    def test_missing_skill_suggestion_mentions_skill_name(self):
        suggestions = generate_suggestions(frozenset({"Kubernetes"}), coverage_score=40)
        assert any("Kubernetes" in s for s in suggestions)

    def test_empty_missing_skills_no_skill_suggestions(self):
        # score < 80 and no missing skills → no suggestions (score note not added
        # because score is not >= 80 and not 100).
        suggestions = generate_suggestions(frozenset(), coverage_score=60)
        assert suggestions == []

    def test_no_missing_skills_with_high_score_returns_positive_note(self):
        suggestions = generate_suggestions(frozenset(), coverage_score=85)
        assert len(suggestions) == 1
        # High-score note, not a skill suggestion.
        assert "stand out" in suggestions[0].lower() or "quantify" in suggestions[0].lower()

    def test_perfect_score_returns_perfect_note(self):
        suggestions = generate_suggestions(frozenset(), coverage_score=100)
        assert len(suggestions) == 1
        assert "all the skills" in suggestions[0].lower() or "all skills" in suggestions[0].lower() or "covers all" in suggestions[0].lower()


class TestClusterGrouping:
    def test_docker_kubernetes_grouped(self):
        missing = frozenset({"Docker", "Kubernetes"})
        suggestions = generate_suggestions(missing, coverage_score=50)
        # Should be ONE grouped suggestion, not two separate ones.
        docker_count = sum(1 for s in suggestions if "Docker" in s and "Kubernetes" in s)
        assert docker_count >= 1

    def test_cicd_tools_grouped(self):
        missing = frozenset({"CI/CD", "GitHub Actions"})
        suggestions = generate_suggestions(missing, coverage_score=40)
        # Both should appear in a single grouped suggestion.
        grouped = [s for s in suggestions if "CI/CD" in s and "GitHub Actions" in s]
        assert len(grouped) >= 1

    def test_single_cluster_skill_not_grouped(self):
        # Only one skill from a cluster → no grouping, individual suggestion.
        suggestions = generate_suggestions(frozenset({"Docker"}), coverage_score=50)
        # Should be a single-skill suggestion (not a container cluster sentence).
        assert any("Docker" in s for s in suggestions)

    def test_cloud_cluster_grouped(self):
        missing = frozenset({"AWS", "Azure"})
        suggestions = generate_suggestions(missing, coverage_score=40)
        grouped = [s for s in suggestions if "AWS" in s and "Azure" in s]
        assert len(grouped) >= 1


class TestMaxSuggestions:
    def test_does_not_exceed_max_suggestions(self):
        # 10 distinct missing skills → capped at MAX_SUGGESTIONS.
        missing = frozenset({
            "Docker", "Terraform", "Ansible", "Prometheus", "Grafana",
            "ArgoCD", "Helm", "Airflow", "dbt", "Snowflake"
        })
        suggestions = generate_suggestions(missing, coverage_score=20)
        assert len(suggestions) <= MAX_SUGGESTIONS

    def test_high_score_note_counts_toward_max(self):
        missing = frozenset({
            "Docker", "Kubernetes", "Terraform", "Ansible", "Prometheus",
        })
        suggestions = generate_suggestions(missing, coverage_score=85)
        assert len(suggestions) <= MAX_SUGGESTIONS


class TestHighScoreNote:
    def test_high_score_prepends_positive_note(self):
        missing = frozenset({"Docker"})
        suggestions = generate_suggestions(missing, coverage_score=HIGH_SCORE_THRESHOLD)
        # First item should be the encouraging note.
        assert "quantify" in suggestions[0].lower() or "stand out" in suggestions[0].lower()

    def test_high_score_note_appears_before_skill_suggestions(self):
        missing = frozenset({"Docker"})
        suggestions = generate_suggestions(missing, coverage_score=90)
        # Positive note first, skill suggestion second.
        assert len(suggestions) >= 2
        assert "Docker" not in suggestions[0]

    def test_below_threshold_no_positive_note(self):
        missing = frozenset({"Docker"})
        suggestions = generate_suggestions(missing, coverage_score=HIGH_SCORE_THRESHOLD - 1)
        # No encouraging note — only skill suggestion.
        assert not any("quantify" in s.lower() for s in suggestions)


class TestEdgeCases:
    def test_empty_missing_and_zero_score(self):
        suggestions = generate_suggestions(frozenset(), coverage_score=0)
        assert suggestions == []

    def test_returns_list(self):
        result = generate_suggestions(frozenset({"Python"}), coverage_score=50)
        assert isinstance(result, list)

    def test_suggestions_are_non_empty_strings(self):
        suggestions = generate_suggestions(frozenset({"Docker"}), coverage_score=50)
        for s in suggestions:
            assert isinstance(s, str)
            assert len(s) > 0

    def test_single_missing_skill_produces_at_most_max(self):
        suggestions = generate_suggestions(frozenset({"Docker"}), coverage_score=50)
        assert len(suggestions) <= MAX_SUGGESTIONS
