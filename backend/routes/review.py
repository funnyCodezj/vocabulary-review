from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import date, datetime, timedelta

from database import get_db
from models import Word, UserProgress, ReviewSession, ReviewLog
from schemas import ReviewNextResponse, ReviewSubmit, WordDetail, ErrorWordsResponse, ErrorWord
from services.spaced_repetition import sm2_calculate

router = APIRouter(prefix="/api/review", tags=["review"])


@router.post("/next", response_model=ReviewNextResponse)
def next_word(
    stage_filter: str = Query("due", description="due, all, new, learning, reviewing, mastered"),
    db: Session = Depends(get_db)
):
    """Get the next word for review, optionally filtered by stage."""
    today = date.today()
    query = db.query(Word).outerjoin(UserProgress)

    if stage_filter == "new":
        query = query.filter(
            (UserProgress.id == None) |  # noqa: never reviewed
            (UserProgress.stage == 0)
        )
    elif stage_filter == "learning":
        query = query.filter(UserProgress.stage == 1)
    elif stage_filter == "reviewing":
        query = query.filter(UserProgress.stage.in_([2, 3]))
    elif stage_filter == "mastered":
        query = query.filter(UserProgress.stage.in_([4, 5]))
    elif stage_filter == "all":
        pass  # no filter, show all words
    else:
        # "due" — default SM-2 behaviour
        query = query.filter(
            (UserProgress.id == None) |  # noqa: never reviewed
            (UserProgress.next_review_date <= today)
        )

    word = (
        query
        .order_by(UserProgress.next_review_date.asc().nullsfirst())
        .first()
    )
    if not word:
        raise HTTPException(404, "No words due for review")

    # ensure UserProgress exists
    if not word.progress:
        word.progress = UserProgress(word_id=word.id)
        db.commit()

    return ReviewNextResponse(word=_word_to_detail(word))


@router.post("/submit")
def submit_review(data: ReviewSubmit, db: Session = Depends(get_db)):
    """Submit review result and update SM-2 progress."""
    word = db.query(Word).filter(Word.id == data.word_id).first()
    if not word:
        raise HTTPException(404, "Word not found")

    p = word.progress
    if not p:
        p = UserProgress(word_id=word.id)
        db.add(p)
        db.flush()

    # apply SM-2 algorithm
    new_stage, new_repetition, new_ef, new_interval = sm2_calculate(
        quality=data.quality,
        repetition=p.repetition,
        ease_factor=p.ease_factor,
        interval=p.interval,
    )

    p.stage = new_stage
    p.repetition = new_repetition
    p.ease_factor = new_ef
    p.interval = new_interval
    p.last_reviewed = datetime.now()
    p.next_review_date = date.today() + timedelta(days=new_interval)

    if data.quality >= 3:
        p.correct_count = (p.correct_count or 0) + 1
    else:
        p.incorrect_count = (p.incorrect_count or 0) + 1

    # log to review session
    today = date.today()
    session = db.query(ReviewSession).filter(
        ReviewSession.date == today
    ).first()
    if not session:
        session = ReviewSession(date=today)
        db.add(session)
        db.flush()

    log = ReviewLog(
        word_id=data.word_id,
        session_id=session.id,
        quality=data.quality,
        response_time_ms=data.response_time_ms,
    )
    db.add(log)

    session.total_reviewed = (session.total_reviewed or 0) + 1
    if data.quality >= 3:
        session.correct_count = (session.correct_count or 0) + 1

    db.commit()
    return {
        "ok": True,
        "stage": p.stage,
        "next_review_date": str(p.next_review_date),
        "interval_days": new_interval,
    }


@router.post("/errors/{word_id}/clear")
def clear_error(word_id: int, db: Session = Depends(get_db)):
    """Reset incorrect_count for a word (remove from error list)."""
    word = db.query(Word).filter(Word.id == word_id).first()
    if not word:
        raise HTTPException(404, "Word not found")
    if word.progress:
        word.progress.incorrect_count = 0
        db.commit()
    return {"ok": True}


@router.get("/errors", response_model=ErrorWordsResponse)
def error_words(db: Session = Depends(get_db)):
    """Get words that have been answered incorrectly."""
    words = (
        db.query(Word)
        .join(UserProgress)
        .filter(UserProgress.incorrect_count > 0)
        .order_by(UserProgress.last_reviewed.desc().nullslast())
        .all()
    )
    items = [ErrorWord(
        id=w.id, word=w.word, chinese=w.chinese or "",
        definition=w.definition, phonetic=w.phonetic,
        image_url=w.image_url,
        incorrect_count=w.progress.incorrect_count or 0,
        correct_count=w.progress.correct_count or 0,
        stage=w.progress.stage or 0,
    ) for w in words]
    return ErrorWordsResponse(items=items, total=len(items))


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
