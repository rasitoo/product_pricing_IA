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
    # ── Tables missing from 0001 ───────────────────────────────────────────────

    op.create_table(
        "historical_references",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("product_id", sa.Uuid(), sa.ForeignKey("products.id"), nullable=False),
        sa.Column("comparable_product_id", sa.String(255), nullable=False),
        sa.Column("sold_price", sa.Numeric(12, 2), nullable=False),
        sa.Column("sold_at", sa.DateTime(), nullable=False),
        sa.Column("condition_label", sa.String(100), nullable=True),
        sa.Column("similarity_score", sa.Float(), nullable=True),
    )

    op.create_table(
        "product_images",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("product_id", sa.Uuid(), sa.ForeignKey("products.id"), nullable=False),
        sa.Column("storage_uri", sa.String(1024), nullable=False),
        sa.Column("sha256_hash", sa.String(64), nullable=False),
        sa.Column("width", sa.Integer(), nullable=True),
        sa.Column("height", sa.Integer(), nullable=True),
        sa.Column("mime_type", sa.String(100), server_default="image/jpeg"),
        sa.Column("ai_annotations", sa.JSON(), nullable=True),
        sa.Column("quality_score", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_product_images_sha256_hash", "product_images", ["sha256_hash"])

    op.create_table(
        "external_comparables",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("proposal_id", sa.Uuid(), sa.ForeignKey("ai_proposals.id"), nullable=False),
        sa.Column("source_name", sa.String(100), nullable=False),
        sa.Column("listing_url", sa.String(2048), nullable=False),
        sa.Column("listed_price", sa.Numeric(12, 2), nullable=True),
        sa.Column("currency", sa.String(3), nullable=True),
        sa.Column("observed_at", sa.DateTime(), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=True),
    )

    op.create_table(
        "llm_metrics",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("product_id", sa.Uuid(), sa.ForeignKey("products.id"), nullable=True),
        sa.Column("proposal_id", sa.Uuid(), sa.ForeignKey("ai_proposals.id"), nullable=True),
        sa.Column("provider", sa.String(50), server_default="openai"),
        sa.Column("model_name", sa.String(100), server_default="mock-model"),
        sa.Column("input_tokens", sa.Integer(), server_default="0"),
        sa.Column("output_tokens", sa.Integer(), server_default="0"),
        sa.Column("cost_usd", sa.Numeric(12, 6), server_default="0"),
        sa.Column("latency_ms", sa.Integer(), server_default="0"),
        sa.Column("outcome", sa.String(50), server_default="success"),
        sa.Column("error_type", sa.String(100), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )

    op.create_table(
        "operator_reviews",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("proposal_id", sa.Uuid(), sa.ForeignKey("ai_proposals.id"), nullable=False),
        sa.Column("operator_id", sa.String(255), nullable=False),
        sa.Column("decision", sa.String(50), nullable=False),
        sa.Column("edited_description_text", sa.String(), nullable=True),
        sa.Column("edited_price", sa.Numeric(12, 2), nullable=True),
        sa.Column("reject_reason", sa.String(), nullable=True),
        sa.Column("notes", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )

    op.create_table(
        "publication_drafts",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("product_id", sa.Uuid(), sa.ForeignKey("products.id"), nullable=False),
        sa.Column("proposal_id", sa.Uuid(), sa.ForeignKey("ai_proposals.id"), nullable=False),
        sa.Column("export_format", sa.String(20), server_default="json"),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("status", sa.String(50), server_default="ready"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )

    # ── Carousel review tables (feature 002) ──────────────────────────────────
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
    op.drop_table("publication_drafts")
    op.drop_table("operator_reviews")
    op.drop_table("llm_metrics")
    op.drop_table("external_comparables")
    op.drop_index("ix_product_images_sha256_hash", table_name="product_images")
    op.drop_table("product_images")
    op.drop_table("historical_references")
