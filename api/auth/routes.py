from flask import Blueprint, request
from api.util import jwt_encode, api_response, format_mongo_data
from api.middleware import json_keys_required
from api import Api

auth = Blueprint('auth', __name__, url_prefix='/auth')


@auth.route('/login', methods=['POST'])
@json_keys_required(['email', 'password'])
def login():
    users_col = Api.collection('users')
    data = request.json

    user = format_mongo_data(users_col.find_one({'email': data['email']}))
    if not user:
        return api_response(message='User not found', status=401)

    if Api.bcrypt().check_password_hash(user['password'], data['password']):
        token = jwt_encode(email=user['email'], user_id=user['_id'])
        return api_response(
            message='User authenticated',
            data={
                'userId': user['_id'],
                'email': user['email'],
                'username': user['username'],
                'token': token,
            },
            status=200,
        )

    return api_response(message='Failed to verify user', status=401)


@auth.route('/register', methods=['POST'])
@json_keys_required(['username', 'email', 'password'])
def register():
    users_col = Api.collection('users')
    data = request.json

    if users_col.find_one({'email': {'$regex': data['email'], '$options': 'i'}}):
        return api_response(
            message='An account with this email already exists', status=422
        )

    if users_col.find_one({'username': {'$regex': data['username'], '$options': 'i'}}):
        return api_response(message='Username taken', status=422)

    user = users_col.insert_one(
        {
            'username': data['username'],
            'email': data['email'],
            'password': Api.bcrypt()
            .generate_password_hash(data['password'])
            .decode('utf-8'),
        }
    )

    return api_response(
        message='Registered new user',
        data={
            'userId': str(user.inserted_id),
            'username': data['username'],
            'email': data['email'],
        },
        status=201,
    )
