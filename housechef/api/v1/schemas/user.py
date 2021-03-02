from marshmallow import fields

from housechef.database.models import User
from housechef.extensions import db, ma


class UserSchema(ma.SQLAlchemyAutoSchema):
    id = ma.Int(dump_only=True)
    time_created = fields.DateTime(dump_only=True)
    time_updated = fields.DateTime(dump_only=True)
    password = ma.String(load_only=True, required=True)
    roles = fields.List(fields.String)
    household_id = fields.Integer()

    class Meta:
        model = User
        sqla_session = db.session
        load_instance = True
        exclude = ("_password",)
