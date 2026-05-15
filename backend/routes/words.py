import asyncio, os
from fastapi import APIRouter, Depends, Query, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import Optional

from database import get_db
from models import Word, UserProgress
from schemas import WordOut, WordDetail, WordListResponse
from services.dictionary import fetch_word_data, fetch_chinese_translation
from config import IMAGE_DIR

router = APIRouter(prefix="/api/words", tags=["words"])


@router.get("", response_model=WordListResponse)
def list_words(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    search: Optional[str] = None,
    stage: Optional[int] = None,
    sort_by: str = "word",
    sort_order: str = "asc",
    db: Session = Depends(get_db),
):
    query = db.query(Word)
    if search:
        query = query.filter(Word.word.ilike(f"%{search}%"))

    # join progress if needed for filter or sort
    if stage is not None or sort_by == "stage":
        query = query.outerjoin(Word.progress)

    if stage is not None:
        query = query.filter(UserProgress.stage == stage)

    total = query.count()

    # apply sorting
    if sort_by == "stage":
        col = UserProgress.stage
        items = (
            query.order_by(col.asc().nullsfirst() if sort_order == "asc" else col.desc().nullslast())
            .offset((page - 1) * page_size).limit(page_size).all()
        )
    else:
        col = Word.word
        items = (
            query.order_by(col.asc() if sort_order == "asc" else col.desc())
            .offset((page - 1) * page_size).limit(page_size).all()
        )

    return WordListResponse(
        items=[_word_to_out(w) for w in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{word_id}", response_model=WordDetail)
def get_word(word_id: int, db: Session = Depends(get_db)):
    word = db.query(Word).filter(Word.id == word_id).first()
    if not word:
        raise HTTPException(404, "Word not found")
    return _word_to_detail(word)


@router.delete("/clear-all")
def clear_all_words(db: Session = Depends(get_db)):
    """Delete all words, progress data, and local images."""
    from models import ReviewLog, ReviewSession
    import shutil
    count = db.query(Word).count()
    db.query(ReviewLog).delete()
    db.query(ReviewSession).delete()
    db.query(UserProgress).delete()
    db.query(Word).delete()
    db.commit()
    # remove all local image files
    if os.path.exists(IMAGE_DIR):
        shutil.rmtree(IMAGE_DIR)
        os.makedirs(IMAGE_DIR, exist_ok=True)
    return {"ok": True, "deleted": count}


@router.delete("/{word_id}")
def delete_word(word_id: int, db: Session = Depends(get_db)):
    word = db.query(Word).filter(Word.id == word_id).first()
    if not word:
        raise HTTPException(404, "Word not found")
    # delete local image file
    img_path = os.path.join(IMAGE_DIR, f"{word_id}.jpg")
    if os.path.exists(img_path):
        os.remove(img_path)
    db.delete(word)
    db.commit()
    return {"ok": True}


@router.post("/import", response_model=dict)
def import_words(file: UploadFile = File(...), db: Session = Depends(get_db)):
    import json
    content = file.file.read().decode("utf-8")
    imported = 0
    skipped = 0
    updated = 0

    # detect JSON format
    if file.filename and file.filename.lower().endswith(".json"):
        try:
            data = json.loads(content)
        except json.JSONDecodeError:
            raise HTTPException(400, "Invalid JSON file")
        if not isinstance(data, list):
            raise HTTPException(400, "JSON must be an array of objects with 'en' and 'zh' fields")
        for item in data:
            en = item.get("en", "").strip().lower()
            zh = item.get("zh", "").strip()
            if not en:
                continue
            exists = db.query(Word).filter(Word.word == en).first()
            if exists:
                if zh and not exists.chinese:
                    exists.chinese = zh
                    updated += 1
                skipped += 1
                continue
            db_word = Word(word=en, chinese=zh)
            db.add(db_word)
            imported += 1
    else:
        # TXT format: one word per line, or "word,phonetic"
        lines = [line.strip() for line in content.splitlines() if line.strip()]
        for line in lines:
            parts = line.split(",")
            word_text = parts[0].strip().lower()
            if not word_text:
                continue
            exists = db.query(Word).filter(Word.word == word_text).first()
            if exists:
                skipped += 1
                continue
            db_word = Word(word=word_text)
            if len(parts) > 1:
                db_word.phonetic = parts[1].strip()
            db.add(db_word)
            imported += 1
    db.commit()
    return {"imported": imported, "skipped": skipped, "updated": updated, "total": imported + skipped}


@router.post("/{word_id}/dict")
def fetch_dictionary_data(word_id: int, db: Session = Depends(get_db)):
    """Fetch dictionary data (phonetic, definition, example) for a word."""
    word = db.query(Word).filter(Word.id == word_id).first()
    if not word:
        raise HTTPException(404, "Word not found")

    data = asyncio.run(fetch_word_data(word.word))
    if not data:
        raise HTTPException(404, f"No dictionary data found for '{word.word}'")

    word.phonetic = data.get("phonetic", "")
    meanings = data.get("meanings", [])
    if meanings:
        m = meanings[0]
        word.part_of_speech = m.get("partOfSpeech", "")
        defs = m.get("definitions", [])
        if defs:
            word.definition = defs[0].get("definition", "")
            word.example = defs[0].get("example", "")

    if not word.chinese:
        word.chinese = asyncio.run(fetch_chinese_translation(word.word))

    db.commit()
    return {"ok": True, "word": word.word, "phonetic": word.phonetic,
            "definition": word.definition, "chinese": word.chinese}


@router.post("/batch-translate")
def batch_translate(db: Session = Depends(get_db)):
    """Batch-fetch Chinese translations for words missing them."""
    words = db.query(Word).filter(Word.chinese == "").limit(50).all()
    translated = 0
    for word in words:
        try:
            chinese = asyncio.run(fetch_chinese_translation(word.word))
            if chinese:
                word.chinese = chinese
                translated += 1
        except Exception:
            continue
    db.commit()
    remaining = db.query(Word).filter(Word.chinese == "").count()
    return {"translated": translated, "remaining": remaining}


@router.post("/fill-dict")
def batch_fill_dictionary(db: Session = Depends(get_db)):
    """Batch-fill dictionary data for words missing definitions."""
    words = db.query(Word).filter(Word.definition == "").limit(50).all()
    filled = 0
    for word in words:
        try:
            data = asyncio.run(fetch_word_data(word.word))
            if data:
                word.phonetic = data.get("phonetic", "")
                meanings = data.get("meanings", [])
                if meanings:
                    m = meanings[0]
                    word.part_of_speech = m.get("partOfSpeech", "")
                    defs = m.get("definitions", [])
                    if defs:
                        word.definition = defs[0].get("definition", "")
                        word.example = defs[0].get("example", "")
                if not word.chinese:
                    word.chinese = asyncio.run(fetch_chinese_translation(word.word))
                filled += 1
        except Exception:
            continue
    db.commit()
    return {"filled": filled, "remaining": db.query(Word).filter(Word.definition == "").count()}


def _word_to_out(word: Word) -> WordOut:
    stage = word.progress.stage if word.progress else 0
    next_review = word.progress.next_review_date if word.progress else None
    return WordOut(
        id=word.id,
        word=word.word,
        phonetic=word.phonetic,
        part_of_speech=word.part_of_speech,
        definition=word.definition,
        example=word.example,
        chinese=word.chinese or "",
        image_url=word.image_url,
        image_source=word.image_source,
        audio_path=word.audio_path,
        stage=stage,
        next_review_date=next_review,
        created_at=word.created_at,
    )


def _word_to_detail(word: Word) -> WordDetail:
    p = word.progress
    return WordDetail(
        id=word.id,
        word=word.word,
        phonetic=word.phonetic,
        part_of_speech=word.part_of_speech,
        definition=word.definition,
        example=word.example,
        chinese=word.chinese or "",
        image_url=word.image_url,
        image_source=word.image_source,
        audio_path=word.audio_path,
        stage=p.stage if p else 0,
        repetition=p.repetition if p else 0,
        ease_factor=p.ease_factor if p else 2.5,
        interval=p.interval if p else 0,
        correct_count=p.correct_count if p else 0,
        incorrect_count=p.incorrect_count if p else 0,
        last_reviewed=p.last_reviewed if p else None,
        next_review_date=p.next_review_date if p else None,
        created_at=word.created_at,
    )
