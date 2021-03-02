from abc import ABC, abstractmethod

from flask_restx import Model


class RestXSchema(object):
    """
    Abstract class used to enforce a method that returns a RestX-compatible model. It's over-engineering
    the whole (de)serialization system, but the API currently uses both Marshmallow and Flask-RestX for
    those jobs. Implementing this method makes model management a bit easier

    """

    @staticmethod
    @abstractmethod
    def get_restx_model() -> Model:
        pass
