from celery import Celery
from src.mail import mail, create_message
from typing import List
from asgiref.sync import async_to_sync

# CE E CELERY?
# - celery e un task queue, care te lasa sa dai run la taskuri in background, inafara de requesturi normale
# FARA CELERY:
# - useru trimite POST /signup
# - serveru creeaza useru -> asteapta pentru SMTP -> da un raspuns
# - useru asteapta 2-3 secunde pt email inainte sa primeasca un response
# CU CELERY:
# - useru trimite POST /signup
# - serveru creeaza useru -> trimite tasku la redis queue -> returneaza raspunsu imediat
# - useru asteapta 50ms in total
# - celery worker da pick up la task din queue si trimite emailu in background ( useru niciodata nu asteapta mailu, vine instant )


# creeaza Celery instanceu odata
# Celery() fara argumente foloseste default settings pana e configurat

celery_app = Celery()

# da load la configuratia din src.config.py 
# Celery cauta variabile specifice pana e configurat, in acel object
# - broker_url ( unde taskurile sunt trimise ) - REDIS
# - result_backend ( unde resultatele sunt stored ) - REDIS
# - broker_connection_retry_on_startup - da retry daca redisu nu e inca gata

celery_app.config_from_object('src.config')

# celery_app.task() da register la functia asta ca un Celery task
# acum nu mai e o functie normala, devine un task
# PENTRU FISIERE:
# - send_email() direct ii da run normal
# - send_email.delay() trimite la redis queue ca sa dea run in background
# - send_email.apply_async() e la fel ca .delay() dar cu mai multe optiuni

@celery_app.task()
def send_email(recipients: List[str] , subject: str, body: str):
    
    # IMPORTANT: celery taskurile sunt syncron, nu asyncron
    # celery da run intrun worker process separat care nu are un async event loop, deci nu poti folosi await intrun celery task direct
    
    message = create_message(
        recipients=recipients, subject=subject, body=body  # creeaza mesaju cu create_message din mail.py, e ceva foarte basic doar urmareste schema si pune variabilele de mai sus
    )


    # mail.send_message e un ASYNC function, are nevoie de asta, dar celery e sync, deci nu putem folosi await
    
    # async_to_sync() din asgiref e un bridge care:
    # - ia un async function si ii da wrap ca sa poata fi folosit intro functie sync
    # - creaza un event loop temporar, da run la functia async in el, si dupa returenaza rezultatu
    #
    # async_to_sync(mail.send_message) - da wrap la functia async
    # (message) - da call la functia wrap cu argumentul necesar
    #
    # pe scurt, linia asta e fix ca await mail.send_message(message) dar e facuta sa mearga intro functie sync unde nu merge cu await
    
    async_to_sync(mail.send_message)(message)
    
    # asta e printat in terminalu de la celery worker, nu in fastapi
    
    print("Email sent")