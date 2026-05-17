from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List
from datetime import datetime, date

from database import get_db
from models import Word, UserProgress, ReviewSession, ReviewLog

router = APIRouter(prefix="/api/backup", tags=["backup"])


def _serialize_word(w):
    return {
        "id": w.id, "word": w.word, "phonetic": w.phonetic,
        "part_of_speech": w.part_of_speech, "definition": w.definition,
        "example": w.example, "image_url": w.image_url,
        "image_source": w.image_source, "audio_path": w.audio_path,
        "chinese": w.chinese, "meanings": w.meanings,
        "created_at": w.created_at.isoformat() if w.created_at else None,
        "updated_at": w.updated_at.isoformat() if w.updated_at else None,
    }


def _serialize_progress(p):
    return {
        "id": p.id, "word_id": p.word_id, "stage": p.stage,
        "repetition": p.repetition, "ease_factor": p.ease_factor,
        "interval": p.interval, "correct_count": p.correct_count,
        "incorrect_count": p.incorrect_count,
        "last_reviewed": p.last_reviewed.isoformat() if p.last_reviewed else None,
        "next_review_date": p.next_review_date.isoformat() if p.next_review_date else None,
    }


def _serialize_session(s):
    return {
        "id": s.id,
        "date": s.date.isoformat() if s.date else None,
        "total_reviewed": s.total_reviewed,
        "correct_count": s.correct_count,
        "duration_minutes": s.duration_minutes,
    }


def _serialize_log(l):
    return {
        "id": l.id, "word_id": l.word_id, "session_id": l.session_id,
        "quality": l.quality, "response_time_ms": l.response_time_ms,
        "reviewed_at": l.reviewed_at.isoformat() if l.reviewed_at else None,
    }


@router.get("/export")
def export_data(db: Session = Depends(get_db)):
    words = db.query(Word).all()
    progress = db.query(UserProgress).all()
    sessions = db.query(ReviewSession).all()
    logs = db.query(ReviewLog).all()

    return {
        "version": 1,
        "exported_at": datetime.now().isoformat(),
        "words": [_serialize_word(w) for w in words],
        "progress": [_serialize_progress(p) for p in progress],
        "sessions": [_serialize_session(s) for s in sessions],
        "logs": [_serialize_log(l) for l in logs],
    }


@router.post("/import")
def import_data(payload: dict, db: Session = Depends(get_db)):
    # Delete in reverse FK order
    db.query(ReviewLog).delete()
    db.query(ReviewSession).delete()
    db.query(UserProgress).delete()
    db.query(Word).delete()
    db.commit()

    # Reset auto-increment
    try:
        db.execute(text("DELETE FROM sqlite_sequence"))
        db.commit()
    except Exception:
        pass

    # Import words
    for w in payload.get("words", []):
        db.add(Word(
            id=w["id"], word=w["word"],
            phonetic=w.get("phonetic", ""),
            part_of_speech=w.get("part_of_speech", ""),
            definition=w.get("definition", ""),
            example=w.get("example", ""),
            image_url=w.get("image_url", ""),
            image_source=w.get("image_source", ""),
            audio_path=w.get("audio_path", ""),
            chinese=w.get("chinese", ""),
            meanings=w.get("meanings", ""),
            created_at=datetime.fromisoformat(w["created_at"]) if w.get("created_at") else datetime.now(),
            updated_at=datetime.fromisoformat(w["updated_at"]) if w.get("updated_at") else datetime.now(),
        ))
    db.commit()

    # Import progress
    for p in payload.get("progress", []):
        db.add(UserProgress(
            id=p["id"], word_id=p["word_id"],
            stage=p.get("stage", 0),
            repetition=p.get("repetition", 0),
            ease_factor=p.get("ease_factor", 2.5),
            interval=p.get("interval", 0),
            correct_count=p.get("correct_count", 0),
            incorrect_count=p.get("incorrect_count", 0),
            last_reviewed=datetime.fromisoformat(p["last_reviewed"]) if p.get("last_reviewed") else None,
            next_review_date=date.fromisoformat(p["next_review_date"]) if p.get("next_review_date") else None,
        ))
    db.commit()

    # Import sessions
    for s in payload.get("sessions", []):
        db.add(ReviewSession(
            id=s["id"],
            date=date.fromisoformat(s["date"]) if s.get("date") else date.today(),
            total_reviewed=s.get("total_reviewed", 0),
            correct_count=s.get("correct_count", 0),
            duration_minutes=s.get("duration_minutes", 0),
        ))
    db.commit()

    # Import logs
    for l in payload.get("logs", []):
        db.add(ReviewLog(
            id=l["id"], word_id=l["word_id"], session_id=l["session_id"],
            quality=l.get("quality", 0),
            response_time_ms=l.get("response_time_ms", 0),
            reviewed_at=datetime.fromisoformat(l["reviewed_at"]) if l.get("reviewed_at") else datetime.now(),
        ))
    db.commit()

    return {
        "ok": True,
        "words": len(payload.get("words", [])),
        "progress": len(payload.get("progress", [])),
        "sessions": len(payload.get("sessions", [])),
        "logs": len(payload.get("logs", [])),
    }
