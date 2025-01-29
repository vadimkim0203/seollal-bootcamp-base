from fastapi import Depends
from sqlalchemy import literal_column
from sqlalchemy.ext.asyncio.engine import AsyncConnection

from app.database.connection_provider import database_connection
from app.models.order import order_table
from app.schemas.order import OrderCreateRequest, OrderDetailResponse, OrderListResponse


class OrderService:
    def __init__(self, db: AsyncConnection = Depends(database_connection)):
        # It's not exactly a Connection, but this will help our auto-complete
        self.db = db

    async def create(self, order: OrderCreateRequest) -> OrderDetailResponse:
        # Use the table object to help identify the columns to be inserted
        # Dump our model to a dictionary for SQLAlchemy to map the attributes to columns
        # Then return all columns
        insert_statement = order_table.insert().values(order.model_dump()).returning(literal_column("*"))
        # Run the insert. Don't forget to await!
        result_records = await self.db.execute(insert_statement)
        # mappings() to map the results back to a dictionary
        # first() because we want the first (only) result
        result = result_records.mappings().first()
        # ** unpacks the dictionary items to key-value parameters
        response = OrderDetailResponse(**result)
        return response

    async def list() -> OrderListResponse:
        raise NotImplementedError()

    async def get(id: int) -> OrderDetailResponse:
        raise NotImplementedError()
