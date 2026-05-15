from sqlalchemy import (
    Column, Integer, String, Text, Float, DateTime, ForeignKey, Date
)
from sqlalchemy.orm import relationship
from datetime import datetime, date

from database import Base


class Word(Base):
    __tablename__ = "words"

    id = Column(Integer, primary_key=True, index=True)
    word = Column(String(200), nullable=False, index=True)
    phonetic = Column(String(200), default="")
    part_of_speech = Column(String(50), default="")
    definition = Column(Text, default="")
    example = Column(Text, default="")
    image_url = Column(String(500), default="")
    image_source = Column(String(50), default="")
    audio_path = Column(String(300), default="")
    chinese = Column(String(500), default="")
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    progress = relationship("UserProgress", back_populates="word", uselist=False,
                            cascade="all, delete-orphan")


class UserProgress(Base):
    __tablename__ = "user_progress"

    id = Column(Integer, primary_key=True, index=True)
    word_id = Column(Integer, ForeignKey("words.id"), nullable=False, unique=True)
    stage = Column(Integer, default=0)          # 0=new, 1-5=memory stages (SM-2)
    repetition = Column(Integer, default=0)     # consecutive correct reviews
    ease_factor = Column(Float, default=2.5)    # SM-2 ease factor
    interval = Column(Integer, default=0)       # days until next review
    correct_count = Column(Integer, default=0)
    incorrect_count = Column(Integer, default=0)
    last_reviewed = Column(DateTime, nullable=True)
    next_review_date = Column(Date, nullable=True)

    word = relationship("Word", back_populates="progress")


class ReviewSession(Base):
    __tablename__ = "review_sessions"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, default=date.today)
    total_reviewed = Column(Integer, default=0)
    correct_count = Column(Integer, default=0)
    duration_minutes = Column(Integer, default=0)

    logs = relationship("ReviewLog", back_populates="session",
                        cascade="all, delete-orphan")


class ReviewLog(Base):
    __tablename__ = "review_logs"

    id = Column(Integer, primary_key=True, index=True)
    word_id = Column(Integer, ForeignKey("words.id"), nullable=False)
    session_id = Column(Integer, ForeignKey("review_sessions.id"), nullable=False)
    quality = Column(Integer, default=0)         # SM-2 quality 0-5
    response_time_ms = Column(Integer, default=0)
    reviewed_at = Column(DateTime, default=datetime.now)

    session = relationship("ReviewSession", back_populates="logs")
