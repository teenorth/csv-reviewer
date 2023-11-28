from api import Api
from bson.objectid import ObjectId
import logging
from api.util.mongo import push_pull_to_array
from datetime import datetime
from . import table, review
import csv
from io import TextIOWrapper
from api.errors import NoFileAttached, NoFileSelected


def index(object_ids=None, page=1, per_page=10, paginate=True):
    timelines_col = Api.collection("timelines")
    cursor = None

    if not object_ids:
        cursor = timelines_col.find()
        logging.info("Retrieved all timelines from the 'timelines' collection.")
    else:
        object_ids = [ObjectId(id) for id in object_ids]
        cursor = timelines_col.find({"_id": {"$in": object_ids}})
        logging.info(
            f"Retrieved timelines with IDs {object_ids} from the 'timelines' collection."
        )

    if paginate:
        cursor.skip((page - 1) * per_page).limit(per_page)

    timelines = list(cursor)
    total_timelines = len(timelines)
    logging.info(f"Total {total_timelines} timelines retrieved.")
    return timelines


def show(object_id=""):
    timelines_col = Api.collection("timelines")
    found = timelines_col.find_one({"_id": ObjectId(object_id)})
    logging.info(
        f"Retrieved timeline with ID {object_id} from the 'timelines' collection."
    )
    return found


def create(title=None):
    timelines_col = Api.collection("timelines")
    new_document = {"title": title, "created_at": datetime.now()}
    result = timelines_col.insert_one(new_document)
    new_document["_id"] = result.inserted_id
    logging.info(
        f"Created a new timeline with ID {new_document['_id']} in the 'timelines' collection."
    )
    return new_document


def update(object_id=None, table_ids=None):
    timelines_col = Api.collection("timelines")
    update_data = {}
    found = show(object_id)

    if table_ids is not None:
        push_pull_to_array(update_data, "table_ids", table_ids)

    timelines_col.update_one({"_id": found["_id"]}, update_data)
    found = show(object_id)
    logging.info(f"Updated timeline with ID {object_id} in the 'timelines' collection.")
    return found


def snapshot(object_id=None, title=None, description=None):
    rows_col = Api.collection("rows")
    reviews_col = Api.collection("reviews")
    tables_col = Api.collection("tables")

    found = show(object_id)

    new_table = table.create(
        title=title, description=description, timeline_id=found["_id"]
    )

    pipeline = [
        {"$match": {"_id": {"$in": found["table_ids"]}}},
        {"$sort": {"created_at": -1}},
        {"$limit": 1},
    ]
    most_recent_table = list(tables_col.aggregate(pipeline))[0]
    logging.info("most_recent_table: %s", most_recent_table["row_ids"])

    pipeline = [
        {"$match": {"_id": {"$in": most_recent_table["row_ids"]}}},
        {"$set": {"table_id": new_table["_id"], "base_id": "$_id"}},
        {"$project": {"_id": 0}},
    ]
    rows = list(rows_col.aggregate(pipeline))

    result = rows_col.insert_many(rows)

    table.update(object_id=new_table["_id"], row_ids={"push": result.inserted_ids})

    reviews = list(reviews_col.find({"row_ids": {"$in": most_recent_table["row_ids"]}}))
    logging.info("reviews: %s", result)
    for review_doc in reviews:
        review.rebase(object_id=review_doc["_id"])

    logging.info(f"Created a snapshot for timeline with ID {object_id}.")

    return {"table_id": new_table["_id"]}


def import_csv(files=None, table_id=None, timeline_id=None):
    rows_col = Api.collection("rows")

    result = None

    if "csv_file" not in files:
        raise NoFileAttached

    file = files["csv_file"]

    if file.filename == "":
        raise NoFileSelected

    if file:
        try:
            text_file = TextIOWrapper(file, encoding="utf-8", newline="")
            data = csv.DictReader(text_file)
            imported_rows = []

            for row in data:
                row_data = {}
                row_data["fields"] = row
                if row_data["fields"].get("id"):
                    row_data["fields"]["id"] = int(row_data["fields"]["id"])
                row_data["table_id"] = table_id
                row_data["base_id"] = None
                row_data["timeline_id"] = timeline_id

                imported_rows.append(row_data)

            if imported_rows:
                result = rows_col.insert_many(imported_rows)
                logging.info(
                    f"Imported {len(imported_rows)} rows into the 'rows' collection."
                )

            return result

        except Exception as e:
            logging.error(f"An error occurred while importing CSV: {str(e)}")
            raise e
