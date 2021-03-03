from marshmallow import fields

from housechef.extensions import db, ma


class SchemaWithIdMixin:
    id = ma.Int(dump_only=True)


class SchemaWithTimestampsMixin:
    time_created = fields.DateTime(dump_only=True)
    time_updated = fields.DateTime(dump_only=True)
