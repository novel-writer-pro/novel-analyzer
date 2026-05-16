"""add loom_pairwise_evaluations table for B5 Elo wiring

Revision ID: 20260516_01
Revises: 20260513_01
Create Date: 2026-05-16
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "20260516_01"
down_revision = "20260513_01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if inspector.has_table("loom_pairwise_evaluations"):
        return
    op.create_table(
        "loom_pairwise_evaluations",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("branch_id", sa.String(36), nullable=False),
        sa.Column("chapter_index", sa.Integer, nullable=False),
        sa.Column("pair_id", sa.String(128), nullable=False),
        sa.Column("variant_a_id", sa.String(128), nullable=False),
        sa.Column("variant_b_id", sa.String(128), nullable=False),
        sa.Column("overall_preference", sa.String(8), nullable=False),
        sa.Column("overall_reason", sa.Text, nullable=False, default=""),
        sa.Column("confidence", sa.Float, nullable=False, default=0.0),
        sa.Column("evaluation_method", sa.String(32), nullable=False, default="llm_judge"),
        sa.Column("elo_rating_a_before", sa.Float, nullable=True),
        sa.Column("elo_rating_b_before", sa.Float, nullable=True),
        sa.Column("elo_rating_a_after", sa.Float, nullable=True),
        sa.Column("elo_rating_b_after", sa.Float, nullable=True),
        sa.Column("metadata_json", sa.JSON, nullable=False, default=dict),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    existing_indexes = {idx["name"] for idx in inspector.get_indexes("loom_pairwise_evaluations")} if inspector.has_table("loom_pairwise_evaluations") else set()
    if "ix_loom_pairwise_evaluations_branch_id" not in existing_indexes:
        op.create_index("ix_loom_pairwise_evaluations_branch_id",
                        "loom_pairwise_evaluations", ["branch_id"])
    if "ix_loom_pairwise_evaluations_pair_id" not in existing_indexes:
        op.create_index("ix_loom_pairwise_evaluations_pair_id",
                        "loom_pairwise_evaluations", ["pair_id"])


def downgrade() -> None:
    op.drop_table("loom_pairwise_evaluations")
