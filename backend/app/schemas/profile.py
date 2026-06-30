from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class ExamProfileBase(BaseModel):
    first_politics_score: int = Field(64, ge=0, le=100)
    first_english_score: int = Field(46, ge=0, le=100)
    first_math_score: int = Field(74, ge=0, le=150)
    first_408_score: int = Field(83, ge=0, le=150)
    target_politics_score: int = Field(65, ge=0, le=100)
    target_english_score: int = Field(55, ge=0, le=100)
    target_math_score: int = Field(110, ge=0, le=150)
    target_408_score: int = Field(100, ge=0, le=150)
    target_total_score: int = Field(330, ge=0, le=500)
    exam_date: date | None = None
    daily_target_minutes: int = Field(405, ge=0, le=1440)
    weak_points: str = "英语不断档，数学主攻，408 稳步提分"


class ExamProfileUpdate(ExamProfileBase):
    pass


class ExamProfileResponse(ExamProfileBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

