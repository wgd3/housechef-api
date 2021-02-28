from housechef.database.models import RecipeIngredient
from housechef.extensions import ma, db


class RecipeIngredientSchema(ma.SQLAlchemyAutoSchema):
    id = ma.Int(dump_only=True)

    class Meta:
        model = RecipeIngredient
        sqla_session = db.session
        load_instance = True
