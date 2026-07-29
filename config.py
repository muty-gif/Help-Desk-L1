from pathlib import Path


class Config:
    """Configuración base de la aplicación."""

    SECRET_KEY = "dev-secret-key"

    BASE_DIR = Path(__file__).resolve().parent

    SQLALCHEMY_DATABASE_URI = (
        f"sqlite:///{BASE_DIR / 'app' / 'database' / 'helpdesk.db'}"
    )

    SQALCHEMY_TRACK_MODIFICATIONS = False