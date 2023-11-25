from api import Api
from bson.objectid import ObjectId
import logging
from api.util.mongo import push_pull_to_array
from . import timeline
from datetime import datetime


def index(object_ids=None, timeline_id=None, page=1, per_page=10, paginate=True, row_ids=False):
    tables_col = Api.collection('tables')
    cursor = None

    query = {}

    if timeline_id:
        query['timeline_id'] = ObjectId(timeline_id)

    if object_ids:
        object_ids = [ObjectId(id) for id in object_ids]
        query['_id'] = {'$in': object_ids}

    cursor = tables_col.find(query)

    cursor.sort('created_at', -1)

    if paginate:
        cursor.skip((page - 1) * per_page).limit(per_page)

    tables = list(cursor)

    if row_ids:
        for table in tables:
            table['row_ids'] = table.get('row_ids', [])
    else:
        for table in tables:
            table['row_ids'] = len(table.get('row_ids', []))

    total_tables = len(tables)
    logging.info(
        f"Retrieved {total_tables} tables from the 'tables' collection.")
    return tables


def show(object_id=''):
    tables_col = Api.collection('tables')
    found = tables_col.find_one({
        '_id': ObjectId(object_id)
    })
    logging.info(
        f"Retrieved table with ID {object_id} from the 'tables' collection.")
    return found


def create(title='', description='', timeline_id=''):
    tables_col = Api.collection('tables')
    new_document = {
        'title': title,
        'description': description,
        'timeline_id': timeline_id,
        'row_ids': [],
        'created_at': datetime.now()
    }
    result = tables_col.insert_one(new_document)
    timeline.update(
        timeline_id,
        table_ids={
            'push': [result.inserted_id]
        }
    )
    new_document['_id'] = result.inserted_id
    logging.info(
        f"Created a new table with ID {new_document['_id']} in the 'tables' collection.")
    return new_document


def update(object_id='', row_ids=None):
    tables_col = Api.collection('tables')
    update_data = {}
    found = show(object_id)

    if row_ids is not None:
        push_pull_to_array(update_data, 'row_ids', row_ids)

    tables_col.update_one(
        {'_id': found.get('_id')},
        update_data
    )
    found = show(object_id)
    logging.info(
        f"Updated table with ID {object_id} in the 'tables' collection.")
    return found
