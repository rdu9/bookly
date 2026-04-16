# aici prescurtezi comenzile la db, in loc sa scrii acelasi kkt mereu poti face asta, ai nevoie doar de:
# - self ( ca e clasa gen , ca sa fie totu importat deodata in fisier sa nu scrii 1 pentru toate 4 sau cate o sa fie)
# - sesiunea , neaparat, ca sa stie pe ce db sa execute, sesiunea e conexiunea dintre python si baza de date, esentiala
# - variabile normale, gen book_uid: str ( e doar un exemplu )
# - si in final payloadu, pe care il verifici ca inainte, din schemas
# in concluzie totu e la fel ca la routes, doar ca te conectezi cu baza de date ( SESSION ) si ai self ( ca sa dai import la clasa )
# important: niciun obiect nu e validat, gen session: AsyncSession , book_data: BookCreateModel, e doar ca developerii sa stie ce fel de data asteapta, nu afecteaza peformanta

from sqlalchemy.ext.asyncio.session import AsyncSession
from src.books.schemas import BookCreateModel, BookUpdateModel
from sqlmodel import select, desc
from src.db.models import Book
from datetime import datetime
import uuid

# bookservice tine toata logica bazei de date intrun fisier, e gen un shortcut atat


class BookService:

    # sintaxa peste tot e fix ca la un db normal, da ca comenzile sunt cu select() etc pt securitate, nu raw sqltext

    async def get_all_books(self, session: AsyncSession):

        # functii foarte basic aici , sql normal, doar ca cu syntaxa asta putin diferita

        statement = select(Book).order_by(desc(Book.created_at))
        result = await session.exec(statement)
        return result.all()

    async def get_user_books(self, user_uid: str, session: AsyncSession):

        # functii foarte basic aici , sql normal, doar ca cu syntaxa asta putin diferita

        statement = (
            select(Book)
            .where(Book.user_uid == user_uid)
            .order_by(desc(Book.created_at))
        )
        result = await session.exec(statement)
        return result.all()

    async def get_book(self, book_uid: uuid.UUID, session: AsyncSession):

        # functii foarte basic aici , sql normal, doar ca cu syntaxa asta putin diferita

        statement = select(Book).where(Book.uid == book_uid)
        result = await session.exec(statement)
        book = result.first()
        return book if book is not None else None

    async def create_book(
        self, book_data: BookCreateModel, user_uid: str, session: AsyncSession
    ):

        # face dictionar

        book_data_dict = book_data.model_dump()

        # **book_data_dict despacheteaza dictionaru ca argumente
        # aceasti chestie cu Book(title="pula", author="mata"... etc)
        # uid, created_at, updated_at , sunt generate automat prin default_factory din models cred

        new_book = Book(**book_data_dict) # asta da shape la data direct in tabla Book cu **dictionar 

        new_book.published_date = book_data_dict["published_date"]

        new_book.user_uid = user_uid
        # asta adauga un nou field la carti, cu useru care a adaugato, gen idu lui
        # user_uid e un foreign key in books table, care da point direct la user.uid

        # adauga cartea in sesiune, da gen inca nu e in db

        session.add(new_book)

        # aici se salveaza permanent in db
        await session.commit()

        # dupa se da refresh doar ca un safety measure , ca sa nu fie None la return sau ceva rau de genu

        await session.refresh(new_book)
        return new_book

    async def update_book(
        self, book_uid: uuid.UUID, update_data: BookUpdateModel, session: AsyncSession
    ):

        # await e obligatoriu, ca get_book e async, amintesteti de discord.py
        # get_book ia doar din acelasi fisier, ca sa nu mai repete functia, ii da book_uid u si sessiunea, ca de asta are nevoie ca sa stie ce sa faca

        book_to_update = await self.get_book(book_uid, session)

        if book_to_update is not None:

            book_update_data_dict = (
                update_data.model_dump()
            )  # face dictionar, stii deja

            # setattr salveaza dinamic campurile obiectului
            # echivalent cu book_to_update.title = "Pulamealabaie"
            # util cand nu stii dinainte ce campuri se schimba
            # setattr te poti gandi ca doar seteaza atributeu gen, e foarte simplu, ii dai dictionaru si ce vrei sa adaugi (Key , Value)
            # nu trebuie sa scrii book.title = v, book.author = v etc pentru fiecare camp
            # daca clientu trimite doar title, doar title se schimba

            for k, v in book_update_data_dict.items():
                setattr(book_to_update, k, v)

            # aici baga in db oficial, dar nu trebuie sa dea refresh, pentru ca nu schimba total sau adauga sau kkt
            await session.commit()
            return book_to_update
        else:
            return None

    async def delete_book(self, book_uid: str, session: AsyncSession):

        # await e obligatoriu , fix mai sus, pentru ca functia e await ca in discord.py si o ia din acelasi fisier

        book_to_delete = await self.get_book(book_uid, session)

        if book_to_delete is not None:

            # marcheaza obiectivu pt stergere, inainte sa o faca

            await session.delete(book_to_delete)

            # acum se sterge oficial din db

            await session.commit()
            return {}
        else:
            return None
