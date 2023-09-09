from fastapi.routing import APIRouter


router = APIRouter()


# Here's a custom route. Since we're prefixing the route
# with `/fancy` in our main file, we can hit this endpoint
# by visiting "<server>/fancy/hello".
@router.get("/hello")
def fancy_hello():
    return "HELLO YOU MAJESTIC BEING!"
