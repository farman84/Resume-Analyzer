# AI Resume Analyzer

A local web application that compares your resume against a job description to surface matched skills, missing skills, a keyword match score, and practical improvement suggestions.

> **No paid APIs or API keys required.** All analysis runs locally using Python and spaCy.

---

## Prerequisites

Install these once on your machine before doing anything else.

| Tool | Minimum version | Download |
|------|----------------|---------|
| Node.js | 18 | https://nodejs.org |
| Python | 3.11 | https://www.python.org/downloads |
| Git (optional) | any | https://git-scm.com |

Verify your versions in PowerShell:
```powershell
node --version    # should print v18.x.x or higher
python --version  # should print 3.11.x or higher
```

---

## Project structure

```
AI Resume/
├── project-plan.md        ← architecture and phased roadmap
├── README.md              ← this file
├── backend/               ← Python FastAPI application
│   ├── main.py            ← app entry point and CORS config
│   ├── requirements.txt   ← Python dependencies
│   ├── routers/           ← API route handlers (Phase 3+)
│   ├── services/          ← analysis logic modules (Phase 2+)
│   ├── data/              ← skills_list.json (Phase 2+)
│   └── tests/             ← pytest unit tests (Phase 2+)
└── frontend/              ← React + Vite application
    ├── src/
    │   ├── App.jsx
    │   ├── api/           ← fetch wrappers (Phase 4+)
    │   ├── components/    ← UI components (Phase 4+)
    │   ├── pages/         ← page-level components (Phase 4+)
    │   └── styles/        ← global CSS (Phase 6+)
    └── package.json
```

---

## Setup (run once)

### Backend

Open a PowerShell terminal in the project root:

```powershell
cd backend

# Create a Python virtual environment
python -m venv venv

# Activate it
.\venv\Scripts\Activate.ps1

# Install Python dependencies
pip install -r requirements.txt

# Download the spaCy English language model
python -m spacy download en_core_web_sm
```

> **Note for Windows users:** If you see a script-execution error when running `Activate.ps1`, run this first (once per machine):
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```

### Frontend

Open a second PowerShell terminal in the project root:

```powershell
cd frontend
npm install
```

---

## Running the application

You need **two terminals open at the same time** — one for the backend and one for the frontend.

### Terminal 1 — Backend

```powershell
cd backend
.\venv\Scripts\Activate.ps1
uvicorn main:app --reload
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process ...
```

Verify it is working:
- Open http://localhost:8000/api/health in your browser.
- You should see: `{"status":"ok"}`
- Open http://localhost:8000/docs for the interactive API documentation.

### Terminal 2 — Frontend

```powershell
cd frontend
npm run dev
```

You should see:
```
VITE v6.x.x  ready in xxx ms
➜  Local:   http://localhost:5173/
```

Open http://localhost:5173 in your browser.

---

## Running the tests

With the backend virtual environment activated:

```powershell
cd backend
.\venv\Scripts\Activate.ps1
pytest tests/ -v
```

> Phase 2 will add the first real test files. This command will report "no tests found" until then, which is expected.

---

## Development phases

| Phase | What it adds | Status |
|-------|-------------|--------|
| 1 — Scaffold | Both servers start, `/api/health` returns OK | ✅ Complete |
| 2 — Analysis engine | Text processing, skill extraction, matching, suggestions + tests | ⬜ Pending |
| 3 — API route | `POST /api/analyze` endpoint | ⬜ Pending |
| 4 — Input form | React form wired to the API | ⬜ Pending |
| 5 — Results display | Score cards, skill lists, suggestions on screen | ⬜ Pending |
| 6 — Polish | Responsive styles, all UX states verified | ⬜ Pending |

---

## Stopping the servers

Press `Ctrl + C` in each terminal to stop the backend and frontend servers.
