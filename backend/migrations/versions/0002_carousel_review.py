"""carousel review feature

Revision ID: 0002_carousel_review
Revises: 0001_initial_schema
Create Date: 2026-05-09
"""

from alembic import op
import sqlalchemy as sa

revision = "0002_carousel_review"
down_revision = "0001_initial_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add modified_pending_reapproval to publication_status enum.
    # On PostgreSQL this requires ALTER TYPE; on SQLite (tests) the column is VARCHAR so this is a no-op.
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute("ALTER TYPE publication_status ADD VALUE IF NOT EXISTS 'modified_pending_reapproval'")

    op.create_table(
        "review_locks",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("proposal_id", sa.Uuid(), sa.ForeignKey("ai_proposals.id"), nullable=False, unique=True),
        sa.Column("session_id", sa.String(255), nullable=False),
        sa.Column("locked_at", sa.DateTime(), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
    )

    op.create_table(
        "feedback_signals",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("proposal_id", sa.Uuid(), sa.ForeignKey("ai_proposals.id"), nullable=False),
        sa.Column("review_id", sa.Uuid(), sa.ForeignKey("operator_reviews.id"), nullable=False),
        sa.Column("field_name", sa.String(100), nullable=False),
        sa.Column("original_value", sa.String(), nullable=False),
        sa.Column("corrected_value", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("feedback_signals")
    op.drop_table("review_locks")
