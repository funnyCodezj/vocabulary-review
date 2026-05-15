# Vocabulary Review / 单词复习

An English vocabulary memorization tool based on **SM-2 spaced repetition algorithm**. Supports flashcard review, multiple-choice quizzes, Chinese translations, image fetching, and TTS audio. Packaged as a single Windows executable (no Python required).

基于 **SM-2 间隔重复算法** 的英语单词记忆工具。支持翻卡复习、选择题测验、中文翻译、图片获取和 TTS 语音。打包为单个 Windows exe 文件，无需 Python 环境。

---

## Features / 功能

- **Spaced Repetition (SM-2)** — Smart review scheduling based on your memory performance
- **Flashcard Review** — Flip cards to recall meanings, rate your memory on a 5-level scale
- **Multiple-Choice Quiz** — Four-option quiz to test your knowledge
- **Chinese Translations** — Import JSON with `{"en": "...", "zh": "..."}` format, auto-translate via MyMemory API
- **Text-to-Speech** — Edge TTS for English pronunciation
- **Image Search** — Auto-fetch images from Pexels / Unsplash / Picsum
- **Wrong Answer Collection** — Track and review words you frequently miss
- **Batch Import** — TXT or JSON file import
- **Dictionary Lookup** — Auto-fetch phonetic, definition, and example sentences
- **Single EXE** — One-click start, auto-opens browser

---

## Quick Start / 快速开始

### Option 1: Download EXE (recommended)

Download `VocabularyReview.exe` from Releases, double-click to run. The browser opens automatically at `http://localhost:8004`.

### Option 2: Run from Source

**Backend:**
```bash
cd backend
pip install -r requirements.txt
python main.py
```

**Frontend (development):**
```bash
cd frontend
npm install
npm run dev
```

---

## Usage / 使用说明

1. **Import words** — Upload a TXT or JSON file on the import page
   - TXT: one word per line, optional `word,phonetic` format
   - JSON: `[{"en": "apple", "zh": "苹果"}, ...]`
2. **Review** — Use flashcard or quiz mode to practice
3. **Track** — Check your stats on the home page, review wrong answers
4. **Customize** — Set Pexels/Unsplash API keys in `.env` for image search

---

## Tech Stack / 技术栈

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.10+, FastAPI, SQLAlchemy, SQLite |
| Frontend | Vue 3 (Composition API), Vite, Pinia, Vue Router |
| APIs | Free Dictionary API, MyMemory Translation API, Edge TTS, Pexels / Unsplash |
| Packaging | PyInstaller (single-file EXE) |

---

## Project Structure / 项目结构

```
VocabularyReview/
├── backend/
│   ├── main.py              # Entry point
│   ├── app.py               # FastAPI app + static file serving
│   ├── config.py            # Paths, API keys
│   ├── database.py          # SQLAlchemy engine
│   ├── models.py            # ORM models
│   ├── schemas.py           # Pydantic schemas
│   ├── routes/
│   │   ├── words.py         # Word CRUD, import, dictionary
│   │   ├── review.py        # SM-2 review, errors
│   │   ├── stats.py         # Statistics
│   │   └── media.py         # Audio & image endpoints
│   └── services/
│       ├── dictionary.py    # Free Dictionary API + MyMemory
│       ├── audio.py         # Edge TTS generation
│       ├── image.py         # Image search (Pexels/Unsplash/Picsum)
│       └── spaced_repetition.py  # SM-2 algorithm
├── frontend/
│   └── src/
│       ├── views/           # Page components
│       ├── components/      # Reusable components
│       ├── api/index.js     # Axios API client
│       └── router/index.js  # Vue Router
├── dist_exe/                # Built EXE output
└── README.md
```

---

## Build EXE / 打包

```bash
cd backend
pyinstaller --clean --onefile --name "VocabularyReview" --distpath "..\dist_exe" \
  --add-data "..\frontend\dist;frontend\dist" \
  --add-data ".env;." --add-data "audio;audio" --add-data "images;images" \
  --hidden-import "uvicorn.logging" --hidden-import "uvicorn.loops.auto" \
  --hidden-import "uvicorn.protocols.http.auto" --hidden-import "uvicorn.protocols.http.h11_impl" \
  --hidden-import "uvicorn.lifespan.on" --hidden-import "dotenv" \
  --hidden-import "edge_tts" --hidden-import "sqlalchemy" \
  --collect-all "uvicorn" --collect-all "edge_tts" "main.py"
```

---

## License / 许可

MIT
