from marshmallow import fields

from housechef.database.models import Meal
from housechef.extensions import db, ma
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
    # recipes = fields.Pluck("self", "id", many=True)
    nutrition = fields.Raw(dump_only=True)
    date = fields.Date(required=True)

    def load(self, data, *args, **kwargs):
        # data = [
        #     {"recipes": super().load(item)} if isinstance() else item
        #     for item in data
        # ]
        return super().load(data, *args, **kwargs)

    class Meta:
        model = Meal
        ssqla_session = db.session
        load_instance = True
        ordered = True
