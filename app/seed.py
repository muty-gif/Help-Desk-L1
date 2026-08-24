import click

from app.extensions import db

from app.models import Category, State, Priority


def seed_data():
    """Inserta los datos iniciales que no existan."""

    categories = [
        "Hardware",
        "Software",
        "Red",
        "Cuentas",
        "Otros",
    ]

    states = [
        "Abierto",
        "En progreso",
        "Pendiente",
        "Resuelto",
        "Cerrado",
    ]

    priorities = [
        "Baja",
        "Media",
        "Alta",
        "Crítica",
    ]

    for name in categories:
        if not Category.query.filter_by(name=name).first():
            db.session.add(Category(name=name))

    for name in states:
        if not State.query.filter_by(name=name).first():
            db.session.add(State(name=name))

    for name in priorities:
        if not Priority.query.filter_by(name=name).first():
            db.session.add(Priority(name=name))

    db.session.commit()


def register_seed_command(app):
    """Registra el comando CLI para insertar datos iniciales."""

    @app.cli.command("seed")
    def seed():
        """Inserta los datos iniciales de la aplicación."""

        seed_data()

        click.echo("Datos iniciales comprobados correctamente.")