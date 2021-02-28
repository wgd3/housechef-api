from housechef.database.models import Tag
from housechef.extensions import ma, db


class TagSchema(ma.SQLAlchemyAutoSchema):

    id = ma.Int(dump_only=True)

    class Meta:
        model = Tag
        sqla_session = db.session
        load_instance = True
