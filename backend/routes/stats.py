from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date

from database import get_db
from models import Word, UserProgress, ReviewSession
from schemas import StatsResponse

router = APIRouter(prefix="/api/stats", tags=["stats"])


@router.get("", response_model=StatsResponse)
def get_stats(db: Session = Depends(get_db)):
    total_words = db.query(Word).count()

    stage_0 = db.query(UserProgress).filter(UserProgress.stage == 0).count()
    # words with no progress are also "new" (stage 0)
    no_progress = db.query(Word).filter(~Word.progress.has()).count()

    stage_1 = db.query(UserProgress).filter(UserProgress.stage == 1).count()
    stage_2_3 = db.query(UserProgress).filter(
        UserProgress.stage.in_([2, 3])
    ).count()
    stage_4_5 = db.query(UserProgress).filter(
        UserProgress.stage.in_([4, 5])
    ).count()

    today = date.today()
    session = db.query(ReviewSession).filter(
        ReviewSession.date == today
    ).first()

    today_reviewed = session.total_reviewed if session else 0
    today_correct = session.correct_count if session else 0
    today_accuracy = (today_correct / today_reviewed * 100) if today_reviewed > 0 else 0

    total_reviewed = db.query(func.sum(ReviewSession.total_reviewed)).scalar() or 0

    return StatsResponse(
        total_words=total_words,
        stage_0_new=stage_0 + no_progress,
        stage_1_learning=stage_1,
        stage_2_3_reviewing=stage_2_3,
        stage_4_5_known=stage_4_5,
        today_reviewed=today_reviewed,
        today_correct=today_correct,
        today_accuracy=round(today_accuracy, 1),
        total_reviewed_all=total_reviewed,
    )
