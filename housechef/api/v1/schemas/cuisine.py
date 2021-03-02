from housechef.database.models import Cuisine
from housechef.extensions import db, ma

from flask_restx import Model, fields

from .restx_schema import RestXSchema


class CuisineSchema(ma.SQLAlchemyAutoSchema, RestXSchema):
    id = ma.Int(dump_only=True)

    class Meta:
        model = Cuisine
        sqla_session = db.session
        load_instance = True

    @staticmethod
    def get_restx_model() -> Model:
        return Model(
            "Cuisine Model",
            {
                "id": fields.Integer(readonly=True),
                "time_created": fields.DateTime(readonly=True),
                "time_updated": fields.DateTime(readonly=True),
                "name": fields.String(required=True),
            },
        )
