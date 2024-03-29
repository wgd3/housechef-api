from flask import Blueprint, jsonify
from flask_jwt_extended.exceptions import (
    NoAuthorizationError,
)
from flask_restx import Api
from jwt.exceptions import MissingRequiredClaimError
from marshmallow import ValidationError

from housechef.exceptions import (
    EntityNotFoundError,
    EntityValidationError,
    EntityAlreadyExistsError,
    HousechefDatabaseOpsError,
    HousechefSerializationError,
)

from .namespaces import (
    auth_ns,
    cuisine_ns,
    households_ns,
    ingredient_ns,
    recipe_ns,
    user_ns,
    diet_type_ns,
)

api_v1 = Blueprint("api_v1", __name__, url_prefix="/api/v1")
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
api.add_namespace(ingredient_ns, path="/ingredients")
api.add_namespace(households_ns, path="/households")
api.add_namespace(cuisine_ns, path="/cuisines")
api.add_namespace(diet_type_ns, path="/diet_types")


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


@api_v1.errorhandler(NoAuthorizationError)
def handle_missing_role(e):
    """Return json error when a route requires a certain role, but the user is missing that role"""
    return {
        "message": "You do not have sufficient privileges to access this route!",
        "data": None,
    }, 401


@api_v1.errorhandler(MissingRequiredClaimError)
def handle_missing_role_claims(e):
    """Return json error when a route requires a certain role, but the user's JWT is missing the roles dictionary"""
    return {
        "message": "You do not have sufficient privileges to access this route!",
        "data": None,
    }, 400


@api_v1.errorhandler(EntityValidationError)
def handle_invalid_data(e: EntityValidationError):
    return {"data": e.data, "message": e.message}, 400


@api_v1.errorhandler(EntityNotFoundError)
def handle_missing_entity_error(e: EntityNotFoundError):
    return {"data": e.data, "message": e.message}, 404


@api_v1.errorhandler(HousechefDatabaseOpsError)
def handle_missing_entity_error(e: HousechefDatabaseOpsError):
    return {"data": e.data, "message": e.message}, 500


@api_v1.errorhandler(HousechefSerializationError)
def handle_serialization_error(e: HousechefSerializationError):
    return {"data": e.data, "message": e.message}, 500
