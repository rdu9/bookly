from logging import exception
from typing import Any, Callable
from fastapi import FastAPI, status
from fastapi.requests import Request
from fastapi.responses import JSONResponse

# inainte de fisieru asta fiecare ruta avea propriu lui HTTPException

# problema: 20 rute 20 diferite formate de eroare, lucru care un cosmar pt debugging in general

# fisieru asta centralizeaza tot, toate definitile de eroare in 1 loc


# booklyexception e root u pt tot hierarchy u de erori
# fiecare eroare custom trb sa dea inherit din asta
# asta ajuta sa prinda toate app errors urile cu un singur booklyexception


class BooklyException(Exception):
    """This is the base class for all bookly errors"""

    pass


# fiecare clasa de mai jos e pt o eroare specifica
# toate dau inherit din booklyexception - nimic altceva nu mai e necesar


class InvalidToken(BooklyException):
    """User has provided an invalid or expired token"""

    pass


class RevokedToken(BooklyException):
    """User has provided a token that has been revoked"""

    pass


class AccesTokenRequired(BooklyException):
    """User has provided a refresh token when an acces token is needed"""

    pass


class RefreshTokenRequired(BooklyException):
    """User has provided a acces token when an refresh token is needed"""

    pass


class UserAlreadyExists(BooklyException):
    """User has provided an email for a user who exists during sign up"""

    pass


class InsufficientPermission(BooklyException):
    """User does not have the necessary permissions to perform an action"""

    pass


class BookNotFound(BooklyException):
    """Book not found"""

    pass


class UserNotFound(BooklyException):
    """User not found"""

    pass


class InvalidCredentials(BooklyException):
    """User has provided wrong email or password during login"""

    pass

class AccountNotVerified(BooklyException):
    """User account is not verified"""
    
    pass


# create_exception_handler - o functie factory

# un factory e o functie care creeaza si returneaza alta functie, in loc sa scrie acelasi handler de 9 ori ( 1 data pt fiecare error class )
# accesezi asta 1 data si face handleru pentru noi
# parametri:
# - status_code - HTTP STATUS CODEU care trebuie returnat
# - initial_detail - JSON BODYU care trebuie returnat la client

# returneaza: o functie async care e called de fastapi cand apare o eroare


def create_exception_handler(
    status_code: int, initial_detail: Any
) -> Callable[[Request, Exception], JSONResponse]:
    
    # inceputu da capture la status_code si detaliu
    
    async def exception_handler(request: Request, exc: BooklyException):
        
        # functia sta aici pana o eroare chiar se intampla

        return JSONResponse(content=initial_detail, status_code=status_code)

        # JSONResponse construieste http response u cu:
        # - status codeu pasat de noi
        # - detail dict ca json body u
        # fastapi trimite asta direct la client

    return exception_handler
    # returneaza functia in sine - nu rezultatu
    # fastapi da store la asta si ii da call cand apare o eroare

# register_all_errors - called odata in src/__init__.py

# app.add_exception_handler(ErrorClass, handler_function) ii zice la fastapi:
# - oricand clasa asta de eroare e raised, da call la functia respectiva de handler in loc sa il lasi sa dea crash
# asta inseamna ca functiile pot sa zica raise UserAlreadyExists() in loc de ceva lung

def register_all_errors(app: FastAPI):
    
    # tot de aici functioneaza la fel
    
    app.add_exception_handler(
        UserAlreadyExists,
        create_exception_handler(
            status_code=status.HTTP_403_FORBIDDEN,
            initial_detail={
                "message": "User with email already exists",
                "error_code": "user_exists",
                # asta e evident, doar completeaza tot ce are nevoie create_exception_handler de mai sus
            },
        ),
    )

    app.add_exception_handler(
        UserNotFound,
        create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            initial_detail={
                "message": "User with email not found",
                "error_code": "user_not_found",
            },
        ),
    )

    app.add_exception_handler(
        InvalidCredentials,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail={
                "message": "Invalid email or password",
                "error_code": "invalid_credentials",
            },
        ),
    )

    app.add_exception_handler(
        InsufficientPermission,
        create_exception_handler(
            status_code=status.HTTP_403_FORBIDDEN,
            initial_detail={
                "message": "You don't have permission to perform this action",
                "error_code": "insufficient_permission",
            },
        ),
    )

    app.add_exception_handler(
        AccesTokenRequired,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail={
                "message": "Access token is required to perform this action",
                "error_code": "access_token_required",
            },
        ),
    )

    app.add_exception_handler(
        InvalidToken,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail={"message": "Invalid token", "error_code": "invalid_token"},
        ),
    )

    app.add_exception_handler(
        RefreshTokenRequired,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail={
                "message": "Refresh token is required to perform this action",
                "error_code": "refresh_token_required",
            },
        ),
    )

    app.add_exception_handler(
        RevokedToken,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail={
                "message": "Token has been revoked",
                "error_code": "revoked_token",
            },
        ),
    )

    app.add_exception_handler(
        BookNotFound,
        create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            initial_detail={
                "message": "Book with id not found",
                "error_code": "book_not_found",
            },
        ),
    )
    
    app.add_exception_handler(
        AccountNotVerified,
        create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            initial_detail={
                "message": "This account is not verified",
                "error_code": "account_not_verified",
                "resolution": "Please check your email for verification details"
            },
        ),
    )

    # in schimb, 500 handleru e diferit, foloseste un decorator
    # @app.exception_handler(500) da catch la tot ce e unhandled
    # orice care da slip through prin toate erorile mele, ajung aici
    # returneaza un mesaj generic, niciodata nu da expose la detalii interne clientului
    # something went wrong e intentionat asa vag, doar pentru securitate
    
    @app.exception_handler(500)
    async def internal_server_error(requst, exc):

        return JSONResponse(
            content={
                "messsage": "Oops! Something went wrong",
                "error_code": "server_error",
            },
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    
