from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, InputRequired, Length, Optional

from app.forms.fields import TrimmedStringField


class TicketForm(FlaskForm):
    title = TrimmedStringField(
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
            InputRequired()
        ]
    )

    priority_id = SelectField(
        "Prioridad",
        coerce=int,
        validators=[
            InputRequired()
        ]
    )

    submit = SubmitField("Crear ticket")

class TicketEditForm(FlaskForm):
    """Permite editar el contenido de un ticket existente."""

    title = TrimmedStringField(
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
            InputRequired()
        ]
    )

    submit = SubmitField("Guardar cambios")

class TicketStateForm(FlaskForm):
    state_id = SelectField(
        "Estado",
        coerce=int,
        validators=[
            InputRequired()
        ]
    )

    submit = SubmitField("Cambiar estado")

class TicketPriorityForm(FlaskForm):
    priority_id = SelectField(
        "Prioridad",
        coerce=int,
        validators=[
            InputRequired()
        ]
    )

    submit = SubmitField("Cambiar prioridad")

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
            InputRequired()
        ]
    )

    submit = SubmitField("Asignar técnico")

class TicketFilterForm(FlaskForm):
    """Filtros de búsqueda del listado de tickets (método GET).

    El valor 0 en los selectores significa "sin filtro".
    """

    q = TrimmedStringField(
        "Buscar",
        validators=[
            Optional(),
            Length(max=150)
        ]
    )

    state_id = SelectField(
        "Estado",
        coerce=int,
        validators=[
            Optional()
        ]
    )

    priority_id = SelectField(
        "Prioridad",
        coerce=int,
        validators=[
            Optional()
        ]
    )

    submit = SubmitField("Filtrar")
