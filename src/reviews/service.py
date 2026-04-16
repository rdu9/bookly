from src.auth.routers import user_service
from src.db.models import Review, Depends
from src.auth.service import UserService
from src.books.service import BookService
from sqlmodel.ext.asyncio.session import AsyncSession
from src.db.main import get_session
from .schemas import ReviewCreateModel
from fastapi.exceptions import HTTPException
from fastapi import status
import logging
from src.errors import BookNotFound, UserNotFound

# iar nimic wow, singuru lucru nou e try si except Exception, si dupa ca se da log la eroare cu logging, in rest e tot model_dump() si creearea objectului cu **

user_service = UserService()
book_service = BookService()


class ReviewService:

    async def add_review(
        self,
        user_email: str,
        book_uid: str,
        review_data: ReviewCreateModel,
        session: AsyncSession,
    ):
        try:
            book = await book_service.get_book(book_uid, session)
            
            if not book:
                raise BookNotFound()
                         
            user = await user_service.get_user_by_email(user_email, session)
            
            if not user:
                raise UserNotFound()

            review_data_dict = review_data.model_dump()

            new_review = Review(**review_data_dict)
            
            new_review.user = user
            
            new_review.book = book

            session.add(new_review)

            await session.commit()

            return new_review
        
        except Exception as e:
            logging.exception(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Oops ... something went wrong",
            )
