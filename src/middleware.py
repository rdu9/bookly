from fastapi import FastAPI, status
from fastapi.requests import Request
from fastapi.responses import JSONResponse
import time
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import logging

# middleware sta intre internet si rutele de functie
# fiecare request trece prin middleware inainte sa ajunga la ruta
# fiecare response trece prin middleware inainte sa iasa
# e securitatea suprema, orice request e verificat inainte sa ajunga la ruta macar

logger = logging.getLogger("uvicorn.access")
logger.disabled = True

# uvicorn da print la propriile acces logs din default, si asta da disable la functia build-in de logs, pt ca ii dam replace cu propriul nostru logging, cu mai multe informatii

def register_middleware(app: FastAPI):
    
    # called odata in src/__init__.py - da register la tot middlewareu pt aplicatie
    
    # -- ASTA FUNCTIONEAZA MIDDLEWAREU --
    # @app.middleware("http") - da wrap la fiecare http request
    # request: Request - asta e objectu de request care vine la server
    # call_next - urmatoru layer in chain, ori alt middleware ori ruta in sine
    # patternu este:
    # - faci ceva inainte de ruta ( start timer, log request etc )
    # - await call_next(request) - asta da requestu la ruta, si asteapta responseu
    # - dupa faci ceva, dupa ce ruta da run ( de ex cat de lung a durat tot )

    @app.middleware("http")
    async def custom_logging(request: Request, call_next):
        start_time = time.time()
        # timpu inainte de reuqest

        response = await call_next(request)
        # LINIA ASTA E RUTA CARE DA RUN
        # totu inainte - pre processing
        # totu dupa - post processing 
        
        processing_time = time.time() - start_time
        # cat de mult a durat toata ruta

        message = f"{request.client.host}:{request.client.port} - {request.method} - {request.url.path} - {response.status_code} completed after {processing_time}s"
        # construieste un log gen:
        # - 127.0.0.1:52341 - GET - /api/v1/books - 200 completed after 0.023s

        print(message)
        # da print la mesaj in consola, ca sa dea log 

        return response
        # IMPORTANT: trb sa returnezi responseu, daca uiti asta clientu nu primeste response, deci requestu sta degeaba pt totdeauna
    
    # -- ASA FUNCTIONEAZA CORS MIDDLEWAREU --
    
    # cors - cross origin resource sharing
    # browserurile dau block la diferite domainuri default
    # de exemplu: frontendu la localhost:3000 da call la api u la localhost:8000
    # browseru vede 2 origini diferite si le da block
    # CORS MIDDLEWAREU zice la browser ca asta e permis
    #
    # allow_origins = ["*"] - accepta requesturi de la ORICE domain ( prea deschis pt productie )
    # allow_methods = ["*"] - accepta toate metodele HTTP ( get , post , delete etc)
    # allow_headers = ["*"] - accepta toate headerele ( Authorization , Content-Type etc)
    # allow_credentials = ["*"] - accepta cookie uri si Authorization headers
    # 
    # in productie schimbi ["*"] cu frontend domainu tau real
    # allow_origins=["https://yoursaas.com", "https://app.yoursaas.com"]
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins = ["*"],
        allow_methods = ["*"],
        allow_headers = ["*"],
        allow_credentials = True,
    )
    
    # -- ASA FUNCTIONEAZA TRUSTED HOST MIDDLEWARE --
    
    # da prevent la http host header injection attacks
    # un host leader poate sa dea trick la serveru tau ca un request a venit dintrun trusted domain, cand defapt a venit de la attacker
    # de exemplu: un attacker trimite hostu evil.com in request.com, si serveru poate genera linkuri , care dau point la domainu attackerului
    #
    # allowed_hosts = ["localhost","yourdomain"] doar accepta requesturi unde host headeru da match la lista
    # daca hostu nu da match la lista, da return la 400 error code automat
    # in productie setezi cu domainu tau real
    # allowed_hosts=["yoursaas.com", "www.yoursaas.com", "localhost"]
    
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts = ["localhost","127.0.0.1"]
    )

    # CORS IN DETALIU EXPLICAT AICI: https://prnt.sc/xcl3x4IUlX8z










    # ---------------------------------

    # @app.middleware('http')
    # async def authorization(request: Request, call_next):
    #    if not "Authorization" in request.headers:
    #        return JSONResponse(
    #            content={
    #                "message": "Not authenticated",
    #                "resolution": "Please provide the right credentials to proceed"
    #            },
    #            status_code = status.HTTP_401_UNAUTHORIZED
    #        )
    #
    #    response = await call_next(request)
    #
    #    return response
