# astea sunt rutele, aici se dau handle la toate requesturile pe api, si se filtreaza tot. asta e inima adevarata a comenzilor


from fastapi import APIRouter, status, Depends
from fastapi.exceptions import HTTPException
from pydantic import BaseModel
from typing import List
from .schemas import BookUpdateModel, Book, BookCreateModel, BookDetailModel
from typing import List, Optional
from src.db.main import get_session
from sqlmodel.ext.asyncio.session import AsyncSession
from .service import BookService
import uuid
from src.auth.dependencies import AccesTokenBearer, RoleChecker
from src.errors import BookNotFound

book_router = APIRouter()
book_service = BookService()
acces_token_bearer = AccesTokenBearer()
role_checker = RoleChecker(["admin", "user"])

# la toate astea noi dam call la book_service, care face parte din service.py care e prescurtarea noastra
# toate apeleaza acele functii si le da tot ce au nevoie ca sa mearga, asta face totu mai simplu si mai optimizat
# singuru lucru iesti din comun e sesiunea, pe care trb sa o tinem dupa noi mereu, ca asa e la postgres
# si depends face conexiunea cu get_session, care gen ia direct sesiunea autentica,  fara ea n ar merge nimic
# pe scurt asta e HTTML, ia ce vrea useru, si trimite requestu altundeva, unde chiar se modifica baza de date, asta e doar FATADA

# putem refolosi Book si la response model si la payload, nu conteaza
# aici punem List[] din typing la book ca sa mearga cum trb returnu

# nota, depends inseamna ca functia DEPINDE de chestiile alea, daca get_session sau acces_token_bearer nu merg, functia de rute niciodata nu va merge nici ea
# la toate functiile de aici trebuie sa dai un acces token, ca sa ai acces la chestiile astea
# acces token bearer doar verifica daca useru a trimis un acces token, atat. si user details ia toate detaliile lui si pune intro variabila in caz de asta
# token_details doar decodeaza tokenu pe care deja il dai in authorization


# chestie noua, dependencies=[] la nivelu de decorator
# inainte puneam Depends() in functii direct, dar acm este la nivelu de decorator dependencies=[Depends(role_checker)]
# diferenta e ca:
# - folisim inauntru functiei doar cand avem nevoie de valoarea returnata
# - de exemplu la token_details: dict = Depends(acces_token_bearer) e nevoie de token_details, deci punem in functie
# - in schimb la nivelu de decorator, folosim doar cand avem nevoie de verificarea in sine
# - dependencies=[Depends(role_checker)] trebuie doar sa verificam daca useru e ok sau il blocam
# - daca nu avem nevoie de functia de return, punem in decorator.


@book_router.get("/", response_model=List[Book], dependencies=[Depends(role_checker)])
async def get_all_books(
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(acces_token_bearer),
):
    books = await book_service.get_all_books(session)
    return books
    # role_checker e rulat automat inainte de functia asta, si daca rolu userului nu e in alllowed roles atunci se da 403 si functia nu merge niciodata


@book_router.get(
    "/user/{user_uid}", response_model=List[Book], dependencies=[Depends(role_checker)]
)
async def get_user_books_submissions(
    user_uid: str,
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(acces_token_bearer),
):

    books = await book_service.get_user_books(user_uid, session)
    return books
    # aceasi chestie ca mai sus, doar ca cu user_uid necesar si un nou book_service din services.py


# modulu status are toate codurile, si se intampla cand totu e valid


@book_router.post(
    "/", status_code=status.HTTP_201_CREATED, dependencies=[Depends(role_checker)]
)
async def create_a_book(
    payload: BookCreateModel,
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(acces_token_bearer),
):
    user_id = token_details.get("user")[
        "user_uid"
    ]  # pe scurt, iei idu userului din token, si il bagi automat aici, useru nu trimite nmc, totu e in backend
    new_book = await book_service.create_book(payload, user_id, session)
    return new_book


# book['id'] ca e dictionar gen si luam 1 cate 1
# raise EXCEPTION doar ia exceptionu cand se intampla ceva rau, si status codeu ii ia status codeu, si detail e mesaju pe care il da acolo


@book_router.get(
    "/{book_uid}", response_model=BookDetailModel, dependencies=[Depends(role_checker)]
)
async def get_book(
    book_uid: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(acces_token_bearer),
):

    book = await book_service.get_book(book_uid, session)
    if book:
        return book
    else:
        raise BookNotFound()


@book_router.patch("/{book_uid}", dependencies=[Depends(role_checker)])
async def update_book(
    book_uid: uuid.UUID,
    payload: BookUpdateModel,
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(acces_token_bearer),
) -> dict:
    book_to_update = await book_service.update_book(book_uid, payload, session)
    if book_to_update:
        return book_to_update
    else:
        raise BookNotFound()


# aici e fara response body, care e gen -> dict ( de la status code 204 )


@book_router.delete(
    "/{book_uid}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(role_checker)],
)
async def delete_book(
    book_uid: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(acces_token_bearer),
):
    deleted_book = await book_service.delete_book(book_uid, session)
    if deleted_book:
        return None
    else:
        raise BookNotFound()


@book_router.post(
    "/{book_uid}", status_code=status.HTTP_200_OK, dependencies=[Depends(role_checker)]
)
async def update_book(
    payload: BookUpdateModel,
    book_uid: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(acces_token_bearer),
):
    response = await book_service.update_book(book_uid, payload, session)
    if response:
        return response
    else:
        raise BookNotFound()


# from fastapi import FastAPI, Request, Depends
# from fastapi.responses import HTMLResponse
# from fastapi.templating import Jinja2Templates
# from sqlmodel import select, desc
# from sqlalchemy.ext.asyncio import AsyncSession
# from ..books.models import Book
# from ..db.main import get_session
#
# templates = Jinja2Templates(directory=".templates")
#
# @book_router.get("/test/da", response_class=HTMLResponse)
# async def get_books_page(request: Request, session: AsyncSession = Depends(get_session)):
#
#    from sqlmodel import select, desc
#    from .models import Book
#
#    statement = select(Book).order_by(desc(Book.created_at))
#    result = await session.exec(statement)
#    books = result.all()
#
#    # 2. Return the template using the book_router's context
#    return templates.TemplateResponse(
#        "index.html",
#        {"request": request, "books": books}
#    )
# https://prnt.sc/0-HA9EjEJmyF
