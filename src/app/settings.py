from pydantic_settings import BaseSettings


# This Settings class automatically retrieves environment variables and stores them
# in these class variables. Environment variable names are expected to be in all caps.
# Type validation is done automatically.
class Settings(BaseSettings):
    public_base_url: str = "http://localhost:5000"
    host_address: str = "0.0.0.0"
    port: int = 5000
    db_host: str = "localhost"
    db_port: int = 5432
    db_username: str = "root"
    db_password: str = "root"
    db_database: str = "ecommerce"
