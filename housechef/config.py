"""Default configuration

Use env var to override
"""
import datetime
import os

ENV = os.getenv("FLASK_ENV")
DEBUG = ENV == "development"
SECRET_KEY = os.getenv("SECRET_KEY")

print("Setting database env vars..")
SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URI")
SQLALCHEMY_TRACK_MODIFICATIONS = False

SERVER_NAME = os.getenv("SERVER_NAME", None)

SPOONACULAR_API_KEY = os.getenv("SPOONACULAR_API_KEY", "")

# Logging options
LOG_TO_STDOUT = os.getenv("LOG_TO_STDOUT", False)

# Flask-Mail
MAIL_SERVER = os.getenv("MAIL_SERVER")
MAIL_PORT = os.getenv("MAIL_PORT")
MAIL_USE_TLS = os.getenv("MAIL_USE_TLS")
MAIL_USERNAME = os.getenv("MAIL_USERNAME")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")

CELERY = {
    "broker_url": os.getenv("CELERY_BROKER_URL"),
    "result_backend": os.getenv("CELERY_RESULT_BACKEND_URL"),
}

JWT_ACCESS_TOKEN_EXPIRES = datetime.timedelta(
    seconds=int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES", 900))
)
