from sqlmodel import Relationship, SQLModel, Field, Column, Relationship
import uuid
from typing import Optional, List
import sqlalchemy.dialects.postgresql as pg
from datetime import datetime, date
from fastapi import Depends

# fix acealasi pattern ca la Book ,foarte simplu


class User(SQLModel, table=True):
    __tablename__ = "users"
    uid: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        sa_column=Column(
            pg.UUID,
            nullable=False,
            primary_key=True,
        ),
    )
    username: str
    email: str
    first_name: str
    last_name: str
    role: str = Field(
        sa_column=Column(pg.VARCHAR, nullable=False, server_default="user")
    )

    # fiecare user incepe ca neverificat, si dupa intro aplicatie noramala primesti link cu email, si asta se face true, ca gen se verifica
    # acm e doar stored, da nu e folosit la nimic

    is_verified: bool = Field(default=False)

    # exclude=True inseamna ca niciodata nu va fi inclus in api responses, asta e al 2 lea layer de securitate
    # asta face clar parola imposibil de dat leak

    password_has: str = Field(exclude=True)
    created_at: datetime = Field(
        default_factory=datetime.now, sa_column=Column(pg.TIMESTAMP)
    )
    updated_at: datetime = Field(
        default_factory=datetime.now, sa_column=Column(pg.TIMESTAMP)
    )
    
    books: List["Book"] = Relationship(back_populates="user", sa_relationship_kwargs={'lazy':'selectin'})
    
    
    # asta ii zice User ului ca poate sa aiba o lista de carti
    # back_populates = user, asta ii zice unde sa se uite ca sa gaseasca variabila, cu ajotorul lui models.Book
    # pe scurt, user e variabila, si models.Book e table u
    # selectin e pe scurt un fel de async, care da fetch la user intrun query secundal mult mai simply. fara asta, se intampla Lazy Loadingu si erau multe erori
    
    
    reviews: List["Review"] = Relationship(back_populates="user", sa_relationship_kwargs={'lazy':'selectin'})
    
    # asta e o lista cu toate reviewurile scrise de respectivu user ( ca obiect )

    def __repr__(self):
        return f"<User {self.username}"


# --------------------------


# cand updatezi user_uidu si dai commit, incepe totul:
# - pythonu se uita la relationship si vede back_populates=books
# - logica zice: cartea acm e a lui useru 123, acm trebuie sa gasim care parte din memorie are idu 123
# - atunci cand gaseste acel User boject, se da append direct

class Book(SQLModel, table=True):
    
    # seteaza numele tablei in db 
    # table=True spune la postgres sa creze o tabela reala in db
    # field aici e ca la schemas, nu e mare diferenta
    
    __tablename__ = "books"
    
    uid: uuid.UUID = Field(
        default_factory=uuid.uuid4,   
        sa_column=Column(
            pg.UUID,
            nullable=False,
            primary_key=True,
        )
    )
    title: str
    author: str
    publisher: str
    published_date: date
    page_count: int
    language: str
    user_uid: Optional[uuid.UUID] = Field(default_factory=None, foreign_key="users.uid")
    
    # foreign_key ii zice databaseului sa se duca la users table ( User, asa e denumita cu __tablename__ ) si sa caute variabila uid
    # asta da check sa vada daca ce ai bagat tu aici exista in users.uid, asta e chestia, foreign_key e sa verifice daca exista respectivu lucru in celalalt table, o conexiune directa
    # pe scurt verifica daca cel ce a facut requestu si a pasat aici user idu exista in User db, e un check in plus in caz de orice
    # daca user_uid u dat de tine nu exista in users.uid ( User.uid ) se distruge tot

    created_at: datetime = Field(default_factory=datetime.now,sa_column=Column(pg.TIMESTAMP))
    updated_at: datetime = Field(default_factory=datetime.now,sa_column=Column(pg.TIMESTAMP))
    
    user: Optional["User"] = Relationship(back_populates="books")
    
    # user: are tot User objectu cu idu cartii ( care e luat cu foreign key ), tot despre el
    # Optional["models.User"] - baza de date pe care o cauta
    # Relationship() - ii tine in sync
    # back_populates - face sa se updateze constant
    #-----------------------------------
    # asta cu optional ii zice pythonului unde sa se uite ca sa gaseasca acel table, adica in models.User
    # asta ii zice modelului Book ca useru cartii este pentru un User
    # back_populates="books" - asta spune ca daca python se uita la acel User, ce cauta este variabila books
    # user: ia informatiile la TOATA TABLA, tot din User
    
    reviews: List["Review"] = Relationship(back_populates="book", sa_relationship_kwargs={'lazy':'selectin'}) # contine object de review full
    #SQLModel looks at that List["Review"] and says: "Okay, the user wants a collection of the class named Review." - DIN CLAUDE
    
    # asta e o lista cu toate reviewurile scrise pentru cartea respectiva ( ca obiect )


    def __repr__(self):
        return f"<Book {self.title}>"
    

class Review(SQLModel, table=True):
    
    __tablename__ = "reviews"
    
    uid: uuid.UUID = Field(
        default_factory=uuid.uuid4,   
        sa_column=Column(
            pg.UUID,
            nullable=False,
            primary_key=True,
        )
    )
    rating: int = Field(lt=5, gt=1)
    review_text: str
    
    user_uid: Optional[uuid.UUID] = Field(default_factory=None, foreign_key="users.uid")
    book_uid: Optional[uuid.UUID] = Field(default_factory=None, foreign_key="books.uid")
    
    # asta verifica ca user idu si book idu chiar exista in baza de date
    # asta face si linku dintre db, important
    
    created_at: datetime = Field(default_factory=datetime.now,sa_column=Column(pg.TIMESTAMP))
    updated_at: datetime = Field(default_factory=datetime.now,sa_column=Column(pg.TIMESTAMP))  
    
    user: Optional["User"] = Relationship(back_populates="reviews")
    book: Optional["Book"] = Relationship(back_populates="reviews")
    
    # acest object de review are nevoie de objectu User care a lasat reviewu, dar si cartea, tot obiectu full
    # obiectele sunt date direct din services.py, dupa ce sunt luate cu get_user_by_email si get_current_user ca sa ia emailu
    

    def __repr__(self):
        return f"<Review for book {self.self.book_uid} by {self.user_uid}>"
    