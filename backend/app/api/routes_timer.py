from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.api.routes_tasks import get_user_task
from app.core.config import get_settings
from app.core.database import get_db
from app.models.study import StudyRecord, StudyTask, TimerSession
from app.models.user import User
from app.schemas.study import (
    TimerFinishRequest,
    TimerFinishWithImagesResponse,
    TimerSessionResponse,
    TimerStartRequest,
)
from app.services.doubao import DoubaoService
from app.services.record_images import save_and_analyze_uploads

router = APIRouter(prefix="/timer", tags=["timer"])


def current_timer(db: Session, user_id: int) -> TimerSession | None:
    return (
        db.query(TimerSession)
        .filter(TimerSession.user_id == user_id, TimerSession.status.in_(["running", "paused"]))
        .order_by(TimerSession.id.desc())
        .first()
    )


def seconds_between(start: datetime, end: datetime) -> int:
    return max(0, int((end.replace(tzinfo=UTC) - start.replace(tzinfo=UTC)).total_seconds()))


@router.get("/current", response_model=TimerSessionResponse | None)
def read_current_timer(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> TimerSession | None:
    return current_timer(db, current_user.id)


@router.post("/start", response_model=TimerSessionResponse, status_code=status.HTTP_201_CREATED)
def start_timer(
    payload: TimerStartRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> TimerSession:
    if current_timer(db, current_user.id) is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Timer already running")

    task = get_user_task(db, current_user.id, payload.task_id)
    task.status = "in_progress"
    timer = TimerSession(
        user_id=current_user.id,
        task_id=task.id,
        status="running",
        started_at=datetime.now(UTC),
    )
    db.add(task)
    db.add(timer)
    db.commit()
    db.refresh(timer)
    return timer


@router.post("/pause", response_model=TimerSessionResponse)
def pause_timer(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> TimerSession:
    timer = current_timer(db, current_user.id)
    if timer is None or timer.status != "running":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Running timer not found")

    now = datetime.now(UTC)
    timer.accumulated_seconds += seconds_between(timer.started_at, now)
    timer.paused_at = now
    timer.status = "paused"
    db.add(timer)
    db.commit()
    db.refresh(timer)
    return timer


@router.post("/resume", response_model=TimerSessionResponse)
def resume_timer(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> TimerSession:
    timer = current_timer(db, current_user.id)
    if timer is None or timer.status != "paused":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Paused timer not found")

    timer.started_at = datetime.now(UTC)
    timer.paused_at = None
    timer.status = "running"
    db.add(timer)
    db.commit()
    db.refresh(timer)
    return timer


@router.post("/finish")
def finish_timer(
    payload: TimerFinishRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> dict[str, int]:
    record = finish_current_timer(payload=payload, current_user=current_user, db=db)
    return {"record_id": record.id, "duration_minutes": record.duration_minutes}


@router.post("/finish-with-images", response_model=TimerFinishWithImagesResponse)
def finish_timer_with_images(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    summary: str = Form(default=""),
    blockers: str = Form(default=""),
    quality: str = Form(default="medium"),
    files: list[UploadFile] | None = File(default=None),
) -> TimerFinishWithImagesResponse:
    payload = TimerFinishRequest(summary=summary, blockers=blockers, quality=quality)
    record = finish_current_timer(payload=payload, current_user=current_user, db=db)
    settings = get_settings()
    images = save_and_analyze_uploads(
        db=db,
        settings=settings,
        doubao=DoubaoService(settings),
        user_id=current_user.id,
        record=record,
        files=files or [],
    )
    return TimerFinishWithImagesResponse(record=record, images=images)


def finish_current_timer(
    payload: TimerFinishRequest,
    current_user: User,
    db: Session,
) -> StudyRecord:
    timer = current_timer(db, current_user.id)
    if timer is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Timer not found")

    now = datetime.now(UTC)
    total_seconds = timer.accumulated_seconds
    if timer.status == "running":
        total_seconds += seconds_between(timer.started_at, now)

    duration_minutes = max(1, round(total_seconds / 60))
    task = get_user_task(db, current_user.id, timer.task_id)
    task.actual_minutes += duration_minutes
    task.status = "completed"
    timer.status = "finished"
    timer.ended_at = now

    record = StudyRecord(
        user_id=current_user.id,
        task_id=task.id,
        subject=task.subject,
        module=task.module,
        task_type=task.task_type,
        title=task.title,
        started_at=timer.created_at,
        ended_at=now,
        duration_minutes=duration_minutes,
        summary=payload.summary,
        blockers=payload.blockers,
        quality=payload.quality,
        is_manual=False,
    )
    db.add_all([task, timer, record])
    db.commit()
    db.refresh(record)
    return record
