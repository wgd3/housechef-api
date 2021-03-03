from flask_restx import Model
from marshmallow import fields, validate

from housechef.database.models import Role
from housechef.extensions import db, ma

from ..utils import SchemaWithIdMixin, SchemaWithTimestampsMixin
from .restx_schema import RestXSchema


class RoleSchema(
    ma.SQLAlchemyAutoSchema, SchemaWithIdMixin, SchemaWithTimestampsMixin, RestXSchema
):

    name = fields.String(required=True)

    @staticmethod
    def get_restx_model() -> Model:
        pass

    class Meta:
        model = Role
        sqla_session = db.session
        load_instance = True
