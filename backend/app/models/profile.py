from datetime import UTC, date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class ExamProfile(Base):
    __tablename__ = "exam_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True, index=True)
    first_politics_score: Mapped[int] = mapped_column(Integer, default=64)
    first_english_score: Mapped[int] = mapped_column(Integer, default=46)
    first_math_score: Mapped[int] = mapped_column(Integer, default=74)
    first_408_score: Mapped[int] = mapped_column(Integer, default=83)
    target_politics_score: Mapped[int] = mapped_column(Integer, default=65)
    target_english_score: Mapped[int] = mapped_column(Integer, default=55)
    target_math_score: Mapped[int] = mapped_column(Integer, default=110)
    target_408_score: Mapped[int] = mapped_column(Integer, default=100)
    target_total_score: Mapped[int] = mapped_column(Integer, default=330)
    exam_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    daily_target_minutes: Mapped[int] = mapped_column(Integer, default=405)
    weak_points: Mapped[str] = mapped_column(Text, default="英语不断档，数学主攻，408 稳步提分")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )

