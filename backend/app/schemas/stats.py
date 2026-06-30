from datetime import date

from pydantic import BaseModel


class TrendPoint(BaseModel):
    date: date
    minutes: int


class DistributionItem(BaseModel):
    name: str
    minutes: int


class DashboardStats(BaseModel):
    today_minutes: int
    today_target_minutes: int
    today_completion_rate: float
    week_minutes: int
    month_minutes: int
    task_completion_rate: float
    english_scheduled_today: bool
    math_scheduled_today: bool
    computer_scheduled_today: bool
    english_streak_days: int
    math_week_ratio: float
    computer_week_ratio: float
    recent_7_days: list[TrendPoint]
    subject_distribution: list[DistributionItem]

