from http import HTTPStatus

from flask import jsonify
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    jwt_required,
)
from flask_restx import fields, Namespace, Resource

from housechef.database.models import User
from housechef.extensions import pwd_context

ns = Namespace("Auth", description="JWT Operations")

token_get_model = ns.model(
    "token_get_model", {"access_token": fields.String, "refresh_token": fields.String}
)
login_post_model = ns.model(
    "login_model", {"username": fields.String, "password": fields.String}
)
refresh_resp_model = ns.model("refresh_resp_model", {"access_token": fields.String})


@ns.route("/login", endpoint="auth_login")
@ns.response(HTTPStatus.OK.value, HTTPStatus.OK.phrase, model=token_get_model)
@ns.response(HTTPStatus.BAD_REQUEST.value, HTTPStatus.BAD_REQUEST.phrase)
@ns.response(HTTPStatus.UNAUTHORIZED.value, HTTPStatus.UNAUTHORIZED.phrase)
class LogInResource(Resource):
    """Authenticates and returns tokens"""

    @ns.expect(login_post_model, validate=False)
    def post(self):
        username = ns.payload["username"] if "username" in ns.payload else None
        password = ns.payload["password"] if "password" in ns.payload else None
        if not username or not password:
            return {
                "message": "Missing username or password"
            }, HTTPStatus.BAD_REQUEST.value

        user = User.query.filter(User.username == username).one_or_none()
        if user is None or not pwd_context.verify(password, user.password):
            return {
                "message": f"Authentication failed for user {user.username}. Please check the username and password and try again"
            }, HTTPStatus.UNAUTHORIZED

        access_token = user.get_access_token()
        refresh_token = user.get_refresh_token()

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
        }, HTTPStatus.OK


@ns.route("/refresh", endpoint="auth_refresh")
@ns.response(HTTPStatus.OK.value, HTTPStatus.OK.phrase, model=refresh_resp_model)
class RefreshTokenResource(Resource):
    @ns.doc(security="apiKey")
    @jwt_required(refresh=True)
    def post(self):
        user_identity = get_jwt_identity()
        user = User.get_by_id(user_identity["id"])
        access_token = user.get_refresh_token()
        return {"access_token": access_token}, HTTPStatus.OK
