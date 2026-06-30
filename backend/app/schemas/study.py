from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class StudyTaskBase(BaseModel):
    plan_date: date
    subject: str = Field(min_length=1, max_length=32)
    module: str = Field(min_length=1, max_length=64)
    title: str = Field(min_length=1, max_length=200)
    task_type: str = Field(default="practice", min_length=1, max_length=32)
    estimated_minutes: int = Field(default=60, ge=0, le=1440)
    priority: int = Field(default=2, ge=1, le=3)
    note: str = ""


class StudyTaskCreate(StudyTaskBase):
    pass


class StudyTaskUpdate(BaseModel):
    plan_date: date | None = None
    subject: str | None = Field(default=None, min_length=1, max_length=32)
    module: str | None = Field(default=None, min_length=1, max_length=64)
    title: str | None = Field(default=None, min_length=1, max_length=200)
    task_type: str | None = Field(default=None, min_length=1, max_length=32)
    estimated_minutes: int | None = Field(default=None, ge=0, le=1440)
    actual_minutes: int | None = Field(default=None, ge=0, le=1440)
    priority: int | None = Field(default=None, ge=1, le=3)
    status: str | None = Field(default=None, min_length=1, max_length=32)
    note: str | None = None


class StudyTaskResponse(StudyTaskBase):
    id: int
    user_id: int
    actual_minutes: int
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PostponeTaskRequest(BaseModel):
    plan_date: date


class GenerateDailyTemplateRequest(BaseModel):
    plan_date: date | None = None


class TimerStartRequest(BaseModel):
    task_id: int


class TimerFinishRequest(BaseModel):
    summary: str = ""
    blockers: str = ""
    quality: str = Field(default="medium", min_length=1, max_length=32)


class TimerSessionResponse(BaseModel):
    id: int
    user_id: int
    task_id: int
    status: str
    started_at: datetime
    paused_at: datetime | None
    accumulated_seconds: int
    ended_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class StudyRecordCreate(BaseModel):
    task_id: int | None = None
    subject: str = Field(min_length=1, max_length=32)
    module: str = Field(min_length=1, max_length=64)
    task_type: str = Field(default="manual", min_length=1, max_length=32)
    title: str = Field(min_length=1, max_length=200)
    started_at: datetime
    ended_at: datetime
    duration_minutes: int = Field(ge=1, le=1440)
    summary: str = ""
    blockers: str = ""
    quality: str = Field(default="medium", min_length=1, max_length=32)


class StudyRecordUpdate(BaseModel):
    subject: str | None = Field(default=None, min_length=1, max_length=32)
    module: str | None = Field(default=None, min_length=1, max_length=64)
    task_type: str | None = Field(default=None, min_length=1, max_length=32)
    title: str | None = Field(default=None, min_length=1, max_length=200)
    started_at: datetime | None = None
    ended_at: datetime | None = None
    duration_minutes: int | None = Field(default=None, ge=1, le=1440)
    summary: str | None = None
    blockers: str | None = None
    quality: str | None = Field(default=None, min_length=1, max_length=32)


class StudyRecordResponse(BaseModel):
    id: int
    user_id: int
    task_id: int | None
    subject: str
    module: str
    task_type: str
    title: str
    started_at: datetime
    ended_at: datetime
    duration_minutes: int
    summary: str
    blockers: str
    quality: str
    is_manual: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

