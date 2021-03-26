from http import HTTPStatus

from flask import jsonify, abort
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    jwt_required,
)
from flask_restx import fields, Namespace, Resource, reqparse

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


@ns.route("/reset_password_request", endpoint="reset_password_request")
@ns.response(HTTPStatus.OK.value, HTTPStatus.OK.phrase)
@ns.response(HTTPStatus.BAD_REQUEST.value, HTTPStatus.BAD_REQUEST.phrase)
class ResetPasswordRequest(Resource):

    arg_parser = reqparse.RequestParser()
    arg_parser.add_argument(
        "reset_token",
        type=str,
        required=True,
    )

    def get(self):
        args = self.arg_parser.parse_args()
        if args.get("reset_token", None) is None:
            abort(400)

    def post(self):
        """Endpoint for triggering a password reset email to be sent"""
        user_email = ns.payload["email"]
        if user_email is None or user_email == "":
            # TODO use a marshmallow model for email validation?
            abort(401, "Invalid email!")

        user = User.query.filter(User.email == user_email).one_or_none()
        if user:
            pass

        return {
            "message": "Password reset requested, please check your inbox for instructions!"
        }, 200


@ns.route("/reset_password/<token>", endpoint="reset_password")
class UserPasswordResource(Resource):
    def get(self, token: str):
        pass
