import asyncio, os, json
from fastapi import APIRouter, Depends, Query, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import date

from database import get_db
from models import Word, UserProgress
from schemas import WordOut, WordDetail, WordListResponse, MeaningItem
from services.dictionary import fetch_word_data, fetch_chinese_translation, translate_examples
from config import IMAGE_DIR

router = APIRouter(prefix="/api/words", tags=["words"])


@router.get("", response_model=WordListResponse)
def list_words(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    search: Optional[str] = None,
    stage_filter: str = Query("all", description="all, new, due, learning, reviewing, mastered, errors"),
    db: Session = Depends(get_db),
):
    query = db.query(Word)
    if search:
        query = query.filter(Word.word.ilike(f"%{search}%"))

    query = query.outerjoin(Word.progress)

    today = date.today()
    if stage_filter == "new":
        query = query.filter(
            (UserProgress.id == None) | (UserProgress.stage == 0)
        )
    elif stage_filter == "due":
        query = query.filter(
            (UserProgress.id != None) &
            (UserProgress.next_review_date <= today)
        )
    elif stage_filter == "learning":
        query = query.filter(UserProgress.stage == 1)
    elif stage_filter == "reviewing":
        query = query.filter(UserProgress.stage.in_([2, 3]))
    elif stage_filter == "mastered":
        query = query.filter(UserProgress.stage.in_([4, 5]))
    elif stage_filter == "errors":
        query = query.filter(
            (UserProgress.incorrect_count > 0) & (UserProgress.id != None)
        )
    # "all" — no filter

    total = query.count()

    items = (
        query.order_by(Word.word.asc())
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


@router.post("/{word_id}/clear-image")
def clear_word_image(word_id: int, db: Session = Depends(get_db)):
    """Delete the local image and reset image_url to placeholder."""
    word = db.query(Word).filter(Word.id == word_id).first()
    if not word:
        raise HTTPException(404, "Word not found")
    img_path = os.path.join(IMAGE_DIR, f"{word_id}.jpg")
    if os.path.exists(img_path):
        os.remove(img_path)
    word.image_url = ""
    word.image_source = ""
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
        # TXT format: one word per line, or "word 中文"
        lines = [line.strip() for line in content.splitlines() if line.strip()]
        for line in lines:
            parts = line.split(maxsplit=1)
            word_text = parts[0].strip().lower()
            if not word_text:
                continue
            exists = db.query(Word).filter(Word.word == word_text).first()
            if exists:
                skipped += 1
                continue
            db_word = Word(word=word_text)
            if len(parts) > 1:
                db_word.chinese = parts[1].strip()
            db.add(db_word)
            imported += 1
    db.commit()
    return {"imported": imported, "skipped": skipped, "updated": updated, "total": imported + skipped}


@router.post("/{word_id}/dict")
def fetch_dictionary_data(word_id: int, db: Session = Depends(get_db)):
    """Fetch dictionary data with all parts of speech, definitions, and examples."""
    word = db.query(Word).filter(Word.id == word_id).first()
    if not word:
        raise HTTPException(404, "Word not found")

    data = asyncio.run(fetch_word_data(word.word))
    if not data:
        raise HTTPException(404, f"No dictionary data found for '{word.word}'")

    word.phonetic = data.get("phonetic", "")
    raw_meanings = data.get("meanings", [])

    # translate examples to Chinese
    raw_meanings = asyncio.run(translate_examples(raw_meanings))

    # store all meanings as JSON
    meaning_list = []
    for m in raw_meanings:
        meaning_list.append({
            "pos": m.get("partOfSpeech", ""),
            "definition": m.get("definition", ""),
            "example": m.get("example", ""),
            "example_cn": m.get("chinese", ""),
        })
    word.meanings = json.dumps(meaning_list, ensure_ascii=False)

    # keep first meaning in legacy fields for backward compat
    if meaning_list:
        word.part_of_speech = meaning_list[0]["pos"]
        word.definition = meaning_list[0]["definition"]
        word.example = meaning_list[0]["example"]

    if not word.chinese:
        word.chinese = asyncio.run(fetch_chinese_translation(word.word))

    db.commit()
    return {"ok": True, "word": word.word, "meanings_count": len(meaning_list)}


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
                raw_meanings = data.get("meanings", [])
                raw_meanings = asyncio.run(translate_examples(raw_meanings))
                meaning_list = []
                for m in raw_meanings:
                    meaning_list.append({
                        "pos": m.get("partOfSpeech", ""),
                        "definition": m.get("definition", ""),
                        "example": m.get("example", ""),
                        "example_cn": m.get("chinese", ""),
                    })
                word.meanings = json.dumps(meaning_list, ensure_ascii=False)
                if meaning_list:
                    word.part_of_speech = meaning_list[0]["pos"]
                    word.definition = meaning_list[0]["definition"]
                    word.example = meaning_list[0]["example"]
                if not word.chinese:
                    word.chinese = asyncio.run(fetch_chinese_translation(word.word))
                filled += 1
        except Exception:
            continue
    db.commit()
    return {"filled": filled, "remaining": db.query(Word).filter(Word.definition == "").count()}


def _parse_meanings(word: Word) -> list:
    if not word.meanings:
        return []
    try:
        return json.loads(word.meanings)
    except (json.JSONDecodeError, TypeError):
        return []


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
        meanings=[MeaningItem(**m) for m in _parse_meanings(word)],
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
        meanings=[MeaningItem(**m) for m in _parse_meanings(word)],
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
