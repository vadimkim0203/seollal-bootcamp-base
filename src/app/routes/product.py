from fastapi import APIRouter, Depends

from app.schemas.base import BasePaginationRequest
from app.schemas.product import (
    ProductCreateRequest,
    ProductCreateResponse,
    ProductDetailResponse,
    ProductListResponse,
    ProductUpdateRequest,
)
from app.services.product import ProductService
from app.settings import Settings

router = APIRouter(tags=["products"])


settings = Settings()


@router.post("/", status_code=201)
async def create_product(
    product: ProductCreateRequest,
    product_service: ProductService = Depends(ProductService),
) -> ProductCreateResponse:
    return await product_service.create(product)


@router.get("/")
async def paginate_products(
    pagination_query: BasePaginationRequest = Depends(BasePaginationRequest),
    product_service: ProductService = Depends(ProductService),
) -> ProductListResponse:
    return await product_service.paginate(
        pagination_query,
        requesting_path="{public_base_url}/products".format(public_base_url=settings.public_base_url),
    )


@router.get("/{id}")
async def get_product_detail(
    id: int,
    product_service: ProductService = Depends(ProductService),
) -> ProductDetailResponse:
    return await product_service.get_detail(id)


@router.patch("/{id}")
async def edit_product(
    id: int,
    product: ProductUpdateRequest,
    product_service: ProductService = Depends(ProductService),
) -> ProductDetailResponse:
    return await product_service.update(id, product)


@router.delete("/{id}", status_code=204)
async def delete_product(
    id: int,
    product_service: ProductService = Depends(ProductService),
):
    await product_service.delete(id)
