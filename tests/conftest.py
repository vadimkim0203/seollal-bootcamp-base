import math
import random

from fastapi.testclient import TestClient
from pytest import fixture
from sqlalchemy import String, cast
from sqlalchemy.ext.asyncio import create_async_engine

from app.main import app
from app.models.product import product_table
from app.settings import Settings


@fixture
def client():
    return TestClient(app)


@fixture
async def db_connection():
    settings = Settings()
    connection_string = (
        "postgresql+asyncpg://{username}:{password}@{host}:{port}/{database}".format(
            username=settings.db_username,
            password=settings.db_password,
            host=settings.db_host,
            port=settings.db_port,
            database=settings.db_database,
        )
    )
    # This stores the SQLAlchemy engine back in the module-level object.
    # This ensures we don't accidentally create multiple connection pools.
    engine = create_async_engine(connection_string)

    # https://docs.sqlalchemy.org/en/20/tutorial/dbapi_transactions.html#committing-changes
    # Automatically create a transaction. Rollback on error. Commit on completion of the context.
    async with engine.connect() as connection:
        # Yield to ensure we return back to this context in order to commit properly.
        yield connection


@fixture
async def seed_product(db_connection):
    insert_statement = (
        product_table.insert()
        .values(
            {
                "name": "test product {rand}".format(
                    rand=math.floor(random.random() * 10000)
                ),
                "description": "best product",
                "price": 1000,
                "stock": 10,
            }
        )
        .returning(
            product_table.c.id,
            product_table.c.name,
            product_table.c.description,
            product_table.c.image,
            cast(product_table.c.price, String),
            product_table.c.stock,
        )
    )
    result_records = await db_connection.execute(insert_statement)
    result = result_records.mappings().first()
    await db_connection.commit()
    try:
        yield result
    finally:
        delete_statement = product_table.delete().where(
            product_table.c.id == result["id"]
        )
        await db_connection.execute(delete_statement)
        await db_connection.commit()
