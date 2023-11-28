from flask import Blueprint, request
from api.util import api_response
from api.middleware import json_keys_required, json_keys_accepted
from api import database as db
from api.database.repositories import RowRepository

rows = Blueprint("rows", __name__, url_prefix="/rows")


@rows.route("/<string:row_id>", methods=["PUT"])
@json_keys_required(["updates"])
@json_keys_accepted(["updates"])
def update(row_id):
    data = request.json
    db.row.update(row_id, data.get("updates"))

    return api_response(message="Successful")


@rows.route("/<string:row_id>", methods=["GET"])
def show(row_id):
    history = request.args.get("history", default=False, type=bool)

    result = db.row.show(row_id, history=history)

    return api_response(message="Successful", data=result)


@rows.route("/", methods=["PUT"])
def update_many():
    data = request.json
    new_review = db.review.create(message=data["message"], updates=data["updates"])
    db.row.update_many(data["updates"], new_review["_id"])

    return api_response(message="Successful")


@rows.route("/insert-one", methods=["POST"])
def insert_one():
    data = request.json
    row_repo = RowRepository()
    row_model = row_repo.insert_one(data)

    return api_response(message="Successful", data=row_model)
