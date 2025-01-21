import psycopg2.pool as pool

from app.settings import Settings

_db_connection_pool: pool.ThreadedConnectionPool = None


def database_cursor():
    global _db_connection_pool
    if _db_connection_pool is None:
        settings = Settings()
        _db_connection_pool = pool.ThreadedConnectionPool(
            minconn=1,
            maxconn=10,
            host=settings.db_host,
            port=settings.db_port,
            user=settings.db_username,
            password=settings.db_password,
            dbname=settings.db_database,
        )

    with _db_connection_pool.getconn() as connection:
        with connection.cursor() as cursor:
            yield cursor
    _db_connection_pool.putconn(connection)
