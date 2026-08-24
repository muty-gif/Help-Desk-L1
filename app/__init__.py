from flask import Flask

from config import Config
from app.extensions import db, migrate
from app.routes import main_bp
from app.routes.auth import auth_bp
from app.seed import register_seed_command


def create_app():
    """Crea y configura la aplicación Flask."""

    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)

    from app import models

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)

    register_seed_command(app)

    return app