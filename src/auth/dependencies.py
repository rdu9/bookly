from fastapi import Depends, Request, status, Depends
from fastapi.security.http import HTTPAuthorizationCredentials
from fastapi.security import HTTPBearer
from sqlalchemy.orm import raiseload
from .utils import decode_token
from fastapi.exceptions import HTTPException
from src.db.redis import token_in_blocklist, token_in_blocklist
from src.db.main import get_session
from sqlmodel.ext.asyncio.session import AsyncSession
from .service import UserService
from typing import List
from src.db.models import User
from src.errors import(
    InvalidToken,
    RefreshTokenRequired,
    AccesTokenRequired,
    InsufficientPermission,
    AccountNotVerified
)

user_service = UserService()

# Tokenbearer - clasa principala
# clasa asta NICIODATA nu e folosita in rute
# exista doar ca AccesTokenBearer si RefreshTokenBearer sa iasa din el si sa foloseasca logica
# acest pattern se numeste inheritance, si e folosit pentru a evita duplicarea codului
# child classes urile iau toata logica de la parent class, si doar o suprascriu cu logica specifica


class TokenBearer(HTTPBearer):

    def __init__(self, auto_error=True):
        super().__init__(auto_error=auto_error)

    # super().__init__ ruleaza setupul propriu al HTTPbear
    # auto_error = True daca authorization headeru e missing atunci fastapi returneaza automat un 403 fara sa intre in __call__

    async def __call__(self, request: Request) -> HTTPAuthorizationCredentials | None:
        creds = await super().__call__(request)

        # HTTPBearer citeste authorization bearer din headeru de request si extrage automat doar stringu de token
        # daca headeru nu exista si auto_error e True, acesta o sa returneze automat un 403 si __call__ niciodata nu se apel
        # de asemena __call__ ul face functia callable pt route cu Depends()

        token = creds.credentials

        # creds.credential e raw token stringu dupa Bearer
        # authorization: bearer TOKEN --> creds.credentials = TOKEN
        # asta e tokenu pur si simplu, fara Bearer prefixul

        token_data = decode_token(token)

        # decode_token din utils.pt - verifica daca tokenul e valid , daca nu returneaza None
        # returneaza payloadu dictionar daca valid: {"user": {"email": "user@example.com", "user_uid": "1234567890"}
        # , "exp": 1716883200, "jti": "1234567890", "refresh": False}
        # returneaza None daca tokenul e invalid sau expirat

        if not token_data:
            raise InvalidToken()

        # daca e none ->> tokenu e rau --> 403 e ridicat si functia route niciodata nu da run
        # ruta depinde de clasa asta cu Depends() deci daca asta pica fastapi opreste tot requestul aici

        if await token_in_blocklist(token_data["jti"]):
            raise InvalidToken()

        # asta verifica daca tokenu e in blocklist, gasim asta in redis.py, nimic asa wow

        self.verify_token_data(
            token_data
        )  # aici trece sa ruleze clasele child, e un fel de pausa la base, asta nu stiam pana acm ( selfu face toata magia , si e facut ca sa nu dea nimeni run la base, si doar la child, foarte inteligent )

        # asta e un check custom, definita diferita in fiecare clasa child
        # accestokenbearer verifica: refresh trb sa fie fals, daca nu ridica 403
        # refreshtokenbearer verifica: refresh trb sa fie true, daca nu ridica 403
        # clasa base nu stie ce sa faca cu asta, asa ca fiecare clasa child trebuie sa implementeze acest check

        return token_data

        # returneaza payloadu decodat la ruta ca user_details
        # contine email , user_id, expirare, jti, refresh flag
        # ruta asa stie cine face requestul fara sa acceseze baza de date

    def verify_token_data(self, token_data):
        raise NotImplementedError("Please Ovveride this method in child classes")
        # metoda asta da crash initial daca e apelata direct in clasa base, deoarece nu e implementata
        # FORTEAZA clasa child sa implementeze acest check cu propria ei logica
        # daca cineva creeaza tokenbearer() direct fara sa foloseasca un child class:
        # - o sa primeasca o eroare clara spunandui ce sa faca
        # - asta se numeste un abstract method pattern


# AccesTokenBearer - folosita la rute protejate
# verifica daca tokenu e un ACCES TOKEN ( refresh=False )
# daca e refresh token, o sa dea 403 si o sa opreasca requestul
# usage in ruta : user_details = Depends(AccesTokenBearer())


class AccesTokenBearer(TokenBearer):  # clasa e aici ca sa extraga token_data u gen

    def verify_token_data(self, token_data: dict) -> None:
        if token_data and token_data["refresh"]:  # daca e refresh arunca eroare
            raise AccesTokenRequired()

    # token_data["refresh"] is True -> asta e un refresh token
    # refresh tokenurile sunt DOAR ca sa faca rost de tokenuri de acces noi cand cele vechi expira, niciodata nu atinge resurse direct
    # n ar trebui niciodata sa fie folosite la rute protejate, si daca cineva incearca direct 403
    # totul se ruleaza in Tokenbearer(), dupa la self asta, si dupa se returneaza tokenu ( ultima linie )


# RefreshTokenBearer - folosita doar la rute /refresh_token
# verifica daca tokenu e un token refresh ( refresh = True )
# daca cineva trimite un acces token la ruta de refresh arunca direct 403
# usage in ruta: token_details = Depends(refresh_token_bearer)


class RefreshTokenBearer(TokenBearer):  # clasa e aici ca sa extraga token_data u gen

    def verify_token_data(self, token_data: dict) -> None:
        if token_data and not token_data["refresh"]:  # daca nu e refresh arunca eroare
            raise RefreshTokenRequired()

    # not token_data[refresh] inseamna ca refresh=False deci asta e un token de acces automat
    # endpointu de refresh asteapta un refresh token, nu un acces token
    # daca cineva trimite un acces token aici -> 403
    # totul se ruleaza in Tokenbearer(), dupa la self asta, si dupa se returneaza tokenu ( ultima linie )


# asta tot ce face e sa ia emailu din token, si dupa sa scoata useru din utils.py get_user_by_email
# get_current_user doar returneaza o forma User object fix ca in db, cu abs toate info
# depends de asemenea da si valoarea, si mai si depinde de chestia aia

async def get_current_user(
    token_details: dict = Depends(AccesTokenBearer()),
    session: AsyncSession = Depends(get_session),
):
    
    # asta e un dependency care combina alte 2 
    # AccesTokenBearer() valideaza tokenu jwt de acces si returenaza payloadu decodat
    # get_session da sesiunea de db
    # fastapi rezolva totu automat inainte sa inceapa functia asta
    
    user_email = token_details["user"]["email"]
    
    # token_details e jwt payloadu decodat, cu utils.py
    
    user = await user_service.get_user_by_email(user_email, session)
    
    # ia full user objectu din postgres, cu emailu de la token
    # asta e singuru call de database pentru a lua useru curent, cel mai precis
    # usage in orice ruta:
    # - current_user: User = Depends(get_current_user)
    # - acm current_user are un full User object cu toate field urile
    # - ruta stie EXACT cine face requestu
    
    return user

    # returnam useru FULL din models, de el avem nevoie


class RoleChecker:
    
    # rolechecker e o clasa calabila folosita ca un fastapi dependancy
    # verifica daca useru curent are permisiune sa faca ceva pe harta

    
    def __init__(self, allowed_roles: List[str]) -> None:

        self.allowed_roles = allowed_roles
        
        # asta se intampla cand scrii RoleChecker(["admin", "editor"])
        # da store la lista cu rolurile care au acces la respectiva ruta
        # rute diferite pot avea orice fel de lista de genu

    def __call__(self, current_user: User = Depends(get_current_user)):
        
        # asta e called automatic de fastapi la fiecare request la o ruta protejata
        # current_user e injectat de get_current_user ca sa luam full User objectu din db, cu scopu sa ii luam rolu
        
        if not current_user.is_verified:
            raise AccountNotVerified()

        if current_user.role in self.allowed_roles:
            return True
        
        # daca rolu userului e allowed, are voie pe harta

        raise InsufficientPermission()
        
        # daca nu e allowed, n are voie
        
# if not self.token_valid:
#            raise HTTPException(
#                status_code = status.HTTP_403_FORBIDDEN, detail="Invalid or expired token"
#            )
#
#        # token_valid() apeleaza decode_token iar si verifica daca resultatu e none
#        # daca e none ->> tokenu e rau --> 403 e ridicat si functia route niciodata nu da run
#        # ruta depinde de clasa asta cu Depends() deci daca asta pica fastapi opreste tot requestul aici
#


# def token_valid(self, token: str) -> bool:
#    token_data = decode_token(token)
#    return True if token_data is not None else False
#    # decode_token returenaza None la orice failure
#    # True = valid
#    # False = invalid / expirat / modificat



