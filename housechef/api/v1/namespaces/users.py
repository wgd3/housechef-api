from http import HTTPStatus

from flask import request
from flask_jwt_extended import jwt_required
from flask_restx import Namespace, Resource

from housechef.database.models import User
from housechef.extensions import db
from ..schemas import UserSchema
from ..utils import role_required

ns = Namespace("Users", description="User Operations")


@ns.route("/<int:user_id>", endpoint="get_user")
@ns.response(HTTPStatus.OK.value, HTTPStatus.OK.phrase)
@ns.response(HTTPStatus.BAD_REQUEST.value, HTTPStatus.BAD_REQUEST.phrase)
@ns.response(
    HTTPStatus.SERVICE_UNAVAILABLE.value, HTTPStatus.SERVICE_UNAVAILABLE.phrase
)
@ns.response(HTTPStatus.UNAUTHORIZED.value, HTTPStatus.UNAUTHORIZED.phrase)
@ns.doc(security="apiKey")
class UserResource(Resource):
    """Single object resource"""

    @jwt_required()
    def get(self, user_id):
        schema = UserSchema()
        user = User.query.get_or_404(user_id)
        return {"user": schema.dump(user)}

    @jwt_required()
    def put(self, user_id):
        schema = UserSchema(partial=True)
        user = User.query.get_or_404(user_id)
        user = schema.load(request.json, instance=user)

        db.session.commit()

        return {"msg": "user updated", "user": schema.dump(user)}

    @jwt_required()
    def delete(self, user_id):
        user = User.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()

        return {"msg": "user deleted"}


@ns.route("", endpoint="list_users")
@ns.response(HTTPStatus.OK.value, HTTPStatus.OK.phrase)
@ns.response(HTTPStatus.BAD_REQUEST.value, HTTPStatus.BAD_REQUEST.phrase)
@ns.response(
    HTTPStatus.SERVICE_UNAVAILABLE.value, HTTPStatus.SERVICE_UNAVAILABLE.phrase
)
@ns.response(HTTPStatus.UNAUTHORIZED.value, HTTPStatus.UNAUTHORIZED.phrase)
@ns.doc(security="apiKey")
class UserList(Resource):
    """Creation and get_all"""

    @jwt_required()
    @role_required("Admin")
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
