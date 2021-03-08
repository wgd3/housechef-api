from marshmallow import fields

from housechef.database.models import DishType
from housechef.extensions import db, ma


class DishTypeSchema(ma.SQLAlchemyAutoSchema):
    id = ma.Int(dump_only=True)
    time_created = fields.DateTime(dump_only=True)
    time_updated = fields.DateTime(dump_only=True)
    name = fields.String()

    class Meta:
        model = DishType
        sqla_session = db.session
        load_instance = True
