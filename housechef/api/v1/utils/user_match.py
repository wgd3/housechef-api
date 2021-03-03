from flask_jwt_extended import get_jwt


def requested_user_matches_jwt_user(user_id: int, admin_allowed=True):

    jwt = get_jwt()
    jwt_user_id = jwt["sub"]["id"]
    roles = jwt["roles"] if "roles" in jwt else []

    return jwt_user_id == user_id or (admin_allowed and "Admin" in roles)
