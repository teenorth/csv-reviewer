from functools import wraps
from api.util import (
    api_response,
    jwt_decode,
    get_bearer_jwt,
    missing_keys,
    accept_keys,
    missing_keys_message,
    accept_keys_message,
    get_bearer_jwt,
    jwt_contains_role,
    get_user_id,
)
from flask import request
from api import database as db


def jwt_required(func):
    '''Will validate that the user has provided a valid JWT
    token before allowing the route method to called
    '''

    @wraps(func)
    def wrapper(*args, **kwargs):
        token = get_bearer_jwt()
        if not token:
            return api_response(
                message='Unauthorized access: No bearer token provided', status=401
            )
        if not jwt_decode(token):
            return api_response(
                message='Unauthorized access: Token is invalid', status=401
            )
        user_id = get_user_id()
        if user_id:
            found_user = db.user.show(object_id=user_id)
            if not found_user:
                return api_response(
                    message='Unauthorized access: User does not exist', status=401
                )
        return func(*args, **kwargs)

    return wrapper


def json_keys_required(keys):
    '''Will validate that the JSON keys provided match and
    have been sent over in the request body as JSON
    '''

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            json = request.json
            if missing_keys(json, keys):
                return api_response(
                    message=missing_keys_message(json, keys), status=422
                )
            return func(*args, **kwargs)

        return wrapper

    return decorator


def json_keys_accepted(keys):
    '''Will validate that the JSON keys provided are the only
    keys provided in the request body as JSON
    '''

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            json = request.json
            if not accept_keys(json, keys):
                return api_response(message=accept_keys_message(json, keys), status=422)
            return func(*args, **kwargs)

        return wrapper

    return decorator


def has_role(roles):
    '''Will validate that one of the roles provided are
    present in the users JWT token
    '''

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not jwt_contains_role(roles):
                return api_response(
                    message='Unauthorized access: Invalid role', status=401
                )
            return func(*args, **kwargs)

        return wrapper

    return decorator
