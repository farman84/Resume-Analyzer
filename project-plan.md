# AI Resume Analyzer — Project Plan

## Status Legend
- `[ ]` pending
- `[-]` in progress
- `[x]` done

---

## Top-Level Overview

**Goal:** Build a web application that lets a job seeker paste their resume text and a job description, then receive a transparent keyword-match score, a list of matched and missing skills, and actionable suggestions for improving the resume.

**Scope (MVP only):**
- React + Vite single-page frontend
- Python + FastAPI backend
- Python-based NLP skill extraction (spaCy, no paid APIs)
- No authentication, no deployment, no payment systems
- No SQLite in the first version — analysis is stateless; persistence is deferred to a future phase

**Out of scope for MVP:**
- User accounts / authentication
- Saving or comparing multiple analyses
- Integration with external AI APIs (OpenAI, watsonx, etc.)
- ATS simulation or hiring-probability claims
- File upload (PDF/DOCX parsing)
- Deployment to any cloud or server

**Approach:** Pure keyword and noun-phrase matching using a curated skill list plus spaCy's English model. The score is explicitly labelled "keyword match score" and described clearly to the user so there is no false impression of guaranteed ATS or employer outcomes.

---

## User Workflow

1. User opens the app in a browser (`http://localhost:5173`).
2. User pastes their resume text into one text area and a job description into another.
3. User clicks **Analyze**.
4. The frontend sends both texts to the FastAPI backend.
5. The backend extracts skills from each text, calculates a match score, identifies matched and missing skills, and generates suggestions.
6. The frontend displays a results section with:
   - Keyword match score (0–100%) with a plain-language explanation
   - Matched skills list
   - Missing skills list
   - Suggestions for improvement
7. User can edit the inputs and re-analyze at any time.

---

## Architecture

```
User Browser
    |
    | HTTP (localhost:5173)
    v
React + Vite Frontend
    |
    | POST /api/analyze  (JSON)
    | (localhost:8000)
    v
FastAPI Backend
    |
    v
Analysis Engine (pure Python)
  - Text normalizer
  - Skill extractor  (spaCy + curated skill list)
  - Match calculator (Jaccard-style overlap)
  - Suggestion generator
```

**No database in MVP.** Every request is self-contained. The backend processes inputs and returns results; nothing is persisted between requests.

---

## Folder and File Structure

```
AI Resume/                         ← workspace root
├── project-plan.md                ← this file
├── README.md                      ← setup and run instructions
│
├── frontend/                      ← React + Vite app
│   ├── index.html
│   ├── vite.config.js
│   ├── package.json
│   ├── public/
│   └── src/
│       ├── main.jsx               ← app entry point
│       ├── App.jsx                ← root component, routing
│       ├── api/
│       │   └── analyzeApi.js      ← fetch wrapper for POST /api/analyze
│       ├── components/
│       │   ├── InputForm.jsx      ← resume + JD text areas + submit button
│       │   ├── ScoreCard.jsx      ← match score display
│       │   ├── SkillList.jsx      ← reusable matched / missing skill chips
│       │   ├── Suggestions.jsx    ← improvement suggestions list
│       │   ├── LoadingSpinner.jsx ← loading state overlay
│       │   └── ErrorMessage.jsx   ← inline error display
│       ├── pages/
│       │   ├── HomePage.jsx       ← landing page with InputForm
│       │   └── ResultsPage.jsx    ← analysis results display
│       └── styles/
│           └── index.css          ← global styles (responsive, clean)
│
└── backend/                       ← Python FastAPI app
    ├── requirements.txt
    ├── main.py                    ← FastAPI app entry point, CORS config
    ├── routers/
    │   └── analyze.py             ← POST /api/analyze route
    ├── services/
    │   ├── text_processor.py      ← text cleaning and normalization
    │   ├── skill_extractor.py     ← spaCy-based skill extraction
    │   ├── matcher.py             ← match score and gap calculation
    │   └── suggester.py           ← suggestion generation logic
    ├── data/
    │   └── skills_list.json       ← curated skill keywords (tech + soft skills)
    └── tests/
        ├── test_text_processor.py
        ├── test_skill_extractor.py
        ├── test_matcher.py
        └── test_suggester.py
```

---

## Frontend Pages and Components

### Pages

| Page | Route | Purpose |
|------|-------|---------|
| `HomePage.jsx` | `/` | Landing page: headline, brief description, `InputForm` |
| `ResultsPage.jsx` | `/results` (in-memory state, not a URL route) | Shows `ScoreCard`, `SkillList` (matched), `SkillList` (missing), `Suggestions` |

The app uses React state to switch between the input view and results view — no React Router needed for MVP. The "Back / Analyze Again" button resets state to show the form.

### Components

| Component | Responsibility |
|-----------|---------------|
| `InputForm.jsx` | Two `<textarea>` fields (resume, job description), character-count hints, a submit button, and inline validation messages for empty inputs |
| `ScoreCard.jsx` | Receives a `scores` array and renders one card per score, each with its own label, value, progress bar, and one-line explanation. Used for "Job Coverage" and "Overall Overlap" |
| `SkillList.jsx` | Accepts a `title` prop and a `skills` array; renders each skill as a pill/chip. Used twice: matched (green) and missing (amber) |
| `Suggestions.jsx` | Ordered list of plain-text improvement suggestions |
| `LoadingSpinner.jsx` | Centered spinner shown while the API call is in flight |
| `ErrorMessage.jsx` | Dismissable banner for API or validation errors |

### UX States to Handle

- **Empty state:** Both fields empty → "Please paste your resume and a job description."
- **One field empty:** Inline message on the empty field.
- **Loading:** Spinner replaces the submit button while waiting.
- **Error:** `ErrorMessage` banner with a user-friendly message; original inputs preserved.
- **Empty results:** If no skills are extracted → "We couldn't identify specific skills. Try adding more detail to your resume or job description."

---

## Backend API Endpoints

### `POST /api/analyze`

**Purpose:** Accept resume and job description texts, return full analysis.

**Request body (JSON):**
```json
{
  "resume_text": "string  (1–20 000 characters)",
  "job_description": "string  (1–20 000 characters)"
}
```

**Response body (JSON) — success 200:**
```json
{
  "coverage_score": 67,
  "overlap_score": 50,
  "matched_skills": ["Python", "REST API", "teamwork", "SQL"],
  "missing_skills": ["Docker", "Kubernetes", "CI/CD"],
  "resume_skills": ["Python", "REST API", "teamwork", "SQL", "Excel"],
  "job_skills": ["Python", "REST API", "Docker", "Kubernetes", "CI/CD", "SQL"],
  "suggestions": [
    "Add Docker to your resume if you have any container experience.",
    "Mention CI/CD tools such as GitHub Actions or Jenkins if applicable.",
    "Consider adding a projects section to demonstrate Kubernetes exposure."
  ],
  "score_note": null,
  "score_disclaimer": "These scores reflect keyword overlap only. They are not ATS scores or measures of hiring probability."
}
```

- **`coverage_score`** — `matched / job_skills` × 100. Answers: "What % of this job's requirements appear in my resume?"
- **`overlap_score`** — `matched / union(resume_skills, job_skills)` × 100. Answers: "What % of all skills mentioned across both documents do I share?"

**Response body (JSON) — validation error 422:**
```json
{
  "detail": "resume_text and job_description must each be between 1 and 20000 characters."
}
```

**Response body (JSON) — server error 500:**
```json
{
  "detail": "An unexpected error occurred. Please try again."
}
```

---

## Skill Extraction and Matching Algorithm

### Step 1 — Text Normalization (`text_processor.py`)
- Lowercase the full text.
- Remove punctuation except hyphens (to preserve terms like "ci-cd").
- Collapse whitespace.
- Strip HTML tags if present.

### Step 2 — Skill Extraction (`skill_extractor.py`)
Two complementary approaches run together and their results are merged:

**A. Curated list lookup**
- Load `data/skills_list.json` — a hand-curated list of ~300 skill keywords: primarily tech skills (languages, frameworks, tools, cloud platforms) plus a focused set of universal soft skills (communication, teamwork, problem-solving, critical thinking, time management, leadership, adaptability).
- For each skill in the list, check if it appears in the normalized text (whole-word match to avoid "Java" matching "JavaScript").

**B. spaCy noun-phrase extraction**
- Run spaCy's `en_core_web_sm` model on the original text.
- Extract noun chunks (2–4 tokens) that look like skill phrases.
- Filter against the curated list to keep only recognized skills.
- This catches skills spelled slightly differently or in context.

**Result:** A deduplicated set of skill strings for each input text.

### Step 3 — Match Calculation (`matcher.py`)
```
matched_skills  = resume_skills ∩ job_skills
missing_skills  = job_skills - resume_skills
extra_skills    = resume_skills - job_skills  (not shown to user but available)

coverage_score (%) = len(matched_skills) / len(job_skills) * 100
                     rounded to nearest integer, clamped 0–100
                     Label: "Job Coverage"
                     Explanation: "% of this job's required skills found in your resume"

overlap_score (%)  = len(matched_skills) / len(resume_skills ∪ job_skills) * 100
                     rounded to nearest integer, clamped 0–100
                     Label: "Overall Overlap"
                     Explanation: "% of all skills mentioned in both documents that you share"
```

Both scores are returned in the API response. `ScoreCard.jsx` accepts a `scores` array and renders one card per score, so adding or removing a score in future requires no component changes.

**Edge cases:**
- `job_skills` is empty → `coverage_score = 0`; `score_note` explains no job skills were detected.
- Union is empty → both scores = 0; `score_note` explains no skills were detected in either text.

### Step 4 — Suggestion Generation (`suggester.py`)
For each skill in `missing_skills` (up to 5, to avoid overwhelming the user):
- Generate a sentence: "Consider adding [skill] to your resume if you have relevant experience."
- For well-known tool clusters (e.g. Docker + Kubernetes, Git + CI/CD), group suggestions: "You appear to be missing container-related skills (Docker, Kubernetes). If you have any hands-on experience, consider adding a relevant project."

If `coverage_score >= 80`:
- Add a positive note: "Your resume already covers most of the required skills. Focus on quantifying your achievements."

---

## Database Decision

**SQLite is deferred from the MVP.**

**Rationale:**
- Analysis is stateless — each request is self-contained (inputs in, results out).
- No user accounts, no history, no saved analyses.
- Adding a database in the first version introduces migration tooling, ORM setup, and additional test surface for no user-visible benefit.

**When to add persistence (Phase 2+):**
- Users want to save and revisit past analyses.
- Comparison of multiple job descriptions against one resume.
- Aggregate analytics (most-requested skills across all analyses).

**If/when added:** Use SQLite with SQLAlchemy (async). Table: `analyses(id, created_at, resume_hash, job_hash, score, matched_skills_json, missing_skills_json)`. Resume and JD text are hashed, not stored verbatim, for privacy.

---

## Error Handling, Privacy, and Security

### Input Validation
- Both fields required; max 20 000 characters each (prevents abuse, keeps spaCy fast).
- Validated at the FastAPI layer using Pydantic models; errors return HTTP 422 with a clear message.
- Frontend shows field-level validation before even making the API call.

### Error Handling
- Backend wraps the analysis pipeline in a try/except; unexpected errors return HTTP 500 with a safe generic message (no stack traces exposed to clients).
- Frontend handles network errors, HTTP 4xx, and HTTP 5xx separately with appropriate user-facing messages.

### Privacy
- Resume and job description text are processed in memory only. Nothing is written to disk or a database in the MVP.
- No analytics, tracking, or third-party SDKs in the frontend.
- CORS is restricted to `http://localhost:5173` during development.

### Security
- No authentication surface means no session/token attack surface.
- Character limit and Pydantic validation guard against excessively large payloads.
- spaCy processes text locally; no text is sent to any external service.

---

## Testing Strategy

### Backend Unit Tests (pytest)

| Test file | What it covers |
|-----------|---------------|
| `test_text_processor.py` | Lowercasing, punctuation removal, HTML stripping, whitespace collapsing |
| `test_skill_extractor.py` | Known skill found in text, skill NOT found, partial word not matched ("Java" ≠ "JavaScript"), empty text input |
| `test_matcher.py` | Score = 100% when resume contains all job skills; score = 0% when no overlap; correct matched/missing sets; edge case of empty job_skills |
| `test_suggester.py` | Correct number of suggestions generated; high-score positive note triggered; cluster grouping logic |

**Sample test cases:**

```
test_skill_extractor:
  input: "Experienced in Python and SQL databases"
  expected skills: {"Python", "SQL"}

test_matcher:
  resume_skills: {"Python", "SQL", "Docker"}
  job_skills:    {"Python", "SQL", "Kubernetes"}
  expected: match_score=67, matched={"Python","SQL"}, missing={"Kubernetes"}

test_suggester:
  missing_skills: {"Docker", "Kubernetes"}
  expected: suggestion contains "container" or both skill names
```

### Frontend Manual Test Checklist (no test framework required for MVP)
- [ ] Both fields empty → validation message appears, no API call made
- [ ] One field empty → correct field highlighted
- [ ] Valid inputs → spinner shows, results appear
- [ ] API offline → error banner shown, inputs preserved
- [ ] Very long input (20 001 chars) → rejected with clear message
- [ ] "Analyze Again" → form resets, previous results cleared

### Integration Test (manual)
- Start backend, start frontend, perform a full end-to-end analysis using a sample resume and JD. Verify results are non-empty and score matches expected calculation.

---

## Phased Implementation Roadmap

Each phase has clear completion criteria. Do not start the next phase until the current one is verified.

---

### Phase 1 — Project Scaffold ✅
**Intent:** Create the folder structure, install tooling, and verify both servers start.

**Todo:**
- [x] Create `frontend/` with Vite + React template (`npm create vite@latest`)
- [x] Create `backend/` with `requirements.txt` listing FastAPI, uvicorn, spaCy, pytest
- [x] Add `backend/main.py` with a health-check endpoint `GET /api/health → {"status": "ok"}`
- [x] Verify `uvicorn main:app --reload` starts without errors
- [x] Verify `npm run dev` starts Vite at `localhost:5173`
- [x] Add `README.md` with setup instructions

**Completion criteria:** Both servers start; `GET /api/health` returns `{"status": "ok"}` in a browser or curl.

**Outcome:** All criteria met. `/api/health` returns `{"status":"ok"}` (HTTP 200). Frontend builds clean (0 errors, 0 vulnerabilities). `httpx2` pinned in `requirements.txt` to avoid deprecation warning in tests.

---

### Phase 2 — Backend Analysis Engine ✅
**Intent:** Implement all backend logic with unit tests passing.

**Todo:**
- [x] Create `data/skills_list.json` with ~300 curated skills
- [x] Implement `text_processor.py`
- [x] Implement `skill_extractor.py` (curated list lookup + word-boundary regex; spaCy deferred — DLL blocked by Windows Application Control on Python 3.14)
- [x] Implement `matcher.py` (coverage_score + overlap_score, matched, missing, extra)
- [x] Implement `suggester.py` (up to 5 suggestions, cluster grouping, high-score note)
- [x] Write and pass all pytest unit tests in `backend/tests/`

**Completion criteria:** `pytest backend/tests/` reports all tests passing with no errors.

**Outcome:** 97 tests collected, 97 passed in 0.15s. Zero failures, zero warnings.
Note: spaCy noun-phrase extraction is listed as a future enhancement. The pure-regex curated-list approach is the primary extraction method and is sufficient for MVP.

---

### Phase 3 — Backend API Route ✅
**Intent:** Expose the analysis engine via FastAPI.

**Todo:**
- [x] Create `routers/analyze.py` with `POST /api/analyze`
- [x] Add Pydantic request/response models with character-length validation
- [x] Wire the router into `main.py`
- [x] Configure CORS for `http://localhost:5173` (already done in Phase 1)
- [x] Test the endpoint with FastAPI TestClient (38 API tests added)

**Completion criteria:** A POST to `/api/analyze` with sample resume and JD returns a valid JSON response matching the schema.

**Outcome:** 135 tests collected (97 Phase 2 + 38 Phase 3), 135 passed in 0.65s. Zero failures, zero regressions.

---

### Phase 4 — Frontend Core UI ✅
**Intent:** Build the complete frontend and wire it to the API.

**Todo:**
- [x] Create `InputForm.jsx` with two text areas, character counters, and a submit button
- [x] Add client-side validation (empty check, length check)
- [x] Create `analyzeApi.js` fetch wrapper (Vite proxy, 422 handling, network errors)
- [x] Add `LoadingSpinner.jsx` and `ErrorMessage.jsx`
- [x] Wire `App.jsx` state machine (idle → loading → results → error)
- [x] Create `ScoreCard.jsx` (two-card layout, progress bars, colour-coded levels)
- [x] Create `SkillList.jsx` (matched / missing / extra chip variants)
- [x] Create `Suggestions.jsx` (numbered list, empty state)
- [x] Build `HomePage.jsx` and `ResultsPage.jsx`
- [x] Apply full responsive CSS (mobile breakpoint at 600px)

**Completion criteria:** Full end-to-end flow works in the browser.

**Outcome:** `npm run build` — 0 errors, 0 warnings. `npm run lint` — 0 errors, 0 warnings (12 files, 104 rules). Backend pytest — 135/135 passed, 0 regressions.
Vite proxy configured in `vite.config.js` — no CORS changes needed in the backend.

---

### Phase 5 — Frontend Results Display
**Intent:** Render the full analysis results clearly.

**Todo:**
- [ ] Create `ScoreCard.jsx` (score %, progress bar, disclaimer text)
- [ ] Create `SkillList.jsx` (reusable chip list for matched and missing)
- [ ] Create `Suggestions.jsx` (ordered suggestion list)
- [ ] Build `ResultsPage.jsx` composing all result components
- [ ] Add "Analyze Again" button that resets state to the input form
- [ ] Handle empty-results state (no skills found message)

**Completion criteria:** A full end-to-end analysis displays score, matched skills, missing skills, and suggestions correctly on screen.

---

### Phase 6 — Polish and Validation
**Intent:** Add responsive styling, all error/empty/loading states, and a final manual test pass.

**Todo:**
- [ ] Apply responsive CSS (mobile-friendly layout)
- [ ] Verify all UX states: empty, loading, error, empty results, success
- [ ] Add homepage headline and brief "how it works" description
- [ ] Final review of score disclaimer wording
- [ ] Run full backend test suite one final time
- [ ] Complete frontend manual test checklist

**Completion criteria:** All manual test checklist items pass; the app looks clean on both desktop and a narrow (375px) viewport.

---

## Windows Setup and Run Instructions

_(These will be written in full in `README.md` during Phase 1. Summary below.)_

### Prerequisites
- Node.js 18+ (download from nodejs.org)
- Python 3.11+ (download from python.org)
- Git (optional but recommended)

### Backend setup (run once)
```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### Run backend
```powershell
cd backend
.\venv\Scripts\Activate.ps1
uvicorn main:app --reload
# Listening on http://localhost:8000
```

### Frontend setup (run once)
```powershell
cd frontend
npm install
```

### Run frontend
```powershell
cd frontend
npm run dev
# Open http://localhost:5173
```

### Run backend tests
```powershell
cd backend
.\venv\Scripts\Activate.ps1
pytest tests/ -v
```

---

## Future Enhancements (Not in MVP)

These are intentionally excluded from the MVP to keep the first version small and testable.

| Enhancement | Why deferred |
|-------------|-------------|
| PDF / DOCX file upload | Requires parsing libraries; adds complexity and binary file handling |
| Save analysis history (SQLite) | No user accounts in MVP; stateless is simpler |
| User authentication | Not needed until history/saving is introduced |
| watsonx / OpenAI integration | Optional advanced phase; requires API keys and costs money |
| ATS simulation | Cannot be done honestly without employer-specific data |
| Side-by-side comparison of multiple JDs | Needs persistence |
| Export results as PDF | Nice-to-have; out of scope |
| Semantic similarity (embeddings) | Valuable future upgrade from keyword matching; requires a local model download |
| Deployment (Docker, cloud) | Out of scope for first version |
| Dark mode | UX enhancement; not a functional requirement |
