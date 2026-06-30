"""doubao image reviews

Revision ID: 20260630_0002
Revises: 20260630_0001
Create Date: 2026-06-30
"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "20260630_0002"
down_revision: str | None = "20260630_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "daily_reviews",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("review_date", sa.Date(), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("completed_content", sa.Text(), nullable=False),
        sa.Column("weak_points", sa.Text(), nullable=False),
        sa.Column("next_actions", sa.Text(), nullable=False),
        sa.Column("source_record_ids", sa.Text(), nullable=False),
        sa.Column("model_status", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "review_date", name="uq_daily_reviews_user_date"),
    )
    op.create_index(op.f("ix_daily_reviews_id"), "daily_reviews", ["id"], unique=False)
    op.create_index(op.f("ix_daily_reviews_review_date"), "daily_reviews", ["review_date"], unique=False)
    op.create_index(op.f("ix_daily_reviews_user_id"), "daily_reviews", ["user_id"], unique=False)

    op.create_table(
        "study_record_images",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("record_id", sa.Integer(), nullable=False),
        sa.Column("original_filename", sa.String(length=255), nullable=False),
        sa.Column("stored_path", sa.String(length=500), nullable=False),
        sa.Column("content_type", sa.String(length=100), nullable=False),
        sa.Column("file_size", sa.Integer(), nullable=False),
        sa.Column("analysis_status", sa.String(length=32), nullable=False),
        sa.Column("analysis_text", sa.Text(), nullable=False),
        sa.Column("knowledge_points", sa.Text(), nullable=False),
        sa.Column("mistakes", sa.Text(), nullable=False),
        sa.Column("suggestions", sa.Text(), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["record_id"], ["study_records.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_study_record_images_analysis_status"), "study_record_images", ["analysis_status"], unique=False)
    op.create_index(op.f("ix_study_record_images_id"), "study_record_images", ["id"], unique=False)
    op.create_index(op.f("ix_study_record_images_record_id"), "study_record_images", ["record_id"], unique=False)
    op.create_index(op.f("ix_study_record_images_user_id"), "study_record_images", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_study_record_images_user_id"), table_name="study_record_images")
    op.drop_index(op.f("ix_study_record_images_record_id"), table_name="study_record_images")
    op.drop_index(op.f("ix_study_record_images_id"), table_name="study_record_images")
    op.drop_index(op.f("ix_study_record_images_analysis_status"), table_name="study_record_images")
    op.drop_table("study_record_images")
    op.drop_index(op.f("ix_daily_reviews_user_id"), table_name="daily_reviews")
    op.drop_index(op.f("ix_daily_reviews_review_date"), table_name="daily_reviews")
    op.drop_index(op.f("ix_daily_reviews_id"), table_name="daily_reviews")
    op.drop_table("daily_reviews")
