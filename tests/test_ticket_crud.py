from app.extensions import db
from app.models import Category, Comment, History, Priority, State, Ticket


def test_anonymous_user_cannot_create_ticket(client):
    response = client.post(
        "/tickets/create",
        data={
            "title": "Sin sesión",
            "description": "No debería crearse.",
            "category_id": 1,
            "priority_id": 1
        }
    )

    assert response.status_code == 302
    assert "/auth/login" in response.headers["Location"]


def test_user_creates_ticket_with_open_state(app, login, make_user):
    user = make_user()
    login(user)

    category = Category.query.filter_by(name="Hardware").first()
    priority = Priority.query.filter_by(name="Alta").first()

    response = login.post(
        "/tickets/create",
        data={
            "title": "La impresora no imprime",
            "description": "Desde ayer no responde.",
            "category_id": category.id,
            "priority_id": priority.id
        }
    )

    assert response.status_code == 302

    with app.app_context():
        ticket = Ticket.query.filter_by(title="La impresora no imprime").first()

        assert ticket is not None
        assert ticket.user_id == user.id
        assert ticket.state.name == "Abierto"
        assert ticket.priority.name == "Alta"
        assert ticket.category.name == "Hardware"


def test_ticket_creation_requires_reference_data(app, login, make_user, seed):
    user = make_user()
    login(user)

    state = State.query.filter_by(name="Abierto").first()
    db.session.delete(state)
    db.session.commit()

    category = Category.query.filter_by(name="Red").first()
    priority = Priority.query.filter_by(name="Baja").first()

    response = login.post(
        "/tickets/create",
        data={
            "title": "Sin estados",
            "description": "La referencia de estados no existe.",
            "category_id": category.id,
            "priority_id": priority.id
        }
    )

    assert response.status_code == 200

    with app.app_context():
        assert Ticket.query.filter_by(title="Sin estados").first() is None


def test_owner_can_edit_own_ticket(app, login, make_user, make_ticket):
    user = make_user()
    login(user)

    ticket = make_ticket(user, title="Título original")
    new_category = Category.query.filter_by(name="Software").first()

    response = login.post(
        f"/tickets/{ticket.id}/edit",
        data={
            "title": "Título corregido",
            "description": "Descripción corregida.",
            "category_id": new_category.id
        }
    )

    assert response.status_code == 302

    with app.app_context():
        updated = db.session.get(Ticket, ticket.id)

        assert updated.title == "Título corregido"
        assert updated.description == "Descripción corregida."
        assert updated.category.name == "Software"

        actions = [
            history.action
            for history in updated.history
        ]

        assert "Edición de título" in actions
        assert "Cambio de categoría" in actions


def test_owner_edit_form_is_rendered(app, login, make_user, make_ticket):
    user = make_user()
    login(user)

    ticket = make_ticket(user)

    response = login.get(f"/tickets/{ticket.id}/edit")

    assert response.status_code == 200
    assert ticket.title.encode() in response.data


def test_user_cannot_edit_another_users_ticket(app, login, make_user, make_ticket):
    owner = make_user()
    intruder = make_user()

    ticket = make_ticket(owner)

    login(intruder)

    response = login.post(
        f"/tickets/{ticket.id}/edit",
        data={
            "title": "Vandalizado",
            "description": "No debería poder editarse.",
            "category_id": ticket.category_id
        }
    )

    assert response.status_code == 403

    with app.app_context():
        assert db.session.get(Ticket, ticket.id).title != "Vandalizado"


def test_technician_cannot_edit_content_of_others_ticket(
    app, login, make_user, make_ticket
):
    """El contenido solo lo edita el creador; el técnico gestiona el flujo."""
    owner = make_user()
    technician = make_user(role="technician")

    ticket = make_ticket(owner)

    login(technician)

    response = login.post(
        f"/tickets/{ticket.id}/edit",
        data={
            "title": "Editado por el técnico",
            "description": "No debería poder editarse.",
            "category_id": ticket.category_id
        }
    )

    assert response.status_code == 403

    with app.app_context():
        assert db.session.get(Ticket, ticket.id).title != "Editado por el técnico"


def test_owner_can_delete_own_ticket(app, login, make_user, make_ticket):
    user = make_user()
    login(user)

    ticket = make_ticket(user)

    ticket_id = ticket.id

    response = login.post(f"/tickets/{ticket_id}/delete")

    assert response.status_code == 302

    with app.app_context():
        assert db.session.get(Ticket, ticket_id) is None


def test_delete_removes_comments_and_history(
    app, login, make_user, make_ticket
):
    user = make_user()
    login(user)

    ticket = make_ticket(user)

    db.session.add(Comment(
        content="Comentario que debe borrarse.",
        ticket_id=ticket.id,
        user_id=user.id
    ))
    db.session.commit()

    ticket_id = ticket.id

    response = login.post(f"/tickets/{ticket_id}/delete")

    assert response.status_code == 302

    with app.app_context():
        assert Comment.query.filter_by(ticket_id=ticket_id).count() == 0
        assert History.query.filter_by(ticket_id=ticket_id).count() == 0


def test_user_cannot_delete_another_users_ticket(
    app, login, make_user, make_ticket
):
    owner = make_user()
    intruder = make_user()

    ticket = make_ticket(owner)
    ticket_id = ticket.id

    login(intruder)

    response = login.post(f"/tickets/{ticket_id}/delete")

    assert response.status_code == 403

    with app.app_context():
        assert db.session.get(Ticket, ticket_id) is not None


def test_technician_cannot_delete_another_users_ticket(
    app, login, make_user, make_ticket
):
    owner = make_user()
    technician = make_user(role="technician")

    ticket = make_ticket(owner)
    ticket_id = ticket.id

    login(technician)

    response = login.post(f"/tickets/{ticket_id}/delete")

    assert response.status_code == 403

    with app.app_context():
        assert db.session.get(Ticket, ticket_id) is not None


def test_missing_ticket_returns_404(login, make_user):
    user = make_user()
    login(user)

    assert login.get("/tickets/9999").status_code == 404
    assert login.post("/tickets/9999/delete").status_code == 404
