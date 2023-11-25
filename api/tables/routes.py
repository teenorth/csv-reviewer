from flask import Blueprint, request
from api.util import api_response
from api import database as db

tables = Blueprint('tables', __name__, url_prefix='/tables')


@tables.route('/<string:table_id>/rows', methods=['GET'])
def rows(table_id):
    rows = db.row.index(table_id=table_id, paginate=False)

    return api_response(message='Indexing tables rows', data=rows)
