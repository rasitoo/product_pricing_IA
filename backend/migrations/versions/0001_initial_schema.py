"""initial schema

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-05-05
"""

from alembic import op
import sqlalchemy as sa


revision = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "products",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("external_reference", sa.String(255), nullable=True),
        sa.Column("source_channel", sa.String(50), nullable=False),
        sa.Column("title", sa.String(255), nullable=True),
        sa.Column("category", sa.String(255), nullable=True),
        sa.Column("tags", sa.JSON(), nullable=False),
        sa.Column("status", sa.String(50), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_table(
        "ai_proposals",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("product_id", sa.Uuid(), sa.ForeignKey("products.id"), nullable=False),
        sa.Column("description_text", sa.String(), nullable=False),
        sa.Column("suggested_price", sa.Numeric(12, 2), nullable=False),
        sa.Column("suggested_price_min", sa.Numeric(12, 2), nullable=True),
        sa.Column("suggested_price_max", sa.Numeric(12, 2), nullable=True),
        sa.Column("confidence_score", sa.Float(), nullable=False),
        sa.Column("rationale_internal", sa.JSON(), nullable=False),
        sa.Column("rationale_external", sa.JSON(), nullable=False),
        sa.Column("expected_days_to_sell", sa.Integer(), nullable=True),
        sa.Column("model_name", sa.String(100), nullable=False),
        sa.Column("prompt_version", sa.String(50), nullable=False),
        sa.Column("status", sa.String(50), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("ai_proposals")
    op.drop_table("products")
