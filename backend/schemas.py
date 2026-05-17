from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import date, datetime


class MeaningItem(BaseModel):
    pos: str = ""
    definition: str = ""
    example: str = ""
    example_cn: str = ""


class WordCreate(BaseModel):
    word: str


class WordOut(BaseModel):
    id: int
    word: str
    phonetic: str
    part_of_speech: str
    definition: str
    example: str
    chinese: str = ""
    image_url: str
    image_source: str
    audio_path: str
    meanings: List[MeaningItem] = []
    stage: int = 0
    next_review_date: Optional[date] = None
    created_at: datetime

    class Config:
        from_attributes = True


class WordDetail(BaseModel):
    id: int
    word: str
    phonetic: str
    part_of_speech: str
    definition: str
    example: str
    chinese: str = ""
    image_url: str
    image_source: str
    audio_path: str
    meanings: List[MeaningItem] = []
    stage: int
    repetition: int
    ease_factor: float
    interval: int
    correct_count: int
    incorrect_count: int
    last_reviewed: Optional[datetime]
    next_review_date: Optional[date]
    created_at: datetime

    class Config:
        from_attributes = True


class WordListResponse(BaseModel):
    items: List[WordOut]
    total: int
    page: int
    page_size: int


class ReviewNextResponse(BaseModel):
    word: WordDetail


class ReviewSubmit(BaseModel):
    word_id: int
    quality: int  # 0-5 SM-2 quality
    response_time_ms: int = 0


class StatsResponse(BaseModel):
    total_words: int
    stage_0_new: int
    stage_1_learning: int
    stage_2_3_reviewing: int
    stage_4_5_known: int
    errors_count: int = 0
    due_count: int = 0
    today_reviewed: int
    today_correct: int
    today_accuracy: float
    total_reviewed_all: int


class ErrorWord(BaseModel):
    id: int
    word: str
    chinese: str = ""
    definition: str = ""
    phonetic: str = ""
    image_url: str = ""
    incorrect_count: int = 0
    correct_count: int = 0
    stage: int = 0


class ErrorWordsResponse(BaseModel):
    items: List[ErrorWord]
    total: int
