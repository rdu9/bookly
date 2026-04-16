from passlib.context import CryptContext
from datetime import timedelta,datetime
import jwt
from src.config import Config
import uuid
import logging
from itsdangerous import URLSafeTimedSerializer

# passlib e libraria care se ocupa cu password hashingu
# niciodata nu putem da store la parole normale in baza de date, doar cu hash
# daca baza de date e hackuita, hackerii nu fac nimic cu hashu 

# JWT Tokens ( facute pentru auth ) - facute pentru machine-to-machine communication, doar pt headers
# tokenurile pt email sunt diferite:
# - se duc in urlurile pe care useru da click in inbox
# - nu poate contine anumite caractere care JWT le foloseste ( + / =)
# - email verification tokens trebuie sa expire dupa deobicei 24h
# - trebuie doar sa encodeze un lucru, user emailu
#
# URLSafeTimedSerializer de la itsdangerous face:
# - produce URL-safe strings ( fara caractere speciale )
# - are un expiry built on
# - foloseste semnatura HMAC ca sa fie safe


passwd_context = CryptContext(
    schemes=['bcrypt']
    # bcrypt e algoritmu de hashing3
    # e intentionat slow, face ca bruteforceu sa dureze ani
    # schema e o lista pt mai multe algoritme
    # bcrypt e standardu in industrie
)

ACCES_TOKEN_EXPIRY = 3600 



token_serializer = URLSafeTimedSerializer(
        # foloseste acelasi secret key ca JWTs
        # daca cineva nu stie secret keyu nu poate face un token valid
        # semnatura HMAC da cover la data + secret key + timestamp
        secret_key=Config.JWT_SECRET_KEY, 
        
        # salt adauga extra context la semnatura
        # si daca folosesti aceasi cheie pt mai multe motive, un token signed cu salt="email-verification" nu poate fi folosit unde salt e "password-reset", sunt tokenuri isolate peste tot
        salt="email-verification"
    )

# ---------------

def generate_passwwd_hash(password: str) -> str:
    hash = passwd_context.hash(password)
    # ia parola si returneaza un string random cu hash
    # parola originala n are cum sa fie recuperata dupa string
    # asta e si ideea, sa fie one way, secreta
    return hash

def verify_password(password: str, hash: str) -> bool:
    # ia parola simpla trimisa de user
    # bcrypt da hash iar la parola originala, si o combina cu hashu , si daca sunt valide returneaza True daca nu False
    # niciodata nu poti compara un hash cu parola normala, sunt 2 lucruri diferite, de asemenea hashu e stored in db, nu parola
    return passwd_context.verify(password,hash)

#------------------------

def create_acces_token(user_data: dict, expiry: timedelta = None, refresh: bool = False): # pe scurt, asta creeaza tokenul , refresh sau nu, cu asta se ocupa
    
    # asta are nevoie ruta
    #user_data={
    #                "email": user.email,
    #                "user_uid": str(user.uid),
    #                "role": user.role,
    #            }
    # asta pregateste datele doar, nimic interesnat
    # informatiile sunt trimise direct din ruta
    
    payload = {}
    
    # da store la email si la uid in payload, ca daca o sa fie nevoie de ele sa fie stocate direct in token, scurteaza pasii mult
    
    payload['user'] = user_data
    
    # dupa acest timp, jwt automat respinge tokenul, daca e refresh token, o sa aiba un expiry mai mare, daca nu, o sa fie 1 ora
    
    payload['exp'] = datetime.now() + (expiry if expiry is not None else timedelta(seconds=ACCES_TOKEN_EXPIRY))
    
    # jti este un id unic pentru fiecare token creat, e folosit pt token revocation, daca cineva da log out poti da store la jit intro lista neagra
    # dupa poti verifica daca jit ul e in lista neagra, si daca e , poti respinge tokenul fara probleme
    
    payload['jti'] = str(uuid.uuid4())
    
    # asta e un flag care indica daca tokenul e refresh sau access, daca e refresh, o sa aiba un expiry mai mare, si o sa fie folosit doar pt a obtine un access token nou, nu pt a accesa resurse direct
    
    payload['refresh'] = refresh
    
    # asta creeaza tokenul cu toate datele de mai sus, folosind algoritmu si cheia secreta din .env
    
    token = jwt.encode(
        payload=payload,
        key = Config.JWT_SECRET_KEY,
        algorithm=Config.JWT_ALGORITHM
    )
    
    # returneaza tokenul obtinut , care e un string criptat, cu toate datele de mai sus, dar intro forma sigura
     
    return token

def decode_token(token: str) -> dict: # asta decodeeaza tokenul, si verifica daca e valid, si daca nu e returneaza none
    
    # asta face 3 chestii simultan:
    # - da decode la token, adica il transforma inapoi din stringul criptat intro structura de date 
    # - verifica daca tokenul e valid, daca nu a expirat, daca e corect semnat, si etc
    # - daca totul e ok, returneaza datele din token, daca nu, returneaza None sau arunca o eroare
    
    try:
     token_data = jwt.decode(
         jwt=token,
         key=Config.JWT_SECRET_KEY,
         algorithms=[Config.JWT_ALGORITHM] # pentru ca jwt.decode vrea o lista mai mare de algoritmi, chiar daca noi putem folosi doar unul
     )
     return token_data
    
    # in caz de o eroare la decodare, cum ar fi token expirat, semnatura invalida etc, logam eroarea si returnam None, asta e important ca daca tokenu nu e valid, sa dam handle cum trb
    
    except jwt.PyJWTError as e:
        logging.exception(e)
        return None 


#------------------------
   
    
def create_url_safe_token(data: dict):
    
    # data trebuie sa dea  {"email": "user@example.com"}
    
    token = token_serializer.dumps(data) # .dumps() da serialize la dictionar si il semneaza, asa se face rost de data
    
    # input:  {"email": "user@example.com"}
    # output: "eyJlbWFpbCI6InVzZXJAZXhhbXBsZS5jb20ifQ.ZxY8Qw.abc123xyz"
    #          ─────────────────────────────────────  ──────  ──────────
    #          base64 encoded data                    timestamp  signature
    
    return token

def decode_url_safe_token(token: str):
    try:
        
        # loads face 3 lucruri simultan:
        # - da decode la data base64 ( tokenu )
        # - verifica semnatura HMAC, ca sa dea reject la tokenurile face
        # - verifica timestampu ( rejecta tokenurile expired )
        
        token_data = token_serializer.loads(token)

        # returneaza dictionaru original, adica data de la create_url_safe_token ( {"email": "user@example.com"} )
        # daca e invalid da o exceptie, care se duce acolo jos
        
        return token_data
    
    except Exception as e:
        logging.error(str)