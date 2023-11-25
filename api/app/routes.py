from flask import Blueprint
from api.util import api_response

app = Blueprint('app', __name__, url_prefix='/app')


@app.route('/health', methods=['GET'])
def health():
    return api_response(message='Application healthy')
