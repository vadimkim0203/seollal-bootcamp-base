from fastapi import Query
from pydantic import BaseModel


class BaseListResponse(BaseModel):
    results: list
    next: str
    previous: str


class BasePaginationRequest(BaseModel):
    # Can't get a page below 0
    page: int = Query(ge=0, default=0)
    # Let's not allow more than 200 results per page
    size: int = Query(ge=1, le=200, default=20)
