"""Cria tabela order_items com FK para orders.

Revision ID: 20260127_0002
Revises: 20260126_0001
Create Date: 2026-01-27

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260127_0002"
down_revision: str | None = "20260126_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "order_items",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("order_id", sa.Integer(), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("unit_price", sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(
            ["order_id"],
            ["orders.id"],
            name="order_items_order_id_fkey",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="order_items_pkey"),
    )
    op.create_index(
        "ix_order_items_order_id",
        "order_items",
        ["order_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_order_items_order_id", table_name="order_items")
    op.drop_table("order_items")
