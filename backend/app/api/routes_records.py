from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.study import StudyRecord
from app.models.user import User
from app.schemas.study import StudyRecordCreate, StudyRecordResponse, StudyRecordUpdate

router = APIRouter(prefix="/records", tags=["records"])


def get_user_record(db: Session, user_id: int, record_id: int) -> StudyRecord:
    record = (
        db.query(StudyRecord)
        .filter(StudyRecord.id == record_id, StudyRecord.user_id == user_id)
        .first()
    )
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Record not found")
    return record


@router.get("", response_model=list[StudyRecordResponse])
def list_records(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    start_date: date | None = None,
    end_date: date | None = None,
    subject: str | None = Query(default=None),
    module: str | None = Query(default=None),
) -> list[StudyRecord]:
    query = db.query(StudyRecord).filter(StudyRecord.user_id == current_user.id)
    if start_date is not None:
        query = query.filter(func.date(StudyRecord.started_at) >= start_date)
    if end_date is not None:
        query = query.filter(func.date(StudyRecord.started_at) <= end_date)
    if subject:
        query = query.filter(StudyRecord.subject == subject)
    if module:
        query = query.filter(StudyRecord.module == module)
    return query.order_by(StudyRecord.started_at.desc(), StudyRecord.id.desc()).all()


@router.post("", response_model=StudyRecordResponse, status_code=status.HTTP_201_CREATED)
def create_record(
    payload: StudyRecordCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> StudyRecord:
    if payload.ended_at <= payload.started_at:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid time range")

    record = StudyRecord(user_id=current_user.id, is_manual=True, **payload.model_dump())
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.put("/{record_id}", response_model=StudyRecordResponse)
def update_record(
    record_id: int,
    payload: StudyRecordUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> StudyRecord:
    record = get_user_record(db, current_user.id, record_id)
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(record, key, value)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_record(
    record_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> None:
    record = get_user_record(db, current_user.id, record_id)
    db.delete(record)
    db.commit()

