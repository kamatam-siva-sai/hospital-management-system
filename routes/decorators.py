from functools import wraps

from flask import jsonify

from flask_jwt_extended import (
    jwt_required,
    get_jwt
)


def role_required(required_role):

    def decorator(function):

        @wraps(function)
        @jwt_required()
        def wrapper(*args, **kwargs):

            claims = get_jwt()

            user_role = claims.get("role")

            if user_role != required_role:

                return jsonify({
                    "message": "Access denied",
                    "required_role": required_role,
                    "your_role": user_role
                }), 403

            return function(*args, **kwargs)

        return wrapper

    return decorator