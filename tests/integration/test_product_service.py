from decimal import Decimal
from typing import Sequence

import pytest
from sqlalchemy import CursorResult, RowMapping, Select
from sqlalchemy.ext.asyncio.engine import AsyncConnection

from app.database import SqlAlchemyRepository
from app.models.product import product_table
from app.schemas.product import ProductCreateRequest, ProductCreateResponse, ProductDetailResponse, ProductUpdateRequest
from app.services.product import ProductService

# here, we show how tests can be useful in terms of refactoring existing code
# and to demonstrate the concept of DI
# we have testcode of the current ProductService which is tightly coupled with database stuff
# we are going to take out the database stuff and replace it with an abstraction we created
# called a Repository


@pytest.mark.asyncio(loop_scope="session")
async def test_product_create(product_repository: SqlAlchemyRepository, test_conn: AsyncConnection, product_data: dict):
    # GIVEN
    service = ProductService(repository=product_repository)

    # WHEN
    await service.create(product=ProductCreateRequest(**product_data))

    # THEN
    query: Select = product_table.select()
    execution: CursorResult = await test_conn.execute(query)
    found: Sequence[RowMapping] = execution.mappings().all()
    assert len(found) == 1
    created = found[0]
    for k, v in product_data.items():
        assert created[k] == v


@pytest.mark.asyncio(loop_scope="session")
async def test_product_update(
    product_repository: SqlAlchemyRepository,
    test_conn: AsyncConnection,
    product_data: dict,
):
    # GIVEN
    service = ProductService(repository=product_repository)
    product: ProductCreateResponse = await service.create(product=ProductCreateRequest(**product_data))

    product_data["stock"] = product.stock + 1
    product_data["price"] = round(product.price * Decimal(0.9), 2)

    # WHEN
    update_req = ProductUpdateRequest(**product_data)

    await service.update(
        id=product.id,
        product=update_req,
    )

    # THEN
    query: Select = product_table.select().where(product_table.c.id == product.id)
    execution: CursorResult = await test_conn.execute(query)
    found: RowMapping | None = execution.mappings().first()
    assert found is not None
    assert found["stock"] == update_req.stock
    assert found["price"] == update_req.price


@pytest.mark.asyncio(loop_scope="session")
async def test_product_delete(
    product_repository: SqlAlchemyRepository,
    test_conn: AsyncConnection,
    product_data: dict,
):
    # GIVEN
    service = ProductService(repository=product_repository)
    product: ProductCreateResponse = await service.create(product=ProductCreateRequest(**product_data))

    # WHEN
    await service.delete(id=product.id)

    # THEN
    query: Select = product_table.select().where(product_table.c.id == product.id)
    execution: CursorResult = await test_conn.execute(query)
    found: RowMapping | None = execution.mappings().first()
    assert found is None


@pytest.mark.asyncio(loop_scope="session")
async def test_product_get_one(
    product_repository: SqlAlchemyRepository,
    product_data: dict,
):
    # GIVEN
    service = ProductService(repository=product_repository)
    product: ProductCreateResponse = await service.create(product=ProductCreateRequest(**product_data))

    # WHEN
    found: ProductDetailResponse | None = await service.get_detail(id=product.id)

    # THEN
    assert found is not None
    assert found.id == product.id
