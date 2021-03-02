from functools import wraps

from flask_jwt_extended import get_jwt
from flask_jwt_extended.exceptions import (
    NoAuthorizationError,
)
from flask_jwt_extended.view_decorators import verify_jwt_in_request
from jwt.exceptions import MissingRequiredClaimError


def role_required(role_name: str, optional: bool = False):
    """Decorator for ensuring a certain route is only accessible by users with certain roles"""

    def role_decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            try:
                claims = get_jwt()
                roles = claims["roles"]
                if role_name not in roles and not optional:
                    raise NoAuthorizationError
            except KeyError as e:
                raise MissingRequiredClaimError("roles")

            return fn(*args, **kwargs)

        return wrapper

    return role_decorator
