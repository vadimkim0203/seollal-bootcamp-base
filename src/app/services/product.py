from fastapi import Depends
from sqlalchemy import Connection, literal_column

from app.database import database_connection
from app.models.product import product_table
from app.schemas.base import BaseListRequest
from app.schemas.product import (
    ProductCreateRequest,
    ProductCreateResponse,
    ProductDetailResponse,
    ProductListResponse,
    ProductListResponseItem,
    ProductUpdateRequest,
)


class ProductService:
    def __init__(self, db: Connection = Depends(database_connection)):
        # It's not exactly a Connection, but this will help our auto-complete
        self.db = db

    async def create(self, product: ProductCreateRequest) -> ProductCreateResponse:
        # Use the table object to help identify the columns to be inserted
        # Dump our model to a dictionary for SQLAlchemy to map the attributes to columns
        # Then return all columns
        insert_statement = (
            product_table.insert()
            .values(product.model_dump())
            .returning(literal_column("*"))
        )
        # Run the insert. Don't forget to await!
        result_records = await self.db.execute(insert_statement)
        # mappings() to map the results back to a dictionary
        # first() because we want the first (only) result
        result = result_records.mappings().first()
        # ** unpacks the dictionary items to key-value parameters
        response = ProductCreateResponse(**result)
        return response

    async def list(
        self, list_query: BaseListRequest, requesting_path: str
    ) -> list[ProductListResponse]:
        if list_query.page > 0:
            previous_page = (
                "{requesting_path}?page={page}&count_per_page={count_per_page}".format(
                    requesting_path=requesting_path,
                    page=list_query.page - 1,
                    count_per_page=list_query.count_per_page,
                )
            )
        else:
            previous_page = ""

        next_page = (
            "{requesting_path}?page={page}&count_per_page={count_per_page}".format(
                requesting_path=requesting_path,
                page=list_query.page + 1,
                count_per_page=list_query.count_per_page,
            )
        )

        select_statement = (
            product_table.select()
            .limit(list_query.count_per_page)
            .offset(list_query.page * list_query.count_per_page)
        )
        result_records = await self.db.execute(select_statement)
        records = result_records.mappings().all()
        response = ProductListResponse(
            results=[ProductListResponseItem(**record) for record in records],
            next=next_page,
            previous=previous_page,
        )
        return response

    async def get_detail(self, id: int) -> ProductDetailResponse:
        select_statement = product_table.select().where(product_table.c.id == id)
        result_records = await self.db.execute(select_statement)
        result = result_records.mappings().first()
        response = ProductDetailResponse(**result)
        return response

    # https://fastapi.tiangolo.com/tutorial/body-updates/#partial-updates-recap
    async def update(
        self, id: int, product: ProductUpdateRequest
    ) -> ProductDetailResponse:
        product_detail = await self.get_detail(id)
        update_data = product.model_dump(exclude_unset=True)
        updated_item = product_detail.model_copy(update=update_data)
        update_statement = (
            product_table.update()
            .where(product_table.c.id == id)
            .values(updated_item.model_dump())
            .returning(literal_column("*"))
        )
        result_records = await self.db.execute(update_statement)
        result = result_records.mappings().first()
        response = ProductDetailResponse(**result)
        return response

    async def delete(self, id: int):
        delete_statement = product_table.delete().where(product_table.c.id == id)
        await self.db.execute(delete_statement)
