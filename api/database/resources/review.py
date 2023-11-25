from api import Api
from bson.objectid import ObjectId
import logging
from . import row, user
from datetime import datetime
from api.util.errors import ReviewCommitted
from api.util import get_user_id
import logging
import copy
from api.util.mongo import push_pull_to_array
import csv
from io import StringIO


def index(object_ids=None, page=1, per_page=10, paginate=True):
    reviews_col = Api.collection("reviews")
    cursor = None

    if not object_ids:
        cursor = reviews_col.find()
        logging.info(f"Retrieved all reviews from the 'reviews' collection.")
    else:
        object_ids = [ObjectId(id) for id in object_ids]
        cursor = reviews_col.find({"_id": {"$in": object_ids}})
        logging.info(
            f"Retrieved reviews with IDs {object_ids} from the 'reviews' collection."
        )

    if paginate:
        cursor.skip((page - 1) * per_page).limit(per_page)

    reviews = list(cursor)
    logging.info(f"Total {len(reviews)} reviews retrieved.")
    return reviews


def show(object_id=None):
    reviews_col = Api.collection("reviews")
    found = reviews_col.find_one({"_id": ObjectId(object_id)})
    logging.info(f"Retrieved review with ID {object_id} from the 'reviews' collection.")
    return found


def create(message="", updates=[]):
    reviews_col = Api.collection("reviews")
    rows = {}
    row_ids = []

    found_user = user.show(object_id=get_user_id())

    for update in updates:
        id = ObjectId(update["_id"])
        update["_id"] = id
        row_ids.append(id)

        old_row = row.show(id)
        new_row = copy.deepcopy(old_row)
        new_row["fields"].update(update["fields"])

        row_id = str(id)
        rows[row_id] = {
            "old": old_row,
            "new": new_row,
            "base": row.show(old_row["base_id"]) if old_row["base_id"] else None,
            "update": update,
            "amendments": [],
        }

    new_document = {
        "created_at": datetime.now(),
        "message": message,
        "rows": rows,
        "approved": False,
        "committed": False,
        "comment_ids": [],
        "row_ids": row_ids,
        "timeline_id": old_row["timeline_id"],
        "user": {"_id": found_user['_id'], "username": found_user['username']},
        "created_at": datetime.now(),
    }

    result = reviews_col.insert_one(new_document)
    new_document["_id"] = result.inserted_id
    logging.info(
        f"Created a new review with ID {new_document['_id']} in the 'reviews' collection."
    )
    return new_document


def update(
    object_id="",
    message="",
    amendment=None,
    approved=None,
    committed=None,
    comment_ids=None,
):
    update_data = {}
    found = show(object_id)

    if found["committed"]:
        raise ReviewCommitted

    if message:
        update_data["message"] = message

    if amendment is not None:
        current_rows = found.get("rows", {})
        for update in amendment.get("updates", []):
            amendment_id = update["_id"]
            update["_id"] = ObjectId(update["_id"])
            if amendment_id in current_rows:
                current_row = current_rows[amendment_id]
                current_row["new"] = row.show(object_id=amendment_id)
                current_row["amendments"].append(
                    create_amendment(
                        amendment["message"], current_row["update"], update
                    )
                )
                current_row["update"] = update
                current_row["new"]["fields"].update(update["fields"])
                current_rows[amendment_id] = current_row
            else:
                logging.warning(f"Row with ID {amendment_id} not found.")
        update_data["$set"] = {"rows": current_rows}

    if comment_ids:
        push_pull_to_array(update_data, 'comment_ids', comment_ids)

    if approved is not None:
        update_data["$set"] = {"approved": approved}

    if committed is not None:
        update_data["$set"] = {"committed": committed}

    if update_data:
        reviews_col = Api.collection("reviews")
        reviews_col.update_one({"_id": found["_id"]}, update_data)
        logging.info(f"Updated review with ID {object_id} in the 'reviews' collection.")

    found = show(object_id)

    if found["committed"]:
        row.update_many(updates=[r["update"] for r in found["rows"].values()])
        logging.info(
            f"Updated associated rows after review with ID {object_id} was committed."
        )

    return found


def rebase(object_id=None):
    reviews_col = Api.collection("reviews")
    rows_col = Api.collection("rows")
    found = show(object_id=object_id)
    before_row_ids = found["row_ids"]
    rows = row.index(object_ids=before_row_ids, paginate=False)

    current_rows = found["rows"]
    found["rows"] = {}
    found["row_ids"] = []

    for row_document in rows:
        base_row = row_document
        old_row = rows_col.find_one({"base_id": row_document["_id"]})
        found["row_ids"].append(old_row["_id"])

        review_row = current_rows[str(base_row["_id"])]

        review_row["base"] = base_row
        review_row["old"] = old_row

        review_row["update"]["_id"] = old_row["_id"]
        new_row = copy.deepcopy(old_row)
        new_row["fields"].update(review_row["update"]["fields"])
        review_row["new"] = new_row

        found["rows"][str(old_row["_id"])] = review_row

        reviews_col.update_one({"_id": found["_id"]}, {"$set": found})
        logging.info(
            f"Rebased review review with ID {object_id}. Row IDs before {before_row_ids} and after {found['row_ids']}"
        )


def export_as_csv(object_id=None):
    found = show(object_id=object_id)

    csv_data = []

    for row in found['rows'].values():
        if not len(csv_data):
            csv_data.append(list(row['new']['fields'].keys()))
        csv_data.append(list(row['new']['fields'].values()))

    csv_buffer = StringIO()
    csv_writer = csv.writer(csv_buffer, quoting=csv.QUOTE_ALL)
    csv_writer.writerows(csv_data)
    csv_buffer.seek(0)

    return csv_buffer.getvalue().encode()


def create_amendment(message="", before={}, after={}):
    current_datetime = datetime.now()
    found_user = user.show(object_id=get_user_id())
    return {
        "message": message,
        "before": before,
        "after": after,
        "created_at": current_datetime,
        "user": {"_id": found_user['_id'], "username": found_user['username']},
    }
