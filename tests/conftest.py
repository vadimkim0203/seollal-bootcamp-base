import math
import random
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from pytest import fixture
from sqlalchemy import RowMapping
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlalchemy.ext.asyncio.engine import AsyncConnection
from testcontainers.postgres import PostgresContainer

from app.database import SqlAlchemyRepository
from app.main import app
from app.models import metadata
from app.models.product import product_table
from app.schemas.product import ProductCreateResponse
from app.settings import Settings


@fixture
def client():
    return TestClient(app)


# we can mock, stub or fake away the database during our tests
# but I think the best way to test while using a relational database
# 1. use the actual database we'll be using (postgres)
# 2. use an in-memory database
# we will go with option 1

settings = Settings()


# when the scope of the fixture is "session"
# the fixture is created and deleted once per entire test session
# test session means the beginning of the first test to the end of the final test
@pytest.fixture(scope="session")
def pg_container():
    """
    Spins up a PostgreSQL container for the entire test session.
    The container is torn down at the end of all tests.
    """
    container = PostgresContainer(
        image="postgres:latest",
        username=settings.db_username,
        password=settings.db_password,
        dbname=settings.db_database,
        driver="asyncpg",
    )
    container.start()
    try:
        yield container
    finally:
        container.stop()


# 2) Create an AsyncEngine to connect to the container (async fixture).
@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def pg_engine(pg_container: PostgresContainer) -> AsyncGenerator[AsyncEngine]:
    """
    Creates a single AsyncEngine pointing to the Postgres test container.
    Initializes (drop + create) tables once per entire session.
    """
    async_url = pg_container.get_connection_url()
    engine = create_async_engine(async_url, future=True)
    async with engine.connect() as connection:
        async with connection.begin():
            await connection.run_sync(metadata.drop_all)
            await connection.run_sync(metadata.create_all)

    yield engine

    # Properly dispose of the engine at session teardown
    await engine.dispose()


# 3) For each test function, yield a new connection and truncate data afterwards.
@pytest_asyncio.fixture(scope="function", loop_scope="session")
async def pg_conn(pg_engine: AsyncEngine) -> AsyncGenerator[AsyncConnection]:
    """
    Yields a new async connection for each test,
    and truncates all data from the tables afterwards.
    """
    async with pg_engine.connect() as connection:
        try:
            yield connection
        finally:
            # After each test, remove all data from the tables
            async with pg_engine.connect() as cleanup_conn:
                async with cleanup_conn.begin():
                    for table in reversed(metadata.sorted_tables):
                        await cleanup_conn.execute(table.delete())
                    await cleanup_conn.commit()


@pytest_asyncio.fixture
def product_data() -> dict:
    return {
        "name": "test product {rand}".format(rand=math.floor(random.random() * 10000)),
        "description": "best product",
        "price": random.randrange(1000, 3000),
        "stock": random.randrange(10, 100),
    }


@pytest_asyncio.fixture(loop_scope="session")
async def product_repository(pg_conn: AsyncConnection) -> SqlAlchemyRepository:
    repository = SqlAlchemyRepository(db=pg_conn, table=product_table)
    return repository


# fixtures work by pytest figuring out which fixture to use based on the fixture name
# here, we defined the "product_data" fixture and "product_repository" above
# and we use them in the fixture below by using the exact same name
@pytest_asyncio.fixture(loop_scope="session")
async def test_product_and_repository(
    product_repository: SqlAlchemyRepository,
    product_data: dict,
) -> tuple[SqlAlchemyRepository, ProductCreateResponse]:
    result: RowMapping = await product_repository.insert(product_data)
    return product_repository, ProductCreateResponse(**result)
