import sqlalchemy as sa
from pydantic import BaseModel

from app.models import metadata


class Order(BaseModel):
    id: int
    customer_name: str
    address: str
    contents: str


order_table = sa.Table(
    "order",
    metadata,
    sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
    sa.Column("customer_name", sa.Unicode(255), index=True, nullable=False),
    sa.Column("address", sa.Text(), nullable=False),
    sa.Column("contents", sa.String(1024)),
)
