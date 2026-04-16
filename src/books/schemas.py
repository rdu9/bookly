# aici setezi schemele, cum trebuie fiecare obiect sa fie, un fel de check in plus pentru fiecare

from pydantic import BaseModel
import uuid
from typing import List
from src.reviews.schemas import ReviewModel
from datetime import datetime,date

class Book(BaseModel):
        uid: uuid.UUID
        title: str
        author:str
        publisher: str
        published_date: date
        page_count: int
        language:  str 
        created_at: datetime
        updated_at: datetime
  
class BookDetailModel(Book):
        reviews: List[ReviewModel]
     
class BookCreateModel(BaseModel):
        title: str
        author:str
        publisher: str
        page_count: int
        published_date: date
        language:  str       
        
class BookUpdateModel(BaseModel):
        title: str
        author:str
        publisher: str
        page_count: int
        language:  str  