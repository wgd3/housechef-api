from flask import request
from flask_jwt_extended import jwt_required
from flask_restx import Resource

from housechef.commons.pagination import paginate
from housechef.extensions import db
from housechef.database.models import User, Household
from ..schemas import UserSchema


class UserResource(Resource):
    """Single object resource"""

    # method_decorators = [jwt_required]

    def get(self, user_id):
        schema = UserSchema()
        user = User.query.get_or_404(user_id)
        return {"user": schema.dump(user)}

    def put(self, user_id):
        schema = UserSchema(partial=True)
        user = User.query.get_or_404(user_id)
        user = schema.load(request.json, instance=user)

        db.session.commit()

        return {"msg": "user updated", "user": schema.dump(user)}

    def delete(self, user_id):
        user = User.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()

        return {"msg": "user deleted"}


class UserList(Resource):
    """Creation and get_all"""

    # method_decorators = [jwt_required]

    def get(self):
        schema = UserSchema(many=True)
        query = User.query.all()
        # return paginate(query, schema)
        return {"users": schema.dump(query)}

    def post(self):
        schema = UserSchema()
        user = schema.load(request.json)

        db.session.add(user)
        db.session.commit()

        return {"msg": "user created", "user": schema.dump(user)}, 201
