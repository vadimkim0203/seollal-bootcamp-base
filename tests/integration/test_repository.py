import math
import random
from decimal import Decimal
from typing import Any, Sequence

import pytest
from sqlalchemy import CursorResult, RowMapping, Select
from sqlalchemy.ext.asyncio.engine import AsyncConnection
from sqlalchemy.sql.elements import ColumnElement, UnaryExpression

from app.database import SqlAlchemyRepository
from app.models.product import Product, product_table


@pytest.mark.asyncio(loop_scope="session")
async def test_repository_insert(test_conn: AsyncConnection, product_data: dict):
    # GIVEN
    repository = SqlAlchemyRepository(db=test_conn, table=product_table)

    # WHEN
    await repository.start()
    await repository.insert(data=product_data)
    await repository.commit()

    # THEN
    query: Select = product_table.select()
    execution: CursorResult = await test_conn.execute(query)
    found: Sequence[RowMapping] = execution.mappings().all()
    assert len(found) == 1
    created = found[0]
    for k, v in product_data.items():
        assert created[k] == v


@pytest.mark.asyncio(loop_scope="session")
async def test_repository_update(
    test_conn: AsyncConnection,
    test_product_and_repository: tuple[SqlAlchemyRepository, Product],
):
    # GIVEN
    repository, product = test_product_and_repository

    # WHEN
    update_req = {
        "stock": product.stock - 1,
        "price": int(product.price * Decimal(0.9)),
    }
    await repository.start()
    await repository.update(id=product.id, data=update_req)
    await repository.commit()

    # THEN
    query: Select = product_table.select().where(product_table.c.id == product.id)
    execution: CursorResult = await test_conn.execute(query)
    found: RowMapping | None = execution.mappings().first()
    assert found is not None
    assert found["stock"] == update_req["stock"]
    assert found["price"] == update_req["price"]


@pytest.mark.asyncio(loop_scope="session")
async def test_repository_delete(
    test_conn: AsyncConnection,
    test_product_and_repository: tuple[SqlAlchemyRepository, Product],
):
    # GIVEN
    repository, product = test_product_and_repository

    # WHEN
    await repository.start()
    await repository.delete(product.id)
    await repository.commit()

    # THEN
    query: Select = product_table.select().where(product_table.c.id == product.id)
    execution: CursorResult = await test_conn.execute(query)
    found: RowMapping | None = execution.mappings().first()
    assert found is None


@pytest.mark.asyncio(loop_scope="session")
async def test_repository_get_one(
    test_product_and_repository: tuple[SqlAlchemyRepository, Product],
):
    # GIVEN
    repository, product = test_product_and_repository

    # WHEN
    found: RowMapping | None = await repository.get_one(id=product.id)

    # THEN
    assert found is not None
    assert found["id"] == product.id


@pytest.mark.asyncio(loop_scope="session")
async def test_paginate(product_repository: SqlAlchemyRepository):
    # GIVEN
    product_repository.start()
    products: list[Product] = []
    for _ in range(40):
        test_product = {
            "name": "test product {rand}".format(rand=math.floor(random.random() * 10000)),
            "description": "best product",
            "price": random.randrange(1000, 3000),
            "stock": random.randrange(10, 100),
        }
        res = await product_repository.insert(test_product)
        products.append(Product(**res))
    product_repository.commit()

    # WHEN
    query: Select = product_table.select()

    filters: list[ColumnElement[bool]] = [
        product_table.c.price < 1500,
        product_table.c.stock > 45,
    ]

    ordering: list[UnaryExpression[Any]] = [
        product_table.c.id.asc(),
    ]

    res: Sequence[RowMapping] = await product_repository.paginate(
        select_statement=query,
        filters=filters,
        ordering=ordering,
        offset=0,
        size=20,
    )

    count: int = await product_repository.get_count(
        select_statement=query,
        filters=filters,
    )

    # THEN
    expected: list[Product] = [x for x in products if x.price < 1500 and x.stock > 45]
    assert count == len(expected)
    assert set([x["id"] for x in res]) == set([x.id for x in expected])
