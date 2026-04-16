from turtle import settiltangle
from src.db.models import User
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import delete, select
from .utils import generate_passwwd_hash
from .schemas import UserCreateModel, UserLoginModel


class UserService:

    async def get_user_by_email(self, email: str, session: AsyncSession):
        statement = select(User).where(User.email == email)
        result = await session.exec(statement)
        user = result.first()
        return user
    
        # aceasi logica ca la get_book, nimic nou, e simple sql syntax da cu functii

    async def user_exists(self, email: str, session: AsyncSession):
        
        # da call la functia veche, ca sa vada daca useru exista, si daca exista zice True ( 403 ) inseamna ca e luat nu poti face cont, si daca e False totu e bine
        # routeru da call la asta inainte sa creeze useru, ca sa nu fie 2 valori una peste cealalta
        
        user = await self.get_user_by_email(email, session)
        return True if user is not None else False

    async def create_user(self, payload: UserCreateModel, session: AsyncSession):
        user_data_dict = payload.model_dump() # creeaza dictionaru, si atat
        
        # pune totu in user, dar da unpack la ABSOLUT tot, pana si parola simpla
        # linia urmatoare face fix asta, inlocuieste parola normala pusa in db cu aia hashata, si dupa pune in db
        # important , new_user merge adaugat in session pentru ca asta cu ** ii da shape in modelu de table, adica User() , asta e logica
        
        new_user = User(**user_data_dict)
        
        # schimba parola normala din new_user cu cea hashata
        # parola normala niciodata nu atinge data de baze, care e luata cu new_user.password_has (trebuia hash da sunt eu prost)
        # generate_passwd_hash() e direct din utils, si doar ia hashu gen
        # pe scurt, inlo
        # cuieste parola normala , cu alternativa ei hashuita, care se stocheaza in db
        
        new_user.password_has = generate_passwwd_hash(user_data_dict["password"])
        new_user.role = "user"
        # aici updateaza obiectu de new_user, formatat in stil de db cu stringu "user", adica pe scurt DEFAULT, useru niciodata nu va fi admin
        
        # fara session.refresh() - ca la create_book
        # asta merge doar daca fielduruile returnate nu sunt bazate pe chesti generate pe baza de date
        # dar evident daca dai valori None in response, bagi await session.refresh(new_user)
        
        session.add(new_user)
        await session.commit()
        return new_user
    
    async def update_user(self, user: User ,user_data: dict, session: AsyncSession):
        
        # asta are nevoie de:
        # - user object, ca sa stie unde sa schimbe parola
        # - datele care trebuie sa fie inserate nou
        # - evident, sesiunea de db ca schimbarile sa pot fi aplicate
        
        for key,value in user_data.items(): # pentru key, value in itemele de la user_data ( adica doar emailu ) se pune direct in user
            setattr(user,key,value)       
        
        # se da commit ca deobicei si dupa se returneaza useru
        
        await session.commit() 
        
        return user