# asta testeaza rutele pentru books

# da define la url prefix odata sus de tot, folositor ca sa fie o variabila pentru orice link
books_prefix = f"/api/v1/books"

def test_get_all_books(test_client, fake_book_service, fake_session):
    
    # test_client, fake_book_service, fake_session - toate fixtures din conftest.py
    # pytest le injecteaza automat dupa nume, nu e nevoie de import
    
    # response trimite GET /api/v1/books la fastapi app
    # aplicatia da run, da de functia reala dar:
    # - get_session returenaza mock_session ( nu un db real )
    # - role_checker e bypassed 
    # deci ruta da call la book_service.get_all_books(session)

    response = test_client.get(url=f"{books_prefix}")

    # Mock da record automat la fiecare method call facut la el
    # .get_all_books_called_once() e un Mock "magic assertion" method
    # verifica ca get_all_books e called exact 1 singura data
    # daca e called de 0, 2+ ori da fail

    assert fake_book_service.get_all_books_called_once()
    
    # verifica ca get_all_books e called cu mock_session ca argument
    # daca ruta pasata are sesiunea invalida, asta da fail
    #
    # aceste 2 linii se intreaba daca ruta a dat call la service methodu corect, cu argumentu corect
    # asta e testing route behaviour, nu service logic
    
    assert fake_book_service.get_all_books_called_once_with(fake_session)
