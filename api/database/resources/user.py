from api import Api
from bson.objectid import ObjectId


def show(object_id=None):
    users_col = Api.collection('users')
    found = users_col.find_one({'_id': ObjectId(object_id)})
    return found
