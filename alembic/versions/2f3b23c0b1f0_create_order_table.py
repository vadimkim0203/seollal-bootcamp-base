"""create order table

Revision ID: 2f3b23c0b1f0
Revises: 97219e6f07e5
Create Date: 2025-01-28 18:41:43.287585

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "2f3b23c0b1f0"
down_revision: Union[str, None] = "97219e6f07e5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "order",
        sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column("customer_name", sa.Unicode(255), index=True, nullable=False),
        sa.Column("address", sa.Text(), nullable=False),
        sa.Column("contents", sa.String(1024)),
        sa.Column("created_at", sa.TIMESTAMP, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP,
            server_default=sa.text("CURRENT_TIMESTAMP"),
            server_onupdate=sa.text("CURRENT_TIMESTAMP"),
        ),
    )


def downgrade() -> None:
    op.drop_table("order")
