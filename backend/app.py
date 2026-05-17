import os
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from database import engine, Base
from routes import words, review, stats, media

# Path resolution
# PyInstaller: code in _MEIPASS, user data next to exe
# Normal run: everything relative to this file's directory
if getattr(sys, "frozen", False):
    CODE_DIR = sys._MEIPASS
    DATA_DIR = os.path.dirname(sys.executable)
else:
    CODE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_DIR = CODE_DIR

FRONTEND_DIST = os.path.join(CODE_DIR, "frontend", "dist")
# For normal python run, frontend dist is at ../frontend/dist relative to backend/
if not os.path.isdir(FRONTEND_DIST):
    FRONTEND_DIST = os.path.join(os.path.dirname(CODE_DIR), "frontend", "dist")

AUDIO_DIR = os.path.join(DATA_DIR, "audio")
IMAGE_DIR = os.path.join(DATA_DIR, "images")
os.makedirs(AUDIO_DIR, exist_ok=True)
os.makedirs(IMAGE_DIR, exist_ok=True)

# Copy seed files from bundle (PyInstaller _MEIPASS) to DATA_DIR
if getattr(sys, "frozen", False):
    import shutil
    for subdir in ("audio", "images"):
        src = os.path.join(CODE_DIR, subdir)
        dst = os.path.join(DATA_DIR, subdir)
        if os.path.isdir(src):
            for fname in os.listdir(src):
                dst_file = os.path.join(dst, fname)
                if not os.path.exists(dst_file):
                    try:
                        shutil.copy2(os.path.join(src, fname), dst_file)
                    except OSError:
                        pass

Base.metadata.create_all(bind=engine)

# Migration: add chinese column for existing databases
try:
    from sqlalchemy import text as sa_text
    with engine.connect() as conn:
        conn.execute(sa_text("ALTER TABLE words ADD COLUMN chinese VARCHAR(500) DEFAULT ''"))
        conn.commit()
except Exception:
    pass  # column already exists

# Migration: add meanings column
try:
    with engine.connect() as conn:
        conn.execute(sa_text("ALTER TABLE words ADD COLUMN meanings TEXT DEFAULT ''"))
        conn.commit()
except Exception:
    pass

app = FastAPI(title="Vocabulary Review API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/audio", StaticFiles(directory=AUDIO_DIR), name="audio")
app.mount("/api/media/images", StaticFiles(directory=IMAGE_DIR), name="images")

app.include_router(words.router)
app.include_router(review.router)
app.include_router(stats.router)
app.include_router(media.router)


@app.get("/api/health")
def health():
    return {"status": "ok", "words": 0}


# Serve frontend SPA
if os.path.isdir(FRONTEND_DIST):
    app.mount("/", StaticFiles(directory=FRONTEND_DIST, html=True), name="frontend")
