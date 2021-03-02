from flask_restx import Resource
from flask_sqlalchemy import Model


class RestfulEntityResource(Resource):
    """Base Resource intended to be used for endpoints that focus on a single entity"""

    def __init__(self, obj_model: Model):
        self._model = obj_model
