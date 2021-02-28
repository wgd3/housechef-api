from flask import Blueprint, jsonify
from flask_restx import Api
from marshmallow import ValidationError

from housechef.extensions import apispec
from .namespaces import user_ns, recipe_ns, auth_ns

api_v1 = Blueprint("api_v1", __name__, url_prefix="/v1", subdomain="api")
api = Api(
    api_v1,
    version="1.0",
    title="HouseChef.io API",
    authorizations={
        "apiKey": {
            "type": "apiKey",
            "in": "header",
            "name": "Authorization",
            "description": "Type in the *'Value'* input box below: **'Bearer &lt;JWT&gt;'**, where JWT is the token",
        }
    },
)

api.add_namespace(user_ns, path="/users")
api.add_namespace(recipe_ns, path="/recipes")
api.add_namespace(auth_ns, path="/auth")


# @api_v1.before_app_first_request
# def register_views():
#     apispec.spec.components.schema("UserSchema", schema=UserSchema)
#     apispec.spec.path(view=UserResource, app=current_app)
#     apispec.spec.path(view=UserList, app=current_app)


@api_v1.errorhandler(ValidationError)
def handle_marshmallow_error(e):
    """Return json error for marshmallow validation errors.

    This will avoid having to try/catch ValidationErrors in all endpoints, returning
    correct JSON response with associated HTTP 400 Status (https://tools.ietf.org/html/rfc7231#section-6.5.1)
    """
    return jsonify(e.messages), 400