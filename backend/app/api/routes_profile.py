from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.profile import ExamProfile
from app.models.user import User
from app.schemas.profile import ExamProfileResponse, ExamProfileUpdate

router = APIRouter(prefix="/profile", tags=["profile"])


def get_or_create_profile(db: Session, user_id: int) -> ExamProfile:
    profile = db.query(ExamProfile).filter(ExamProfile.user_id == user_id).first()
    if profile is not None:
        return profile

    profile = ExamProfile(user_id=user_id)
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


@router.get("", response_model=ExamProfileResponse)
def read_profile(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> ExamProfile:
    return get_or_create_profile(db, current_user.id)


@router.put("", response_model=ExamProfileResponse)
def update_profile(
    payload: ExamProfileUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> ExamProfile:
    profile = get_or_create_profile(db, current_user.id)
    for key, value in payload.model_dump().items():
        setattr(profile, key, value)
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile

