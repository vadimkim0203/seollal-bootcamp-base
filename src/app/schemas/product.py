from decimal import Decimal
from typing import List

from pydantic import BaseModel, Field, HttpUrl

from app.models.product import Product
from app.schemas.base import BaseListResponse


class ProductCreateRequest(BaseModel):
    name: str
    description: str | None
    image: HttpUrl | None
    price: Decimal = Field(max_digits=12, decimal_places=2)
    stock: int | None = 0


class ProductCreateResponse(Product):
    pass


class ProductListResponseItem(Product):
    pass


class ProductListResponse(BaseListResponse):
    results: List[ProductListResponseItem]


class ProductDetailResponse(Product):
    pass


class ProductUpdateRequest(ProductCreateRequest):
    name: str | None = None
    description: str | None = None
    image: HttpUrl | None = None
    price: Decimal | None = Field(default=None, max_digits=12, decimal_places=2)
    stock: int | None = None
