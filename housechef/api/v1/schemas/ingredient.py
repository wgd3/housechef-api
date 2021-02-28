from housechef.database.models import Ingredient
from housechef.extensions import ma, db


class IngredientSchema(ma.SQLAlchemyAutoSchema):

    id = ma.Int(dump_only=True)

    class Meta:
        model = Ingredient
        sqla_session = db.session
        load_instance = True
