from flask import Flask

from config import Config
from app.extensions import db, migrate
from app.routes import main_bp
from app.routes.auth import auth_bp
from app.routes.tickets import tickets_bp
from app.seed import register_seed_command
from app.auth import get_current_user


def create_app():
    """Crea y configura la aplicación Flask."""

    app = Flask(__name__)

    if test_config is None:
        app.config.from_object(Config)
    else:
        app.config.from_mapping(test_config)

    db.init_app(app)
    migrate.init_app(app, db)

    from app import models

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(tickets_bp)

    @app.context_processor
    def inject_current_user():
        return {
            "current_user": get_current_user()
        }

    register_seed_command(app)

    return app