"""
skill_extractor.py — Deterministic skill extraction for the AI Resume Analyzer.

Algorithm
---------
1. Load the curated skill taxonomy from data/skills_list.json (once, at import).
   Each entry has a canonical name and zero or more aliases.

2. Build a lookup table:
     normalised_alias -> canonical_name

3. For a given text:
   a. Normalise the text via text_processor.normalize().
   b. For each (alias, canonical) pair — longest aliases first to prefer
      specific matches over short ones — search for whole-word occurrences
      using a pre-compiled regex with word-boundary anchors (\b).
   c. Collect the canonical names of every match, deduplicated.

Word-boundary matching prevents "Java" from matching "JavaScript", and
"R" from matching "Ruby" or "REST".

No external NLP dependencies — pure Python standard library (re + json).
"""

import json
import re
from pathlib import Path
from functools import lru_cache
from typing import FrozenSet

from services.text_processor import normalize


# ---------------------------------------------------------------------------
# Taxonomy loading
# ---------------------------------------------------------------------------

_DATA_FILE = Path(__file__).parent.parent / "data" / "skills_list.json"


@lru_cache(maxsize=1)
def _load_taxonomy() -> list[tuple[str, str, re.Pattern[str]]]:
    """Load skills_list.json and return a list of
    (normalised_alias, canonical_name, compiled_regex) tuples,
    sorted by alias length descending so longer aliases match first.

    The result is cached — the file is read once per process.
    """
    with _DATA_FILE.open(encoding="utf-8") as fh:
        data = json.load(fh)

    entries: list[tuple[str, str]] = []  # (normalised_alias, canonical)

    for skill in data["skills"]:
        canonical: str = skill["canonical"]
        # Build the full set of surface forms to check.
        surface_forms: list[str] = [canonical] + skill.get("aliases", [])

        for form in surface_forms:
            normalised = form.lower()
            entries.append((normalised, canonical))

    # Sort longest alias first — ensures "spring boot" matches before "spring".
    entries.sort(key=lambda t: len(t[0]), reverse=True)

    # Compile a regex for each unique normalised alias.
    result: list[tuple[str, str, re.Pattern[str]]] = []
    seen_aliases: set[str] = set()

    for norm_alias, canonical in entries:
        if norm_alias in seen_aliases:
            continue
        seen_aliases.add(norm_alias)

        # Escape dots and pluses in skill names (e.g. "c++", "node.js").
        escaped = re.escape(norm_alias)
        # Use word-boundary anchors where the alias starts/ends on a word char.
        # For aliases ending in punctuation (e.g. "c++") we skip the trailing \b.
        left_b  = r"\b" if norm_alias[0].isalnum() or norm_alias[0] == "_" else ""
        right_b = r"\b" if norm_alias[-1].isalnum() or norm_alias[-1] == "_" else ""
        pattern = re.compile(left_b + escaped + right_b)
        result.append((norm_alias, canonical, pattern))

    return result


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def extract_skills(text: str) -> FrozenSet[str]:
    """Return the frozenset of canonical skill names found in *text*.

    Matching is:
    - Case-insensitive (text is normalised to lowercase first).
    - Word-boundary-aware (avoids "Java" matching inside "JavaScript").
    - Deterministic (same input always gives same output).

    Args:
        text: Raw resume or job-description string.

    Returns:
        Frozenset of canonical skill name strings (e.g. {"Python", "Docker"}).
        Returns an empty frozenset for blank/empty input.
    """
    if not text or not text.strip():
        return frozenset()

    normalised_text = normalize(text)
    taxonomy = _load_taxonomy()

    found: set[str] = set()
    for _alias, canonical, pattern in taxonomy:
        if pattern.search(normalised_text):
            found.add(canonical)

    return frozenset(found)
