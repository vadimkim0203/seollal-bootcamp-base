from sqlalchemy.ext.asyncio import create_async_engine

from app.settings import Settings

# We use this as a hidden, module-level object to ensure we re-use it.
__engine = None


async def database_connection():
    # Make sure we use the module-level object.
    global __engine
    if __engine is None:
        settings = Settings()
        connection_string = "postgresql+asyncpg://{username}:{password}@{host}:{port}/{database}".format(
            username=settings.db_username,
            password=settings.db_password,
            host=settings.db_host,
            port=settings.db_port,
            database=settings.db_database,
        )
        # This stores the SQLAlchemy engine back in the module-level object.
        # This ensures we don't accidentally create multiple connection pools.
        __engine = create_async_engine(connection_string)

    # https://docs.sqlalchemy.org/en/20/tutorial/dbapi_transactions.html#committing-changes
    # Automatically create a transaction. Rollback on error. Commit on completion of the context.
    async with __engine.begin() as connection:
        # Yield to ensure we return back to this context in order to commit properly.
        yield connection
