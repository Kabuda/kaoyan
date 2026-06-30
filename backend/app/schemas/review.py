from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class WeeklyReviewBase(BaseModel):
    week_start: date
    summary: str = ""
    biggest_problem: str = ""
    delay_reason: str = ""
    english_review: str = ""
    math_review: str = ""
    computer_review: str = ""
    politics_review: str = ""
    next_week_adjustment: str = ""


class WeeklyReviewCreate(WeeklyReviewBase):
    pass


class WeeklyReviewUpdate(BaseModel):
    week_start: date | None = None
    summary: str | None = None
    biggest_problem: str | None = None
    delay_reason: str | None = None
    english_review: str | None = None
    math_review: str | None = None
    computer_review: str | None = None
    politics_review: str | None = None
    next_week_adjustment: str | None = None


class WeeklyReviewResponse(WeeklyReviewBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

