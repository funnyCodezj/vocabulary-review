# Vocabulary Review — Project Guide

## Architecture

- **Backend**: FastAPI + SQLAlchemy + SQLite (`backend/`)
- **Frontend**: Vue 3 + Vite + Axios (`frontend/`)
- **Entry Point**: `backend/main.py` starts uvicorn on port 8001
- **Packaging**: PyInstaller single-file EXE via `pyinstaller` command

## Key Conventions

- All API routes are in `backend/routes/` with prefix `/api`
- Pydantic schemas live in `backend/schemas.py`
- Database models in `backend/models.py` (Word, UserProgress, ReviewSession, ReviewLog)
- SM-2 spaced repetition algorithm in `backend/services/spaced_repetition.py`
- Chinese translations use MyMemory API (free, no key)
- Image search: Pexels → Unsplash → Picsum (3-tier fallback)
- Audio: Edge TTS

## Frontend

- `frontend/src/api/index.js` — all API calls via Axios
- `frontend/src/views/` — page components (Home, WordList, WordDetail, ReviewFlash, ReviewQuiz, ReviewErrors, Import)
- `frontend/src/components/` — reusable (NavBar, WordCard, AudioButton, ImageWithFallback)
- `frontend/src/router/index.js` — Vue Router config
- Build: `npm run build` outputs to `frontend/dist/`

## Build EXE

```bash
cd backend
pyinstaller --clean --onefile --name "VocabularyReview" --distpath "..\dist_exe" \
  --add-data "..\\frontend\\dist;frontend\\dist" \
  --add-data ".env;." --add-data "audio;audio" --add-data "images;images" \
  --hidden-import "uvicorn.logging" --hidden-import "uvicorn.loops.auto" \
  --hidden-import "uvicorn.protocols.http.auto" --hidden-import "uvicorn.protocols.http.h11_impl" \
  --hidden-import "uvicorn.lifespan.on" --hidden-import "dotenv" \
  --hidden-import "edge_tts" --hidden-import "sqlalchemy" \
  --collect-all "uvicorn" --collect-all "edge_tts" "main.py"
```

## Path Resolution (PyInstaller)

- Frozen: `CODE_DIR = sys._MEIPASS`, `DATA_DIR = os.path.dirname(sys.executable)`
- Normal: `CODE_DIR = os.path.dirname(__file__)`
- DB + media stored next to EXE for persistence

## API Notes

- `GET /api/words` accepts `stage_filter` param: all, new, due, learning, reviewing, mastered, errors
- `POST /api/review/next` accepts `stage_filter` param (same values)
- `GET /api/stats` returns `errors_count`, `due_count` and per-stage counts
- Review/Quiz flash views use mode selection screen before starting

## Common Tasks

- Add API endpoint: route in `backend/routes/`, schema in `schemas.py`, import in `app.py`
- Add frontend page: view in `frontend/src/views/`, route in `router/index.js`, nav in `NavBar.vue`
- CSS variables available: `--primary`, `--error`, `--success`, `--bg-card`, `--border`, `--radius`, `--shadow`

## Database

- SQLite, auto-created at `DATA_DIR/vocab.db`
- Migration: ALTER TABLE added in `app.py` after `Base.metadata.create_all()`
- Existing `chinese` column migration uses try/except for idempotency
