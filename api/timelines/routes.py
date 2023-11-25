from flask import Blueprint, request
from api.util import api_response
from api import database as db, Api

timelines = Blueprint("timelines", __name__, url_prefix="/timelines")


@timelines.route("/", methods=["GET"])
def index():
    timelines = db.timeline.index()

    return api_response(message="Indexing timelines", data=timelines)


@timelines.route("/<string:timeline_id>/tables", methods=["GET"])
def tables(timeline_id):
    tables = db.table.index(timeline_id=timeline_id)

    return api_response(message="Indexing timelines tables", data=tables)


@timelines.route("/<string:timeline_id>/snapshot", methods=["POST"])
def snapshot(timeline_id):
    data = request.json
    result = db.timeline.snapshot(
        timeline_id, title=data["title"], description=data["description"]
    )

    return api_response(message="Snapshot created", data=result)


@timelines.route("/import-csv", methods=["POST"])
def import_csv():
    data = {key: value for key, value in request.form.items()}

    timeline = db.timeline.create(title=data.get("timeline_title"))

    table = db.table.create(
        title=data.get("table_title"),
        description=data.get("description"),
        timeline_id=timeline["_id"],
    )

    result = db.timeline.import_csv(
        files=request.files, table_id=table["_id"], timeline_id=timeline["_id"]
    )

    db.table.update(object_id=table["_id"], row_ids={"push": result.inserted_ids})

    return api_response(
        message="Imported successfully",
        data={"timeline_id": timeline["_id"], "table_id": table["_id"]},
        status=201,
    )


@timelines.route("/<string:timeline_id>/reviews", methods=["GET"])
def reviews(timeline_id):
    # TODO: Integrate this into the review index

    reviews_col = Api.collection("reviews")
    found = db.timeline.show(object_id=timeline_id)
    reviews = reviews_col.find({"timeline_id": found["_id"]})

    return api_response(
        message="Indexing timelines reviews",
        data=reviews,
    )
