from housechef.database.models import DishType
from housechef.extensions import ma, db


class RecipeTypeSchema(ma.SQLAlchemyAutoSchema):

    id = ma.Int(dump_only=True)

    class Meta:
        model = DishType
        sqla_session = db.session
        load_instance = True
