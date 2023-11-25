from flask import request, make_response, jsonify
import jwt
import datetime
from api import Api
from bson.errors import InvalidId
from bson.objectid import ObjectId


def get_bearer_jwt():
    '''From the request, takes the header attribute "Authorization"
    and parses the token from it
    '''
    bearer = request.headers.get('Authorization')
    if bearer:
        return bearer.split()[1]


def get_organization_id(token=None):
    token_data = jwt.decode(
        token or get_bearer_jwt(), Api.config('JWT_SECRET_KEY'), algorithms=['HS256']
    )
    organization_id = token_data.get('oid')
    if not organization_id:
        return None
    return organization_id


def api_response(message='Successful request', data={}, status=200):
    '''Uses "make_response" to create a formal API response

    Parameters:
      message (string): Default "Successful request"
      data (dict): Optional data attribute will be returned with the response
      status (int): Default status code 200

    Returns:
      Response
    '''
    response = {'message': message}
    if data:
        response['data'] = format_mongo_data(data)
    return make_response(jsonify(response), status)


def jwt_encode(email='', user_id='', expires_in=30):
    '''Encodes a new JWT token including the users email and user id

    Parameters:
      email (string): Users email
      user_id (string): Users MongoDB ObjectId
      expires_in (int): Minutes until the token is invalid

    Returns:
      String
    '''
    return jwt.encode(
        {
            'email': email,
            'userId': user_id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=expires_in),
        },
        Api.config('JWT_SECRET_KEY'),
        algorithm='HS256',
    )


def jwt_decode(token):
    '''Attempts to decode a JWT token

    Parameters:
      token (string): The token to decode

    Returns:
      Boolean: True if token was successfully decoded
    '''
    try:
        jwt.decode(token, Api.config('JWT_SECRET_KEY'), algorithms=['HS256'])
        return True
    except:
        return False


def format_mongo_data(data):
    '''Recursively works through an array or dictionary going into
    each nested array or dictionary converting any Object that is not
    a String, Integer, Float or Boolean to a String value.

    Used primarily for recursively converting MongoDB ObjectIds to Strings

    Parameters:
      data (dictionary or array): To format the values of

    Returns:
      Dictionary or Array
    '''
    if not data:
        return

    def formatter(record):
        if type(record) is dict:
            formatted = {}
            for key, value in record.items():
                if isinstance(value, (str, int, float, bool, type(None))):
                    formatted[key] = value
                    continue
                if isinstance(value, (list, dict)):
                    formatted[key] = formatter(value)
                    continue
                formatted[key] = str(value)
            return formatted

        if type(record) is list:
            formatted = []
            for value in record:
                if isinstance(value, (str, int, float, bool, type(None))):
                    formatted.append(value)
                    continue
                if isinstance(value, (list, dict)):
                    formatted.append(formatter(value))
                    continue
                formatted.append(str(value))
            return formatted

        if isinstance(record, (str, int, float, bool, type(None))):
            return record
        return str(record)

    if type(data) is dict:
        return formatter(data)

    formatted_records = []
    for record in data:
        formatted_records.append(formatter(record))
    return formatted_records


def get_user_id():
    '''Will get the users ID from their JWT token

    Returns:
      String or None
    '''
    token = get_bearer_jwt()
    try:
        return ObjectId(
            jwt.decode(token, Api.config('JWT_SECRET_KEY'), algorithms=['HS256'])[
                'userId'
            ]
        )
    except InvalidId:
        return jwt.decode(token, Api.config('JWT_SECRET_KEY'), algorithms=['HS256'])[
            'userId'
        ]
    except:
        return None


def missing_keys(data, keys):
    '''Checks if a given dictionary contains each key given
    in an array

    Parameters:
      data (dictionary): Dataset to validate
      keys (array): Keys to validate against

    Returns:
      Boolean
    '''
    if not keys or not len(keys):
        raise ('Expects keys to be an array')
    return not all(k in data for k in keys)


def accept_keys(data, keys):
    '''Checks if a given dictionary contains any keys that
    aren't in an array

    Parameters:
      data (dictionary): Dataset to validate
      keys (array): Keys to validate against

    Returns:
      Boolean
    '''
    if not keys or not len(keys):
        raise ('Expects keys to be an array')
    return not any(k not in keys for k in data)


def missing_keys_message(data, keys):
    '''Creates a message containing all the keys that where
    missing from a dictionary

    Parameters:
      data (dictionary): Dataset to validate
      keys (array): Keys to validate against

    Returns:
      String
    '''
    missing = [key for key in keys if key not in data]

    if len(missing) == 1:
        return f'{missing[0]} is missing from the request'
    if len(missing) == 2:
        return f'{missing[0]} and {missing[1]} is missing from the request'

    message = ''
    for idx, key in enumerate(missing):
        if idx + 2 == len(missing):
            message += f'{key} and {missing[idx + 1]} is missing from the request'
            break
        else:
            message += f'{key}, '

    return message


def accept_keys_message(data, keys):
    '''Creates a message containing all the keys not
    meant to be in a dictionary

    Parameters:
      data (dictionary): Dataset to validate
      keys (array): Keys to validate against

    Returns:
      String
    '''
    not_accepted = [key for key in data if key not in keys]

    if len(not_accepted) == 1:
        return f'{not_accepted[0]} are not accepted on the request'
    if len(not_accepted) == 2:
        return (
            f'{not_accepted[0]} and {not_accepted[1]} are not accepted on the request'
        )

    message = ''
    for idx, key in enumerate(not_accepted):
        if idx + 2 == len(not_accepted):
            message += (
                f'{key} and {not_accepted[idx + 1]} are not accepted on the request'
            )
            break
        else:
            message += f'{key}, '

    return message


def jwt_contains_role(roles):
    '''Given an array of roles this method will
    return true if their JWT contains at least one role

    Parameters:
      roles (array): Roles to check

    Returns:
      Boolean
    '''
    token_data = jwt.decode(
        get_bearer_jwt(), Api.config('JWT_SECRET_KEY'), algorithms=['HS256']
    )
    return any(role in token_data.get('roles') for role in roles)


# def mongo_session():
#     def decorator(func):
#         def wrapper(*args, **kwargs):
#             client = Api._client
#             session = client.start_session()
#             try:
#                 # kwargs["session"] = session
#                 result = func(*args, **kwargs)
#                 session.commit_transaction()
#                 return result
#             except Exception as e:
#                 session.abort_transaction()
#                 raise e
#             finally:
#                 session.end_session()
#                 client.close()
#         return wrapper
#     return decorator
