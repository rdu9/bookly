from src.db.main import get_session
from src.auth.dependencies import AccesTokenBearer,RoleChecker,RefreshTokenBearer
from src import app
from fastapi.testclient import TestClient
from unittest.mock import Mock
import pytest

# pytest automat citeste conftest.py inainte sa dea run la orice test
# orice e definit aici e valabil pt toate test files urile din folder
# fisieru asta face 2 lucruri:
# - creeaza Mock objects ca sa dea replace la service uri reale si la sesiunea reala de DB
# - da register la dependency_overrides ca sa zica la Fastapi sa citeasca acele mock uri
#------

# Mock() creeaza un fake python object care:
# - accepta orice metoda fara sa dea crash: mock.anything()
# - accepta orice atribute acces: mock.anything 
# - da record la orice call facut la el - poti sa dai assert la ele mai tarziu
# - returneaza alt Mock ca default dupa orice method call
#
# mock_session - da replace la AsyncSession ( nu e nevoie de un db real )
# mock_user_service da replace la UserService 
# mock_book_service da replace la BookService
#
# testu controleaza exact ce mockurile returenaza
# asa ca e testata logica rutelor, nu serviceu sau DB ul

mock_session = Mock() # get_session
mock_user_service = Mock() # UserService din service.py
mock_book_service = Mock() # BookService din service.py

# instantele la auth classes 
# - astea sunt instantele reale din dependencies.py
# - ele nu sunt mocked - sunt folosite ca cheie pentru dependency_overrides
# - fastapi identifica dependencieurile cu object identity u lor ( adica instanta )
# - deci e nevoie de aceasi instanta folosita de rute
# - dependencieurile reale sunt definite cu functiile lor reale, si dupa bagate in app.dependency_overrides cu inlocuirile lor

acces_token_bearer = AccesTokenBearer()
refresh_token_bearer = RefreshTokenBearer()
role_checker = RoleChecker(['admin']) 

# yield inseamna ca asta e un generator - acelasi pattern ca realu get_session
# fastapi da inject la orice e yielded ca session parameteru in rute
# acum orice ruta care da call la get_session ia mock_session in loc de un db real

def get_mock_session():
    yield mock_session

# asta da register la override uri
# - app.dependency_override e un dictionar {real_dependency: replacementu ei}
# - cand fastapi vede Depends(get_session) in rute, se uita aici
# - daca gaseste get_session ca cheie, da call la get_mock_session()
# - asta inseamna ca niciodata nu e facuta o conexiunea la PostgreSQL

app.dependency_overrides[get_session] = get_mock_session
app.dependency_overrides[role_checker] = Mock() # inlocuit cu un Mock() normal, ca sa dea pass mereu, fara erori 403
app.dependency_overrides[refresh_token_bearer] = Mock() # inlocuit cu un Mock() normal, ca sa dea pass mereu, fara erori 403, dar acces tokenu nu e asa

# asta da define la pytest fixtures
# - @pytest.fixture face o functie sa fei fixture
# - cand o functie de test da list la un nume de fixture ca parametru, pytest o injecteaza
# - test_get_all_books(test_client , fake_book_service , fake_ session ) <-- pytest vede aceste nume si da call la respectivele fixtures automat

@pytest.fixture
def fake_session():
    return mock_session

@pytest.fixture
def fake_user_service():
    return mock_user_service

@pytest.fixture
def fake_book_service():
    return mock_book_service

# TestClient da wrap la app u fastapi pentru testing
# .get .post .patch .delete - la fel ca httpx dar sincron
# dependency_overrides sunt deja registrate mai sus, deci totu e cum trb

@pytest.fixture
def test_client():
    return TestClient(app)