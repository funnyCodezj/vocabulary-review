from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy.orm import Session
import os, httpx, logging

from database import get_db
from models import Word
from config import AUDIO_DIR, IMAGE_DIR

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/media", tags=["media"])


@router.get("/audio/{word_id}")
def get_audio(word_id: int, db: Session = Depends(get_db)):
    """Return cached audio file path, or trigger generation."""
    word = db.query(Word).filter(Word.id == word_id).first()
    if not word:
        raise HTTPException(404, "Word not found")

    if word.audio_path and os.path.exists(word.audio_path):
        return FileResponse(word.audio_path, media_type="audio/mp3")

    raise HTTPException(404, "Audio not generated yet. Use POST /api/media/audio/{word_id} first.")


@router.post("/audio/{word_id}")
def generate_audio(word_id: int, db: Session = Depends(get_db)):
    """Generate audio for a word using edge-tts."""
    from services.audio import generate_audio_for_word

    word = db.query(Word).filter(Word.id == word_id).first()
    if not word:
        raise HTTPException(404, "Word not found")

    audio_path = generate_audio_for_word(word.word)
    word.audio_path = audio_path
    db.commit()
    return {"audio_path": audio_path}


@router.get("/ping")
def ping():
    """Debug endpoint to verify this code is running."""
    return {"version": "2.0", "image_dir": IMAGE_DIR}


@router.post("/image/{word_id}")
def fetch_image(word_id: int, db: Session = Depends(get_db)):
    """Fetch image for a word, download to local storage."""
    from services.image import fetch_image_for_word

    word = db.query(Word).filter(Word.id == word_id).first()
    if not word:
        raise HTTPException(404, "Word not found")

    # extract previous photo id from source (format: "pexels:12345")
    prev_photo_id = None
    if word.image_source and ":" in word.image_source:
        prev_photo_id = word.image_source.split(":", 1)[1]

    external_url, source, photo_id = fetch_image_for_word(word.word, prev_photo_id)
    logger.info(f"fetch_image word={word.word} external_url={external_url} source={source} photo_id={photo_id}")
    if not external_url:
        word.image_url = generate_placeholder(word.word)
        word.image_source = "placeholder"
        db.commit()
        return {"image_url": word.image_url, "source": "placeholder"}

    # delete old local image file if it exists
    old_path = os.path.join(IMAGE_DIR, f"{word_id}.jpg")
    if os.path.exists(old_path):
        os.remove(old_path)

    import time
    ts = int(time.time())

    # download and save new image locally
    try:
        resp = httpx.get(external_url, timeout=15, verify=False, follow_redirects=True)
        if resp.status_code == 200:
            with open(old_path, "wb") as f:
                f.write(resp.content)
            word.image_url = f"/api/media/images/{word_id}.jpg?t={ts}"
            word.image_source = f"{source}:{photo_id}" if photo_id else source
        else:
            word.image_url = generate_placeholder(word.word)
            word.image_source = "placeholder"
    except Exception as e:
        logger.error(f"download failed: {e}")
        word.image_url = generate_placeholder(word.word)
        word.image_source = "placeholder"

    logger.info(f"result image_url={word.image_url}")
    db.commit()
    return {"image_url": word.image_url, "source": word.image_source}


@router.post("/batch-images")
def batch_fetch_images(db: Session = Depends(get_db)):
    """Batch fetch images for words missing them (max 50 per call)."""
    from services.image import fetch_image_for_word

    words = db.query(Word).filter(Word.image_url == "").limit(50).all()
    fetched = 0
    for word in words:
        try:
            external_url, source, photo_id = fetch_image_for_word(word.word)
            if not external_url:
                word.image_url = generate_placeholder(word.word)
                word.image_source = "placeholder"
                fetched += 1
                continue

            save_path = os.path.join(IMAGE_DIR, f"{word.id}.jpg")
            resp = httpx.get(external_url, timeout=15, verify=False, follow_redirects=True)
            if resp.status_code == 200:
                with open(save_path, "wb") as f:
                    f.write(resp.content)
                word.image_url = f"/api/media/images/{word.id}.jpg"
                word.image_source = f"{source}:{photo_id}" if photo_id else source
            else:
                word.image_url = generate_placeholder(word.word)
                word.image_source = "placeholder"
            fetched += 1
        except Exception:
            continue
    db.commit()
    remaining = db.query(Word).filter(Word.image_url == "").count()
    return {"fetched": fetched, "remaining": remaining, "batch_size": 50}


def generate_placeholder(word: str) -> str:
    """Generate a simple SVG placeholder based on the word."""
    import hashlib
    colors = ["#4A90D9", "#50C878", "#E87461", "#9B59B6", "#F39C12", "#1ABC9C"]
    idx = int(hashlib.md5(word.encode()).hexdigest(), 16) % len(colors)
    color = colors[idx]
    letter = word[0].upper() if word else "?"

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="400" height="300" viewBox="0 0 400 300">
  <rect width="400" height="300" fill="{color}" rx="8"/>
  <text x="200" y="160" text-anchor="middle" dominant-baseline="central"
        font-family="Arial,sans-serif" font-size="80" font-weight="bold" fill="white">{letter}</text>
  <text x="200" y="220" text-anchor="middle" dominant-baseline="central"
        font-family="Arial,sans-serif" font-size="18" fill="rgba(255,255,255,0.8)">{word}</text>
</svg>'''
    return f"data:image/svg+xml;base64,{__import__('base64').b64encode(svg.encode()).decode()}"
