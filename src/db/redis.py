import aioredis
from src.config import Config

# aioredis e versiunea asyn de redis client, care normal bloca aplicatia dupa fiecare operatie
# aioredis merge doar cu async / await , la fel ca AsyncSession pentru postgres

JTI_EXPIRY = 3600

# cat timp un token blocat sta in redis, 1 ora
# asta e matchy cu acces_token_expiry in utils.py, intentionat
# dupa 1 ora tokenu de acces expira oricum deci n are rost sa tina blocklistu mai mult de atat

token_blocklist = aioredis.from_url(Config.REDIS_URL) # asta e simplu o scurtatura, o singura variabila in .env care da cover la tot ce e nevoie pentru redis, e pe scurt versiunea mai buna si mai moderna


#token_blocklist = aioredis.StrictRedis(
#    host = Config.REDIS_HOST,
#    port = Config.REDIS_PORT,
#    db=0
#)
#
# StrictRedis face conexiunea cu serverul redis
# host si port vin de la .env cu config.py
# db=0 inseamna ca foloseste baza de date 0 , redis suporta mai multe logical databases ( 0 - 15 )
# acest obiect e creat odata si refolosit, fix ca Config = Settings()

async def add_jti_to_blocklist(jti: str) -> None:
    await token_blocklist.set(
        name=jti,
        value="",
        ex=JTI_EXPIRY
    )
    # cand un user da log out, tokenu jti e adaugat aici
    # name = jti - cheia in retis, token idu unic de la jwt payload
    # value = "" - aici nu avem nevoie de nimic, doar existenta cheii conteaza
    # ex=JIT_EXPIRY  - cheia se sterge automat dupa 3600 secunde
    # asta se numeste blocklist sau blacklist pattern pentru token revocation
    
async def token_in_blocklist(jti: str)->bool:
    jti = await token_blocklist.get(jti)
    return jti is not None # if none - tokenu nu a fost niciodata blocaft, daca e not None inseamna ca tokenu e gasit in blacklist, deci useru s a delogat probabil
    
    # verifica daca un jti exista in redis
    # se returenaza valoarea daca cheia exista, None daca mnu
    # aceasta functie este called in tokenbearer __call__ la FIECARE protected request, ca sa mearga log inu
    # redis lookup e 0.1 ms , foarte rapid, fara probleme cu performanta