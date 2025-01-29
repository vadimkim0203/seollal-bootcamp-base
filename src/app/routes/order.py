from fastapi import APIRouter, Depends

from app.schemas.order import OrderCreateRequest, OrderDetailResponse, OrderListResponse
from app.services.order import OrderService

router = APIRouter(tags=["orders"])


@router.get("/")  # GET /orders/
async def list(order_service: OrderService = Depends(OrderService)) -> OrderListResponse:
    return await order_service.list()


@router.post("/")  # POST /orders/
async def create(
    new_order_data: OrderCreateRequest, order_service: OrderService = Depends(OrderService)
) -> OrderDetailResponse:
    return await order_service.create(new_order_data)


@router.get("/{id}")  # GET  /orders/{id}
async def get_detail(id: int, order_service: OrderService = Depends(OrderService)) -> OrderDetailResponse:
    return await order_service.get(id)
