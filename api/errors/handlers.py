from flask import make_response, jsonify
import traceback


def handle_api_exception(err):
    return make_response(
        jsonify({"message": err.message, "error": err.__class__.__name__}),
        err.status_code,
    )


def handle_500_exception(err):
    return make_response(
        jsonify(
            {
                "message": traceback.format_exc(limit=None, chain=True),
                "error": err.__class__.__name__,
            }
        ),
        500,
    )
