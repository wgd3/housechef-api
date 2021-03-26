import random
import time

from flask import current_app, render_template
from flask_mail import Message

from housechef.database.models import User
from housechef.extensions import celery, mail


@celery.task(bind=True)
def send_email(self, subject, sender, recipients, text_body, html_body):
    """
    Placeholder/sample function for sending an email via a background task:
    >>> msg = Message(subject, sender=sender, recipients=recipients)
    >>> msg.body = text_body
    >>> msg.html = html_body
    >>> mail.send(msg)

    Initially pulled from https://blog.miguelgrinberg.com/post/using-celery-with-flask
    """
    pass


@celery.task
def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


@celery.task
def send_password_reset_email(user: User):
    msg = Message(
        "Password Reset Request on Housechef",
        recipients=[user.email],
        sender="noreply@housechef.io",
        body=render_template(
            "email_templates/reset_password.txt.j2",
            user=user,
            token=user.get_password_reset_token(),
        ),
        html=render_template(
            "email_templates/reset_password.html.j2",
            user=user,
            token=user.get_password_reset_token(),
        ),
    )
    mail.send(msg)
