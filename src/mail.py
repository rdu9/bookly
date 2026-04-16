from fastapi_mail import FastMail, ConnectionConfig, MessageSchema, MessageType
from src.config import Config
from pathlib import Path
from typing import List
 
# fastapi_mail e libraria care da handle la trimiterea emailurilor cu fastapi
# se conecteaza cu un SMTP server ( gmail , sendgrid, mailgun etc)
# si trimite emailuri asyncron, fara a bloca aplicatia

BASE_DIR = Path(__file__).resolve().parent

# __file__ e pathu acestui file ( mail.py )
# .resolve() da convert la un path absolut
# .parent se duce un level in sus adica la folderu care contine __file__ adica mail.py ( src/ folder e resultatu)
# e folosit mai jos pt gasirea templateurilor/folderu pt html email templates

mail_config = ConnectionConfig(
    
    # SMTP credentials - in .env , niciodata hardcoded
    MAIL_USERNAME = Config.MAIL_USERNAME,
    MAIL_PASSWORD=Config.MAIL_PASSWORD,
    
    
    # adresa from pe care useru il vede in inbox
    # exemplu: noreply@yoursaas.com
    MAIL_FROM = Config.MAIL_FROM, 
    
    
    # portu 587 e standardu SMTP port pt trimiterea emailurilor cu starttls
    MAIL_PORT = 587,
    
    
    # SMTP server adress
    MAIL_SERVER = Config.MAIL_SERVER,
    
    
    # display nameu in inbox in loc de mail_from
    MAIL_FROM_NAME=Config.MAIL_FROM_NAME,
    
    
    # STARTTLS upgradeaza conexiunea sa fie encrypted TLS dupa ce se conecteaza, asta e modul corect si secure de a trimite emailuri pe portu 587
    MAIL_STARTTLS=True,
    
    
    # asta e metoda veche de trimitere a mailurilor, trb sa fie false
    MAIL_SSL_TLS=False,
    
    
    # intri pe serverul SMTP cu username si parola
    USE_CREDENTIALS=True,
    
    
    # verifica certificatu SSL la mail server, mereu e folosit in production, ca da prevent la atacuri
    VALIDATE_CERTS=True,
    
    
    # asta da point la src/templates 
    # HTML email templates au loc aici , Jinja2 foloseste fisiere ca verify_email.html
    TEMPLATE_FOLDER= Path(BASE_DIR, 'templates')
)

# instanta FastMail, creata odata si refolosita peste tot
# acelasi pattern ca Config = Settings() si token_blocklist = StrictRedis(): o instanta, shared la toate rutele care au nevoie de asta

mail = FastMail(
    config=mail_config
)


def create_message(recipients: List[str], subject: str, body: str):
    
    message = MessageSchema(
        recipients=recipients, # List[str] combinat cu asta poate trimite emailuri la mai multe conturi in acelasi timp
        subject=subject, # asta e subiectu pe care useru il vede in inbox
        body=body, # contentu html al emailului, poate sa fie un plain string sau un template Jinja2
        subtype=MessageType.html # ii spune clientului email sa dea render ca un HTML, nu plain text. fara asta HTMLU ar arata ca raw text, gen <h1>Hello</h1>
    )
    
    return message # returneaza un obiect MessageSchema gata sa fie passed la mail.send_message()