import pytest

from app import create_app
from app.extensions import db
from app.models import (
    Category,
    Comment,
    History,
    Priority,
    State,
    Ticket,
    User,
)


@pytest.fixture
def app():
    app = create_app({
        "TESTING": True,
        "SECRET_KEY": "test-secret-key",
        "WTF_CSRF_ENABLED": False,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"
    })

    with app.app_context():
        db.create_all()

        yield app

        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def create_user():
    def _create_user(name, email, role):
        user = User(
            name=name,
            email=email,
            role=role
        )
        user.set_password("Password123!")

        db.session.add(user)
        db.session.commit()

        return user

    return _create_user

def test_user_cannot_comment_on_another_users_ticket(app, client):
    with app.app_context():
        user_1 = User(
            name="Usuario 1",
            email="usuario1@test.com",
            role="user"
        )
        user_1.set_password("Password123!")

        user_2 = User(
            name="Usuario 2",
            email="usuario2@test.com",
            role="user"
        )
        user_2.set_password("Password123!")

        db.session.add_all([user_1, user_2])
        db.session.commit()

        category = Category(name="Hardware")
        state = State(name="Abierto")
        priority = Priority(name="Media")

        db.session.add_all([
            category,
            state,
            priority
        ])
        db.session.commit()

        ticket = Ticket(
            title="Ordenador no enciende",
            description="El ordenador no muestra ninguna señal.",
            category_id=category.id,
            state_id=state.id,
            priority_id=priority.id,
            user_id=user_2.id
        )

        db.session.add(ticket)
        db.session.commit()

        ticket_id = ticket.id
        user_1_id = user_1.id

    with client.session_transaction() as session:
        session["user_id"] = user_1_id

    response = client.post(
        f"/tickets/{ticket_id}/comments",
        data={
            "content": "Intento de comentario sobre un ticket ajeno."
        }
    )

    assert response.status_code == 403

def test_user_can_comment_on_own_ticket(app, client):
    with app.app_context():
        user = User(
            name="Usuario",
            email="usuario@test.com",
            role="user"
        )
        user.set_password("Password123!")

        db.session.add(user)
        db.session.commit()

        category = Category(name="Hardware")
        state = State(name="Abierto")
        priority = Priority(name="Media")

        db.session.add_all([
            category,
            state,
            priority
        ])
        db.session.commit()

        ticket = Ticket(
            title="Ordenador no enciende",
            description="El ordenador no muestra ninguna señal.",
            category_id=category.id,
            state_id=state.id,
            priority_id=priority.id,
            user_id=user.id
        )

        db.session.add(ticket)
        db.session.commit()

        ticket_id = ticket.id
        user_id = user.id

    with client.session_transaction() as session:
        session["user_id"] = user_id

    response = client.post(
        f"/tickets/{ticket_id}/comments",
        data={
            "content": "Este es un comentario válido."
        }
    )

    assert response.status_code == 302

    with app.app_context():
        comment = Comment.query.first()

        assert comment is not None
        assert comment.content == "Este es un comentario válido."
        assert comment.ticket_id == ticket_id
        assert comment.user_id == user_id

def test_technician_can_comment_on_another_users_ticket(app, client, create_user):
    with app.app_context():

        user = create_user(
            "Usuario",
            "usuario@test.com",
            "user"
        )

        technician = create_user(
            "Tecnico",
            "tecnico@test.com",
            "technician"
        )

        db.session.add_all([user, technician])
        db.session.commit()

        category = Category(name="Hardware")
        state = State(name="Abierto")
        priority = Priority(name="Media")

        db.session.add_all([
            category,
            state,
            priority
        ])
        db.session.commit()

        ticket = Ticket(
            title="Ordenador no enciende",
            description="El ordenador no muestra ninguna señal.",
            category_id=category.id,
            state_id=state.id,
            priority_id=priority.id,
            user_id=user.id
        )

        db.session.add(ticket)
        db.session.commit()

        ticket_id = ticket.id
        technician_id = technician.id

    with client.session_transaction() as session:
        session["user_id"] = technician_id

    response = client.post(
        f"/tickets/{ticket_id}/comments",
        data={
            "content": "He revisado la incidencia."
        }
    )

    assert response.status_code == 302

    with app.app_context():
        comment = Comment.query.first()

        assert comment is not None
        assert comment.content == "He revisado la incidencia."
        assert comment.ticket_id == ticket_id
        assert comment.user_id == technician_id

def test_user_cannot_change_ticket_state(app, client):
    with app.app_context():
        user = User(
            name="Usuario",
            email="usuario@test.com",
            role="user"
        )
        user.set_password("Password123!")

        db.session.add(user)
        db.session.commit()

        category = Category(name="Hardware")
        state_open = State(name="Abierto")
        state_progress = State(name="En progreso")
        priority = Priority(name="Media")

        db.session.add_all([
            category,
            state_open,
            state_progress,
            priority
        ])
        db.session.commit()

        ticket = Ticket(
            title="Ordenador no enciende",
            description="El ordenador no muestra ninguna señal.",
            category_id=category.id,
            state_id=state_open.id,
            priority_id=priority.id,
            user_id=user.id
        )

        db.session.add(ticket)
        db.session.commit()

        ticket_id = ticket.id
        user_id = user.id
        progress_state_id = state_progress.id

    with client.session_transaction() as session:
        session["user_id"] = user_id

    response = client.post(
        f"/tickets/{ticket_id}/state",
        data={
            "state_id": progress_state_id
        }
    )

    assert response.status_code == 403

    with app.app_context():
        ticket = db.session.get(Ticket, ticket_id)

        assert ticket.state_id != progress_state_id

def test_technician_can_change_ticket_state(app, client):
    with app.app_context():
        technician = User(
            name="Tecnico",
            email="tecnico@test.com",
            role="technician"
        )
        technician.set_password("Password123!")

        db.session.add(technician)
        db.session.commit()

        category = Category(name="Hardware")
        state_open = State(name="Abierto")
        state_progress = State(name="En progreso")
        priority = Priority(name="Media")

        db.session.add_all([
            category,
            state_open,
            state_progress,
            priority
        ])
        db.session.commit()

        ticket = Ticket(
            title="Ordenador no enciende",
            description="El ordenador no muestra ninguna señal.",
            category_id=category.id,
            state_id=state_open.id,
            priority_id=priority.id,
            user_id=technician.id
        )

        db.session.add(ticket)
        db.session.commit()

        ticket_id = ticket.id
        technician_id = technician.id
        progress_state_id = state_progress.id

    with client.session_transaction() as session:
        session["user_id"] = technician_id

    response = client.post(
        f"/tickets/{ticket_id}/state",
        data={
            "state_id": progress_state_id
        }
    )

    assert response.status_code == 302

    with app.app_context():
        ticket = db.session.get(Ticket, ticket_id)

        assert ticket.state_id == progress_state_id

        history = History.query.filter_by(
            ticket_id=ticket_id
        ).first()

        assert history is not None
        assert history.action == "Cambio de estado"
        assert history.old_value == "Abierto"
        assert history.new_value == "En progreso"
        assert history.user_id == technician_id

def test_user_cannot_assign_technician(app, client):
    with app.app_context():
        user = User(
            name="Usuario",
            email="usuario@test.com",
            role="user"
        )
        user.set_password("Password123!")

        technician = User(
            name="Tecnico",
            email="tecnico@test.com",
            role="technician"
        )
        technician.set_password("Password123!")

        db.session.add_all([user, technician])
        db.session.commit()

        category = Category(name="Hardware")
        state = State(name="Abierto")
        priority = Priority(name="Media")

        db.session.add_all([
            category,
            state,
            priority
        ])
        db.session.commit()

        ticket = Ticket(
            title="Ordenador no enciende",
            description="El ordenador no muestra ninguna señal.",
            category_id=category.id,
            state_id=state.id,
            priority_id=priority.id,
            user_id=user.id
        )

        db.session.add(ticket)
        db.session.commit()

        ticket_id = ticket.id
        user_id = user.id
        technician_id = technician.id

    with client.session_transaction() as session:
        session["user_id"] = user_id

    response = client.post(
        f"/tickets/{ticket_id}/technician",
        data={
            "technician_id": technician_id
        }
    )

    assert response.status_code == 403

    with app.app_context():
        ticket = db.session.get(Ticket, ticket_id)

        assert ticket.technician_id is None

def test_technician_can_assign_technician(app, client):
    with app.app_context():
        user = User(
            name="Usuario",
            email="usuario@test.com",
            role="user"
        )
        user.set_password("Password123!")

        technician_1 = User(
            name="Tecnico 1",
            email="tecnico1@test.com",
            role="technician"
        )
        technician_1.set_password("Password123!")

        technician_2 = User(
            name="Tecnico 2",
            email="tecnico2@test.com",
            role="technician"
        )
        technician_2.set_password("Password123!")

        db.session.add_all([
            user,
            technician_1,
            technician_2
        ])
        db.session.commit()

        category = Category(name="Hardware")
        state = State(name="Abierto")
        priority = Priority(name="Media")

        db.session.add_all([
            category,
            state,
            priority
        ])
        db.session.commit()

        ticket = Ticket(
            title="Ordenador no enciende",
            description="El ordenador no muestra ninguna señal.",
            category_id=category.id,
            state_id=state.id,
            priority_id=priority.id,
            user_id=user.id
        )

        db.session.add(ticket)
        db.session.commit()

        ticket_id = ticket.id
        technician_1_id = technician_1.id
        technician_2_id = technician_2.id

    with client.session_transaction() as session:
        session["user_id"] = technician_1_id

    response = client.post(
        f"/tickets/{ticket_id}/technician",
        data={
            "technician_id": technician_2_id
        }
    )

    assert response.status_code == 302

    with app.app_context():
        ticket = db.session.get(Ticket, ticket_id)

        assert ticket.technician_id == technician_2_id

        history = History.query.filter_by(
            ticket_id=ticket_id
        ).first()

        assert history is not None
        assert history.action == "Asignación de técnico"
        assert history.old_value == "Sin asignar"
        assert history.new_value == technician_2.name
        assert history.user_id == technician_1_id