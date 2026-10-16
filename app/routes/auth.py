from flask import Blueprint, flash, redirect, render_template, session, url_for
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.forms.auth import LoginForm, RegistrationForm
from app.models import User

auth_bp = Blueprint(
    "auth",
    __name__,
    url_prefix="/auth"
)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()

    if form.validate_on_submit():
        email = form.email.data.strip().lower()

        existing_user = User.query.filter_by(email=email).first()

        if existing_user:
            form.email.errors.append(
                "Ya existe una cuenta con este correco electrónico."
            )
        else:
            user = User(
                name=form.name.data.strip(),
                email=email,
                role="user"
            )

            user.set_password(form.password.data)

            db.session.add(user)

            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()

                form.email.errors.append(
                    "No se pudo crear la cuenta con este correo electrónico."
                )
            else:
                flash(
                    "Cuenta creada correctamente. Ya puedes iniciar sesión.",
                    "success"
                )

                return redirect(url_for("main.index"))

    return render_template(
        "auth/register.html",
        form=form
    )

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        email = form.email.data.strip().lower()

        user = User.query.filter_by(email=email).first()

        if user is None or not user.check_password(form.password.data):
            flash(
                "Correo electrónico o contraseña incorrectos.",
                "danger"
            )
        else:
            session.clear()
            session["user_id"] = user.id

            flash(
                "Has iniciado sesión correctamente.",
                "success"
            )

            return redirect(url_for("main.index"))

    return render_template(
        "auth/login.html",
        form=form
    )

@auth_bp.route("/logout")
def logout():
    session.clear()

    flash(
        "Has cerrado sesión correctamente.",
        "success"
    )

    return redirect(url_for("main.index"))