import json
from datetime import UTC, date, datetime, timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.config import get_settings
from app.core.database import get_db
from app.models.review import DailyReview, WeeklyReview
from app.models.study import StudyRecord, StudyRecordImage
from app.models.user import User
from app.schemas.review import (
    DailyReviewResponse,
    WeeklyReviewCreate,
    WeeklyReviewResponse,
    WeeklyReviewUpdate,
)
from app.services.doubao import DoubaoService

router = APIRouter(prefix="/reviews/weekly", tags=["weekly-reviews"])
daily_router = APIRouter(prefix="/reviews/daily", tags=["daily-reviews"])


def get_user_review(db: Session, user_id: int, review_id: int) -> WeeklyReview:
    review = (
        db.query(WeeklyReview)
        .filter(WeeklyReview.id == review_id, WeeklyReview.user_id == user_id)
        .first()
    )
    if review is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")
    return review


@router.get("", response_model=list[WeeklyReviewResponse])
def list_reviews(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> list[WeeklyReview]:
    return (
        db.query(WeeklyReview)
        .filter(WeeklyReview.user_id == current_user.id)
        .order_by(WeeklyReview.week_start.desc())
        .all()
    )


@router.post("", response_model=WeeklyReviewResponse, status_code=status.HTTP_201_CREATED)
def create_review(
    payload: WeeklyReviewCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> WeeklyReview:
    review = WeeklyReview(user_id=current_user.id, **payload.model_dump())
    db.add(review)
    db.commit()
    db.refresh(review)
    return review


@router.put("/{review_id}", response_model=WeeklyReviewResponse)
def update_review(
    review_id: int,
    payload: WeeklyReviewUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> WeeklyReview:
    review = get_user_review(db, current_user.id, review_id)
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(review, key, value)
    db.add(review)
    db.commit()
    db.refresh(review)
    return review


@router.delete("/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_review(
    review_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> None:
    review = get_user_review(db, current_user.id, review_id)
    db.delete(review)
    db.commit()


@daily_router.get("", response_model=list[DailyReviewResponse])
def list_daily_reviews(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    review_date: date | None = Query(default=None, alias="date"),
) -> list[DailyReview]:
    query = db.query(DailyReview).filter(DailyReview.user_id == current_user.id)
    if review_date is not None:
        query = query.filter(DailyReview.review_date == review_date)
    return query.order_by(DailyReview.review_date.desc()).limit(14).all()


@daily_router.post("/generate", response_model=DailyReviewResponse)
def generate_daily_review(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    review_date: date | None = Query(default=None, alias="date"),
) -> DailyReview:
    target_date = review_date or datetime.now(UTC).date()
    start = datetime(target_date.year, target_date.month, target_date.day, tzinfo=UTC)
    end = start + timedelta(days=1)
    records = (
        db.query(StudyRecord)
        .filter(
            StudyRecord.user_id == current_user.id,
            StudyRecord.started_at >= start,
            StudyRecord.started_at < end,
        )
        .order_by(StudyRecord.started_at)
        .all()
    )
    record_ids = [record.id for record in records]
    images: list[StudyRecordImage] = []
    if record_ids:
        images = (
            db.query(StudyRecordImage)
            .filter(StudyRecordImage.user_id == current_user.id, StudyRecordImage.record_id.in_(record_ids))
            .order_by(StudyRecordImage.id)
            .all()
        )

    result = DoubaoService(get_settings()).generate_daily_review(
        review_date=target_date,
        records=records,
        images=images,
    )
    daily_review = (
        db.query(DailyReview)
        .filter(DailyReview.user_id == current_user.id, DailyReview.review_date == target_date)
        .first()
    )
    if daily_review is None:
        daily_review = DailyReview(user_id=current_user.id, review_date=target_date)
    daily_review.summary = result.summary
    daily_review.completed_content = result.completed_content
    daily_review.weak_points = result.weak_points
    daily_review.next_actions = result.next_actions
    daily_review.source_record_ids = json.dumps(record_ids)
    daily_review.model_status = result.status
    db.add(daily_review)
    db.commit()
    db.refresh(daily_review)
    return daily_review
