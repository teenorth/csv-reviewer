from flask import Blueprint, request
from api.util import api_response
from api import Api
import math
from api import database as db

batches = Blueprint('batches', __name__, url_prefix='/batches')


@batches.route('/<string:table_id>', methods=['GET'])
def index(table_id):
    rows = db.row.index(table_id=table_id, paginate=False)

    batch_size = 50
    batches = []
    batch = None
    for idx, row in enumerate(rows):
        if idx % batch_size == 0:
            if batch and len(batch):
                batch['total'] = len(batch['rows'])
                batches.append(batch)
            index = math.ceil((idx) / batch_size)
            batch = {
                'index': index + 1,
                'rows': [],
                'start': (index * batch_size) + 1,
                'end': (index + 1) * batch_size,
                'total': None
            }
        batch['rows'].append(row.get('_id'))

    return api_response(
        message='Batching a tables rows',
        data=batches
    )


@batches.route('/<int:batch_id>', methods=['GET'])
def show(batch_id):
    row_col = Api.collection('rows')
    rows = row_col.find()

    include_rows = request.args.get(
        'include_rows', default=False, type=bool)

    batch_size = 50
    batches = []
    batch = None
    for idx, row in enumerate(rows):
        if idx % batch_size == 0:
            if batch and len(batch):
                batch['total'] = len(batch['rows'])
                batches.append(batch)
            if batch and batch_id == batch['index']:
                get_batch = batch
                break
            index = math.floor((idx) / batch_size)
            batch = {
                'index': index + 1,
                'rows': [],
                'start': (index * batch_size) + 1,
                'end': (index + 1) * batch_size,
                'total': None
            }

        if include_rows:
            batch['rows'].append(row)
        else:
            batch['rows'].append(row.get('_id'))

    return api_response(
        message=include_rows,
        data=get_batch
    )
