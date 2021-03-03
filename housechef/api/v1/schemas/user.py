from flask_restx import Model, fields as restxFields
from marshmallow import fields, validate

from housechef.database.models import User
from housechef.extensions import db, ma

from ..utils import SchemaWithIdMixin, SchemaWithTimestampsMixin
from .restx_schema import RestXSchema


class UserSchema(ma.SQLAlchemyAutoSchema, RestXSchema):
    id = ma.Int(dump_only=True)
    time_created = fields.DateTime(dump_only=True)
    time_updated = fields.DateTime(dump_only=True)
    username = ma.String(required=True)
    email = fields.Email(required=True)
    active = fields.Boolean()
    first_name = fields.String()
    last_name = fields.String()
    birthday = fields.Date()
    height_inches = fields.Float()
    weight_lbs = fields.Float()
    gender = fields.String(validate=validate.OneOf(["male", "female"]))
    password = ma.String(load_only=True, required=True)
    household = fields.Nested(
        "HouseholdSchema",
        only=(
            "id",
            "name",
        ),
    )
    household_id = fields.Integer()
    roles = fields.List(
        fields.Nested(
            "RoleSchema",
            only=(
                "id",
                "name",
            ),
        )
    )

    @staticmethod
    def get_restx_model() -> Model:
        return Model(
            "User Model",
            {
                "id": restxFields.Integer(),
                "time_created": restxFields.DateTime(),
                "time_updated": restxFields.DateTime(),
                "username": restxFields.String(),
                "email": restxFields.String(),
                "active": restxFields.Boolean(),
                "first_name": restxFields.String(),
                "last_name": restxFields.String(),
                "birthday": restxFields.Date(),
                "height_inches": restxFields.Float(),
                "weight_lbs": restxFields.Float(),
                "gender": restxFields.String(),
                "household": restxFields.Raw(),
                "household_id": restxFields.Integer(),
                "roles": restxFields.List(restxFields.Raw()),
            },
        )

    class Meta:
        model = User
        sqla_session = db.session
        load_instance = True
        exclude = ("_password",)
        ordered = True
