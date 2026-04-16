from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.models import User
from src.auth.dependencies import get_current_user
from .schemas import ReviewCreateModel
from src.db.main import get_session
from src.books.service import BookService
from .service import ReviewService

# aici nu e abs nimic interesant, doar o ruta normala cu service uri ca sa fie accesat db u

review_router = APIRouter()

book_service = BookService()
review_service = ReviewService()

@review_router.post("/book/{book_uid}")
async def add_review_to_book(
    book_uid: str,
    review_data: ReviewCreateModel,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    new_review = await review_service.add_review(
        user_email = current_user.email,
        review_data = review_data,
        book_uid = book_uid,
        session=session,
    )
    
    return new_review
    