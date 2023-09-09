import uvicorn
from fastapi import Depends, FastAPI
from pydantic_settings import BaseSettings

from app.routes import router
from app.schemas import CreateUserResult
from app.util import check_auth, get_user_info


# This Settings class automatically retrieves environment variables and stores them
# in these class variables. Environment variable names are expected to be in all caps.
# Type validation is done automatically.
class Settings(BaseSettings):
    host_address: str = "0.0.0.0"
    port: int = 5000


# Don't forget to create your Settings object to use it!
settings = Settings()
# We'll store our main FastAPI application in this app variable
app = FastAPI()
# We can define routes on the FastAPI application directly, or
# we can create a separate router that can be included in the app
# logic. Note that we can define a prefix and organize routers by
# prefix. This allows you to logically split your application logic.
app.include_router(router, prefix="/fancy")


# Here's a simple example endpoint.
# The application's `get()` method allows us to define the function
# following the annotation as an API endpoint function. The first
# parameter of this annotation function is the path of the endpoint.
# Note that the actual function name can be anything.
@app.get("/hello")
def hello():
    # This will just return the string "hello" to the client
    return "hello"


# We can also define path parameters as part of this annotation function.
# FastAPI will recognize path parts surrounded by curly brackets {} as
# path parameters.
# You can then define function parameters whose name match your path
# parameters. FastAPI will automatically set those values to the path
# parameters' values.
# Note that FastAPI will perform type validation for you if you specify
# a type hint on the parameter.
@app.get("/hello/{name}")
def hello_name(name: str):
    # If you visit "<server address>/hello/myname", the server will output
    # "hello myname" to the client.
    return f"hello {name}"


# We're demonstrating a few things here:
# 1. We can do various HTTP methods using the FastAPI route annotations.
# 2. Dependency injection. More on that shortly.
# 3. We can validate response format using function return type hints.
@app.post("/user")
def create_user(
    auth_role=Depends(check_auth), user_info=Depends(get_user_info)
) -> CreateUserResult:
    # Note the FastAPI Depends() method. This allows us to specify additional
    # methods to run when we receive a request.
    # Also, note that there are no other parameters than these Depends. You
    # can specify request body parameters and query string parameters as
    # method parameters here, or you can do it via your dependency methods.
    # **Do note that I don't recommend what I'm doing here.** Using
    # dependencies to specify endpoint parameters makes it harder to trace
    # logic, especially since you can have multiple layers of dependencies.
    # I just wanted to make a point of it.
    # Also, notice how `check_auth` also depends on `get_user_info`. FastAPI
    # automatically builds a dependency graph and prevents the same dependency
    # from being called multiple times. `get_user_info` will only be called once.
    # Note that you can also use classes as dependencies. The `Depends()`
    # function accepts any Callable, so a class's constructor will be called
    # when used as a dependency. You can do some interesting behavior with
    # this, so be sure to consider it when you're building things.
    """
    Creates a new user (but not really)
    """
    # The above docstring comment will appear in our Swagger UI for the
    # API endpoint description.

    if auth_role == "admin":
        user_info.accepted = True
    else:
        user_info.accepted = False
    # Note that due to this function returning a CreateUserResult type
    # object, we have to make sure `user_info` matches that type.
    return user_info


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
