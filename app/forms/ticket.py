from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length


class TicketForm(FlaskForm):
    title = StringField(
        "Título",
        validators=[
            DataRequired(),
            Length(max=150)
        ]
    )

    description = TextAreaField(
        "Descripción",
        validators=[
            DataRequired()
        ]
    )

    category_id = SelectField(
        "Categoría",
        coerce=int,
        validators=[
            DataRequired()
        ]
    )

    priority_id = SelectField(
        "Prioridad",
        coerce=int,
        validators=[
            DataRequired()
        ]
    )

    submit = SubmitField("Crear ticket")

class TicketStateForm(FlaskForm):
    state_id = SelectField(
        "Estado",
        coerce=int,
        validators=[
            DataRequired()
        ]
    )

    submit = SubmitField("Cambiar estado")

class CommentForm(FlaskForm):
    content = TextAreaField(
        "Comentario",
        validators=[
            DataRequired()
        ]
    )

    submit = SubmitField("Añadir comentario")

class TechnicianForm(FlaskForm):
    technician_id = SelectField(
        "Técnico",
        coerce=int,
        validators=[
            DataRequired()
        ]
    )

    submit = SubmitField("Asignar técnico")