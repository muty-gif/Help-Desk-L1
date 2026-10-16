from app.models import State


def test_user_only_sees_own_tickets(app, login, make_user, make_ticket):
    owner = make_user()
    other = make_user()

    make_ticket(owner, title="Ticket propio visible")
    make_ticket(other, title="Ticket ajeno oculto")

    login(owner)

    response = login.get("/tickets/")

    assert response.status_code == 200
    assert b"Ticket propio visible" in response.data
    assert b"Ticket ajeno oculto" not in response.data


def test_technician_sees_every_ticket(app, login, make_user, make_ticket):
    technician = make_user(role="technician")

    make_ticket(make_user(), title="Ticket de un usuario")
    make_ticket(make_user(), title="Ticket de otro usuario")

    login(technician)

    response = login.get("/tickets/")

    assert b"Ticket de un usuario" in response.data
    assert b"Ticket de otro usuario" in response.data


def test_user_cannot_open_another_users_ticket(
    app, login, make_user, make_ticket
):
    owner = make_user()
    intruder = make_user()

    ticket = make_ticket(owner)

    login(intruder)

    assert login.get(f"/tickets/{ticket.id}").status_code == 403


def test_filter_by_state(app, login, make_user, make_ticket):
    user = make_user()

    make_ticket(user, title="Ticket abierto")
    make_ticket(
        user,
        title="Ticket resuelto",
        state_id=State.query.filter_by(name="Resuelto").first().id
    )

    login(user)

    resolved_id = State.query.filter_by(name="Resuelto").first().id

    response = login.get(f"/tickets/?state_id={resolved_id}")

    assert b"Ticket resuelto" in response.data
    assert b"Ticket abierto" not in response.data


def test_filter_by_priority(app, login, make_user, make_ticket):
    from app.models import Priority

    user = make_user()

    make_ticket(user, title="Ticket de prioridad media")
    make_ticket(
        user,
        title="Ticket de prioridad critica",
        priority_id=Priority.query.filter_by(name="Crítica").first().id
    )

    login(user)

    critical_id = Priority.query.filter_by(name="Crítica").first().id

    response = login.get(f"/tickets/?priority_id={critical_id}")

    assert b"Ticket de prioridad critica" in response.data
    assert b"Ticket de prioridad media" not in response.data


def test_search_by_title(app, login, make_user, make_ticket):
    user = make_user()

    make_ticket(user, title="El ordenador no enciende")
    make_ticket(user, title="Problema con el correo")

    login(user)

    response = login.get("/tickets/?q=ordenador")

    assert b"El ordenador no enciende" in response.data
    assert b"Problema con el correo" not in response.data


def test_search_is_case_insensitive(app, login, make_user, make_ticket):
    user = make_user()

    make_ticket(user, title="Fallo en la impresora")

    login(user)

    response = login.get("/tickets/?q=IMPRESORA")

    assert b"Fallo en la impresora" in response.data


def test_empty_filter_results_show_a_message(
    app, login, make_user, make_ticket
):
    user = make_user()
    login(user)

    response = login.get("/tickets/?q=que-no-existe")

    assert response.status_code == 200
    assert b"No se encontraron tickets con esos filtros." in response.data


def test_anonymous_dashboard_shows_landing(client):
    response = client.get("/")

    assert response.status_code == 200
    assert b"Crear cuenta" in response.data


def test_user_dashboard_shows_own_stats(app, login, make_user, make_ticket):
    user = make_user()
    other = make_user()

    make_ticket(user, title="Ticket mío para el panel")
    make_ticket(other, title="Ticket ajeno que no aparece")

    login(user)

    response = login.get("/")

    assert response.status_code == 200
    assert f"Hola, {user.name}".encode() in response.data
    assert "Ticket mío para el panel".encode() in response.data
    assert b"Ticket ajeno que no aparece" not in response.data


def test_technician_dashboard_shows_unassigned_tickets(
    app, login, make_user, make_ticket
):
    technician = make_user(role="technician")

    make_ticket(make_user())

    login(technician)

    response = login.get("/")

    assert response.status_code == 200
    assert "sin técnico asignado".encode() in response.data
