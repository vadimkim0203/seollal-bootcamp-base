from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field, HttpUrl
from sqlalchemy import (
    BigInteger,
    Column,
    Integer,
    MetaData,
    Numeric,
    String,
    Table,
    Text,
    Unicode,
)


class Product(BaseModel):
    id: int
    name: str
    description: Optional[str]
    image: Optional[HttpUrl]
    price: Optional[Decimal] = Field(max_digits=12, decimal_places=2)
    stock: int = 0


product_table = Table(
    "product",
    MetaData(),
    Column("id", BigInteger, primary_key=True),
    Column("name", Unicode(255), index=True, nullable=False),
    Column("description", Text()),
    Column("image", String(1024)),
    Column("price", Numeric(12, 2), index=True),
    Column("stock", Integer, index=True, nullable=False, server_default="0"),
)
