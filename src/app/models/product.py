from decimal import Decimal

import sqlalchemy as sa
from pydantic import BaseModel, Field, HttpUrl

from app.models import metadata


class Product(BaseModel):
    id: int
    name: str
    description: str | None
    image: HttpUrl | None
    price: Decimal | None = Field(max_digits=12, decimal_places=2)
    stock: int = 0


product_table = sa.Table(
    "product",
    metadata,
    sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
    sa.Column("name", sa.Unicode(255), index=True, nullable=False),
    sa.Column("description", sa.Text()),
    sa.Column("image", sa.String(1024)),
    sa.Column("price", sa.Numeric(12, 2), index=True),
    sa.Column("stock", sa.Integer, index=True, nullable=False, server_default="0"),
)
