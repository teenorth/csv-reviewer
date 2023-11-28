from flask import make_response, jsonify


def handle_api_exception(e):
    return make_response(jsonify({"message": e.message}), e.status_code)
