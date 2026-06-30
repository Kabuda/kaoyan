from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.review import WeeklyReview
from app.models.user import User
from app.schemas.review import WeeklyReviewCreate, WeeklyReviewResponse, WeeklyReviewUpdate

router = APIRouter(prefix="/reviews/weekly", tags=["weekly-reviews"])


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

