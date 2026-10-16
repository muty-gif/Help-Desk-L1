import itertools

import pytest

from app import create_app
from app.extensions import db
from app.models import Category, Priority, State, Ticket, User
from app.seed import seed_data


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
def seed(app):
    """Inserta estados, prioridades y categorías de referencia."""
    seed_data()

    return app


@pytest.fixture
def make_user(app, seed):
    """Crea usuarios de prueba con un correo único por defecto."""
    emails = itertools.count(1)

    def _make_user(name="Usuario de prueba", role="user", email=None):
        user = User(
            name=name,
            email=email or f"usuario{next(emails)}@test.com",
            role=role
        )

        user.set_password("Password123!")

        db.session.add(user)
        db.session.commit()

        return user

    return _make_user


@pytest.fixture
def make_ticket(app, seed):
    """Crea tickets de prueba con los datos de referencia."""
    tickets = itertools.count(1)

    def _make_ticket(user, title=None, **kwargs):
        ticket = Ticket(
            title=title or f"Ticket de prueba {next(tickets)}",
            description=kwargs.pop(
                "description",
                "Descripción del ticket de prueba."
            ),
            category_id=kwargs.pop(
                "category_id",
                Category.query.filter_by(name="Hardware").first().id
            ),
            state_id=kwargs.pop(
                "state_id",
                State.query.filter_by(name="Abierto").first().id
            ),
            priority_id=kwargs.pop(
                "priority_id",
                Priority.query.filter_by(name="Media").first().id
            ),
            user_id=user.id,
            **kwargs
        )

        db.session.add(ticket)
        db.session.commit()

        return ticket

    return _make_ticket


class _AuthenticatedClient:
    """Cliente de prueba que delega en el test_client de Flask.

    Permite dos usos indistintamente:

        client = login(user)   # devuelve el cliente autenticado
        login(user)
        login.get("/tickets/") # o bien llamarlo directamente
    """

    def __init__(self, client):
        self._client = client

    def __call__(self, user):
        with self._client.session_transaction() as session:
            session["user_id"] = user.id

        return self

    def get(self, *args, **kwargs):
        return self._client.get(*args, **kwargs)

    def post(self, *args, **kwargs):
        return self._client.post(*args, **kwargs)

    def session_transaction(self, *args, **kwargs):
        return self._client.session_transaction(*args, **kwargs)


@pytest.fixture
def login(client):
    """Autentica a un usuario directamente en la sesión."""
    return _AuthenticatedClient(client)
