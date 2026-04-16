from pydantic import BaseModel, Field
from datetime import datetime
import uuid
from src.books.schemas import Book
from src.reviews.schemas import ReviewModel
from typing import List

# asta e checku pt cand un user vrea sa si faca contu, absolut nimic nou aici, doar mai multe fielduri ca e mai strict

class UserCreateModel(BaseModel):
    first_name: str = Field(max_length=25)
    last_name: str = Field(max_length = 25)
    username: str = Field(min_length=4,max_length=12)
    email: str = Field(max_length=40)
    password: str = Field(min_length=6)
    # pydantic valideaza toate astea automat, daca e usernameu prea mic - 422 , parola sub 6 caractere - 422
    
    
# asta e ce trimite inapoi api u dupa registrare sua login
# asta e schema de output, da verify la response

class UserModel(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str
    is_verified: bool 
    password_has: str = Field(exclude=True)
    # exclude e pentru protectie dubla, la cel mai safe nivel
    # si daca parola cumva ajunge in obiectu de response, exclude=True o scoate inainte sa ajunga la client
    # si cu asta sunt 2 layere de protectie, parola nu va ajunge niciodata unde nu trebuie
    created_at: datetime
    updated_at: datetime
    
class UserBooksModel(UserModel):
    books: List[Book]
    reviews: List[ReviewModel]
    # List[Book] inseamna ca atunci cand primesti informatia inapoi de la user primesti si toate cartile in acelasi response
    # asta e un request eficient de api, cu toate datele din prima

# schema pentru login, doar emailu si parola, restul nu e necesar pt login, deoarece doar astea verifica identitatea

class UserLoginModel(BaseModel):
    email: str = Field(max_length=40)
    password: str = Field(min_length=6)
    
class EmailModel(BaseModel):
    addresses: List[str]
    
class PaswordResetRequest(BaseModel):
    email: str
    
class PasswordResetConfirmModel(BaseModel):
    new_password: str
    confirm_new_password: str