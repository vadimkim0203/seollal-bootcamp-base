"""add product table

Revision ID: 97219e6f07e5
Revises:
Create Date: 2025-01-28 12:31:35.406565

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "97219e6f07e5"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "product",
        sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column("name", sa.Unicode(255), index=True, nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("image", sa.String(1024)),
        sa.Column("price", sa.Numeric(12, 2), index=True, nullable=False),
        sa.Column("stock", sa.Integer, index=True, nullable=False, server_default="0"),
        sa.Column("created_at", sa.TIMESTAMP, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP,
            server_default=sa.text("CURRENT_TIMESTAMP"),
            server_onupdate=sa.text("CURRENT_TIMESTAMP"),
        ),
    )


def downgrade() -> None:
    op.drop_table("product")
