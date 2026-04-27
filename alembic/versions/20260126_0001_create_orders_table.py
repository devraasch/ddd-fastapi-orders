"""Cria tabela orders (estado inicial do schema).

Revision ID: 20260126_0001
Revises:
Create Date: 2026-01-26

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260126_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "orders",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("customer_name", sa.String(length=255), nullable=False),
        sa.Column("total", sa.Float(), nullable=False),
        sa.Column(
            "status",
            sa.String(length=50),
            nullable=False,
            server_default="PENDING",
        ),
        sa.PrimaryKeyConstraint("id", name="orders_pkey"),
    )


def downgrade() -> None:
    op.drop_table("orders")
