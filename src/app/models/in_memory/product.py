from sqlalchemy import (
    Column,
    Integer,
    Numeric,
    String,
    Table,
    Text,
    Unicode,
)

from app.models.in_memory import metadata

product_table = Table(
    "product",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("name", Unicode(255), index=True, nullable=False),
    Column("description", Text()),
    Column("image", String(1024)),
    Column("price", Numeric(12, 2), index=True),
    Column("stock", Integer, index=True, nullable=False, server_default="0"),
)

# one downside of sqlite is that it can't handle certain data types
# in this case, it can't handle BigInteger for the 'id' column
# so we create the exact same table for sqlite but use the Integer type instead
