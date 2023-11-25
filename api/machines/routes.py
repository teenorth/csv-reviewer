from flask import Blueprint, request
from api.middleware import (
    jwt_required,
    json_keys_required,
    json_keys_accepted,
    has_role,
)
from api.util import api_response
from api.util.roles import roles
import jwt
from api import Api

machines = Blueprint('machines', __name__, url_prefix='/machines')


@machines.route('/create-token', methods=['GET'])
@jwt_required
@has_role([roles.SUPER_ADMIN])
@json_keys_required(['id'])
@json_keys_accepted(['id', 'roles'])
def create_token():
    data = request.json
    token_roles = (
        [role for role in data.get('roles')]
        if data.get('roles') and len(data.get('roles'))
        else roles.MACHINE
    )
    token = {
        'sub': data.get('id'),
        'roles': token_roles,
    }
    if data.get('oid'):
        token['oid'] = data.get('oid')
    encoded_token = jwt.encode(token, Api.config('JWT_SECRET_KEY'), algorithm='HS256')
    return api_response(message='Index devices', data={'token': encoded_token})
