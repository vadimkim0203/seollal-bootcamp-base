import math
import random
from typing import AsyncGenerator

import pytest_asyncio
from fastapi.testclient import TestClient
from pytest import fixture
from sqlalchemy import RowMapping
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlalchemy.ext.asyncio.engine import AsyncConnection

from app.database import SqlAlchemyRepository
from app.main import app
from app.models.in_memory import metadata
from app.models.in_memory.product import product_table
from app.schemas.product import ProductCreateResponse


@fixture
def client():
    return TestClient(app)


# we can mock, stub or fake away the database during our tests
# but I think the best way to test while using a relational database
# is to use a fast, in-memory database
# it works almost exactly like the real thing(unless you use special functions inside a specific database)
# so you can test your code as close as possible to the actual database without actually
# having to use a real database which can be annoying to setup


# when the scope of the fixture is "session"
# the fixture is created and deleted once per entire test session
# test session means the begginning of the first test to the end of the final test
@pytest_asyncio.fixture(scope="session")
async def sqlite_engine() -> AsyncGenerator[AsyncEngine]:
    engine: AsyncEngine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        future=True,
    )
    # create an in memory database for testing
    async with engine.connect() as connection:
        async with connection.begin():
            # before creating the tables for the tests, drop everything
            await connection.run_sync(metadata.drop_all)
            await connection.run_sync(metadata.create_all)
        yield engine


# when the scope of the fixture is "function"
# the fixture is created and deleted once per test function
# by default, all fixtures have the scope "function"
@pytest_asyncio.fixture(scope="function")
async def sqlite_conn(sqlite_engine: AsyncEngine) -> AsyncGenerator[AsyncConnection]:
    async with sqlite_engine.connect() as connection:
        try:
            yield connection
        finally:
            # after we yield the connection and the test function is complete
            # we find all the tables we have created and clear them all of data
            async with sqlite_engine.connect() as connection:
                async with connection.begin():
                    for table in reversed(metadata.sorted_tables):
                        await connection.execute(table.delete())
                    await connection.commit()


@pytest_asyncio.fixture
def product_data() -> dict:
    return {
        "name": "test product {rand}".format(rand=math.floor(random.random() * 10000)),
        "description": "best product",
        "price": random.randrange(1000, 3000),
        "stock": random.randrange(10, 100),
    }


@pytest_asyncio.fixture
async def product_repository(sqlite_conn: AsyncConnection) -> SqlAlchemyRepository:
    repository = SqlAlchemyRepository(db=sqlite_conn, table=product_table)
    return repository


# fixtures work by pytest figuring out which fixture to use based on the fixture name
# here, we defined the "product_data" fixture and "product_repository" above
# and we use them in the fixture below by using the exact same name
@pytest_asyncio.fixture
async def test_product_and_repository(
    product_repository: SqlAlchemyRepository,
    product_data: dict,
) -> tuple[SqlAlchemyRepository, ProductCreateResponse]:
    result: RowMapping = await product_repository.insert(product_data)
    return product_repository, ProductCreateResponse(**result)
