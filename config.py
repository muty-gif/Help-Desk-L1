from os import environ
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


class Config:
    """Configuración base de la aplicación."""

    SECRET_KEY = environ.get("SECRET_KEY", "dev-secret-key")

    SQLALCHEMY_DATABASE_URI = environ.get(
        "DATABASE_URL",
        f"sqlite:///{BASE_DIR / 'app' / 'database' / 'helpdesk.db'}"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False
