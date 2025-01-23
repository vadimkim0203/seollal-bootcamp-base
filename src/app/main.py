import uvicorn
from fastapi import FastAPI

from app.routes.product import router as product_router
from app.settings import Settings

# Don't forget to create your Settings object to use it!
settings = Settings()
# We'll store our main FastAPI application in this app variable
app = FastAPI()
# We can define routes on the FastAPI application directly, or
# we can create a separate router that can be included in the app
# logic. Note that we can define a prefix and organize routers by
# prefix. This allows you to logically split your application logic.
app.include_router(product_router, prefix="/products")


# From our pyproject.toml, we define this main function as our entrypoint.
def main():
    # Here, we run the FastAPI application under the Uvicorn ASGI server.
    # Note that we could also run uvicorn via the CLI directly:
    #   uvicorn --host 0.0.0.0 --port 5000 "app.main:app"
    uvicorn.run(
        "app.main:app",
        host=settings.host_address,
        port=settings.port,
        log_level="debug",
    )
