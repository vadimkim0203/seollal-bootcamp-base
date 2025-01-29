from fastapi import Depends

from app.database import Repository
from app.database.repository_factory import get_product_repository
from app.models.product import product_table
from app.schemas.base import BasePaginationRequest
from app.schemas.product import (
    ProductCreateRequest,
    ProductCreateResponse,
    ProductDetailResponse,
    ProductListResponse,
    ProductListResponseItem,
    ProductUpdateRequest,
)


class ProductService:
    def __init__(self, repository: Repository = Depends(get_product_repository)):
        self.repository = repository

    async def create(self, product: ProductCreateRequest) -> ProductCreateResponse:
        result = await self.repository.insert(product.model_dump())
        await self.repository.commit()
        response = ProductCreateResponse(**result)
        return response

    async def paginate(self, list_query: BasePaginationRequest, requesting_path: str) -> list[ProductListResponse]:
        records = await self.repository.paginate(
            select_statement=product_table.select(),
            filters=[],
            ordering=[],
            offset=list_query.page,
            size=list_query.size,
        )

        count = await self.repository.get_count(select_statement=product_table.select(), filters=[])

        response = ProductListResponse(
            results=[ProductListResponseItem(**record) for record in records],
            page=list_query.page,
            size=list_query.size,
            count=count,
        )
        return response

    async def get_detail(self, id: int) -> ProductDetailResponse | None:
        result = await self.repository.get_one(id)
        if result is not None:
            return ProductDetailResponse(**result)
        return result

    # https://fastapi.tiangolo.com/tutorial/body-updates/#partial-updates-recap
    async def update(self, id: int, product: ProductUpdateRequest) -> ProductDetailResponse:
        result = await self.repository.update(id=id, data=product.model_dump())
        await self.repository.commit()
        response = ProductDetailResponse(**result)
        return response

    async def delete(self, id: int):
        await self.repository.delete(id)
        await self.repository.commit()
