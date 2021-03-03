from http import HTTPStatus

from flask import current_app, request, abort
from flask_jwt_extended import (
    get_current_user,
    get_jti,
    get_jwt,
    get_jwt_identity,
    jwt_required,
)
from flask_restx import Namespace, Resource, fields

from housechef.database.models import User
from housechef.extensions import db
from ..models import links_envelope, meta_envelope, response_envelope
from ..schemas import UserSchema
from ..utils import role_required, requested_user_matches_jwt_user

ns = Namespace("Users", description="User Operations")

response_env = ns.model(response_envelope.get("name"), response_envelope.get("fields"))
meta_env = ns.model(meta_envelope.get("name"), meta_envelope.get("fields"))
links_env = ns.model(links_envelope.get("name"), links_envelope.get("fields"))

user_model = ns.model(UserSchema.get_restx_model().name, UserSchema.get_restx_model())

get_user_model = ns.clone(
    "get_user_model", response_env, {"data": fields.Nested(user_model)}
)
get_user_list_model = ns.inherit(
    "get_user_list_model",
    response_env,
    {
        "data": fields.List(fields.Nested(user_model)),
        "_meta": fields.Nested(meta_env),
        "_links": fields.Nested(links_env),
    },
)


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
    @ns.marshal_with(get_user_model)
    def get(self, user_id: int):
        if not requested_user_matches_jwt_user(user_id):
            current_app.logger.error(
                f"Requested user ({user_id}) does not match user ID from JWT"
            )
            abort(403, "Requested user does not match user found in token!")

        schema = UserSchema()
        user = User.query.get_or_404(user_id)
        return {"data": schema.dump(user), "message": f"Returning user {user.username}"}

    @jwt_required()
    @ns.marshal_with(get_user_model)
    def put(self, user_id):
        if not requested_user_matches_jwt_user(user_id):
            abort(403, "Requested user does not match user found in token!")
        schema = UserSchema(partial=True)
        user = User.query.get_or_404(user_id)
        # user.update(**ns.payload)
        user = schema.load(ns.payload, instance=user)

        db.session.commit()

        return {"data": schema.dump(user), "message": f"Returning user {user.username}"}

    @jwt_required()
    def delete(self, user_id):
        if not requested_user_matches_jwt_user(user_id):
            abort(403, "Requested user does not match user found in token!")

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
    @ns.marshal_with(get_user_list_model)
    def get(self):
        schema = UserSchema(many=True)
        query = User.query.all()
        # return paginate(query, schema)
        return {"data": schema.dump(query), "message": f"Returning {len(query)} users"}

    @ns.marshal_with(get_user_model)
    @ns.expect(user_model)
    def post(self):
        schema = UserSchema()
        user = schema.load(ns.payload)
        db.session.add(user)
        db.session.commit()
        # user = User.create(**ns.payload)

        return {
            "data": schema.dump(user),
            "message": f"Created user {user.username}",
        }, 201
