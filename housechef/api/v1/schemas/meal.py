from marshmallow import fields
from housechef.database.models import Meal
from housechef.extensions import ma, db

from .recipe import RecipeSchema


class MealSchema(ma.SQLAlchemyAutoSchema):

    id = ma.Int(dump_only=True)
    time_created = fields.DateTime(dump_only=True)
    time_updated = fields.DateTime(dump_only=True)

    household_id = fields.Integer(required=True)
    recipes = fields.List(
        fields.Nested(
            RecipeSchema,
            only=(
                "id",
                "name",
            ),
        )
    )
    nutrition = fields.Raw(dump_only=True)
    date = fields.Date(required=True)

    class Meta:
        model = Meal
        ssqla_session = db.session
        load_instance = True
        ordered = True
