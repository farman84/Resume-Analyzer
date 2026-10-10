"""
test_text_processor.py — Unit tests for services/text_processor.py
"""

import pytest
from services.text_processor import normalize


class TestNormalizeBasic:
    def test_empty_string_returns_empty(self):
        assert normalize("") == ""

    def test_whitespace_only_returns_empty(self):
        assert normalize("   \t\n") == ""

    def test_lowercases_text(self):
        result = normalize("Python Django REST")
        assert result == "python django rest"

    def test_collapses_multiple_spaces(self):
        result = normalize("python   django    rest")
        assert result == "python django rest"

    def test_strips_leading_trailing_whitespace(self):
        result = normalize("  python  ")
        assert result == "python"

    def test_collapses_newlines(self):
        result = normalize("python\ndjango\nrest")
        assert result == "python django rest"

    def test_collapses_tabs(self):
        result = normalize("python\tdjango\trest")
        assert result == "python django rest"


class TestNormalizePunctuation:
    def test_removes_commas_and_semicolons(self):
        result = normalize("Python, Django; REST")
        assert "," not in result
        assert ";" not in result

    def test_preserves_hyphens(self):
        # "ci-cd" must survive normalization.
        result = normalize("ci-cd pipeline")
        assert "ci-cd" in result

    def test_preserves_forward_slash(self):
        # "CI/CD" lowercased to "ci/cd" must survive.
        result = normalize("CI/CD pipeline")
        assert "ci/cd" in result

    def test_preserves_hash_for_csharp(self):
        result = normalize("C# developer")
        assert "c#" in result

    def test_preserves_plus_for_cpp(self):
        result = normalize("C++ engineer")
        assert "c++" in result

    def test_preserves_dots_in_tech_names(self):
        # "Node.js" and "Vue.js" use dots.
        result = normalize("Node.js and Vue.js")
        assert "node.js" in result
        assert "vue.js" in result

    def test_removes_exclamation_marks(self):
        result = normalize("Python! Django!")
        assert "!" not in result

    def test_removes_parentheses(self):
        result = normalize("Python (programming language)")
        assert "(" not in result
        assert ")" not in result

    def test_removes_at_sign(self):
        result = normalize("email@example.com skills")
        assert "@" not in result


class TestNormalizeHTML:
    def test_strips_html_tags(self):
        result = normalize("<p>Python developer</p>")
        assert "<" not in result
        assert ">" not in result
        assert "python" in result

    def test_strips_nested_html(self):
        result = normalize("<div><strong>Python</strong> and <em>Django</em></div>")
        assert "python" in result
        assert "django" in result
        assert "<" not in result

    def test_handles_html_with_attributes(self):
        result = normalize('<span class="skill">Docker</span>')
        assert "docker" in result
        assert "<" not in result

    def test_handles_self_closing_tags(self):
        result = normalize("Python<br/>Django")
        assert "python" in result
        assert "django" in result
