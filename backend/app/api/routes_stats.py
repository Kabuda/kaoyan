from datetime import UTC, date, datetime, timedelta
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.api.routes_profile import get_or_create_profile
from app.core.database import get_db
from app.models.study import StudyRecord, StudyTask
from app.models.user import User
from app.schemas.stats import DashboardStats, DistributionItem, TrendPoint

router = APIRouter(prefix="/stats", tags=["stats"])


def day_bounds(target: date) -> tuple[datetime, datetime]:
    start = datetime(target.year, target.month, target.day, tzinfo=UTC)
    return start, start + timedelta(days=1)


def sum_minutes(db: Session, user_id: int, start: datetime, end: datetime) -> int:
    result = (
        db.query(func.coalesce(func.sum(StudyRecord.duration_minutes), 0))
        .filter(
            StudyRecord.user_id == user_id,
            StudyRecord.started_at >= start,
            StudyRecord.started_at < end,
        )
        .scalar()
    )
    return int(result or 0)


def subject_distribution(db: Session, user_id: int, start: datetime, end: datetime) -> list[DistributionItem]:
    rows = (
        db.query(StudyRecord.subject, func.coalesce(func.sum(StudyRecord.duration_minutes), 0))
        .filter(
            StudyRecord.user_id == user_id,
            StudyRecord.started_at >= start,
            StudyRecord.started_at < end,
        )
        .group_by(StudyRecord.subject)
        .all()
    )
    return [DistributionItem(name=subject, minutes=int(minutes or 0)) for subject, minutes in rows]


def completion_rate(db: Session, user_id: int, start_date: date, end_date: date) -> float:
    query = db.query(StudyTask).filter(
        StudyTask.user_id == user_id,
        StudyTask.plan_date >= start_date,
        StudyTask.plan_date <= end_date,
    )
    total = query.count()
    if total == 0:
        return 0.0
    completed = query.filter(StudyTask.status == "completed").count()
    return round(completed / total, 4)


def english_streak(db: Session, user_id: int, today: date) -> int:
    streak = 0
    cursor = today
    while True:
        start, end = day_bounds(cursor)
        minutes = (
            db.query(func.coalesce(func.sum(StudyRecord.duration_minutes), 0))
            .filter(
                StudyRecord.user_id == user_id,
                StudyRecord.subject == "english",
                StudyRecord.started_at >= start,
                StudyRecord.started_at < end,
            )
            .scalar()
        )
        if int(minutes or 0) <= 0:
            return streak
        streak += 1
        cursor -= timedelta(days=1)


@router.get("/dashboard", response_model=DashboardStats)
def dashboard_stats(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> DashboardStats:
    today = datetime.now(UTC).date()
    today_start, tomorrow_start = day_bounds(today)
    week_start_date = today - timedelta(days=today.weekday())
    month_start_date = today.replace(day=1)
    week_start, _ = day_bounds(week_start_date)
    month_start, _ = day_bounds(month_start_date)

    profile = get_or_create_profile(db, current_user.id)
    today_minutes = sum_minutes(db, current_user.id, today_start, tomorrow_start)
    week_minutes = sum_minutes(db, current_user.id, week_start, tomorrow_start)
    month_minutes = sum_minutes(db, current_user.id, month_start, tomorrow_start)

    today_tasks = (
        db.query(StudyTask)
        .filter(StudyTask.user_id == current_user.id, StudyTask.plan_date == today)
        .all()
    )
    subjects_today = {task.subject for task in today_tasks}
    distribution = subject_distribution(db, current_user.id, week_start, tomorrow_start)
    distribution_map = {item.name: item.minutes for item in distribution}
    week_total = sum(item.minutes for item in distribution)

    recent_points: list[TrendPoint] = []
    for offset in range(6, -1, -1):
        point_date = today - timedelta(days=offset)
        start, end = day_bounds(point_date)
        recent_points.append(
            TrendPoint(date=point_date, minutes=sum_minutes(db, current_user.id, start, end))
        )

    return DashboardStats(
        today_minutes=today_minutes,
        today_target_minutes=profile.daily_target_minutes,
        today_completion_rate=(
            round(today_minutes / profile.daily_target_minutes, 4)
            if profile.daily_target_minutes
            else 0.0
        ),
        week_minutes=week_minutes,
        month_minutes=month_minutes,
        task_completion_rate=completion_rate(db, current_user.id, week_start_date, today),
        english_scheduled_today="english" in subjects_today,
        math_scheduled_today="math" in subjects_today,
        computer_scheduled_today="408" in subjects_today,
        english_streak_days=english_streak(db, current_user.id, today),
        math_week_ratio=round(distribution_map.get("math", 0) / week_total, 4) if week_total else 0.0,
        computer_week_ratio=round(distribution_map.get("408", 0) / week_total, 4) if week_total else 0.0,
        recent_7_days=recent_points,
        subject_distribution=distribution,
    )


@router.get("/subject-distribution", response_model=list[DistributionItem])
def read_subject_distribution(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    start_date: date | None = None,
    end_date: date | None = None,
) -> list[DistributionItem]:
    today = datetime.now(UTC).date()
    start, _ = day_bounds(start_date or today - timedelta(days=6))
    _, end = day_bounds(end_date or today)
    return subject_distribution(db, current_user.id, start, end)

@router.get("/range", response_model=list[TrendPoint])
def range_stats(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    start_date: date,
    end_date: date,
) -> list[TrendPoint]:
    points: list[TrendPoint] = []
    cursor = start_date
    while cursor <= end_date:
        start, end = day_bounds(cursor)
        points.append(TrendPoint(date=cursor, minutes=sum_minutes(db, current_user.id, start, end)))
        cursor += timedelta(days=1)
    return points

