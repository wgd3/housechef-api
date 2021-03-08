import random
import time

from flask import current_app
from flask_mail import Message

from housechef.extensions import celery, mail


@celery.task(bind=True)
def send_email(self, subject, sender, recipients, text_body, html_body):
    """
    Placeholder/sample function for sending an email via a background task:
    >>> msg = Message(subject, sender=sender, recipients=recipients)
    >>> msg.body = text_body
    >>> msg.html = html_body
    >>> mail.send(msg)

    Initially pulled from https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-x-email-support
    """
    # with current_app.app_context() as app:
    current_app.logger.debug(f"Testing app context")
    verb = ["Starting up", "Booting", "Repairing", "Loading", "Checking"]
    adjective = ["master", "radiant", "silent", "harmonic", "fast"]
    noun = ["solar array", "particle reshaper", "cosmic ray", "orbiter", "bit"]
    message = ""
    total = random.randint(1, 10)
    for i in range(total):
        if not message or random.random() < 0.25:
            message = "{0} {1} {2}...".format(
                random.choice(verb), random.choice(adjective), random.choice(noun)
            )
        self.update_state(
            state="PROGRESS", meta={"current": i, "total": total, "status": message}
        )
        time.sleep(1)
    return {"current": 100, "total": 100, "status": "Task completed!", "result": 42}
