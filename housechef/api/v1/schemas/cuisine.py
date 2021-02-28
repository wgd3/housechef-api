from housechef.database.models import Cuisine
from housechef.extensions import ma, db


class CuisineSchema(ma.SQLAlchemyAutoSchema):

    id = ma.Int(dump_only=True)

    class Meta:
        model = Cuisine
        sqla_session = db.session
        load_instance = True
