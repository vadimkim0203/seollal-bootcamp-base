from decimal import Decimal

from pydantic import BaseModel, Field, HttpUrl
from sqlalchemy import (
    BigInteger,
    Column,
    Integer,
    Numeric,
    String,
    Table,
    Text,
    Unicode,
)

from app.models import metadata


class Product(BaseModel):
    id: int
    name: str
    description: str | None
    image: HttpUrl | None
    price: Decimal | None = Field(max_digits=12, decimal_places=2)
    stock: int = 0


product_table = Table(
    "product",
    metadata,
    Column("id", BigInteger, primary_key=True),
    Column("name", Unicode(255), index=True, nullable=False),
    Column("description", Text()),
    Column("image", String(1024)),
    Column("price", Numeric(12, 2), index=True),
    Column("stock", Integer, index=True, nullable=False, server_default="0"),
)
