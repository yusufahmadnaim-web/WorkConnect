from functools import wraps

from flask_jwt_extended import get_jwt, verify_jwt_in_request


def roles_required(*allowed_roles):
    def decorator(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()

            claims = get_jwt()
            user_role = claims.get("role")

            if user_role not in allowed_roles:
                return {
                    "message": "You do not have permission to access this resource"
                }, 403

            return function(*args, **kwargs)

        return wrapper

    return decorator