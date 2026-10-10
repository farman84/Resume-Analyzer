"""
text_processor.py — Text normalization for the AI Resume Analyzer.

Cleans raw input text before skill extraction:
  1. Strip HTML tags.
  2. Lowercase.
  3. Remove punctuation except hyphens and forward-slashes
     (to preserve terms like "CI/CD" and "ci-cd").
  4. Collapse all whitespace to single spaces.
  5. Strip leading/trailing whitespace.

No external dependencies — pure Python standard library.
"""

import re


# Pre-compiled patterns for performance (module-level, compiled once).
_HTML_TAG_RE = re.compile(r"<[^>]+>")
_KEEP_CHARS_RE = re.compile(r"[^\w\s\-/#+.]")   # keep word chars, spaces, - / # + .
_WHITESPACE_RE = re.compile(r"\s+")


def normalize(text: str) -> str:
    """Return a cleaned, lowercased version of *text*.

    Args:
        text: Raw resume or job-description string.

    Returns:
        Normalised string, or an empty string if *text* is empty/whitespace.
    """
    if not text or not text.strip():
        return ""

    # 1. Strip HTML tags.
    text = _HTML_TAG_RE.sub(" ", text)

    # 2. Lowercase.
    text = text.lower()

    # 3. Remove characters that are not word chars, spaces, hyphens, slashes,
    #    hash, plus, or dots  (dots kept for "node.js", "vue.js", etc.).
    text = _KEEP_CHARS_RE.sub(" ", text)

    # 4. Collapse whitespace.
    text = _WHITESPACE_RE.sub(" ", text)

    # 5. Strip.
    return text.strip()
