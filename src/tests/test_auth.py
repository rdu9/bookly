# asta testeaza rutele pentru auth

from src.auth.schemas import UserCreateModel

auth_prefix = f"/api/v1/auth"

def test_user_creation(fake_session, fake_user_service, test_client):
    
    # acelasi fixture injection ca test_books.py
    # pytest da match la numele de parametrii cu cei din @pytest.fixture din conftest.py
    
    # asta e niste data de test trimisa la request body
    
    signup_data = {
        "username": "",
        "email": "",
        "first_name": "",
        "last_name": "",
        "password": "",
    }

    # trimite POST /api/v1/auth/signup cu signup_data ca un JSON body
    # functia de ruta da run, da call la user_service.user_exists() si create_user()
    # datorita dependency_overrides, user_serivce e mock_user_service
    # nimic REAL nu se intampla, db sau password hashing

    response = test_client.post(url=f"{auth_prefix}/signup", json=signup_data)
    
    # construieste un UserCreateModel cu acelasi dictionar
    # asta e pydantic modelu care ruta creeaza intern
    # avem nevoie de asta pentru user_data ca sa il folosim in rute
    
    user_data = UserCreateModel(**signup_data)
    
    assert fake_user_service.user_exists_called_once() # verifica daca ruta a verificat ca useru exista, si trebuie, exact 1 data
    assert fake_user_service.user_exists_called_once_with(signup_data['email'],fake_session) # se uita daca a verificat cu emailu bun si sesiunea buna
    
    # a fost create_user called ? trebuie sa fie called doar dupa ce user_exists returenaza false
    # daca user_exists returneaza True ( useru deja exista ) - create_user n ar trebui sa fie called
    # intrun real test aveam un test separat pentru acel path
    
    assert fake_user_service.create_user_called_once() 
    
    # a fost create_user called cu PydanticModelu corect si sesiunea ?
    # orice deviatie in argument -> testu da fail -> exista un bug in ruta
    
    assert fake_user_service.create_user_called_once_with(user_data,fake_session)