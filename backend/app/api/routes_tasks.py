from datetime import UTC, date, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.study import StudyTask
from app.models.user import User
from app.schemas.study import (
    GenerateDailyTemplateRequest,
    PostponeTaskRequest,
    StudyTaskCreate,
    StudyTaskResponse,
    StudyTaskUpdate,
)

router = APIRouter(prefix="/tasks", tags=["tasks"])


def get_user_task(db: Session, user_id: int, task_id: int) -> StudyTask:
    task = (
        db.query(StudyTask)
        .filter(StudyTask.id == task_id, StudyTask.user_id == user_id)
        .first()
    )
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task


@router.get("", response_model=list[StudyTaskResponse])
def list_tasks(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    plan_date: date | None = Query(default=None, alias="date"),
) -> list[StudyTask]:
    query = db.query(StudyTask).filter(StudyTask.user_id == current_user.id)
    if plan_date is not None:
        query = query.filter(StudyTask.plan_date == plan_date)
    return query.order_by(StudyTask.plan_date, StudyTask.priority, StudyTask.id).all()


@router.post("", response_model=StudyTaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    payload: StudyTaskCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> StudyTask:
    task = StudyTask(user_id=current_user.id, **payload.model_dump())
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@router.put("/{task_id}", response_model=StudyTaskResponse)
def update_task(
    task_id: int,
    payload: StudyTaskUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> StudyTask:
    task = get_user_task(db, current_user.id, task_id)
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(task, key, value)
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> None:
    task = get_user_task(db, current_user.id, task_id)
    db.delete(task)
    db.commit()


@router.post("/{task_id}/complete", response_model=StudyTaskResponse)
def complete_task(
    task_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> StudyTask:
    task = get_user_task(db, current_user.id, task_id)
    task.status = "completed"
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@router.post("/{task_id}/skip", response_model=StudyTaskResponse)
def skip_task(
    task_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> StudyTask:
    task = get_user_task(db, current_user.id, task_id)
    task.status = "skipped"
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@router.post("/{task_id}/postpone", response_model=StudyTaskResponse)
def postpone_task(
    task_id: int,
    payload: PostponeTaskRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> StudyTask:
    task = get_user_task(db, current_user.id, task_id)
    task.plan_date = payload.plan_date
    task.status = "postponed"
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@router.post("/generate-daily-template", response_model=list[StudyTaskResponse])
def generate_daily_template(
    payload: GenerateDailyTemplateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> list[StudyTask]:
    plan_date = payload.plan_date or datetime.now(UTC).date()
    template = [
        ("english", "reading", "英语阅读/单词不断档", "weakness", 60, 1),
        ("math", "advanced_math", "数学基础补漏与题型训练", "weakness", 180, 1),
        ("408", "review", "408 四门模块刷题复盘", "practice", 120, 2),
        ("politics", "choice", "政治选择题或背诵保持", "memorize", 45, 3),
    ]
    tasks = [
        StudyTask(
            user_id=current_user.id,
            plan_date=plan_date,
            subject=subject,
            module=module,
            title=title,
            task_type=task_type,
            estimated_minutes=minutes,
            priority=priority,
        )
        for subject, module, title, task_type, minutes, priority in template
    ]
    db.add_all(tasks)
    db.commit()
    for task in tasks:
        db.refresh(task)
    return tasks

