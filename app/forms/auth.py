from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length


class RegistrationForm(FlaskForm):
    name = StringField(
        "Nombre",
        validators=[
            DataRequired(),
            Length(min=2, max=100)
        ]
    )

    email = StringField(
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