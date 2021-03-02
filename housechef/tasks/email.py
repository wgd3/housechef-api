from flask_mail import Message

from housechef.extensions import celery, mail


@celery.task
def send_email(subject, sender, recipients, text_body, html_body):
    """
    Placeholder/sample function for sending an email via a background task:
    >>> msg = Message(subject, sender=sender, recipients=recipients)
    >>> msg.body = text_body
    >>> msg.html = html_body
    >>> mail.send(msg)

    Initially pulled from https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-x-email-support
    """
    pass
