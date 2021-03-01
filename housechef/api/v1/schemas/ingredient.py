from marshmallow import fields
from housechef.database.models import Ingredient
from housechef.extensions import ma, db


class IngredientSchema(ma.SQLAlchemyAutoSchema):

    id = ma.Int(dump_only=True)
    time_created = fields.DateTime(dump_only=True)
    time_updated = fields.DateTime(dump_only=True)

    class Meta:
        model = Ingredient
        sqla_session = db.session
        load_instance = True
        exclude = ("spoonacular_id",)
        ordered = True
