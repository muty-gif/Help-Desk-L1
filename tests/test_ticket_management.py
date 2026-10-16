from app.extensions import db
from app.models import History, Priority, Ticket


def test_technician_can_change_priority(app, login, make_user, make_ticket):
    technician = make_user(role="technician")
    login(technician)

    ticket = make_ticket(make_user())
    new_priority = Priority.query.filter_by(name="Crítica").first()

    response = login.post(
        f"/tickets/{ticket.id}/priority",
        data={"priority_id": new_priority.id}
    )

    assert response.status_code == 302

    with app.app_context():
        updated = db.session.get(Ticket, ticket.id)

        assert updated.priority.name == "Crítica"

        history = History.query.filter_by(
            ticket_id=ticket.id,
            action="Cambio de prioridad"
        ).first()

        assert history is not None
        assert history.old_value == "Media"
        assert history.new_value == "Crítica"
        assert history.user_id == technician.id


def test_user_cannot_change_priority(app, login, make_user, make_ticket):
    user = make_user()
    ticket = make_ticket(user)
    new_priority = Priority.query.filter_by(name="Crítica").first()

    login(user)

    response = login.post(
        f"/tickets/{ticket.id}/priority",
        data={"priority_id": new_priority.id}
    )

    assert response.status_code == 403

    with app.app_context():
        assert db.session.get(Ticket, ticket.id).priority.name == "Media"
        assert History.query.filter_by(
            ticket_id=ticket.id,
            action="Cambio de prioridad"
        ).count() == 0


def test_same_state_does_not_create_history(
    app, login, make_user, make_ticket
):
    technician = make_user(role="technician")
    login(technician)

    ticket = make_ticket(make_user())

    response = login.post(
        f"/tickets/{ticket.id}/state",
        data={"state_id": ticket.state_id}
    )

    assert response.status_code == 302

    with app.app_context():
        assert History.query.filter_by(ticket_id=ticket.id).count() == 0


def test_technician_can_unassign_ticket(app, login, make_user, make_ticket):
    owner = make_user()
    technician_1 = make_user(role="technician")
    technician_2 = make_user(role="technician")

    ticket = make_ticket(owner, technician_id=technician_1.id)
    ticket_id = ticket.id

    login(technician_2)

    response = login.post(
        f"/tickets/{ticket_id}/technician",
        data={"technician_id": 0}
    )

    assert response.status_code == 302

    with app.app_context():
        updated = db.session.get(Ticket, ticket_id)

        assert updated.technician_id is None

        history = History.query.filter_by(
            ticket_id=ticket_id,
            action="Asignación de técnico"
        ).first()

        assert history is not None
        assert history.old_value == technician_1.name
        assert history.new_value == "Sin asignar"


def test_cannot_assign_a_non_technician(app, login, make_user, make_ticket):
    technician = make_user(role="technician")
    plain_user = make_user(role="user")

    ticket = make_ticket(make_user())
    ticket_id = ticket.id

    login(technician)

    response = login.post(
        f"/tickets/{ticket_id}/technician",
        data={"technician_id": plain_user.id}
    )

    # El select solo admite técnicos, así que no se guarda nada.
    assert response.status_code == 302

    with app.app_context():
        updated = db.session.get(Ticket, ticket_id)

        assert updated.technician_id is None
        assert History.query.filter_by(
            ticket_id=ticket_id,
            action="Asignación de técnico"
        ).count() == 0


def test_technician_sees_management_forms_on_detail(
    app, login, make_user, make_ticket
):
    technician = make_user(role="technician")
    ticket = make_ticket(make_user())

    login(technician)

    response = login.get(f"/tickets/{ticket.id}")

    assert response.status_code == 200
    assert b"Cambiar prioridad" in response.data
    assert b"Asignar t\xc3\xa9cnico" in response.data


def test_owner_does_not_see_management_forms(app, login, make_user, make_ticket):
    user = make_user()
    ticket = make_ticket(user)

    login(user)

    response = login.get(f"/tickets/{ticket.id}")

    assert response.status_code == 200
    assert b"Cambiar prioridad" not in response.data
    assert b"Asignar t\xc3\xa9cnico" not in response.data
    assert b"Editar" in response.data


def test_comment_on_missing_ticket_returns_404(login, make_user):
    user = make_user()
    login(user)

    response = login.post(
        "/tickets/9999/comments",
        data={"content": "Comentario huérfano."}
    )

    assert response.status_code == 404
