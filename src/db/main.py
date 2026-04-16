# aici se face sesiunea la db


from sqlmodel import create_engine, text, SQLModel
from sqlalchemy.ext.asyncio import AsyncEngine
from src.db.models import Book
from src.config import Config
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import sessionmaker 

# create_engine face configuratia ca sa te conectezi la baza de date
# nu conecteaza nimic create_engine in sine, doar pregateste tot
# async engine face totu sa mearga cu async si await, ca sa nu se blocheze baza de date dupa fiecare comanda

async_engine = AsyncEngine(
    create_engine(
        url=Config.DATABASE_URL, # config e instanta pentru setari, care e gen basically fisieru .env
        echo=False # asta e ca sa printeze totu in terminal, ca sa invat
))


# functia asta da run cand se porneste aplicatia, cu ajutoru la lifespan "await init_db()"
# acum doar testeaza conexiunea cu un simplu query, mai tarziu o sa fie updatat


async def init_db():
    async with async_engine.begin() as conn:
        
        # run_sync ruleaza o functie sync intr-un thread separat
        # create_all e o functie veche, nu stie de async/await
        # run_sync e podul dintre lumea sync si lumea async
        
        
        await conn.run_sync(SQLModel.metadata.create_all)

async def get_session()->AsyncSession: # asyncsession face doar SESIUNI ASYNC, nu sync , e foarte important, fara asta n ar merge await session exec
    Session = sessionmaker( # session maker pe scurt face sesiuni, cu care poti apela db ul
        bind = async_engine, # zice la sesiune ce engine sa foloseasca, si engineu e conexiunea la db pe scurt 
        class_ = AsyncSession, # spune sa produca doar sesiuni async, ca sa mearga totu perfect 
        expire_on_commit=False # fara asta, dupa obiectele sunt expirate, si pica totu
    )
    
    # deschide sesiunea si imprumuta o conexiune din pool
    # cand se termina — inchide sesiunea automat, chiar daca nu merge- ceva
    
    async with Session() as session: 
        yield session # asta pe scurt da sesiunea la route, foarte important ca sa mearga scriptu1


#async def init_db():
#    async with engine.begin() as conn:
#        # engine.begin() este o tranzactie, acesta da o conexiune si face aceste lucruri:
#        # - daca totu de sub async merge fara eroare, tranzactia da commit, si schimbarile se fac permanent
#        # - daca orice da o exceptie, tranzactia se duce inapoi, adica fix cum era inainte 
#        
#        statement = text(" SELECT 'hello'; ")
#        
#        # text() e neaparat cand dai run a raw strings, asta e pentru securitate ( lucru facut de sqlalchemy )
#        # asta ne face sa fim foarte expliciti
#        
#        result = await conn.execute(statement)
#        print(result.all())
#        # daca asta printeaza ceva inseamna ca merge conexiunea
#        # daca da crash inseamna ca trb sa verificam database_url in .env probabil
#        
#        def __repr__(self):
#            return f"<Book {self.title}"