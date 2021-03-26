import logging
import os
import pprint
from logging.handlers import RotatingFileHandler

from flask import Flask

from housechef import commands
from housechef.api.v1 import api_v1
from housechef.extensions import apispec, celery, db, jwt, mail, migrate, spoon


def create_app(testing=False) -> Flask:
    """Application factory, used to create application"""
    app = Flask("housechef", template_folder="templates")
    app.config.from_object("housechef.config")

    if testing is True:
        app.config["TESTING"] = True

    configure_extensions(app)
    # configure_apispec(app)
    register_blueprints(app)
    init_celery(app)
    configure_logger(app)
    if not testing:
        register_shellcontext(app)
        register_commands(app)
    return app


def configure_extensions(app: Flask):
    """configure flask extensions"""
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    spoon.api_key = app.config["SPOONACULAR_API_KEY"]


def configure_apispec(app: Flask):
    """Configure APISpec for swagger support"""
    apispec.init_app(app, security=[{"jwt": []}])
    apispec.spec.components.security_scheme(
        "jwt", {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"}
    )
    apispec.spec.components.schema(
        "PaginatedResult",
        {
            "properties": {
                "total": {"type": "integer"},
                "pages": {"type": "integer"},
                "next": {"type": "string"},
                "prev": {"type": "string"},
            }
        },
    )


def register_blueprints(app: Flask):
    """register all blueprints for application"""
    app.register_blueprint(api_v1)


def init_celery(app=None):
    app = app or create_app()
    celery.conf.update(app.config.get("CELERY", {}))
    celery.conf["SERVER_NAME"] = app.config.get("SERVER_NAME")

    class ContextTask(celery.Task):
        """Make celery tasks work with Flask app context"""

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery


def register_shellcontext(app: Flask):
    """Register shell context objects."""

    def shell_context():
        """Shell context objects."""
        from housechef.database.models import User, Recipe

        return {
            "db": db,
            "Recipe": Recipe,
            "User": User,
        }

    app.shell_context_processor(shell_context)


def configure_logger(app: Flask):
    """Configure loggers

    This uses env variables to determine logging behavior.
    Prod: Log files only
    Dev: Log files and stdout (optionally)
    Test: None
    """
    if app.config["ENV"] in ["development", "production"]:
        if not os.path.exists("logs"):
            os.mkdir("logs")
        file_handler = RotatingFileHandler(
            "logs/dailymenu-api.log", maxBytes=10240, backupCount=10
        )
        file_handler.setFormatter(
            logging.Formatter(
                "%(asctime)s %(levelname)s: %(message)s " "[in %(pathname)s:%(lineno)d]"
            )
        )
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

    if app.config["ENV"] == "development" and app.config["LOG_TO_STDOUT"]:
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.DEBUG if app.config["DEBUG"] else logging.INFO)
        app.logger.addHandler(stream_handler)

    app.logger.info("DailyMenu API Initialized")
    app.logger.setLevel(logging.DEBUG if app.config["DEBUG"] else logging.INFO)
    app.logger.debug(f":: App Config ::\n{pprint.pformat(app.config)}")


def register_commands(app: Flask):
    app.cli.add_command(commands.gen_test_data)
    app.cli.add_command(commands.create_test_user)
