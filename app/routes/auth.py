from flask import Blueprint, render_template

from app.forms.auth import RegistrationForm


auth_bp = Blueprint(
    "auth",
    __name__,
    url_prefix="/auth"
)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()

    return render_template(
        "auth/register.html",
        form=form
    )