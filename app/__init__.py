from flask import Flask

from config import Config


def create_app():
    """Crea y configura la aplicación Flask."""

    app = Flask(__name__)
    app.config.from_object(Config)

    return app