# 单词复习 (Vocabulary Review)

[中文](#中文) | [English](#english)

> 基于 SM-2 间隔重复算法的英语单词记忆工具。支持翻卡复习、选择题测验、中文翻译、TTS 语音朗读和图片搜索。可打包为单个 Windows exe 文件，无需依赖 Python 环境。
>
> An English vocabulary memorization tool based on SM-2 spaced repetition. Supports flashcard review, multiple-choice quizzes, Chinese translations, TTS audio playback, and image search. Ships as a single Windows executable — no Python required.

---

## 中文

### 功能特性

- **间隔重复（SM-2）** — 根据记忆表现智能安排复习计划
- **翻卡复习** — 翻转卡片回忆释义，五级评分
- **选择题测验** — 四选一测试，巩固记忆
- **中文翻译** — 支持 JSON 格式导入 `{"en": "apple", "zh": "苹果"}`，也可通过 MyMemory API 自动翻译
- **语音朗读** — 基于 Edge TTS 的英语发音
- **图片搜索** — 自动从 Pexels / Unsplash / Picsum 获取配图
- **错题集** — 跟踪并回顾常错的单词
- **阶段筛选** — 单词列表按新词/待复习/学习中/复习中/已掌握/错题筛选
- **范围选择** — 翻卡复习和测验前可选择范围（全部/新词/待复习/学习中/复习中/已掌握/错题）
- **快捷键支持** — 翻卡复习支持空格键翻面与快速评分
- **统计导航** — 首页统计卡片点击直达对应筛选列表
- **批量导入** — 支持 TXT 和 JSON 格式批量导入
- **词典查询** — 自动获取音标、释义和例句
- **单文件运行** — 一键启动，自动打开浏览器

### 快速开始

#### 方式一：下载 EXE（推荐）

下载 `VocabularyReview.exe`，双击运行，浏览器自动打开 `http://localhost:8001`。

#### 方式二：源码运行

**后端：**

```bash
cd backend
pip install -r requirements.txt
python main.py
```

**前端（开发模式）：**

```bash
cd frontend
npm install
npm run dev
```

### 使用说明

1. **导入单词** — 在导入页面上传 TXT 或 JSON 文件
   - TXT：每行一个单词，可选 `单词 中文` 格式（空格分隔）
   - JSON：`[{"en": "apple", "zh": "苹果"}, ...]`
2. **复习** — 使用翻卡或测验模式练习
3. **跟踪** — 首页查看统计，错题集回顾答错的单词
4. **自定义** — 在 `.env` 中配置 Pexels/Unsplash API 密钥

### 技术栈

| 层级 | 技术 |
|------|------|
| 后端 | Python 3.10+, FastAPI, SQLAlchemy, SQLite |
| 前端 | Vue 3 (Composition API), Vite, Pinia, Vue Router |
| 接口服务 | Free Dictionary API, MyMemory 翻译 API, Edge TTS, Pexels / Unsplash |
| 打包 | PyInstaller（单文件 EXE） |

### 项目结构

```
VocabularyReview/
├── backend/
│   ├── main.py               # 入口文件
│   ├── app.py                # FastAPI 应用 + 静态文件服务
│   ├── config.py             # 路径和密钥配置
│   ├── database.py           # SQLAlchemy 引擎
│   ├── models.py             # ORM 模型
│   ├── schemas.py            # Pydantic 数据模型
│   ├── routes/
│   │   ├── words.py          # 单词增删改查、导入、词典
│   │   ├── review.py         # SM-2 复习、错题
│   │   ├── stats.py          # 统计
│   │   └── media.py          # 音频和图片接口
│   └── services/
│       ├── dictionary.py     # 词典 API + MyMemory 翻译
│       ├── audio.py          # Edge TTS 语音生成
│       ├── image.py          # 图片搜索
│       └── spaced_repetition.py  # SM-2 算法
├── frontend/
│   └── src/
│       ├── views/            # 页面组件
│       ├── components/       # 可复用组件
│       ├── api/index.js      # Axios API 客户端
│       └── router/index.js   # 路由配置
├── dist_exe/                 # 打包后的 EXE 输出
└── README.md
```

### 打包为 EXE

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

## English

### Features

- **Spaced Repetition (SM-2)** — Smart review scheduling based on your memory performance
- **Flashcard Review** — Flip cards to recall meanings with a 5-level rating
- **Multiple-Choice Quiz** — Four-option quiz to reinforce learning
- **Chinese Translations** — Import via JSON (`{"en": "apple", "zh": "苹果"}`) or auto-translate with MyMemory API
- **Text-to-Speech** — Edge TTS for English pronunciation
- **Image Search** — Auto-fetch images from Pexels / Unsplash / Picsum
- **Wrong Answer Collection** — Track and review frequently missed words
- **Stage Filter** — Filter word list by new/due/learning/reviewing/mastered/errors
- **Mode Selection** — Choose review scope before starting flashcard or quiz mode
- **Keyboard Shortcuts** — Space key to flip and rate in flashcard mode
- **Stats Navigation** — Click stat cards on home page to jump to filtered word list
- **Batch Import** — TXT or JSON file import
- **Dictionary Lookup** — Auto-fetch phonetic, definition, and example sentences
- **Single EXE** — One-click start with auto browser launch

### Quick Start

#### Option 1: Download EXE (recommended)

Download `VocabularyReview.exe`, double-click to run. The browser opens automatically at `http://localhost:8004`.

#### Option 2: Run from Source

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

### Usage

1. **Import words** — Upload a TXT or JSON file on the import page
   - TXT: one word per line, optional `word 中文` format (space-separated)
   - JSON: `[{"en": "apple", "zh": "苹果"}, ...]`
2. **Review** — Use flashcard or quiz mode to practice
3. **Track** — Check stats on the home page, review wrong answers
4. **Customize** — Set Pexels/Unsplash API keys in `.env` for image search

### Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.10+, FastAPI, SQLAlchemy, SQLite |
| Frontend | Vue 3 (Composition API), Vite, Pinia, Vue Router |
| APIs | Free Dictionary API, MyMemory Translation API, Edge TTS, Pexels / Unsplash |
| Packaging | PyInstaller (single-file EXE) |

### Project Structure

```
VocabularyReview/
├── backend/
│   ├── main.py               # Entry point
│   ├── app.py                # FastAPI app + static file serving
│   ├── config.py             # Paths and API keys
│   ├── database.py           # SQLAlchemy engine
│   ├── models.py             # ORM models
│   ├── schemas.py            # Pydantic schemas
│   ├── routes/
│   │   ├── words.py          # Word CRUD, import, dictionary
│   │   ├── review.py         # SM-2 review, error tracking
│   │   ├── stats.py          # Statistics
│   │   └── media.py          # Audio & image endpoints
│   └── services/
│       ├── dictionary.py     # Dictionary API + MyMemory translation
│       ├── audio.py          # Edge TTS generation
│       ├── image.py          # Image search
│       └── spaced_repetition.py  # SM-2 algorithm
├── frontend/
│   └── src/
│       ├── views/            # Page components
│       ├── components/       # Reusable components
│       ├── api/index.js      # Axios API client
│       └── router/index.js   # Vue Router config
├── dist_exe/                 # Built EXE output
└── README.md
```

### Build EXE

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

## License

MIT
