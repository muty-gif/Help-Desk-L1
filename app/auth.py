from functools import wraps

from flask import flash, redirect, session, url_for

from app.extensions import db
from app.models import User


def get_current_user():
    """Devuelve el usuario autenticado o None."""
    user_id = session.get("user_id")

    if user_id is None:
        return None

    return db.session.get(User, user_id)

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