from flask import Blueprint, request
from api.util import api_response
from api import Api
import math
from api import database as db
from api.middleware import jwt_required
from api.util import get_user_id
from datetime import datetime

comments = Blueprint('comments', __name__, url_prefix='/comments')


@comments.route('/', methods=['POST'])
@jwt_required
def create():
    data = request.json
    found_review = db.review.show(object_id=data['review_id'])
    comments_col = Api.collection('comments')

    found_row = db.row.show(object_id=data['row_id'])
    found_user = db.user.show(object_id=get_user_id())

    new_comment = {
        "content": data['content'],
        "row_id": found_row['_id'],
        'created_at': datetime.now(),
        "user": {"_id": found_user['_id'], "username": found_user['username']},
    }

    result = comments_col.insert_one(new_comment)
    new_comment['_id'] = result.inserted_id

    db.review.update(
        object_id=found_review['_id'], comment_ids={'push': [new_comment['_id']]}
    )

    return api_response(message='Created comment', data=new_comment, status=201)
