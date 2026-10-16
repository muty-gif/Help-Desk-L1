from functools import wraps

from flask import abort, flash, redirect, session, url_for

from app.extensions import db
from app.models import User


def get_current_user():
    """Devuelve el usuario autenticado o None."""
    user_id = session.get("user_id")

    if user_id is None:
        return None

    return db.session.get(User, user_id)

def can_manage_ticket(user, ticket):
    """Indica si un usuario puede ver o administrar un ticket.

    Regla del sistema: el creador es dueño del contenido del ticket
    (editar y borrar) y los técnicos gestionan su flujo (estado,
    prioridad, asignación y comentarios).
    """
    if user is None:
        return False

    if user.role == "technician":
        return True

    return ticket.user_id == user.id

def owns_ticket(user, ticket):
    """Indica si el usuario es el creador del ticket."""
    return user is not None and ticket.user_id == user.id

def login_required(view):
    """Exige que exista un usuario autenticado."""

    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if get_current_user() is None:
            flash(
                "Debes iniciar sesión para acceder a esta página.",
                "warning"
            )

            return redirect(url_for("auth.login"))

        return view(*args, **kwargs)

    return wrapped_view

def role_required(role):
    def decorator(view):
        @wraps(view)
        def wrapped_view(*args, **kwargs):
            user = get_current_user()

            if user is None:
                abort(401)

            if user.role != role:
                abort(403)

            return view(*args, **kwargs)

        return wrapped_view

    return decorator
