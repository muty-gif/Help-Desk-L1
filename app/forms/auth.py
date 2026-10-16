from flask_wtf import FlaskForm
from wtforms import PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length

from app.forms.fields import TrimmedStringField


class RegistrationForm(FlaskForm):
    name = TrimmedStringField(
        "Nombre",
        validators=[
            DataRequired(),
            Length(min=2, max=100)
        ]
    )

    email = TrimmedStringField(
        "Correo electrónico",
        validators=[
            DataRequired(),
            Email(),
            Length(max=120)
        ]
    )

    password = PasswordField(
        "Contraseña",
        validators=[
            DataRequired(),
            Length(min=8)
        ]
    )

    confirm_password = PasswordField(
        "Confirmar contraseña",
        validators=[
            DataRequired(),
            EqualTo("password")
        ]
    )

    submit = SubmitField("Registrarse")

class LoginForm(FlaskForm):
    email = TrimmedStringField(
        "Correo electrónico",
        validators=[
            DataRequired(),
            Email(),
            Length(max=120)
        ]
    )

    password = PasswordField(
        "Contraseña",
        validators=[
            DataRequired()
        ]
    )

    submit = SubmitField("Iniciar sesión")