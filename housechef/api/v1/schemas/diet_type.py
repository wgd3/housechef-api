from flask_restx import fields, Model

from housechef.database.models import DietType, RecipeDietType
from housechef.extensions import db, ma
from .restx_schema import RestXSchema


class DietTypeSchema(ma.SQLAlchemyAutoSchema, RestXSchema):
    id = ma.Int(dump_only=True)
    time_created = fields.DateTime(dump_only=True)

    class Meta:
        model = DietType
        sqla_session = db.session
        load_instance = True

    @staticmethod
    def get_restx_model() -> Model:
        return Model(
            "Diet Type Model",
            {
                "id": fields.Integer(readonly=True),
                "time_created": fields.DateTime(readonly=True),
                "time_updated": fields.DateTime(readonly=True),
                "name": fields.String(required=True),
            },
        )


class RecipeDietTypeSchema(ma.SQLAlchemyAutoSchema):
    recipe_id = ma.Int(dump_only=True)
    diet_type_id = ma.Int(dump_only=True)

    class Meta:
        model = RecipeDietType
        sqla_session = db.session
        load_instance = True
