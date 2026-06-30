from datetime import UTC, date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class WeeklyReview(Base):
    __tablename__ = "weekly_reviews"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    week_start: Mapped[date] = mapped_column(Date, index=True, nullable=False)
    summary: Mapped[str] = mapped_column(Text, default="")
    biggest_problem: Mapped[str] = mapped_column(Text, default="")
    delay_reason: Mapped[str] = mapped_column(Text, default="")
    english_review: Mapped[str] = mapped_column(Text, default="")
    math_review: Mapped[str] = mapped_column(Text, default="")
    computer_review: Mapped[str] = mapped_column(Text, default="")
    politics_review: Mapped[str] = mapped_column(Text, default="")
    next_week_adjustment: Mapped[str] = mapped_column(Text, default="")
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

