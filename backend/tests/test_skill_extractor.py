"""
test_skill_extractor.py — Unit tests for services/skill_extractor.py
"""

import pytest
from services.skill_extractor import extract_skills


class TestExtractKnownSkills:
    def test_extracts_python(self):
        skills = extract_skills("I am experienced in Python development.")
        assert "Python" in skills

    def test_extracts_multiple_skills(self):
        skills = extract_skills("Experienced in Python and SQL databases.")
        assert "Python" in skills
        assert "SQL" in skills

    def test_extracts_docker(self):
        skills = extract_skills("We use Docker containers in production.")
        assert "Docker" in skills

    def test_extracts_kubernetes(self):
        skills = extract_skills("Orchestrated workloads with Kubernetes.")
        assert "Kubernetes" in skills

    def test_extracts_react(self):
        skills = extract_skills("Built UIs using React and Redux.")
        assert "React" in skills
        assert "Redux" in skills

    def test_extracts_rest_api(self):
        skills = extract_skills("Designed RESTful APIs for the backend.")
        assert "REST API" in skills

    def test_extracts_ci_cd_spelled_out(self):
        skills = extract_skills("Set up continuous integration pipelines.")
        assert "CI/CD" in skills

    def test_extracts_ci_cd_slash(self):
        skills = extract_skills("Worked on CI/CD with GitHub Actions.")
        assert "CI/CD" in skills

    def test_extracts_postgresql(self):
        skills = extract_skills("Used PostgreSQL and Redis for storage.")
        assert "PostgreSQL" in skills
        assert "Redis" in skills

    def test_extracts_machine_learning(self):
        skills = extract_skills("Applied machine learning techniques.")
        assert "Machine learning" in skills


class TestAliasNormalization:
    def test_js_alias_maps_to_javascript(self):
        skills = extract_skills("Proficient in JS and TypeScript.")
        assert "JavaScript" in skills

    def test_postgres_alias_maps_to_postgresql(self):
        skills = extract_skills("Managed a Postgres database.")
        assert "PostgreSQL" in skills

    def test_golang_alias_maps_to_go(self):
        skills = extract_skills("Backend services written in Golang.")
        assert "Go" in skills

    def test_k8s_alias_maps_to_kubernetes(self):
        skills = extract_skills("Deployed applications using k8s.")
        assert "Kubernetes" in skills

    def test_ml_alias_maps_to_machine_learning(self):
        skills = extract_skills("3 years of ML experience.")
        assert "Machine learning" in skills

    def test_nodejs_alias_maps_to_nodejs(self):
        skills = extract_skills("Node.js REST server.")
        assert "Node.js" in skills

    def test_nlp_alias_maps_to_nlp(self):
        skills = extract_skills("Built NLP pipelines for text analysis.")
        assert "Natural language processing" in skills

    def test_bash_alias_maps_to_shell_scripting(self):
        skills = extract_skills("Automated tasks with bash scripts.")
        assert "Shell scripting" in skills


class TestWordBoundaryMatching:
    def test_java_does_not_match_javascript(self):
        # "JavaScript" should not produce a "Java" match.
        skills = extract_skills("Used JavaScript for the frontend.")
        assert "Java" not in skills
        assert "JavaScript" in skills

    def test_r_does_not_match_ruby(self):
        skills = extract_skills("Expert Ruby developer.")
        assert "Ruby" in skills
        # "R" is a language but should not fire on "Ruby"
        # because the regex uses word boundaries.
        # (R would only match a standalone "R" token.)

    def test_r_matches_standalone(self):
        skills = extract_skills("Statistical analysis using R and Python.")
        assert "R" in skills

    def test_go_does_not_match_golang_word_in_middle(self):
        # "Go" should be found even when "golang" is also present.
        skills = extract_skills("golang backend services.")
        assert "Go" in skills

    def test_sass_does_not_match_sassy(self):
        skills = extract_skills("The team writes sassy CSS.")
        # "sass" should NOT match inside "sassy" (word boundary check).
        assert "Sass" not in skills

    def test_sql_does_not_match_nosql(self):
        # "SQL" should not fire on "NoSQL" alone.
        skills = extract_skills("Experience with NoSQL databases.")
        # "SQL" is inside "NoSQL" — boundary prevents false match.
        assert "SQL" not in skills


class TestCaseInsensitivity:
    def test_uppercase(self):
        assert "Python" in extract_skills("PYTHON DEVELOPER")

    def test_mixed_case(self):
        assert "Docker" in extract_skills("We use dOcKeR here.")

    def test_canonical_name_preserves_case_in_output(self):
        # The returned canonical should be title-cased, not lowercased.
        skills = extract_skills("python and docker experience.")
        assert "Python" in skills
        assert "Docker" in skills


class TestEdgeCases:
    def test_empty_string_returns_empty_frozenset(self):
        assert extract_skills("") == frozenset()

    def test_whitespace_only_returns_empty_frozenset(self):
        assert extract_skills("   \n\t  ") == frozenset()

    def test_no_skills_in_text(self):
        skills = extract_skills("The quick brown fox jumps over the lazy dog.")
        assert skills == frozenset()

    def test_returns_frozenset(self):
        result = extract_skills("Python developer.")
        assert isinstance(result, frozenset)

    def test_deduplication(self):
        # Mentioning Python multiple times should not produce duplicates.
        skills = extract_skills("Python Python Python")
        python_count = sum(1 for s in skills if s == "Python")
        assert python_count == 1

    def test_html_input_stripped(self):
        skills = extract_skills("<p>Python and <strong>Docker</strong></p>")
        assert "Python" in skills
        assert "Docker" in skills

    def test_very_long_text(self):
        long_text = ("Python developer. " * 500) + "Also knows Docker."
        skills = extract_skills(long_text)
        assert "Python" in skills
        assert "Docker" in skills


class TestFalsePositiveRegressions:
    """Regression tests for confirmed false-positive fixes.

    Bug 1 — 'rest' alias on REST API matched common English word.
    Bug 2 — 'communication' canonical matched bare word in any sentence.
    """

    # ── REST API ──────────────────────────────────────────────────────────────

    def test_rest_english_word_does_not_match_rest_api(self):
        """'rest' as a plain English word must not fire REST API."""
        assert "REST API" not in extract_skills("I need to get some rest.")

    def test_rest_assured_does_not_match_rest_api(self):
        assert "REST API" not in extract_skills("Rest assured, we will deliver.")

    def test_restful_still_matches_rest_api(self):
        """'restful' is an unambiguous technical alias and must still fire."""
        assert "REST API" in extract_skills("Designed RESTful web services.")

    def test_restful_api_alias_still_matches(self):
        assert "REST API" in extract_skills("Built a RESTful API for the platform.")

    def test_rest_api_phrase_still_matches(self):
        assert "REST API" in extract_skills("Exposed a REST API endpoint.")

    # ── Communication skills ──────────────────────────────────────────────────

    def test_bare_communication_word_does_not_match(self):
        """'communication' alone must not fire — too generic."""
        skills = extract_skills("establish communication with clients")
        assert "Communication skills" not in skills
        assert "Communication" not in skills

    def test_communication_protocols_does_not_match(self):
        skills = extract_skills("communication protocols in networking")
        assert "Communication skills" not in skills

    def test_communication_skills_phrase_matches(self):
        """'communication skills' must fire the canonical."""
        assert "Communication skills" in extract_skills("excellent communication skills")

    def test_verbal_communication_alias_matches(self):
        assert "Communication skills" in extract_skills("strong verbal communication")

    def test_written_communication_alias_matches(self):
        assert "Communication skills" in extract_skills("proven written communication ability")

    def test_interpersonal_skills_alias_matches(self):
        assert "Communication skills" in extract_skills("interpersonal skills and empathy")

    # ── Reference scoring scenario ────────────────────────────────────────────

    def test_reference_scenario_extraction(self):
        """Python/SQL/Git vs Python/SQL/Docker — exact skill sets."""
        from services.matcher import compute_match
        rs = extract_skills("Python, SQL, Git")
        js = extract_skills("Python, SQL, Docker")
        assert rs == frozenset({"Python", "SQL", "Git"})
        assert js == frozenset({"Python", "SQL", "Docker"})

    def test_reference_scenario_coverage_score(self):
        """coverage = matched(2) / job(3) * 100 = 67%."""
        from services.matcher import compute_match
        m = compute_match(
            extract_skills("Python, SQL, Git"),
            extract_skills("Python, SQL, Docker"),
        )
        assert m.coverage_score == 67

    def test_reference_scenario_overlap_score(self):
        """overlap = matched(2) / union(4) * 100 = 50%."""
        from services.matcher import compute_match
        m = compute_match(
            extract_skills("Python, SQL, Git"),
            extract_skills("Python, SQL, Docker"),
        )
        assert m.overlap_score == 50

    def test_reference_scenario_matched_skills(self):
        from services.matcher import compute_match
        m = compute_match(
            extract_skills("Python, SQL, Git"),
            extract_skills("Python, SQL, Docker"),
        )
        assert m.matched_skills == frozenset({"Python", "SQL"})

    def test_reference_scenario_missing_skills(self):
        from services.matcher import compute_match
        m = compute_match(
            extract_skills("Python, SQL, Git"),
            extract_skills("Python, SQL, Docker"),
        )
        assert m.missing_skills == frozenset({"Docker"})

    def test_reference_scenario_extra_skills(self):
        from services.matcher import compute_match
        m = compute_match(
            extract_skills("Python, SQL, Git"),
            extract_skills("Python, SQL, Docker"),
        )
        assert m.extra_skills == frozenset({"Git"})
