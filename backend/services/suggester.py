"""
suggester.py — Improvement suggestion generation for the AI Resume Analyzer.

Rules
-----
1. For each skill in missing_skills (up to MAX_SUGGESTIONS):
   - If the skill belongs to a known cluster, group it with other missing
     cluster members into one suggestion.
   - Otherwise generate a single-skill suggestion.

2. If coverage_score >= HIGH_SCORE_THRESHOLD, prepend a positive note.

3. If no skills are missing, return only the positive note (or a congratulations
   message if the coverage score is perfect).

No external dependencies.
"""

from __future__ import annotations

from typing import FrozenSet

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

MAX_SUGGESTIONS = 5
HIGH_SCORE_THRESHOLD = 80  # coverage_score at or above this triggers a positive note.

# Skill clusters: if multiple missing skills belong to the same cluster,
# they are grouped into one combined suggestion.
_CLUSTERS: list[dict] = [
    {
        "name": "container orchestration",
        "skills": {"Docker", "Kubernetes", "Helm"},
        "template": (
            "You appear to be missing container-related skills "
            "({skills}). If you have hands-on experience with containers "
            "or orchestration, consider adding a relevant project or certification."
        ),
    },
    {
        "name": "CI/CD",
        "skills": {"CI/CD", "GitHub Actions", "Jenkins", "ArgoCD"},
        "template": (
            "Several CI/CD tools are listed in the job description "
            "({skills}). If you have pipeline or automation experience, "
            "highlight it explicitly on your resume."
        ),
    },
    {
        "name": "cloud platforms",
        "skills": {"AWS", "Azure", "Google Cloud", "IBM Cloud"},
        "template": (
            "The job description mentions cloud platform experience "
            "({skills}). Adding relevant cloud certifications or projects "
            "could strengthen your application."
        ),
    },
    {
        "name": "data engineering",
        "skills": {"Apache Spark", "Apache Kafka", "Airflow", "dbt", "ETL"},
        "template": (
            "Data pipeline and engineering skills are required "
            "({skills}). If you have worked with data workflows, describe "
            "the tools and scale involved."
        ),
    },
    {
        "name": "infrastructure as code",
        "skills": {"Terraform", "Ansible"},
        "template": (
            "Infrastructure-as-code experience is expected "
            "({skills}). Even personal or learning projects with these tools "
            "are worth mentioning."
        ),
    },
]

_SINGLE_TEMPLATE = (
    "Consider adding {skill} to your resume if you have relevant experience or "
    "have used it in a project."
)

_HIGH_SCORE_NOTE = (
    "Your resume already covers most of the required skills. "
    "To stand out further, quantify your achievements and highlight "
    "specific impact (e.g. 'reduced page load time by 40%' or 'led a team of 5 engineers')."
)

_PERFECT_NOTE = (
    "Excellent — your resume covers all the skills mentioned in the job description. "
    "Focus on quantifying your achievements and tailoring your summary to the role."
)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def generate_suggestions(
    missing_skills: FrozenSet[str],
    coverage_score: int,
) -> list[str]:
    """Generate up to MAX_SUGGESTIONS improvement suggestions.

    Args:
        missing_skills: Skills present in the job description but not the resume.
        coverage_score: Integer 0–100 job-coverage percentage.

    Returns:
        A list of plain-text suggestion strings (may be empty if nothing is missing
        and the score is perfect).
    """
    suggestions: list[str] = []

    if coverage_score == 100:
        return [_PERFECT_NOTE]

    if coverage_score >= HIGH_SCORE_THRESHOLD:
        suggestions.append(_HIGH_SCORE_NOTE)

    if not missing_skills:
        return suggestions

    remaining = set(missing_skills)
    cluster_suggestions: list[str] = []
    used_in_cluster: set[str] = set()

    # --- Cluster pass ---
    for cluster in _CLUSTERS:
        hits = remaining & cluster["skills"]
        if len(hits) >= 2:  # Only group if at least two cluster skills are missing.
            names = ", ".join(sorted(hits))
            cluster_suggestions.append(cluster["template"].format(skills=names))
            used_in_cluster |= hits

    # --- Single-skill pass for skills not covered by a cluster ---
    single_suggestions: list[str] = [
        _SINGLE_TEMPLATE.format(skill=skill)
        for skill in sorted(remaining - used_in_cluster)
    ]

    all_skill_suggestions = cluster_suggestions + single_suggestions

    # Keep total within MAX_SUGGESTIONS (not counting the high-score note).
    available_slots = MAX_SUGGESTIONS - len(suggestions)
    suggestions.extend(all_skill_suggestions[:available_slots])

    return suggestions
