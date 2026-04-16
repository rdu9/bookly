# asta e fisieru principal, aici te conectezi din prima cu baza de date, adaugi toate rutele etc, asta e inima.

from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from src.books.routes import book_router
from contextlib import asynccontextmanager
from src.db.main import init_db
from src.auth.routers import auth_router
from src.reviews.routes import review_router
from .errors import register_all_errors
from .middleware import register_middleware

# asta e gen ca sa arate cand se porneste serveru si cand se opreste
# cand se porneste serveru tot codu de inainte de YIELD apare, si await init_db() e ca sa se conecteze cu baza de date
# dupa yield totu da run gen la final
# nu mai e folosit acm


@asynccontextmanager
async def life_span(app: FastAPI):
    print("server is starting....")
    await init_db()
    yield
    print("server has been stopped")


version = "v1"

version_prefix =f"/api/{version}"

# lifespan = life_span doar conecteaza functia de startup shutdown, atat face lifespanu

app = FastAPI(
    version=version,
    title="bookly",
    description="A REST API for a book review web service",
    #docs_url=f"/api/{version}/docs"
    #redoc_url=f"/api/{version}/redoc"
    contact = {
        "email": "devouration123@gmail.com"
    },
    openapi_url=f"{version_prefix}/openapi.json",
)

register_all_errors(app)

register_middleware(app)


# bagam routerele, adica numele la variabila aia din routes.py
# prefixu seteaza endpointu si nu mai trb sa avem nimic in routes
# version seteaza versionu
# tags e pentru swagger ui

app.include_router(book_router, prefix=f"/api/{version}/books", tags=["books"])
app.include_router(auth_router, prefix=f"/api/{version}/auth", tags=["auth"])
app.include_router(review_router, prefix=f"/api/{version}/reviews", tags=["reviews"])

