# aici se face configu pentru db, setarile lui


from pydantic_settings import BaseSettings, SettingsConfigDict

# importu e ca sa stim cumm sa citim variabilele din .env
# fara el trebuia sa scriem os.getenv("DATABASE_URL") peste tot

class Settings(BaseSettings):
    
    # luam basesetting ca sa luam variabilele
    # nu e valoare default deci fara chestia din .env da crash
    
    # asta defineste toate varabilele din .env
    DATABASE_URL: str
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str
    REDIS_URL: str = "redis://localhost:6379/0"
    #
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_SERVER: str
    MAIL_PORT: int
    MAIL_FROM: str
    MAIL_FROM_NAME: str
    DOMAIN: str
    
    model_config = SettingsConfigDict(
        env_file=".env", # cauta fisieru .env in folder
        extra="ignore" # daca .env n are variabilele ignora situatia
    )

# creem o instanta pentru setari
# orice alt fisier da import la asta
# asta inseamna ca fisieru .env e citit doar la inceput nu de fiecare data, ca gen e un fel de variabila globala    

Config = Settings()


broker_url = Config.REDIS_URL # aici e brokeru unde taskurile sunt trimise si bagate in queue
result_backend = Config.REDIS_URL # dupa ce tasku se termina, aici se da store la rezultat, si variabila asta doar ii zice unde
broker_connection_retry_on_startup = True # cand celery workeru incepe, imediat incearca sa se conecteze la redis, si daca nu merge variabila asta il face sa dea retry, mereu trb sa fie True in production asta e ft important