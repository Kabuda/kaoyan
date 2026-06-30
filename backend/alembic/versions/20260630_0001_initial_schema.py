"""initial schema

Revision ID: 20260630_0001
Revises: None
Create Date: 2026-06-30
"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "20260630_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("username", sa.String(length=64), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_id"), "users", ["id"], unique=False)
    op.create_index(op.f("ix_users_username"), "users", ["username"], unique=True)

    op.create_table(
        "exam_profiles",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("first_politics_score", sa.Integer(), nullable=False),
        sa.Column("first_english_score", sa.Integer(), nullable=False),
        sa.Column("first_math_score", sa.Integer(), nullable=False),
        sa.Column("first_408_score", sa.Integer(), nullable=False),
        sa.Column("target_politics_score", sa.Integer(), nullable=False),
        sa.Column("target_english_score", sa.Integer(), nullable=False),
        sa.Column("target_math_score", sa.Integer(), nullable=False),
        sa.Column("target_408_score", sa.Integer(), nullable=False),
        sa.Column("target_total_score", sa.Integer(), nullable=False),
        sa.Column("exam_date", sa.Date(), nullable=True),
        sa.Column("daily_target_minutes", sa.Integer(), nullable=False),
        sa.Column("weak_points", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_exam_profiles_id"), "exam_profiles", ["id"], unique=False)
    op.create_index(op.f("ix_exam_profiles_user_id"), "exam_profiles", ["user_id"], unique=True)

    op.create_table(
        "study_tasks",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("plan_date", sa.Date(), nullable=False),
        sa.Column("subject", sa.String(length=32), nullable=False),
        sa.Column("module", sa.String(length=64), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("task_type", sa.String(length=32), nullable=False),
        sa.Column("estimated_minutes", sa.Integer(), nullable=False),
        sa.Column("actual_minutes", sa.Integer(), nullable=False),
        sa.Column("priority", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("note", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_study_tasks_id"), "study_tasks", ["id"], unique=False)
    op.create_index(op.f("ix_study_tasks_module"), "study_tasks", ["module"], unique=False)
    op.create_index(op.f("ix_study_tasks_plan_date"), "study_tasks", ["plan_date"], unique=False)
    op.create_index(op.f("ix_study_tasks_status"), "study_tasks", ["status"], unique=False)
    op.create_index(op.f("ix_study_tasks_subject"), "study_tasks", ["subject"], unique=False)
    op.create_index(op.f("ix_study_tasks_task_type"), "study_tasks", ["task_type"], unique=False)
    op.create_index(op.f("ix_study_tasks_user_id"), "study_tasks", ["user_id"], unique=False)

    op.create_table(
        "timer_sessions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("task_id", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("paused_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("accumulated_seconds", sa.Integer(), nullable=False),
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["task_id"], ["study_tasks.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_timer_sessions_id"), "timer_sessions", ["id"], unique=False)
    op.create_index(op.f("ix_timer_sessions_status"), "timer_sessions", ["status"], unique=False)
    op.create_index(op.f("ix_timer_sessions_task_id"), "timer_sessions", ["task_id"], unique=False)
    op.create_index(op.f("ix_timer_sessions_user_id"), "timer_sessions", ["user_id"], unique=False)

    op.create_table(
        "study_records",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("task_id", sa.Integer(), nullable=True),
        sa.Column("subject", sa.String(length=32), nullable=False),
        sa.Column("module", sa.String(length=64), nullable=False),
        sa.Column("task_type", sa.String(length=32), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("duration_minutes", sa.Integer(), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("blockers", sa.Text(), nullable=False),
        sa.Column("quality", sa.String(length=32), nullable=False),
        sa.Column("is_manual", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["task_id"], ["study_tasks.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_study_records_id"), "study_records", ["id"], unique=False)
    op.create_index(op.f("ix_study_records_module"), "study_records", ["module"], unique=False)
    op.create_index(op.f("ix_study_records_subject"), "study_records", ["subject"], unique=False)
    op.create_index(op.f("ix_study_records_task_type"), "study_records", ["task_type"], unique=False)
    op.create_index(op.f("ix_study_records_user_id"), "study_records", ["user_id"], unique=False)

    op.create_table(
        "weekly_reviews",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("week_start", sa.Date(), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("biggest_problem", sa.Text(), nullable=False),
        sa.Column("delay_reason", sa.Text(), nullable=False),
        sa.Column("english_review", sa.Text(), nullable=False),
        sa.Column("math_review", sa.Text(), nullable=False),
        sa.Column("computer_review", sa.Text(), nullable=False),
        sa.Column("politics_review", sa.Text(), nullable=False),
        sa.Column("next_week_adjustment", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_weekly_reviews_id"), "weekly_reviews", ["id"], unique=False)
    op.create_index(op.f("ix_weekly_reviews_user_id"), "weekly_reviews", ["user_id"], unique=False)
    op.create_index(op.f("ix_weekly_reviews_week_start"), "weekly_reviews", ["week_start"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_weekly_reviews_week_start"), table_name="weekly_reviews")
    op.drop_index(op.f("ix_weekly_reviews_user_id"), table_name="weekly_reviews")
    op.drop_index(op.f("ix_weekly_reviews_id"), table_name="weekly_reviews")
    op.drop_table("weekly_reviews")
    op.drop_index(op.f("ix_study_records_user_id"), table_name="study_records")
    op.drop_index(op.f("ix_study_records_task_type"), table_name="study_records")
    op.drop_index(op.f("ix_study_records_subject"), table_name="study_records")
    op.drop_index(op.f("ix_study_records_module"), table_name="study_records")
    op.drop_index(op.f("ix_study_records_id"), table_name="study_records")
    op.drop_table("study_records")
    op.drop_index(op.f("ix_timer_sessions_user_id"), table_name="timer_sessions")
    op.drop_index(op.f("ix_timer_sessions_task_id"), table_name="timer_sessions")
    op.drop_index(op.f("ix_timer_sessions_status"), table_name="timer_sessions")
    op.drop_index(op.f("ix_timer_sessions_id"), table_name="timer_sessions")
    op.drop_table("timer_sessions")
    op.drop_index(op.f("ix_study_tasks_user_id"), table_name="study_tasks")
    op.drop_index(op.f("ix_study_tasks_task_type"), table_name="study_tasks")
    op.drop_index(op.f("ix_study_tasks_subject"), table_name="study_tasks")
    op.drop_index(op.f("ix_study_tasks_status"), table_name="study_tasks")
    op.drop_index(op.f("ix_study_tasks_plan_date"), table_name="study_tasks")
    op.drop_index(op.f("ix_study_tasks_module"), table_name="study_tasks")
    op.drop_index(op.f("ix_study_tasks_id"), table_name="study_tasks")
    op.drop_table("study_tasks")
    op.drop_index(op.f("ix_exam_profiles_user_id"), table_name="exam_profiles")
    op.drop_index(op.f("ix_exam_profiles_id"), table_name="exam_profiles")
    op.drop_table("exam_profiles")
    op.drop_index(op.f("ix_users_username"), table_name="users")
    op.drop_index(op.f("ix_users_id"), table_name="users")
    op.drop_table("users")

