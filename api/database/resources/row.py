from api import Api
from bson.objectid import ObjectId
import logging
from . import table
from api.errors import DocumentNotFound


def index(object_ids=None, table_id=None, page=1, per_page=10, paginate=True):
    rows_col = Api.collection("rows")
    cursor = None

    query = {}

    if not object_ids and not table_id:
        cursor = rows_col.find()
        logging.info("Retrieved all rows from the 'rows' collection.")
    else:
        if object_ids:
            object_ids = [ObjectId(id) for id in object_ids]
            query["_id"] = {"$in": object_ids}

        if table_id:
            query["table_id"] = ObjectId(table_id)

        cursor = rows_col.find(query)

    if paginate:
        cursor.skip((page - 1) * per_page).limit(per_page)

    rows = list(cursor)
    total_rows = len(rows)
    logging.info(f"Total {total_rows} rows retrieved from the 'rows' collection.")
    return rows


def show(object_id=None, history=False):
    rows_col = Api.collection("rows")

    query = {"_id": ObjectId(object_id)}
    root = rows_col.find_one(query)

    if not root:
        raise DocumentNotFound

    if history:
        row_history = []
        document = root
        previous = root
        while "base_id" in document:
            base_id = document["base_id"]
            document = rows_col.find_one({"_id": base_id})
            if not document:
                break
            diff = find_dict_difference_with_changes(document, previous)
            if diff:
                table_id = diff["table_id"]
                found_table = table.show(object_id=table_id)
                diff["table_name"] = found_table.get("title", None)
                row_history.append(diff)

        root["history"] = row_history
        logging.info(
            f"Retrieved row with ID {object_id} including history from the 'rows' collection."
        )
    else:
        logging.info(f"Retrieved row with ID {object_id} from the 'rows' collection.")

    table_id = root["table_id"]
    found_table = table.show(object_id=table_id)
    root["table_name"] = found_table.get("title", None)

    return root


def update(object_id, update={}):
    rows_col = Api.collection("rows")
    found = show(object_id)
    if update.get("fields"):
        found["fields"].update(update["fields"])
    rows_col.update_one({"_id": found.get("_id")}, {"$set": found})
    found = show(object_id)
    logging.info(f"Updated row with ID {object_id} in the 'rows' collection.")
    return found


def update_many(updates=[]):
    for row in updates:
        id = row.pop("_id")
        fields = row.copy()
        update(id, fields)
        logging.info(f"Updated row with ID {id} in the 'rows' collection.")


def find_dict_difference_with_changes(old_dict, new_dict):
    difference = {
        "_id": old_dict["_id"],
        "table_id": old_dict["table_id"],
        "base_id": old_dict["base_id"],
    }
    keys = set(list(old_dict["fields"].keys()) + list(new_dict["fields"].keys()))

    had_diff = False
    for key in keys:
        if old_dict["fields"].get(key) != new_dict["fields"].get(key):
            had_diff = True
            difference[key] = {
                "before": old_dict["fields"].get(key),
                "after": new_dict["fields"].get(key),
            }

    return difference if had_diff else None
