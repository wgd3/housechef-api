from marshmallow import fields

from housechef.database.models import Household
from housechef.extensions import ma, db

from .recipe import RecipeSchema


class HouseholdSchema(ma.SQLAlchemyAutoSchema):

    id = ma.Int(dump_only=True)

    recipes = fields.List(
        fields.Nested(
            RecipeSchema,
            only=("name", "image_url", "rating", "id", "time_created", "time_updated"),
        )
    )

    class Meta:
        model = Household
        sqla_session = db.session
        load_instance = True
