from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.api.routes_auth import router as auth_router
from app.api.routes_profile import router as profile_router
from app.api.routes_records import router as records_router
from app.api.routes_reviews import daily_router as daily_reviews_router
from app.api.routes_reviews import router as reviews_router
from app.api.routes_stats import router as stats_router
from app.api.routes_tasks import router as tasks_router
from app.api.routes_timer import router as timer_router
from app.core.config import get_settings
from app.core.database import Base, engine
from app.core.security import get_password_hash
from app.models import (
    DailyReview,
    ExamProfile,
    StudyRecord,
    StudyRecordImage,
    StudyTask,
    TimerSession,
    WeeklyReview,
)
from app.models.user import User


def create_initial_admin(db: Session) -> None:
    settings = get_settings()
    existing_user = db.query(User).filter(User.username == settings.initial_admin_username).first()
    if existing_user is not None:
        return

    admin = User(
        username=settings.initial_admin_username,
        password_hash=get_password_hash(settings.initial_admin_password),
    )
    db.add(admin)
    db.commit()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    Base.metadata.create_all(bind=engine)
    with Session(engine) as db:
        create_initial_admin(db)
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.app_name, lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(auth_router, prefix="/api")
    app.include_router(profile_router, prefix="/api")
    app.include_router(tasks_router, prefix="/api")
    app.include_router(timer_router, prefix="/api")
    app.include_router(records_router, prefix="/api")
    app.include_router(stats_router, prefix="/api")
    app.include_router(reviews_router, prefix="/api")
    app.include_router(daily_reviews_router, prefix="/api")

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
