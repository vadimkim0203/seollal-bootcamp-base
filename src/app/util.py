from fastapi import Depends

from app.schemas import CreateUserBody, CreateUserResult


def get_user_info(user: CreateUserBody) -> CreateUserResult:
    # Pydantic models can take in a kwargs to fill their values.
    # Here, we dump the create user body as a dictionary, then
    # feed the key-value pairs as named parameters to the
    # CreateUserResult constructor.
    user_result = CreateUserResult(**user.model_dump())
    user_result.role = "admin"
    return user_result


# This is clearly a convoluted example, but I gotta demonstrate something.
# Also, dependencies can call dependencies! This is how we build a
# dependency graph. Note that dependencies are a little magicky, so
# be careful to not over-use them.
def check_auth(user: CreateUserResult = Depends(get_user_info)) -> str:
    return user.role
