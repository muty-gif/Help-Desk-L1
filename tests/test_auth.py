from app.models import User


def _register(client, **overrides):
    data = {
        "name": "Nuevo usuario",
        "email": "nuevo@test.com",
        "password": "Password123!",
        "confirm_password": "Password123!"
    }

    data.update(overrides)

    return client.post("/auth/register", data=data)


def test_register_creates_account(app, client):
    response = _register(client)

    assert response.status_code == 302

    with app.app_context():
        user = User.query.filter_by(email="nuevo@test.com").first()

        assert user is not None
        assert user.name == "Nuevo usuario"
        assert user.role == "user"


def test_register_stores_password_hashed(app, client):
    _register(client)

    with app.app_context():
        user = User.query.filter_by(email="nuevo@test.com").first()

        assert user.password_hash != "Password123!"
        assert user.check_password("Password123!")
        assert not user.check_password("otra-contraseña")


def test_register_normalizes_email(app, client):
    _register(client, email="  NUEVO@Test.COM ")

    with app.app_context():
        user = User.query.filter_by(email="nuevo@test.com").first()

        assert user is not None


def test_register_rejects_duplicate_email(app, client, make_user):
    make_user(email="duplicado@test.com")

    response = _register(client, email="duplicado@test.com")

    assert response.status_code == 200

    with app.app_context():
        assert User.query.filter_by(email="duplicado@test.com").count() == 1


def test_register_rejects_mismatched_passwords(app, client):
    response = _register(client, confirm_password="Distinta123!")

    assert response.status_code == 200

    with app.app_context():
        assert User.query.count() == 0


def test_register_rejects_short_password(app, client):
    response = _register(
        client,
        password="corta",
        confirm_password="corta"
    )

    assert response.status_code == 200

    with app.app_context():
        assert User.query.count() == 0


def test_login_with_valid_credentials(app, client, make_user):
    user = make_user(email="login@test.com")

    response = client.post(
        "/auth/login",
        data={
            "email": "login@test.com",
            "password": "Password123!"
        }
    )

    assert response.status_code == 302

    with client.session_transaction() as session:
        assert session["user_id"] == user.id


def test_login_normalizes_email(app, client, make_user):
    user = make_user(email="login@test.com")

    response = client.post(
        "/auth/login",
        data={
            "email": "  LOGIN@Test.com ",
            "password": "Password123!"
        }
    )

    assert response.status_code == 302

    with client.session_transaction() as session:
        assert session["user_id"] == user.id


def test_login_with_wrong_password_is_rejected(app, client, make_user):
    make_user(email="login@test.com")

    response = client.post(
        "/auth/login",
        data={
            "email": "login@test.com",
            "password": "Contraseña2!"
        }
    )

    assert response.status_code == 200

    with client.session_transaction() as session:
        assert "user_id" not in session


def test_login_with_unknown_user_is_rejected(app, client):
    response = client.post(
        "/auth/login",
        data={
            "email": "nadie@test.com",
            "password": "Password123!"
        }
    )

    assert response.status_code == 200

    with client.session_transaction() as session:
        assert "user_id" not in session


def test_logout_clears_session(app, client, make_user):
    user = make_user()

    with client.session_transaction() as session:
        session["user_id"] = user.id

    response = client.get("/auth/logout")

    assert response.status_code == 302

    with client.session_transaction() as session:
        assert "user_id" not in session


def test_protected_pages_redirect_anonymous_users(client):
    response = client.get("/tickets/")

    assert response.status_code == 302
    assert "/auth/login" in response.headers["Location"]


def test_home_page_is_public(client):
    response = client.get("/")

    assert response.status_code == 200
