from pydantic import BaseModel


# We'll use this model as a request body
class CreateUserBody(BaseModel):
    id: int
    name: str
    display_name: str | None = None


# We'll use this model as a response body
class CreateUserResult(BaseModel):
    id: int
    name: str
    display_name: str | None = None
    accepted: bool | None = None
    role: str | None = None
