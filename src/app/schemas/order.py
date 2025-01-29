from pydantic import BaseModel

from app.schemas.base import BaseListResponse


class OrderListItem(BaseModel):
    id: int
    customer_name: str
    address: str
    contents: str


class OrderListResponse(BaseListResponse):
    results: list[OrderListItem]


class OrderDetailResponse(BaseModel):
    id: int
    customer_name: str
    address: str
    contents: str


class OrderCreateRequest(BaseModel):
    customer_name: str
    address: str
    contents: str
