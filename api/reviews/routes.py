from flask import Blueprint, request
from api.util import api_response
from api import database as db, Api
from api.middleware import jwt_required
from flask import send_file, Response
from io import BytesIO

reviews = Blueprint('reviews', __name__, url_prefix='/reviews')


@reviews.route('/', methods=['GET'])
def index():
    result = db.review.index()
    return api_response(message='Indexing reviews', data=result)


@reviews.route('/<string:review_id>', methods=['GET'])
def show(review_id):
    result = db.review.show(review_id)
    return api_response(message='Showing review', data=result)


@reviews.route('/', methods=['POST'])
@jwt_required
def create():
    data = request.json
    result = db.review.create(data['message'], data['updates'])

    return api_response(message='Created review', data=result)


@reviews.route('/<string:review_id>', methods=['PUT'])
@jwt_required
def update(review_id):
    data = request.json
    result = db.review.update(
        review_id,
        message=data.get('message'),
        amendment=data.get('amendment'),
        approved=data.get('approved'),
        committed=data.get('committed'),
    )

    return api_response(message='Updated review', data=result)


@reviews.route('/<string:review_id>/comments', methods=['GET'])
def comments(review_id):
    found_review = db.review.show(object_id=review_id)
    # TODO: Refactor into database method
    comments_col = Api.collection('comments')
    found_comments = comments_col.find({'_id': {'$in': found_review['comment_ids']}})

    grouped_comments = {}
    for comment in found_comments:
        row_id = str(comment['row_id'])
        if row_id not in grouped_comments:
            grouped_comments[row_id] = []
        grouped_comments[row_id].append(comment)

    return api_response(message='Indexing reviews comments', data=grouped_comments)


@reviews.route('/<string:review_id>/export-csv', methods=['GET'])
def export_csv(review_id):
    csv_file = db.review.export_as_csv(object_id=review_id)

    return send_file(
        BytesIO(csv_file),
        as_attachment=True,
        download_name='data.csv',
        mimetype='text/csv',
        conditional=True,
    )
